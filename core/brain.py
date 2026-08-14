# core/brain.py
import os
import json
import inspect
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from config import HF_MODEL, SYSTEM_INSTRUCTION
from memory.vector_store import ExplicitMemoryManager

load_dotenv()

class Brain:
    def __init__(self, max_history_turns: int = 4):
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN not found in .env file.")
        
        self.client = InferenceClient(model=HF_MODEL, token=hf_token)
        self.tool_map = {}
        self.registered_tools = []
        
        self.memory = ExplicitMemoryManager()
        self.register_tool(self.memory.save_or_update_memory)
        self.register_tool(self.memory.forget_memory)

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

    def process_prompt(self, user_prompt: str) -> str:
        if user_prompt.lower().strip() in ["clear history", "reset conversation", "flush memory"]:
            return self.clear_conversation()

        # Direct memory injection (Instant 0ms, complete context)
        all_memories = self.memory.get_all_memories_string()
        full_system_prompt = (
            f"{SYSTEM_INSTRUCTION}\n"
            f"[User Saved Profile/Preferences]: {all_memories}\n"
            f"If the user asks to play music or their favorite song, look up the song name from the saved profile above and trigger 'play_music'."
        )

        messages = [{"role": "system", "content": full_system_prompt}]
        messages.extend(self.short_term_history)
        messages.append({"role": "user", "content": user_prompt})

        try:
            response = self.client.chat.completions.create(
                messages=messages,
                tools=self.registered_tools if self.registered_tools else None,
                tool_choice="auto",
                max_tokens=400
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
                final_reply = message.content or "No response generated."

            self.short_term_history.append({"role": "user", "content": user_prompt})
            self.short_term_history.append({"role": "assistant", "content": final_reply})

            max_msgs = self.max_history_turns * 2
            if len(self.short_term_history) > max_msgs:
                self.short_term_history = self.short_term_history[-max_msgs:]

            return final_reply

        except Exception as e:
            return f"❌ [Brain Error]: {str(e)}"