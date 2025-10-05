from typing import Optional, Dict, Any
import json

from base_agent import BaseAgent, BaseAgentConfig


class DeduplicateAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None) -> None:
        cfg = BaseAgentConfig(model_name=model_name)
        super().__init__(name="DeduplicateAgent", config=cfg)

    def build_prompts(self, text_a: str, text_b: str) -> tuple[str, str]:
        system_prompt = (
            "You are DeduplicateAgent. Compare educational content chunks to detect redundancy. "
            "Two chunks are redundant if they teach the same concept using similar wording or identical code."
        )
        user_prompt = (
            "CHUNK A:\n" + text_a[:6000] + "\n\n"
            "CHUNK B:\n" + text_b[:6000] + "\n\n"
            'TASK: Determine if these chunks are redundant. Output JSON {"redundant": true|false, "reason": '
            + '"<why>"}'
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
