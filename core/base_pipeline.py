import json
import os
from typing import Any, Dict, Optional


class BasePipeline:
    """
    Shared helpers for content pipelines.

    Provides consistent filesystem helpers for building paths, loading cached
    artifacts, saving outputs, and clearing per-id caches.
    """

    @staticmethod
    def build_path(directory: str, item_id: str) -> str:
        return os.path.join(directory, f"{item_id}.json")

    @staticmethod
    def load_if_exists(directory: str, item_id: str) -> Optional[Dict[str, Any]]:
        path = BasePipeline.build_path(directory, item_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return None

    @staticmethod
    def load_first_existing(
        directories: list[str], item_id: str
    ) -> Optional[Dict[str, Any]]:
        for d in directories:
            path = BasePipeline.build_path(d, item_id)
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return json.load(f)
        return None

    @staticmethod
    def save_json(directory: str, item_id: str, payload: Dict[str, Any]) -> None:
        path = BasePipeline.build_path(directory, item_id)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    @staticmethod
    def clear_caches_for_id(directories: list[str], item_id: str) -> None:
        for d in directories:
            p = BasePipeline.build_path(d, item_id)
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                # best-effort cache clearing
                pass

    # ---------- Generic stage-aware helpers (subclasses set stage maps) ----------
    def _get_stage_order(self) -> list[str]:
        # Prefer generic name `stages`, fallback to legacy `agents_order`
        if hasattr(self, "stages"):
            return getattr(self, "stages") or []
        return getattr(self, "agents_order", []) or []

    def _get_stage_write_dirs(self) -> dict:
        # Prefer generic name `stage_to_dir_write`, fallback to `agents_path_map`
        if hasattr(self, "stage_to_dir_write"):
            return getattr(self, "stage_to_dir_write") or {}
        return getattr(self, "agents_path_map", {}) or {}

    def _get_stage_read_dirs(self) -> dict:
        # Prefer explicit `stage_read_paths` if present; otherwise derive from write dirs
        if hasattr(self, "stage_read_paths"):
            return getattr(self, "stage_read_paths") or {}
        write_map = self._get_stage_write_dirs()
        return {k: [v] for k, v in write_map.items()}

    def has_processed(self, stage: str, item_id: str) -> bool:
        read_map = self._get_stage_read_dirs()
        directories = read_map.get(stage, [])
        return self.load_first_existing(directories, item_id) is not None

    def get_progress_state(self, item_id: str) -> str:
        for name in self._get_stage_order():
            if not self.has_processed(name, item_id):
                return name
        return "Completed"

    def summarize_artifact(self, stage: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Subclasses can override to add small previews (e.g., lengths, counts).
        Default: no summary.
        """
        return {}

    def get_item_status(self, item_id: str) -> Dict[str, Any]:
        status: Dict[str, Any] = {}
        write_map = self._get_stage_write_dirs()
        for name in self._get_stage_order():
            payload = self.get_artifact(name, item_id)
            if payload is None:
                status[name] = {"exists": False}
                continue
            meta: Dict[str, Any] = {"exists": True}
            # try canonical path stats
            try:
                p = self.build_path(write_map.get(name, ""), item_id)
                if p:
                    st = os.stat(p)
                    meta.update(
                        {"path": p, "size": st.st_size, "updated_at": st.st_mtime}
                    )
                else:
                    meta.update({"path": None})
            except Exception:
                pass
            # small, cheap summary
            try:
                meta.update(self.summarize_artifact(name, payload) or {})
            except Exception:
                pass
            status[name] = meta
        status["next_stage"] = next(
            (n for n in self._get_stage_order() if not status.get(n, {}).get("exists")),
            "Completed",
        )
        return status

    def get_artifact(self, stage: str, item_id: str) -> Optional[Dict[str, Any]]:
        read_map = self._get_stage_read_dirs()
        return self.load_first_existing(read_map.get(stage, []), item_id)

    def clear_from(self, stage: str, item_id: str) -> None:
        order = self._get_stage_order()
        write_map = self._get_stage_write_dirs()
        if stage not in order:
            raise ValueError(f"Unknown stage: {stage}")
        idx = order.index(stage)
        dirs = [write_map.get(n) for n in order[idx:] if write_map.get(n)]
        self.clear_caches_for_id(dirs, item_id)