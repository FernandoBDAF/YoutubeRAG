import os
import uuid
import json
import logging
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field
import openai

from core.libraries.error_handling.decorators import handle_errors
from core.libraries.error_handling.context import agent_context
from core.libraries.error_handling.exceptions import format_exception_message
from core.libraries.logging import log_exception

logger = logging.getLogger(__name__)


class BaseAgentConfig(BaseModel):
    """
    Strongly typed configuration object for Agents with validation.
    """

    model_name: Optional[str] = Field(default=None, description="Name of the LLM model")
    temperature: float = Field(
        default=0, ge=0, le=1, description="Sampling temperature"
    )
    max_tokens: int = Field(
        default=8000, gt=0, description="Maximum tokens to generate"
    )
    log_level: str = Field(default="INFO", description="Logging verbosity")
    output_dir: Optional[str] = Field(
        default=None, description="Directory for saving outputs"
    )
    input_dir: Optional[str] = Field(
        default=None, description="Directory for reading inputs"
    )
    extra: Dict = Field(
        default_factory=dict, description="Custom agent-specific config"
    )


class BaseAgent(ABC):
    def __init__(self, name: str, config: Optional[BaseAgentConfig] = None):
        self.id = str(uuid.uuid4())
        self.name = name
        self.config = config

        if config is None:
            self.config = BaseAgentConfig()

        # Load model: explicit > env var > safe default
        self.config.model_name = (
            self.config.model_name or os.getenv("OPENAI_DEFAULT_MODEL") or "gpt-5-nano"
        )

        # Initialize client (require key only when LLM path is used)
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is required for LLM agents. Set it or run without --llm."
            )
        # Use a sane default timeout to avoid hanging calls
        self.model = openai.OpenAI(api_key=api_key, timeout=60)

        self.timestamp = datetime.utcnow().isoformat()

    def run(self, prompt: str) -> str:
        """Default: call model with prompt."""
        result = self.call_model(prompt)
        return result

    def call_model(self, system_prompt: str, prompt: str, **kwargs) -> str:
        """Unified model call."""
        self._log_event(
            {
                "type": "model_call:start",
                "model": self.config.model_name,
                "temperature": kwargs.get("temperature", self.config.temperature),
                "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
                "system_chars": len(system_prompt or ""),
                "user_chars": len(prompt or ""),
            }
        )

        temperature = kwargs.get("temperature", self.config.temperature)
        max_completion_tokens = kwargs.get("max_tokens", self.config.max_tokens)
        timeout = kwargs.get("timeout", 60)

        if hasattr(self.model, "chat"):
            try:
                response = self.model.chat.completions.create(
                    model=self.config.model_name,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": prompt},
                    ],
                    max_completion_tokens=max_completion_tokens,
                    timeout=timeout,
                    **kwargs,
                )
                out = response.choices[0].message.content.strip()
                usage = getattr(response, "usage", None)
                self._log_event(
                    {
                        "type": "model_call:done",
                        "model": self.config.model_name,
                        "ok": True,
                        "output_preview": out[:120],
                        "usage": {
                            "prompt_tokens": (
                                getattr(usage, "prompt_tokens", None) if usage else None
                            ),
                            "completion_tokens": (
                                getattr(usage, "completion_tokens", None)
                                if usage
                                else None
                            ),
                            "total_tokens": (
                                getattr(usage, "total_tokens", None) if usage else None
                            ),
                        },
                    }
                )
                return out
            except Exception as e:
                # Enhanced error logging using library helper
                error_formatted = format_exception_message(e)
                self._log_event(
                    {
                        "type": "model_call:error",
                        "model": self.config.model_name,
                        "error": error_formatted,
                    }
                )
                # Log with full traceback
                log_exception(logger, f"[{self.name}] LLM call failed", e)
                return ""

        elif callable(self.model):
            return self.model(prompt, **kwargs)

        elif isinstance(self.model, str):
            raise RuntimeError(
                f"Model '{self.model}' is just a string. "
                "Provide a proper client instance or wrap it."
            )

        else:
            raise RuntimeError(f"Unsupported model type for {self.name}")

    # ---- Logging ----
    def log(self, prompt: str, output: str):
        """Log agent interaction (called explicitly, not automatically)."""
        log_entry = {
            "agent_id": self.id,
            "agent_name": self.name,
            "timestamp": self.timestamp,
            "prompt_preview": prompt[:100],
            "output_preview": output[:100],
        }
        # Only log if explicitly called (not auto-logged)
        logger.debug(
            f"[{self.name}] Agent interaction: {json.dumps(log_entry, ensure_ascii=False)}"
        )

    def _log_event(self, event: Dict[str, Any]):
        """Internal event logging - uses DEBUG level to avoid terminal flooding."""
        payload = {"agent": self.name, "ts": self.timestamp}
        payload.update(event)

        # Use DEBUG level for detailed events (model_call:start/done)
        # Only log errors at INFO/WARNING level
        event_type = event.get("type", "unknown")
        if "error" in event_type.lower() or event_type == "model_call:error":
            logger.warning(
                f"[{self.name}] {event_type}: {payload.get('error', 'unknown error')}"
            )
        else:
            # Model call start/done, retry attempts - all at DEBUG level
            logger.debug(
                f"[{self.name}] {event_type}: {json.dumps(payload, ensure_ascii=False)}"
            )

    # ---- Generic retry-with-feedback executor ----
    def execute_with_retries(self, max_retries: int, step_fn):
        """
        Generic retry loop that standardizes feedback accumulation and approval flow.

        step_fn(feedback: Optional[str]) -> dict with keys:
          - status: "APPROVE" | "RETURN_FOR_IMPROVEMENT"
          - reasons: list[str]
          - data: any (present when approved)

        Returns the last step_fn result (approved or not).
        """
        feedback = None
        last_result = {"status": "RETURN_FOR_IMPROVEMENT", "reasons": ["not started"]}
        for i in range(1, max_retries + 1):
            self._log_event({"type": "retry:attempt", "attempt": i})
            result = step_fn(feedback)
            last_result = result
            if result.get("status") == "APPROVE":
                self._log_event({"type": "retry:approved", "attempts": i})
                return result
            reasons = result.get("reasons", [])
            feedback = "Reviewer feedback:\n" + "\n".join(f"- {r}" for r in reasons)
            self._log_event(
                {"type": "retry:feedback", "attempt": i, "reasons": reasons}
            )
        return last_result


# Note: do not re-export via relative imports; import BaseAgent directly from this module.
