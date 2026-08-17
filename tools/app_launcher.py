# tools/app_launcher.py
import os
import re
import subprocess
import webbrowser

def open_url(url: str) -> str:
    """
    Opens a website URL in the default web browser.
    :param url: The website URL to open (e.g. 'https://github.com', 'youtube.com').
    """
    clean_url = str(url).strip(" '\"();,.")
    
    # Extract clean URL if surrounding text is present
    url_match = re.search(r"https?://[^\s'\"]+|[a-zA-Z0-9.-]+\.(?:com|org|net|io|in)", clean_url)
    if url_match:
        clean_url = url_match.group(0).rstrip(";,.")

    if not clean_url.startswith("http://") and not clean_url.startswith("https://"):
        clean_url = f"https://{clean_url}"

    try:
        webbrowser.open(clean_url)
        return f"Opened {clean_url}"
    except Exception as e:
        return f"Failed to open URL '{clean_url}': {e}"


# In tools/app_launcher.py
def launch_application(app_name: str) -> str:
    # Strip any prefix artifact like app_name:
    clean_name = str(app_name).lower().strip()
    clean_name = re.sub(r'^[a-zA-Z_]+:\s*', '', clean_name)
    clean_name = clean_name.replace("launch", "").replace("open", "").strip(" '\"():;,.")

    # 1. VS Code / Code
    if clean_name in ["code", "vscode", "vs code", "visual studio code"]:
        user_vscode = os.path.expandvars(r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe")
        prog_vscode = r"C:\Program Files\Microsoft VS Code\Code.exe"
        
        if os.path.exists(user_vscode):
            os.startfile(user_vscode)
            return "Launched VS Code"
        elif os.path.exists(prog_vscode):
            os.startfile(prog_vscode)
            return "Launched VS Code"
        else:
            try:
                subprocess.Popen(["cmd", "/c", "code"], shell=True)
                return "Launched VS Code"
            except Exception as e:
                return f"Error launching VS Code: {e}"

    # 2. Google Chrome
    elif clean_name in ["chrome", "google chrome"]:
        chrome_path_1 = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        chrome_path_2 = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path_1):
            os.startfile(chrome_path_1)
            return "Launched Chrome"
        elif os.path.exists(chrome_path_2):
            os.startfile(chrome_path_2)
            return "Launched Chrome"
        else:
            os.system("start chrome")
            return "Launched Chrome"

    # 3. Generic system applications
    try:
        subprocess.Popen(["cmd", "/c", "start", "", clean_name], shell=True)
        return f"Launched {clean_name}"
    except Exception as e:
        return f"Failed to launch {clean_name}: {e}"