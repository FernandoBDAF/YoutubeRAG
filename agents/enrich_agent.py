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
            "You are EnrichmentAgent, an expert educational annotator. "
            "Your job is to segment cleaned lecture text and extract precise, useful metadata "
            "for downstream retrieval and analytics. Be meticulous and avoid generic fluff."
        )
        user_prompt = (
            "You will read the INPUT TEXT and produce a strict JSON object with this schema:\n"
            "{\n"
            '  "segments": [\n'
            "    {\n"
            '      "start": number,\n'
            '      "end": number,\n'
            '      "text": string,\n'
            '      "tags": string[],\n'
            '      "named_entities": string[],\n'
            '      "topics": string[],\n'
            '      "keyphrases": string[],\n'
            '      "code_blocks": [{ "lang": string, "code": string }],\n'
            '      "difficulty": one of ["beginner", "intermediate", "advanced", null]\n'
            "    }\n"
            "  ]\n"
            "}\n\n"
            "INSTRUCTIONS (think step-by-step):\n"
            "1) Segmenting (CoT): First, identify topic shifts. Group 2–3 related paragraphs per segment.\n"
            "   Keep segments roughly 1200–2200 chars (flex if needed). Do NOT split mid-equation or mid-code.\n"
            '2) Tags: 5–12 topical terms actually present in the segment (e.g., "asymptotic analysis", "hashing").\n'
            '   Avoid generic terms like "video", "lecture", "topic", "learning". Lowercase; multi-words allowed.\n'
            '3) named_entities and topics: proper names go in named_entities; technical concepts go in topics (e.g., "Pigeonhole Principle", "MIT OCW").\n'
            "4) Keyphrases: 3–8 short phrases that summarize the core ideas or steps from this segment.\n"
            "5) Code blocks: extract fenced code if present; otherwise []. Do not invent code.\n"
            "6) Difficulty: estimate comprehension difficulty from the segment (beginner/intermediate/advanced) or null.\n"
            "7) Fidelity: do not add facts not supported by the text.\n"
            "8) Output: VALID JSON ONLY. No markdown, no comments.\n\n"
            "GOOD EXAMPLE (abbreviated):\n"
            "{\n"
            '  "segments": [{\n'
            '    "start": 0, "end": 0,\n'
            '    "text": "Asymptotic analysis compares runtime as input size grows...",\n'
            '    "tags": ["asymptotic analysis", "big o", "runtime", "efficiency"],\n'
            '    "named_entities": ["MIT OCW"],\n'
            '    "topics": ["algorithm analysis"],\n'
            '    "keyphrases": ["compare algorithms by growth rate", "input size n"],\n'
            '    "code_blocks": [],\n'
            '    "difficulty": "beginner"\n'
            "  }]\n"
            "}\n\n"
            "BAD EXAMPLES:\n"
            '- Tags like ["video", "lecture", "topic"] (too generic).\n'
            "- Fabricated code or entities not in the text.\n"
            "- Output that is not strict JSON or includes markdown fences.\n\n"
            "INPUT TEXT:\n" + text_block[:120000]
        )
        return system_prompt, user_prompt

    def annotate(self, text_block: str) -> List[Dict[str, Any]]:
        system_prompt, user_prompt = self.build_prompts(text_block)
        out = self.call_model(system_prompt, user_prompt)
        # Log LLM return preview
        try:
            print(
                json.dumps(
                    {
                        "agent": "EnrichmentAgent",
                        "event": "llm_return",
                        "ok": bool(out),
                        "input_chars": len(text_block or ""),
                        "out_preview": (out[:160] if out else ""),
                    }
                )
            )
        except Exception:
            pass
        if not out:
            segs = self._heuristic_annotate(text_block)
            return segs
        try:
            data = json.loads(out)
            segments = data.get("segments", []) if isinstance(data, dict) else []
            if isinstance(segments, list) and segments:
                try:
                    lens = [len(s.get("text", "")) for s in segments]
                    num = len(segments)
                    avg_len = (sum(lens) / max(1, num)) if num else 0
                    tags_any = sum(1 for s in segments if s.get("tags"))
                    keys_any = sum(1 for s in segments if s.get("keyphrases"))
                    print(
                        json.dumps(
                            {
                                "agent": "EnrichmentAgent",
                                "event": "llm_parsed",
                                "segments": num,
                                "avg_chars": int(avg_len),
                                "tags_any": f"{tags_any}/{num}",
                                "keyphrases_any": f"{keys_any}/{num}",
                            }
                        )
                    )
                except Exception:
                    pass
                return segments
            # Empty or invalid → fallback
            try:
                print(
                    json.dumps(
                        {
                            "agent": "EnrichmentAgent",
                            "event": "llm_empty_or_invalid",
                            "segments_type": type(segments).__name__,
                        }
                    )
                )
            except Exception:
                pass
            return self._heuristic_annotate(text_block)
        except Exception as e:
            try:
                print(
                    json.dumps(
                        {
                            "agent": "EnrichmentAgent",
                            "event": "llm_parse_error",
                            "error": str(e)[:200],
                        }
                    )
                )
            except Exception:
                pass
            return self._heuristic_annotate(text_block)

    def _normalize_text(self, text: str) -> str:
        if text is None:
            return ""
        t = text.replace("\r\n", "\n").replace("\r", "\n")
        t = t.replace("\\n", "\n")
        t = re.sub(r"\n{3,}", "\n\n", t)
        return t.strip()

    def _normalize_segment_fields(
        self, seg: Dict[str, Any], default_text: str
    ) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        out["start"] = float(seg.get("start", 0.0) or 0.0)
        out["end"] = float(seg.get("end", 0.0) or 0.0)
        raw_text = seg.get("text", default_text)
        out["text"] = self._normalize_text(raw_text)
        out["tags"] = list(seg.get("tags", []) or [])
        legacy_entities = list(seg.get("entities", []) or [])
        named_entities = list(seg.get("named_entities", []) or [])
        topics = list(seg.get("topics", []) or [])
        if legacy_entities and not named_entities and not topics:
            named_entities = legacy_entities
        out["named_entities"] = named_entities
        out["topics"] = topics
        out["keyphrases"] = list(seg.get("keyphrases", []) or [])
        out["code_blocks"] = list(seg.get("code_blocks", []) or [])
        out["difficulty"] = seg.get("difficulty")
        # Temporary compatibility
        out["entities"] = (
            (named_entities + topics) if (named_entities or topics) else legacy_entities
        )
        return out

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
        units = [s.strip() for s in re.split(r"\n\n+", text_block or "") if s.strip()]
        for seg in units:
            seg_text = self._normalize_text(seg)
            tags = extract_tags(seg_text)
            named_entities: List[str] = []
            topics: List[str] = []
            keyphrases = tags[:5]
            code_blocks = []
            for m in code_fence_re.finditer(seg_text):
                lang = m.group(1) or ""
                code_blocks.append({"lang": lang, "code": m.group(0)})
            segments.append(
                {
                    "start": 0.0,
                    "end": 0.0,
                    "text": seg_text,
                    "tags": tags,
                    "named_entities": named_entities,
                    "topics": topics,
                    "keyphrases": keyphrases,
                    "code_blocks": code_blocks,
                    "difficulty": None,
                    "entities": (named_entities + topics),
                }
            )
        try:
            lens = [len(s.get("text", "")) for s in segments]
            num = len(segments)
            avg_len = (sum(lens) / max(1, num)) if num else 0
            tags_any = sum(1 for s in segments if s.get("tags"))
            keys_any = sum(1 for s in segments if s.get("keyphrases"))
            print(
                json.dumps(
                    {
                        "agent": "EnrichmentAgent",
                        "event": "heuristic_segments",
                        "segments": num,
                        "avg_chars": int(avg_len),
                        "tags_any": f"{tags_any}/{num}",
                        "keyphrases_any": f"{keys_any}/{num}",
                    }
                )
            )
        except Exception:
            pass
        return segments

    # --- Single-chunk annotation path (expects exactly one segment) ---
    def build_single_prompts(self, text_block: str) -> tuple[str, str]:
        system_prompt = "You are EnrichmentAgent. Annotate a single lecture segment with precise metadata."
        user_prompt = (
            "You will read the INPUT TEXT and produce EXACTLY ONE segment in strict JSON with this schema:\n"
            "{\n"
            '  "segments": [{\n'
            '    "start": 0, "end": 0,\n'
            '    "text": string,\n'
            '    "tags": string[],\n'
            '    "named_entities": string[],\n'
            '    "topics": string[],\n'
            '    "keyphrases": string[],\n'
            '    "code_blocks": [{ "lang": string, "code": string }],\n'
            '    "difficulty": one of ["beginner", "intermediate", "advanced", null]\n'
            "  }]\n"
            "}\n\n"
            "INSTRUCTIONS:\n"
            "- Do NOT split further; return exactly one segment.\n"
            '- Provide 5–12 useful tags; avoid generic ones like "video", "lecture".\n'
            "- Extract 3–8 keyphrases summarizing the content.\n"
            "- Extract fenced code blocks if present.\n"
            "- Output VALID JSON ONLY.\n\n"
            "INPUT TEXT:\n" + text_block[:120000]
        )
        return system_prompt, user_prompt

    def annotate_single(self, text_block: str) -> Dict[str, Any]:
        system_prompt, user_prompt = self.build_single_prompts(text_block)
        out = self.call_model(system_prompt, user_prompt)
        try:
            data = json.loads(out) if out else {}
            segs = data.get("segments", []) if isinstance(data, dict) else []
            if isinstance(segs, list) and segs:
                seg = self._normalize_segment_fields(segs[0], text_block)
                return seg
        except Exception:
            pass
        # Fallback minimal single segment
        return {
            "start": 0.0,
            "end": 0.0,
            "text": self._normalize_text(text_block),
            "tags": [],
            "named_entities": [],
            "topics": [],
            "keyphrases": [],
            "code_blocks": [],
            "difficulty": None,
            "entities": [],
        }
