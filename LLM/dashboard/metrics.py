"""
Dashboard metrics collection.

Provides Prometheus-compatible metrics for monitoring dashboard
performance and usage.

Created: 2025-11-14
Achievement: 0.4 - Library Integration & Production Patterns
"""

from core.libraries.metrics import Counter, Histogram, Gauge, MetricRegistry


# Dashboard action metrics
dashboard_actions_total = Counter(
    "dashboard_actions_total",
    "Total number of dashboard actions executed",
    labels=["action_type", "status"],
)

# Dashboard load time metrics
dashboard_load_duration_seconds = Histogram(
    "dashboard_load_duration_seconds",
    "Time taken to load dashboard in seconds",
    labels=["dashboard_type"],
)

# Cache operation metrics
cache_operations_total = Counter(
    "cache_operations_total",
    "Total cache operations (hits and misses)",
    labels=["cache_name", "operation", "result"],
)

# Plan state metrics
plan_state_info = Gauge(
    "plan_state_info", "Current plan state information", labels=["plan_name", "status"]
)


def register_dashboard_metrics():
    """
    Register all dashboard metrics with the metric registry.

    Should be called once during dashboard initialization.

    **Usage**:
        from LLM.dashboard.metrics import register_dashboard_metrics
        register_dashboard_metrics()
    """
    registry = MetricRegistry.get_instance()
    registry.register(dashboard_actions_total)
    registry.register(dashboard_load_duration_seconds)
    registry.register(cache_operations_total)
    registry.register(plan_state_info)


def track_action(action_type: str, status: str):
    """
    Track a dashboard action.

    Args:
        action_type: Type of action (e.g., 'open_plan', 'close_dashboard')
        status: Action status (e.g., 'success', 'error')

    **Usage**:
        track_action('open_plan', 'success')
    """
    dashboard_actions_total.inc(labels={"action_type": action_type, "status": status})


def track_load_time(dashboard_type: str, duration: float):
    """
    Track dashboard load time.

    Args:
        dashboard_type: Type of dashboard (e.g., 'main', 'plan')
        duration: Load duration in seconds

    **Usage**:
        import time
        start = time.time()
        # ... load dashboard ...
        track_load_time('main', time.time() - start)
    """
    dashboard_load_duration_seconds.observe(
        value=duration, labels={"dashboard_type": dashboard_type}
    )


def track_cache_operation(cache_name: str, operation: str, result: str):
    """
    Track cache operation.

    Args:
        cache_name: Name of the cache (e.g., 'plan_discovery', 'plan_state')
        operation: Operation type (e.g., 'get', 'set', 'invalidate')
        result: Operation result (e.g., 'hit', 'miss', 'success')

    **Usage**:
        track_cache_operation('plan_discovery', 'get', 'hit')
        track_cache_operation('plan_state', 'get', 'miss')
    """
    cache_operations_total.inc(
        labels={"cache_name": cache_name, "operation": operation, "result": result}
    )


def update_plan_state(plan_name: str, status: str, value: float):
    """
    Update plan state gauge.

    Args:
        plan_name: Name of the plan
        status: Current status (e.g., 'active', 'complete', 'needs_attention')
        value: Numeric value (e.g., progress percentage)

    **Usage**:
        update_plan_state('MY-PLAN', 'in_progress', 45.5)
    """
    plan_state_info.set(value=value, labels={"plan_name": plan_name, "status": status})
