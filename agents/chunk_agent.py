from typing import Optional, List, Dict, Any
import json
import re

from core.base_agent import BaseAgent, BaseAgentConfig


class ChunkEmbedAgent(BaseAgent):
    def __init__(self, model_name: Optional[str] = None) -> None:
        cfg = BaseAgentConfig(model_name=model_name)
        super().__init__(name="ChunkEmbedAgent", config=cfg)

    def build_prompts(self, enriched_segments_json: str) -> tuple[str, str]:
        system_prompt = (
            "You are ChunkEmbedAgent. Prepare transcript segments for embedding and retrieval. "
            "Ensure each chunk is semantically complete and <= 500 tokens with ~50-token overlap."
        )
        user_prompt = (
            "INPUT SEGMENTS (JSON):\n" + enriched_segments_json[:120000] + "\n\n"
            "TASKS:\n"
            "1. Merge segments into complete chunks (~400–500 tokens).\n"
            "2. Add small overlaps to preserve continuity.\n"
            '3. Return JSON: {"chunks":[{"text": "..."}]}\n'
        )
        return system_prompt, user_prompt

    def make_chunks(self, segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            system_prompt, user_prompt = self.build_prompts(
                json.dumps({"segments": segments})
            )
            out = self.call_model(system_prompt, user_prompt)
            if not out:
                return self._heuristic_chunks(segments)
            data = json.loads(out)
            chunks = data.get("chunks", []) if isinstance(data, dict) else []
            if not isinstance(chunks, list) or not chunks:
                return self._heuristic_chunks(segments)
            # normalize to list of {text}
            normalized: List[Dict[str, Any]] = []
            for c in chunks:
                if isinstance(c, dict) and c.get("text"):
                    normalized.append({"text": str(c["text"])})
                elif isinstance(c, str):
                    normalized.append({"text": c})
            return normalized or self._heuristic_chunks(segments)
        except Exception:
            return self._heuristic_chunks(segments)

    def _heuristic_chunks(
        self, segments: List[Dict[str, Any]], target_tokens: int = 500
    ) -> List[Dict[str, Any]]:
        chunks: List[Dict[str, Any]] = []
        current: List[str] = []
        count = 0
        for seg in segments:
            text = seg.get("text", "")
            tokens = max(1, len(re.findall(r"\w+", text)))
            if count + tokens > target_tokens and current:
                chunks.append({"text": "\n\n".join(current)})
                # small overlap: keep last sentence
                last = re.split(r"([.!?]\s)", current[-1])
                keep = current[-1] if len(last) < 2 else "".join(last[-2:]).strip()
                current = [keep] if keep else []
                count = max(1, len(re.findall(r"\w+", keep))) if keep else 0
            current.append(text)
            count += tokens
        if current:
            chunks.append({"text": "\n\n".join(current)})
        return chunks
