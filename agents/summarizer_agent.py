from typing import Optional, List, Dict, Any

from base_agent import BaseAgent, BaseAgentConfig


class SummarizerAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None) -> None:
        cfg = BaseAgentConfig(model_name=model_name)
        super().__init__(name="SummarizerAgent", config=cfg)

    def build_prompts(
        self, context_blocks: List[Dict[str, Any]], topic: str
    ) -> tuple[str, str]:
        system_prompt = (
            "You are SummarizerAgent, an expert educator. Summarize multiple YouTube coding tutorials into a clear "
            "Markdown cheat-sheet. Maintain technical precision, preserve code snippets, and include references "
            "(video_id:chunk_id)."
        )
        joined = "\n\n".join(
            f"({c.get('video_id')}:{c.get('chunk_id')})\n{c.get('text','')[:1200]}"
            for c in context_blocks
        )
        user_prompt = (
            f"TOPIC: {topic}\n\nCONTEXT:\n{joined}\n\nTASKS:\n"
            "1. Summarize key learning points (use Markdown headings).\n"
            "2. Preserve code examples with proper fences.\n"
            "3. Group by subtopic.\n"
            "4. Add a short 'Common Mistakes' section if applicable.\n"
            "5. Include citation references (video_id:chunk_id)."
        )
        return system_prompt, user_prompt

    def summarize(self, context_blocks: List[Dict[str, Any]], topic: str) -> str:
        try:
            system_prompt, user_prompt = self.build_prompts(context_blocks, topic)
            out = self.call_model(system_prompt, user_prompt)
            if not out:
                return self._fallback(context_blocks)
            return str(out)
        except Exception:
            return self._fallback(context_blocks)

    def _fallback(self, context_blocks: List[Dict[str, Any]]) -> str:
        header = "# Summary (no LLM configured)\n\n"
        body = "\n\n".join(
            f"({c.get('video_id')}:{c.get('chunk_id')})\n{c.get('text','')[:800]}"
            for c in context_blocks
        )
        return header + body
