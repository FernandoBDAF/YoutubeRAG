from typing import Optional

from core.base_agent import BaseAgent, BaseAgentConfig


class TranscriptCleanAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None):
        cfg = BaseAgentConfig(model_name=model_name)
        super().__init__(name="TranscriptCleanAgent", config=cfg)

    def build_prompts(self, raw_text: str) -> tuple[str, str]:
        system_prompt = (
            "You are TranscriptCleanAgent, an expert at converting raw lecture transcripts "
            "into fluent, readable text without changing meaning. Keep the original language, "
            "preserve technical content and code, and avoid hallucination."
        )
        user_prompt = (
            "You will clean the INPUT TRANSCRIPT following the steps below.\n\n"
            "INSTRUCTIONS (think step-by-step):\n"
            "1) Normalize text: fix casing, punctuation, spacing; join broken lines into full sentences.\n"
            '2) Remove fillers/false starts (e.g., "uh", "um", "you know") and stage cues ([APPLAUSE], etc.).\n'
            "3) Paragraphing: produce natural paragraphs (~4–6 sentences).\n"
            "4) Code: keep code/commands intact with original indentation; do NOT modify code semantics.\n"
            "5) Fidelity: do NOT paraphrase concepts or inject new facts; keep the same language as input.\n"
            "6) Output: CLEANED TEXT ONLY. No JSON, no markdown fences, no extra commentary.\n\n"
            "GOOD EXAMPLE (abbreviated):\n"
            "Asymptotic analysis compares how runtime grows as input size increases. We use Big-O notation to...\n\n"
            "BAD EXAMPLES:\n"
            "- Adding summaries or personal commentary.\n"
            "- Returning JSON or markdown fences.\n"
            "- Deleting or altering code blocks.\n\n"
            "INPUT TRANSCRIPT:\n"
            f"{raw_text[:120000]}"
        )
        return system_prompt, user_prompt

    def clean(self, raw_text: str) -> str:
        # Guard against extremely long inputs by trimming with a clear marker.
        # Splitting is handled at the stage level; this trim protects single-call usage.
        max_chars = 16000
        text = raw_text if len(raw_text) <= max_chars else raw_text[:max_chars]
        system_prompt, user_prompt = self.build_prompts(text)
        out = self.call_model(system_prompt, user_prompt)
        return out or ""
