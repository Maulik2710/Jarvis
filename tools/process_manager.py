# tools/process_manager.py
import os
import re
import subprocess
import psutil

COMMON_APPS = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "vs code": "code.exe",
    "vscode": "code.exe",
    "code": "code.exe",
    "notepad": "notepad.exe",
    "spotify": "spotify.exe",
    "edge": "msedge.exe",
    "msedge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "calculator": "calc.exe",
    "discord": "discord.exe",
    "telegram": "telegram.exe",
    "vlc": "vlc.exe"
}

def terminate_process_tree(target_name: str) -> str:
    """
    Terminates and force-closes all running instances of a specified application or process (e.g. Chrome, VS Code).
    """
    raw = str(target_name).lower().strip()
    
    clean_target = None
    for key in COMMON_APPS:
        if key in raw:
            clean_target = key
            break
            
    if not clean_target:
        words = re.findall(r'\b[a-zA-Z0-9_-]+\b', raw)
        filtered = [w for w in words if w not in ["close", "kill", "terminate", "stop", "end", "all", "the", "task", "tasks", "of", "browser", "app", "application"]]
        clean_target = filtered[-1] if filtered else raw

    exe_name = COMMON_APPS.get(clean_target, f"{clean_target}.exe" if not clean_target.endswith(".exe") else clean_target)

    # 1. Try Windows taskkill using absolute system path
    taskkill_bin = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32", "taskkill.exe")
    killed_any = False
    
    if os.path.exists(taskkill_bin):
        try:
            res = subprocess.run([taskkill_bin, "/F", "/T", "/IM", exe_name], capture_output=True, text=True)
            if res.returncode == 0 or "SUCCESS" in res.stdout:
                killed_any = True
        except Exception:
            pass

    # 2. psutil fallback
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pname = (proc.info['name'] or '').lower()
            target_stem = clean_target.replace(".exe", "")
            if target_stem in pname:
                proc.kill()
                killed_any = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if killed_any:
        return f"Successfully terminated all processes for '{clean_target}'."
    else:
        return f"No active process found for '{clean_target}'."

def get_system_resource_usage() -> str:
    cpu_percent = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory()
    battery = psutil.sensors_battery()
    bat_str = f", Battery: {battery.percent}%" if battery else ""
    return f"CPU: {cpu_percent}%, RAM: {ram.percent}% used ({round(ram.used / (1024**3), 1)}GB / {round(ram.total / (1024**3), 1)}GB){bat_str}."