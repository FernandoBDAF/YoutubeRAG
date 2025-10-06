from typing import Optional

from core.base_agent import BaseAgent, BaseAgentConfig


class TranscriptCleanAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None):
        cfg = BaseAgentConfig(model_name=model_name)
        super().__init__(name="TranscriptCleanAgent", config=cfg)

    def build_prompts(self, raw_text: str) -> tuple[str, str]:
        system_prompt = (
            "You are TranscriptCleanAgent. You specialize in converting auto-generated "
            "video transcripts into clean, human-readable educational text. Preserve "
            "factual content and code syntax while improving punctuation, casing, and "
            "sentence boundaries. Do not paraphrase or add commentary. Maintain the "
            "same language as the input."
        )
        user_prompt = (
            "INPUT TRANSCRIPT:\n"
            f"{raw_text[:120000]}\n\n"
            "TASKS:\n"
            "1. Fix punctuation and casing.\n"
            '2. Remove filler words ("uh", "um", "you know") and false starts.\n'
            "3. Split into natural paragraphs (around 4–6 sentences each).\n"
            "4. Keep all code or command examples intact, preserving indentation.\n"
            "5. If you find malformed code, wrap it in triple backticks with the correct language.\n"
        )
        return system_prompt, user_prompt

    def clean(self, raw_text: str) -> str:
        system_prompt, user_prompt = self.build_prompts(raw_text)
        return self.call_model(system_prompt, user_prompt)
