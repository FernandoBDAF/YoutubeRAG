"""
Stages API - Main Entry Point

This module provides the public API functions that can be:
1. Called directly from Python
2. Exposed via HTTP server
3. Integrated with existing API infrastructure

Reference: API_DESIGN_SPECIFICATION.md Section 3.1
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from .metadata import (
    list_stages,
    get_stage_config,
    get_stage_defaults,
    list_pipeline_stages,
    clear_metadata_cache,
)
from .validation import validate_pipeline_config, validate_stage_config_only
from .execution import (
    execute_pipeline,
    get_pipeline_status,
    cancel_pipeline,
    list_active_pipelines,
    get_pipeline_history,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Response Transformation Functions
# ============================================================================
# These functions transform internal validation results to match the
# frontend API contract defined in StagesUI/src/types/api.ts


def _transform_validation_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform validation result to match frontend API contract.
    
    Backend format:
        errors: List[Dict] with keys: code, message, stage, field, etc.
        warnings: List[Dict] with keys: code, message, stage, resolution, etc.
        execution_plan: {stages, auto_included_dependencies, ...}
    
    Frontend expects:
        errors: Record<string, string[]>  (stage_name -> error messages)
        warnings: string[]  (array of warning messages)
        execution_plan: {stages: string[], resolved_dependencies: string[]}
    """
    transformed = {
        "valid": result.get("valid", False),
        "errors": _transform_errors(result.get("errors", [])),
        "warnings": _transform_warnings(result.get("warnings", [])),
    }
    
    # Transform execution_plan if present
    exec_plan = result.get("execution_plan")
    if exec_plan:
        transformed["execution_plan"] = {
            "stages": exec_plan.get("stages", []),
            "resolved_dependencies": exec_plan.get("auto_included_dependencies", []),
        }
    
    return transformed


