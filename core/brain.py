# core/brain.py
import json
import re
import inspect
from openai import OpenAI
from config import LOCAL_MODEL, OLLAMA_BASE_URL, SYSTEM_INSTRUCTION
from memory.vector_store import ExplicitMemoryManager
from agents.workflow_agent import RoutineEngine
from tools.process_manager import terminate_process_tree, get_system_resource_usage
from tools.app_launcher import launch_application, open_url
from tools.media_control import play_music

class Brain:
    def __init__(self, max_history_turns: int = 4):
        self.client = OpenAI(
            base_url=OLLAMA_BASE_URL,
            api_key="ollama"
        )
        self.model_name = LOCAL_MODEL
        self.tool_map = {}
        self.registered_tools = []
        
        self.memory = ExplicitMemoryManager()
        self.routine_engine = RoutineEngine()

        # Register tools
        self.register_tool(self.memory.save_or_update_memory)
        self.register_tool(self.memory.forget_memory)
        self.register_tool(self.routine_engine.save_routine)
        self.register_tool(self.routine_engine.execute_routine)
        self.register_tool(self.routine_engine.delete_routine)
        self.register_tool(self.routine_engine.get_routine_details)
        self.register_tool(launch_application)
        self.register_tool(open_url)
        self.register_tool(play_music)
        self.register_tool(terminate_process_tree)
        self.register_tool(get_system_resource_usage)

        self.max_history_turns = max_history_turns
        self.short_term_history = []

    def clear_conversation(self):
        self.short_term_history = []
        return "Conversation history cleared."

    def _convert_func_to_schema(self, func):
        sig = inspect.signature(func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            properties[param_name] = {
                "type": "string",
                "description": f"The {param_name} parameter."
            }
            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        return {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": func.__doc__ or "No description provided.",
                "parameters": {
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            }
        }

    def register_tool(self, func, func_name: str = None):
        name = func_name or func.__name__
        self.tool_map[name] = func
        schema = self._convert_func_to_schema(func)
        self.registered_tools.append(schema)

    def _handle_text_tool_call(self, text: str):
        match = re.search(r'(\w+)\s*,\s*(\w+)\s*(\{.*?\})', text, re.DOTALL)
        if match:
            func_name = match.group(2)
            try:
                func_args = json.loads(match.group(3).replace("'", '"'))
                if func_name in self.tool_map:
                    print(f"\n⚙️ [Brain Intercept]: Executing Tool -> '{func_name}' with args {func_args}")
                    return str(self.tool_map[func_name](**func_args))
            except Exception:
                pass

        match_simple = re.search(r'(\w+)\s*(\{.*?\})', text, re.DOTALL)
        if match_simple:
            func_name = match_simple.group(1)
            if func_name in self.tool_map:
                try:
                    func_args = json.loads(match_simple.group(2).replace("'", '"'))
                    print(f"\n⚙️ [Brain Intercept]: Executing Tool -> '{func_name}' with args {func_args}")
                    return str(self.tool_map[func_name](**func_args))
                except Exception:
                    pass

        return None

    def process_prompt(self, user_prompt: str) -> str:
        clean_input = user_prompt.lower().strip()

        # 1. Zero-latency instant greetings
        if clean_input in ["hey jarvis", "hello jarvis", "hi jarvis", "jarvis", "hey", "hello"]:
            return "Yes, sir? I am listening."

        saved_routines = self.routine_engine._read_protocols()

        # 2. PRIORITY: Routine Deletions ("delete code alohomora", "delete alohomora", "remove protocol x")
        if any(w in clean_input for w in ["delete", "remove", "forget"]):
            for key in saved_routines:
                if key in clean_input:
                    return self.routine_engine.delete_routine(key)

        # 3. PRIORITY: Routine Inquiries ("what is code alohomora", "tell me routine x")
        if "what is" in clean_input or "details of" in clean_input:
            for key in saved_routines:
                if key in clean_input:
                    return self.routine_engine.get_routine_details(key)

        # 4. PRIORITY: Routine Creation/Update Check
        # If user mentions update/save/remember, pass to LLM tool-calling (DO NOT execute it)
        is_routine_config = any(w in clean_input for w in ["remember", "update", "change", "set", "configure", "whenever i", "create code", "store code"])

        # 5. Routine Execution (Only if NOT creating/updating/deleting)
        if not is_routine_config:
            # Check for direct single word triggers or "execute / activate X"
            for key in saved_routines:
                # Trigger on exact code word or explicit execute command
                if clean_input in [key, f"code {key}", f"protocol {key}", f"execute {key}", f"activate {key}", f"run {key}", f"open {key}"]:
                    print(f"\n⚙️ [Fast-Path]: Direct Routine Execution -> '{key}'")
                    return self.routine_engine.execute_routine(key)

        # 6. Direct Simple App / Web / Music Controls
        if clean_input.startswith("just open ") or clean_input.startswith("open "):
            target = clean_input.replace("just open", "").replace("open", "").strip(" '\"():;,.")
            if "vs code" in target or "vscode" in target or target == "code":
                return launch_application("code")
            elif "github" in target:
                return open_url("https://github.com")
            elif "youtube" in target:
                return open_url("https://youtube.com")
            elif "chrome" in target or "browser" in target:
                return launch_application("chrome")
            elif ".com" in target or ".org" in target or "http" in target:
                return open_url(target)
            else:
                return launch_application(target)

        if clean_input.startswith("play ") or clean_input.startswith("play music "):
            song_query = clean_input.replace("play music", "").replace("play", "").strip(" '\"():;,.")
            return play_music(song_query)

        if clean_input in ["clear history", "reset conversation", "flush memory"]:
            return self.clear_conversation()

        all_memories = self.memory.get_all_memories_string()
        routines_summary = self.routine_engine.get_all_routines_string()

        full_system_prompt = (
            f"{SYSTEM_INSTRUCTION}\n"
            f"[User Saved Profile]: {all_memories}\n"
            f"[Saved Protocols]: {routines_summary}\n\n"
            "MANDATORY EXECUTION RULES:\n"
            "1. When the user asks to save, remember, create, or update ANY protocol/code word (e.g., 'update the code alohomora...'), YOU MUST CALL 'save_routine'. DO NOT use save_or_update_memory.\n"
            "2. When the user asks to open an app, call 'launch_application'.\n"
            "3. When the user asks to open a website, call 'open_url'.\n"
            "4. When the user asks to play music, call 'play_music'.\n"
            "5. When the user asks to close an app, call 'terminate_process_tree'.\n"
            "6. To delete a routine, call 'delete_routine'."
        )

        messages = [{"role": "system", "content": full_system_prompt}]
        messages.extend(self.short_term_history)
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                tools=self.registered_tools if self.registered_tools else None,
                tool_choice="auto",
                max_tokens=250
            )

            message = response.choices[0].message
            final_reply = ""

            if message.tool_calls:
                for tool_call in message.tool_calls:
                    func_name = tool_call.function.name
                    raw_args = tool_call.function.arguments
                    func_args = json.loads(raw_args) if isinstance(raw_args, str) else (raw_args or {})
                    
                    if func_name in self.tool_map:
                        print(f"\n⚙️ [Brain]: Executing Tool -> '{func_name}' with args {func_args}")
                        tool_result = self.tool_map[func_name](**func_args)
                        final_reply = str(tool_result)
                        break
            else:
                content = message.content or ""
                text_tool_result = self._handle_text_tool_call(content)
                if text_tool_result:
                    final_reply = text_tool_result
                else:
                    # Clean out any leftover hallucinated token fragments or raw function leaks
                    cleaned_content = re.sub(r'\{.*?\}', '', content)
                    cleaned_content = re.sub(r'\b(onauthomora|save_routine|execute_routine|delete_routine|play_music|terminate_process_tree|launch_application|open_url)\b', '', cleaned_content, flags=re.IGNORECASE)
                    cleaned_content = re.sub(r'[,:\"\'\]\}]+', ' ', cleaned_content).strip()
                    final_reply = cleaned_content if len(cleaned_content) > 3 else "Done, sir."

            self.short_term_history.append({"role": "user", "content": user_prompt})
            self.short_term_history.append({"role": "assistant", "content": final_reply})

            max_msgs = self.max_history_turns * 2
            if len(self.short_term_history) > max_msgs:
                self.short_term_history = self.short_term_history[-max_msgs:]

            return final_reply

        except Exception as e:
            return f"❌ [Brain Error]: {str(e)}"