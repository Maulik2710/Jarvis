# tools/app_launcher.py
import os
import subprocess
import webbrowser

# Map common app names to OS commands or file paths
APP_PATHS = {
    "notepad": "notepad.exe",
    "calc": "calc.exe",
    "cmd": "cmd.exe",
    "code": "code",  # VS Code if added to PATH
}

def launch_application(app_name: str) -> str:
    """
    Launches a local desktop application or system utility.
    :param app_name: Name of application (e.g. 'notepad', 'calc', 'code', 'cmd').
    """
    app = app_name.lower().strip()
    if app in APP_PATHS:
        try:
            subprocess.Popen(APP_PATHS[app])
            return f"Successfully launched {app_name}."
        except Exception as e:
            return f"Error launching {app_name}: {str(e)}"
    
    # Fallback execution attempt
    try:
        os.system(f"start {app}")
        return f"Attempted to start application: {app_name}"
    except Exception as e:
        return f"Failed to launch {app_name}: {str(e)}"

def open_url(url: str) -> str:
    """
    Opens a URL directly in default browser.
    :param url: Web link or domain (e.g., 'youtube.com', 'https://github.com').
    """
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    webbrowser.open(url)
    return f"Opened {url} in your browser."