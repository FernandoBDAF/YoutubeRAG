from typing import Optional, Dict, Any
import json

from base_agent import BaseAgent, BaseAgentConfig


class TrustRankAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None) -> None:
        cfg = BaseAgentConfig(model_name=model_name)
        super().__init__(name="TrustRankAgent", config=cfg)

    def build_prompts(self, payload: Dict[str, Any]) -> tuple[str, str]:
        system_prompt = (
            "You are TrustRankAgent. Estimate the trustworthiness of an educational video chunk using: "
            "consensus, recency, engagement, and code validity. Return a normalized trust_score 0–1."
        )
        user_prompt = (
            "INPUT JSON:\n" + json.dumps(payload)[:120000] + "\n\n"
            "TASK: Estimate trust_score (0–1). Explain briefly.\n"
            'OUTPUT JSON: {"trust_score": <float>, "reason": "<brief>"}'
        )
        return system_prompt, user_prompt

    def score(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            system_prompt, user_prompt = self.build_prompts(payload)
            out = self.call_model(system_prompt, user_prompt)
            if not out:
                return {"trust_score": None, "reason": "no-llm"}
            data = json.loads(out)
            score = data.get("trust_score")
            reason = data.get("reason", "")
            try:
                score_f = float(score)
            except Exception:
                score_f = None
            return {"trust_score": score_f, "reason": reason}
        except Exception:
            return {"trust_score": None, "reason": "fallback"}