def _transform_errors(errors: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    """
    Transform error list to Record<stage_name, error_messages[]>.
    
    Groups errors by stage and extracts human-readable messages.
    Errors without a stage are grouped under "_general".
    """
    grouped: Dict[str, List[str]] = {}
    
    for error in errors:
        # Get stage name (fallback to "_general" for non-stage errors)
        stage = error.get("stage", "_general")
        
        # Extract message - try multiple common keys
        message = (
            error.get("message")
            or error.get("msg")
            or error.get("error")
            or str(error)
        )
        
        # Initialize list if needed
        if stage not in grouped:
            grouped[stage] = []
        
        # Add message if not duplicate
        if message not in grouped[stage]:
            grouped[stage].append(message)
    
    return grouped


def _transform_warnings(warnings: List[Dict[str, Any]]) -> List[str]:
    """
    Transform warning objects to array of warning messages.
    
    Includes resolution hint if available.
    """
    messages: List[str] = []
    
    for warning in warnings:
        # Build message with optional resolution
        message = warning.get("message", str(warning))
        resolution = warning.get("resolution")
        
        if resolution:
            full_message = f"{message} ({resolution})"
        else:
            full_message = message
        
        if full_message not in messages:
            messages.append(full_message)
    
    return messages


def _get_active_pipeline_count() -> int:
    """Get count of active pipelines for health check"""
    try:
        from .execution import list_active_pipelines
        result = list_active_pipelines()
        return result.get("count", 0)
    except Exception:
        return 0


__all__ = [
    # Metadata
    "list_stages",
    "get_stage_config",
    "get_stage_defaults",
    "list_pipeline_stages",
    "clear_metadata_cache",
    # Validation
    "validate_pipeline_config",
    "validate_stage_config_only",
    # Execution
    "execute_pipeline",
    "get_pipeline_status",
    "cancel_pipeline",
    "list_active_pipelines",
    "get_pipeline_history",
    # HTTP handlers
    "handle_request",
]


def handle_request(method: str, path: str, body: Optional[Dict] = None) -> tuple:
    """
    Handle HTTP-like requests.

    This function routes requests to appropriate handlers and returns
    (response_data, status_code) tuples.

    Can be used by:
    - SimpleHTTPServer
    - Flask/FastAPI adapters
    - Direct Python calls

    Args:
        method: HTTP method (GET, POST)
        path: URL path (e.g., "/stages", "/stages/graph_extraction/config")
        body: Request body for POST requests

    Returns:
        Tuple of (response_dict, status_code)
    """
    try:
        # Remove leading slash and split path
        path = path.lstrip("/")
        parts = path.split("/")

        # Route: GET /health
        if method == "GET" and path == "health":
            return {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "active_pipelines": _get_active_pipeline_count(),
            }, 200

        # Route: GET /stages
        if method == "GET" and path == "stages":
            return list_stages(), 200

        # Route: GET /stages/{pipeline}
        if method == "GET" and len(parts) == 2 and parts[0] == "stages":
            pipeline = parts[1]
            if pipeline in ["ingestion", "graphrag"]:
                return list_pipeline_stages(pipeline), 200
            # Otherwise, treat as stage name for /stages/{stage_name}/config

        # Route: GET /stages/{stage_name}/config
        if (
            method == "GET"
            and len(parts) == 3
            and parts[0] == "stages"
            and parts[2] == "config"
        ):
            stage_name = parts[1]
            try:
                return get_stage_config(stage_name), 200
            except ValueError as e:
                return {"error": str(e), "stage_name": stage_name}, 404

        # Route: GET /stages/{stage_name}/defaults
        if (
            method == "GET"
            and len(parts) == 3
            and parts[0] == "stages"
            and parts[2] == "defaults"
        ):
            stage_name = parts[1]
            try:
                return get_stage_defaults(stage_name), 200
            except ValueError as e:
                return {"error": str(e), "stage_name": stage_name}, 404

        # Route: POST /pipelines/validate
        if method == "POST" and path == "pipelines/validate":
            if not body:
                return {"error": "Request body required"}, 400

            pipeline = body.get("pipeline")
            stages = body.get("stages", [])
            config = body.get("config", {})

            if not pipeline:
                return {"error": "pipeline field is required"}, 400
            if not stages:
                return {"error": "stages field is required"}, 400

            result = validate_pipeline_config(pipeline, stages, config)
            return _transform_validation_result(result), 200

        # Route: POST /stages/{stage_name}/validate
        if (
            method == "POST"
            and len(parts) == 3
            and parts[0] == "stages"
            and parts[2] == "validate"
        ):
            stage_name = parts[1]
            if not body:
                return {"error": "Request body required"}, 400

            result = validate_stage_config_only(stage_name, body)
            return _transform_validation_result(result), 200

        # Route: POST /pipelines/execute
        if method == "POST" and path == "pipelines/execute":
            if not body:
                return {"error": "Request body required"}, 400

            pipeline = body.get("pipeline")
            stages = body.get("stages", [])
            config = body.get("config", {})
            metadata = body.get("metadata", {})

            if not pipeline:
                return {"error": "pipeline field is required"}, 400
            if not stages:
                return {"error": "stages field is required"}, 400

            result = execute_pipeline(pipeline, stages, config, metadata)

            if "error" in result:
                return result, 400
            return result, 202  # Accepted

        # Route: GET /pipelines/{pipeline_id}/status
        if (
            method == "GET"
            and len(parts) == 3
            and parts[0] == "pipelines"
            and parts[2] == "status"
        ):
            pipeline_id = parts[1]
            result = get_pipeline_status(pipeline_id)

            # Only return 404 if there's a real error message (not just null/None)
            if result.get("error") and result.get("pipeline_id") and result["error"] == "Pipeline not found":
                return result, 404
            return result, 200

        # Route: POST /pipelines/{pipeline_id}/cancel
        if (
            method == "POST"
            and len(parts) == 3
            and parts[0] == "pipelines"
            and parts[2] == "cancel"
        ):
            pipeline_id = parts[1]
            result = cancel_pipeline(pipeline_id)

            if "error" in result:
                return result, 400
            return result, 200

        # Route: GET /pipelines/active
        if method == "GET" and path == "pipelines/active":
            return list_active_pipelines(), 200

        # Route: GET /pipelines/history
        if method == "GET" and path == "pipelines/history":
            limit = 10  # Could be parsed from query string
            return get_pipeline_history(limit), 200

        # Not found
        return {"error": f"Unknown endpoint: {method} /{path}"}, 404

    except Exception as e:
        logger.exception(f"Error handling request: {method} /{path}")
        return {"error": "Internal server error", "message": str(e)}, 500

