from typing import Optional, List, Dict, Any
import json
import re

from core.base_agent import BaseAgent, BaseAgentConfig


class EnrichmentAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None):
        cfg = BaseAgentConfig(model_name=model_name)
        super().__init__(name="EnrichmentAgent", config=cfg)

    def build_prompts(self, text_block: str) -> tuple[str, str]:
        system_prompt = (
            "You are EnrichmentAgent. Annotate cleaned YouTube transcripts for educational analysis. "
            "Extract meaningful metadata (topics, technologies, skills, code snippets, entities)."
        )
        user_prompt = (
            "INPUT TEXT:\n" + text_block[:120000] + "\n\n"
            "TASKS:\n"
            "1. Split into logical segments (2–3 paragraphs each).\n"
            "2. For each segment, extract tags, entities, keyphrases, fenced code blocks, difficulty.\n"
            "3. Maintain original meaning."
        )
        return system_prompt, user_prompt

    def annotate(self, text_block: str) -> List[Dict[str, Any]]:
        system_prompt, user_prompt = self.build_prompts(text_block)
        out = self.call_model(system_prompt, user_prompt)
        if not out:
            return self._heuristic_annotate(text_block)
        try:
            data = json.loads(out)
            segments = data.get("segments", []) if isinstance(data, dict) else []
            return (
                segments
                if isinstance(segments, list) and segments
                else self._heuristic_annotate(text_block)
            )
        except Exception:
            return self._heuristic_annotate(text_block)

    def _heuristic_annotate(self, text_block: str) -> List[Dict[str, Any]]:
        code_fence_re = re.compile(r"```([a-zA-Z0-9_+-]*)[\s\S]*?```", re.MULTILINE)

        def extract_tags(text: str) -> List[str]:
            tags: set[str] = set()
            for kw in [
                "react",
                "python",
                "hooks",
                "state",
                "api",
                "context",
                "reducer",
                "typescript",
                "javascript",
                "node",
            ]:
                if re.search(rf"\\b{re.escape(kw)}\\b", text, flags=re.IGNORECASE):
                    tags.add(kw)
            return sorted(tags)

        segments: List[Dict[str, Any]] = []
        for seg in [s.strip() for s in re.split(r"\n\n+", text_block) if s.strip()]:
            tags = extract_tags(seg)
            entities = [t for t in tags if t.lower() not in {"api"}]
            keyphrases = tags[:5]
            code_blocks = []
            for m in code_fence_re.finditer(seg):
                lang = m.group(1) or ""
                code_blocks.append({"lang": lang, "code": m.group(0)})
            segments.append(
                {
                    "start": 0.0,
                    "end": 0.0,
                    "text": seg,
                    "tags": tags,
                    "entities": entities,
                    "keyphrases": keyphrases,
                    "code_blocks": code_blocks,
                    "difficulty": None,
                }
            )
        return segments
