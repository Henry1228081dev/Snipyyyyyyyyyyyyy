import os
import json
import base64
from typing import Dict, Any, List
from groq import Groq

# System prompt for Snipy Vision MVP
SYSTEM_PROMPT = """You are Snipy, an elite visual AI assistant.
You provide instant, ultra-concise insights based on screen snips.

Rules:
1. Main answer: Digestible bullet points. Max 4 lines.
2. Be direct. Do not explain your process.
3. Use the provided image(s) for context.
4. Output should be high-value and FAST.
"""

class GroqClient:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        # llama-4-scout is the current active vision model on Groq (2026)
        self.model_name = "meta-llama/llama-4-scout-17b-16e-instruct"
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def reset_chat(self):
        self.history = [{"role": "system", "content": SYSTEM_PROMPT}]

    def _encode_image(self, image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    def ask(self, question: str, image_paths: List[str] = None) -> str:
        """Pure Groq vision/text call for maximum speed and stability."""
        content = []
        
        # Add any pending images to the content
        if image_paths:
            for path in image_paths:
                if os.path.exists(path):
                    try:
                        b64 = self._encode_image(path)
                        content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64}"}
                        })
                    except Exception as e:
                        print(f"Error encoding image: {e}")
        
        content.append({"type": "text", "text": question})
        self.history.append({"role": "user", "content": content})

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=self.history,
                temperature=0.2
            )
            
            ans = response.choices[0].message.content
            self.history.append({"role": "assistant", "content": ans})
            return ans

        except Exception as e:
            return f"Groq Error: {str(e)}"
