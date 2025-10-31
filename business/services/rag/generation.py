import os
from typing import Any, Dict, Iterable, List


def answer_with_openai(contexts: List[Dict[str, Any]], question: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        joined = "\n\n".join(f"[ctx] {c.get('text','')[:500]}" for c in contexts)
        return f"Context (no LLM configured):\n\n{joined}"
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        messages = [
            {
                "role": "system",
                "content": "You are a precise educational assistant. Answer using only the provided context. Cite (video_id:chunk_id).",
            },
            {
                "role": "user",
                "content": "Question: "
                + question
                + "\n\nContext:\n"
                + "\n\n".join(
                    f"({c.get('video_id')}:{c.get('chunk_id')})\n{c.get('embedding_text','')[:1200]}"
                    for c in contexts
                ),
            },
        ]
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-5-nano"), messages=messages
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        joined = "\n\n".join(f"[ctx] {c.get('text','')[:500]}" for c in contexts)
        return f"Context (LLM error: {e}):\n\n{joined}"


def stream_answer_with_openai(
    contexts: List[Dict[str, Any]], question: str
) -> Iterable[str]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        yield "[Streaming disabled: OPENAI_API_KEY not set]"
        return
    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        messages = [
            {
                "role": "system",
                "content": "You are a precise educational assistant. Answer using only the provided context. Cite (video_id:chunk_id).",
            },
            {
                "role": "user",
                "content": "Question: "
                + question
                + "\n\nContext:\n"
                + "\n\n".join(
                    f"({c.get('video_id')}:{c.get('chunk_id')})\n{c.get('text','')[:1200]}"
                    for c in contexts
                ),
            },
        ]
        stream = client.chat.completions.create(
            model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-4o-mini"),
            messages=messages,
            stream=True,
        )
        for event in stream:
            delta = getattr(getattr(event, "choices", [None])[0], "delta", None)
            if delta and getattr(delta, "content", None):
                yield delta.content
    except Exception as e:
        yield f"[Streaming error: {e}]"
