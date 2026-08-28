import time
import requests
import sys

class GPULock:
    """
    WSL2 Python 脚本与 Windows 宿主机大模型服务独占调度锁助手。
    使用 Python Context Manager (with 语句) 确保在发生任何异常退出时，GPU 锁都能被安全释放。
    
    使用示例:
    ---------
    from gpu_lock_helper import GPULock
    
    with GPULock(server_url="http://127.0.0.1:8085", owner="openmontage"):
        run_video_generation()
    """
    
    def __init__(self, server_url="http://127.0.0.1:8085", owner="openmontage", retry_interval=10, max_retries=1, fallback_on_fail=True):
        server_url = server_url.rstrip('/')
        
        # 自动识别 WSL2 网关并进行 host 替换 (以防 localhost/127.0.0.1 在 WSL2 内无法通信)
        if "127.0.0.1" in server_url or "localhost" in server_url:
            import os
            import re
            
            # 探测是否在 WSL 中运行
            is_wsl = False
            if os.path.exists('/proc/version'):
                with open('/proc/version', 'r') as f:
                    if 'microsoft' in f.read().lower():
                        is_wsl = True
                        
            if is_wsl:
                host_ip = "127.0.0.1"
                if os.path.exists('/etc/resolv.conf'):
                    with open('/etc/resolv.conf', 'r') as f:
                        for line in f:
                            if line.strip().startswith("nameserver"):
                                parts = line.split()
                                if len(parts) >= 2:
                                    host_ip = parts[1].strip()
                                    break
                if host_ip != "127.0.0.1":
                    server_url = server_url.replace("127.0.0.1", host_ip).replace("localhost", host_ip)
                    print(f"[GPU Lock] 自动识别并重定向 WSL 宿主机网关: {server_url}")

        self.server_url = server_url
        self.owner = owner
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.fallback_on_fail = fallback_on_fail
        self._locked = False

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self):
        print(f"\n[GPU Lock] 正在向网关 {self.server_url} 申请 GPU 独占锁 (所有者: {self.owner})...")
        attempts = 0
        while True:
            attempts += 1
            try:
                url = f"{self.server_url}/api/gpu/acquire"
                response = requests.post(url, json={"owner": self.owner}, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        print("[GPU Lock] 锁申请成功！本地大模型显存已被完全驱逐卸载。")
                        self._locked = True
                        return True
                    else:
                        reason = data.get("reason", "未知原因")
                        print(f"[GPU Lock] 显存正忙：{reason}。")
                else:
                    print(f"[GPU Lock] 网关响应异常 (HTTP {response.status_code})。")
            except requests.exceptions.RequestException as e:
                print(f"[GPU Lock] 无法连接到调度服务器：{e}。", file=sys.stderr)
            
            # 判断是否触发降级或超出尝试上限
            if self.max_retries is not None and attempts >= self.max_retries:
                if self.fallback_on_fail:
                    print("[GPU Lock] [Warning] 无法连接到调度锁服务器或请求超时，已自动触发安全防灾降级，进入无锁直连运行模式。", file=sys.stderr)
                    self._locked = False
                    return False
                else:
                    raise ConnectionError(f"无法连接到 GPU 调度锁服务器，已达到最大尝试次数 ({self.max_retries})。")
            
            print(f"[GPU Lock] 将在 {self.retry_interval} 秒后重试...")
            time.sleep(self.retry_interval)

    def release(self):
        if not self._locked:
            return
        
        print(f"\n[GPU Lock] 正在释放 GPU 锁...")
        try:
            url = f"{self.server_url}/api/gpu/release"
            response = requests.post(url, json={"owner": self.owner}, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print("[GPU Lock] GPU 锁成功释放，微信网桥已恢复排队的 AI 任务。")
                    self._locked = False
                else:
                    print(f"[GPU Lock] 锁释放失败：{data.get('error', '未知错误')}", file=sys.stderr)
            else:
                print(f"[GPU Lock] 释放请求网关响应异常 (HTTP {response.status_code})", file=sys.stderr)
        except requests.exceptions.RequestException as e:
            print(f"[GPU Lock] 无法连接到调度服务器释放锁：{e}", file=sys.stderr)
