# agents/workflow_agent.py
import json
import re
import webbrowser
import time
from pathlib import Path
from config import BASE_DIR
from tools.app_launcher import launch_application, open_url
from tools.media_control import play_music
from tools.process_manager import terminate_process_tree

PROTOCOLS_FILE = BASE_DIR / "memory" / "protocols.json"
MAX_ALLOWED_CODES = 50

class RoutineEngine:
    def __init__(self):
        PROTOCOLS_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not PROTOCOLS_FILE.exists():
            with open(PROTOCOLS_FILE, "w") as f:
                json.dump({}, f)

    def _read_protocols(self) -> dict:
        try:
            with open(PROTOCOLS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_protocols(self, data: dict):
        with open(PROTOCOLS_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def _read_routines(self) -> dict:
        return self._read_protocols()

    def get_protocol_count(self) -> int:
        return len(self._read_protocols())

    def get_routine_details(self, code_name: str) -> str:
        data = self._read_protocols()
        clean = code_name.lower().strip().replace("code ", "").replace("protocol ", "").replace("execute ", "")
        if clean in data:
            return f"Protocol '{clean}' is configured with actions: {data[clean]}."
        return f"Protocol '{code_name}' does not exist."

    def _split_into_atomic_actions(self, raw_input):
        """
        Takes raw string/list input and extracts discrete, clean actions.
        Handles comma-separated, 'and', 'then', and function-call chains.
        """
        raw_items = []
        if isinstance(raw_input, str):
            try:
                parsed = json.loads(raw_input.replace("'", '"'))
                if isinstance(parsed, list):
                    raw_items = parsed
                else:
                    raw_items = [str(raw_input)]
            except Exception:
                raw_items = [str(raw_input)]
        elif isinstance(raw_input, list):
            raw_items = raw_input
        else:
            raw_items = [str(raw_input)]

        atomic_actions = []
        for item in raw_items:
            if isinstance(item, dict):
                atomic_actions.append(item)
                continue

            text = str(item).strip()
            # Split sentences that contain multiple commands
            parts = re.split(r',|\band then\b|\balso\b|\band\b', text, flags=re.IGNORECASE)
            for part in parts:
                clean_part = part.strip(" '\"():;,.")
                if clean_part:
                    atomic_actions.append(clean_part)

        return atomic_actions

    def save_routine(self, code_name: str, actions) -> str:
        """Saves a multi-action protocol (up to 50 protocols)."""
        data = self._read_protocols()
        clean_code = code_name.lower().strip().replace("code ", "").replace("protocol ", "")

        if clean_code not in data and len(data) >= MAX_ALLOWED_CODES:
            return f"Cannot save '{clean_code}'. Limit of {MAX_ALLOWED_CODES} protocols reached."

        parsed_actions = self._split_into_atomic_actions(actions)
        data[clean_code] = parsed_actions
        self._write_protocols(data)
        return f"Protocol '{clean_code}' configured with {len(parsed_actions)} actions ({len(data)}/{MAX_ALLOWED_CODES} slots used)."

    def delete_routine(self, code_name: str) -> str:
        data = self._read_protocols()
        clean_code = code_name.lower().strip().replace("code ", "").replace("protocol ", "")

        if clean_code in data:
            del data[clean_code]
            self._write_protocols(data)
            return f"Protocol '{clean_code}' deleted."
        return f"Protocol '{code_name}' does not exist."

    def _execute_step(self, step) -> str:
        # Structured dictionary step
        if isinstance(step, dict):
            act_type = str(step.get("type", "")).lower()
            target = str(step.get("target", "")).strip(" '\"():;,.")

            if any(k in act_type for k in ["kill", "close", "terminate", "stop", "end", "process"]):
                return terminate_process_tree(target or act_type)
            elif any(k in act_type for k in ["url", "website", "open_url", "browser"]):
                return open_url(target)
            elif any(k in act_type for k in ["music", "song", "youtube", "play_music", "soundtrack"]):
                play_music(target)
                return f"Playing {target}"
            elif any(k in act_type for k in ["app", "application", "launch", "launch_application"]):
                return launch_application(target)

        # Plain-text string step
        s = str(step).strip()
        s_lower = s.lower()

        # 1. Termination checks
        if any(k in s_lower for k in ["terminate", "close", "kill", "end task"]):
            clean_app = (
                s_lower.replace("terminate_process_tree", "")
                .replace("target_name:", "")
                .replace("close", "")
                .replace("kill", "")
                .replace("terminate", "")
                .replace("all the running", "")
                .replace("all the task of", "")
                .replace("all tasks of", "")
                .replace("task", "")
                .replace("browser", "")
                .strip(" '\"():;,.")
            )
            return terminate_process_tree(clean_app or "chrome")

        # 2. Music / Soundtrack checks
        elif any(k in s_lower for k in ["play_music", "play", "soundtrack", "song", "music"]):
            query = (
                s_lower.replace("play_music", "")
                .replace("play", "")
                .replace("soundtrack", "")
                .replace("music", "")
                .replace("song", "")
                .replace("of", "")
                .strip(" '\"():;,.")
            )
            play_music(query or "interstellar")
            return f"Playing {query or 'interstellar'}"

        # 3. URL / Website checks
        elif any(k in s_lower for k in ["open_url", "http", ".com", ".org", "github", "youtube", "leetcode"]):
            url_match = re.search(r"https?://[^\s'\"]+|[a-zA-Z0-9.-]+\.(?:com|org|net|io|in)", s)
            if url_match:
                target_url = url_match.group(0).rstrip(";,.")
            elif "github" in s_lower:
                target_url = "https://github.com"
            elif "youtube" in s_lower:
                target_url = "https://youtube.com"
            else:
                target_url = s.replace("open_url", "").replace("open", "").strip(" '\"():;,.")
            return open_url(target_url)

        # 4. App Launch checks
        elif any(k in s_lower for k in ["launch_application", "launch", "open", "code", "vscode", "vs code"]):
            clean_app = (
                s_lower.replace("launch_application", "")
                .replace("launch", "")
                .replace("open", "")
                .strip(" '\"():;,.")
            )
            return launch_application(clean_app or "code")

        return f"Executed step: {s}"

    def execute_routine(self, code_name: str) -> str:
        data = self._read_protocols()
        clean_code = code_name.lower().strip().replace("code ", "").replace("protocol ", "").replace("execute ", "")

        matched_key = None
        for key in data:
            if key == clean_code or key in clean_code or clean_code in key:
                matched_key = key
                break

        if not matched_key:
            return f"Protocol '{code_name}' not found."

        raw_actions = data[matched_key]
        atomic_actions = self._split_into_atomic_actions(raw_actions)

        executed_steps = []
        for step in atomic_actions:
            try:
                res = self._execute_step(step)
                executed_steps.append(res)
            except Exception as e:
                executed_steps.append(f"Step failed ({e})")
            time.sleep(0.6)  # Stagger execution so apps launch cleanly

        return f"Protocol '{matched_key}' activated: " + ", ".join(executed_steps) + "."

    def get_all_routines_string(self) -> str:
        data = self._read_protocols()
        if not data:
            return "None."
        return ", ".join(data.keys())