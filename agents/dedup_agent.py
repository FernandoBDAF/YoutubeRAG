from typing import Optional, Dict, Any
import json

from base_agent import BaseAgent, BaseAgentConfig


class DeduplicateAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None) -> None:
        cfg = BaseAgentConfig(model_name=model_name)
        super().__init__(name="DeduplicateAgent", config=cfg)

    def build_prompts(self, text_a: str, text_b: str) -> tuple[str, str]:
        system_prompt = (
            "You are DeduplicateAgent. Determine if two chunks are redundant for retrieval (same concept, "
            "substantially overlapping explanation, or identical/near-identical code)."
        )
        user_prompt = (
            "You will compare CHUNK A and CHUNK B and output strict JSON.\n\n"
            "INSTRUCTIONS (think step-by-step):\n"
            "1) Check concept overlap: do they teach the same idea?\n"
            "2) Compare structure: similar sequence of steps/explanations?\n"
            "3) Code: identical or minimal-diff code suggests redundancy.\n"
            "4) If mainly complementary or distinct, mark not redundant.\n"
            '5) Output VALID JSON ONLY: {"redundant": true|false, "reason": "short"}.\n\n'
            "GOOD EXAMPLE:\n"
            '{"redundant": true, "reason": "Same hashing concept and identical code example"}\n\n'
            "BAD EXAMPLES:\n"
            "- Returning prose instead of JSON.\n"
            '- Saying "maybe" or "it depends" without a boolean.\n\n'
            "CHUNK A:\n" + text_a[:6000] + "\n\n"
            "CHUNK B:\n" + text_b[:6000]
        )
        return system_prompt, user_prompt

    def is_redundant(self, text_a: str, text_b: str) -> Dict[str, Any]:
        try:
            system_prompt, user_prompt = self.build_prompts(text_a, text_b)
            out = self.call_model(system_prompt, user_prompt)
            if not out:
                return {"redundant": False, "reason": "no-llm"}
            data = json.loads(out)
            redundant = bool(data.get("redundant", False))
            reason = str(data.get("reason", ""))
            return {"redundant": redundant, "reason": reason}
        except Exception:
            return {"redundant": False, "reason": "fallback"}
