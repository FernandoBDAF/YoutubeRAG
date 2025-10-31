#!/usr/bin/env python3
"""
GraphRAG Production Monitoring Dashboard - FUTURE ENHANCEMENT

⚠️  STATUS: NON-FUNCTIONAL - Missing dependency (graphrag_production.py)

This script was designed to provide a real-time monitoring dashboard for GraphRAG
production systems with performance metrics, alerts, and system status.

CURRENT STATUS:
- ❌ Cannot run - missing app.services.graphrag_production module
- ❌ graphrag_production.py was removed (see documentation/RECENT-UPDATES.md)
- ❌ Premature optimization for development phase

INTENDED USAGE (when implemented):
- Real-time system health monitoring
- Performance metrics (query times, error rates)
- System resources (CPU, memory, disk)
- Alerts and thresholds
- Cache statistics
- Circuit breaker state
- Metrics export

CURRENT ALTERNATIVES:
- GraphRAGPipeline.get_pipeline_status() - Basic pipeline status
- run_graphrag_pipeline.py --status - CLI status check
- Stage logging - Progress and error tracking

FUTURE IMPLEMENTATION:
- Revisit when entering staging/production phase
- Consider simplified version using existing pipeline status
- See documentation/DEPLOYMENT.md for production monitoring plan

This file is preserved as an example of the intended monitoring approach.
"""

import os
import sys
import time
import json
import argparse
from typing import Dict, Any, List
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.graphrag_config import load_config_from_env
from app.services.graphrag_production import create_production_manager

try:
    import psutil
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.animation import FuncAnimation

    HAS_PLOTTING = True
except ImportError:
    HAS_PLOTTING = False
    print("Warning: matplotlib not available. Dashboard will run in text mode only.")


class GraphRAGMonitoringDashboard:
    """Real-time monitoring dashboard for GraphRAG."""

    def __init__(self, config):
        self.config = config
        self.production_manager = create_production_manager(
            config.mongodb_uri,
            config.database_name,
            **config.to_production_config().__dict__,
        )
        self.metrics_history = []
        self.max_history_points = 100

    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        try:
            # Get system status
            status = self.production_manager.get_system_status()

            # Get performance summary
            performance = self.production_manager.monitor.get_performance_summary(
                hours=1
            )

            # Get recent alerts
            alerts = self.production_manager.monitor.get_recent_alerts(hours=1)

            # Get system resources
            system_resources = {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
                "memory_available_mb": psutil.virtual_memory().available / 1024 / 1024,
                "load_average": os.getloadavg()[0] if hasattr(os, "getloadavg") else 0,
            }

            # Get cache statistics
            cache_stats = self.production_manager.cache.get_cache_stats()

            # Get circuit breaker state
            circuit_breaker_state = self.production_manager.circuit_breaker.get_state()

            return {
                "timestamp": time.time(),
                "system_resources": system_resources,
                "cache_stats": cache_stats,
                "performance_summary": performance,
                "recent_alerts": alerts,
                "circuit_breaker_state": circuit_breaker_state,
                "status": status,
            }

        except Exception as e:
            return {"timestamp": time.time(), "error": str(e)}

    def update_metrics_history(self, metrics: Dict[str, Any]):
        """Update metrics history for trending."""
        self.metrics_history.append(metrics)

        # Keep only recent history
        if len(self.metrics_history) > self.max_history_points:
            self.metrics_history.pop(0)

    def print_text_dashboard(self, metrics: Dict[str, Any]):
        """Print a text-based dashboard."""
        os.system("clear" if os.name == "posix" else "cls")

        print("=" * 80)
        print("GraphRAG Production Monitoring Dashboard")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Environment: {self.config.environment}")
        print()

        if "error" in metrics:
            print(f"ERROR: {metrics['error']}")
            return

        # System Resources
        resources = metrics.get("system_resources", {})
        print("SYSTEM RESOURCES:")
        print(f"  CPU Usage: {resources.get('cpu_percent', 0):.1f}%")
        print(f"  Memory Usage: {resources.get('memory_percent', 0):.1f}%")
        print(f"  Disk Usage: {resources.get('disk_percent', 0):.1f}%")
        print(f"  Available Memory: {resources.get('memory_available_mb', 0):.0f} MB")
        print(f"  Load Average: {resources.get('load_average', 0):.2f}")
        print()

        # Cache Statistics
        cache_stats = metrics.get("cache_stats", {})
        print("CACHE STATISTICS:")
        print(f"  Entity Cache: {cache_stats.get('entity_cache_size', 0)} entries")
        print(
            f"  Community Cache: {cache_stats.get('community_cache_size', 0)} entries"
        )
        print(f"  Query Cache: {cache_stats.get('query_cache_size', 0)} entries")
        print(f"  Total Cache Size: {cache_stats.get('total_cache_size', 0)} entries")
        print(f"  Max Cache Size: {cache_stats.get('max_cache_size', 0)} entries")
        print()

        # Performance Summary
        performance = metrics.get("performance_summary", {})
        if performance and "error" not in performance:
            print("PERFORMANCE SUMMARY (Last Hour):")
            print(f"  Total Operations: {performance.get('total_operations', 0)}")
            print(f"  Total Errors: {performance.get('total_errors', 0)}")
            print(f"  Error Rate: {performance.get('error_rate', 0):.2%}")

            operations = performance.get("operations", [])
            if operations:
                print("  Operations Breakdown:")
                for op in operations[:5]:  # Show top 5 operations
                    print(
                        f"    {op['_id']}: {op['total_operations']} ops, "
                        f"{op['avg_execution_time']:.1f}ms avg"
                    )
            print()

        # Recent Alerts
        alerts = metrics.get("recent_alerts", [])
        if alerts:
            print("RECENT ALERTS:")
            for alert in alerts[:5]:  # Show last 5 alerts
                alert_time = datetime.fromtimestamp(alert.get("timestamp", 0))
                print(
                    f"  [{alert_time.strftime('%H:%M:%S')}] {alert.get('type', 'unknown')}: "
                    f"{alert.get('value', 0)} (threshold: {alert.get('threshold', 0)})"
                )
            print()

        # Circuit Breaker State
        cb_state = metrics.get("circuit_breaker_state", {})
        print("CIRCUIT BREAKER:")
        print(f"  State: {cb_state.get('state', 'UNKNOWN')}")
        print(f"  Failure Count: {cb_state.get('failure_count', 0)}")
        print(f"  Threshold: {cb_state.get('failure_threshold', 0)}")
        print()

        # GraphRAG Status
        status = metrics.get("status", {})
        if status and "error" not in status:
            print("GRAPHRAG STATUS:")
            print(f"  Monitoring Enabled: {self.config.enable_monitoring}")
            print(f"  Caching Enabled: {self.config.enable_caching}")
            print(
                f"  Max Concurrent Operations: {self.config.max_concurrent_extractions}"
            )
            print(f"  Operation Timeout: {self.config.operation_timeout_ms}ms")
            print()

        print("=" * 80)
        print("Press Ctrl+C to exit")

    def create_plot_dashboard(self):
        """Create a matplotlib-based dashboard."""
        if not HAS_PLOTTING:
            print("Matplotlib not available. Running in text mode.")
            return

        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle("GraphRAG Production Monitoring Dashboard", fontsize=16)

        # Initialize empty data
        timestamps = []
        cpu_data = []
        memory_data = []
        cache_data = []
        error_rate_data = []

        def update_plot(frame):
            # Get current metrics
            metrics = self.get_current_metrics()
            self.update_metrics_history(metrics)

            if "error" in metrics:
                return

            current_time = datetime.now()
            timestamps.append(current_time)

            # Keep only recent data
            if len(timestamps) > 50:
                timestamps.pop(0)
                cpu_data.pop(0)
                memory_data.pop(0)
                cache_data.pop(0)
                error_rate_data.pop(0)

            # Extract data
            resources = metrics.get("system_resources", {})
            cache_stats = metrics.get("cache_stats", {})
            performance = metrics.get("performance_summary", {})

            cpu_data.append(resources.get("cpu_percent", 0))
            memory_data.append(resources.get("memory_percent", 0))
            cache_data.append(cache_stats.get("total_cache_size", 0))
            error_rate_data.append(performance.get("error_rate", 0) * 100)

            # Clear axes
            for ax in axes.flat:
                ax.clear()

            # Plot CPU usage
            axes[0, 0].plot(timestamps, cpu_data, "b-", linewidth=2)
            axes[0, 0].set_title("CPU Usage (%)")
            axes[0, 0].set_ylabel("CPU %")
            axes[0, 0].grid(True)
            axes[0, 0].set_ylim(0, 100)

            # Plot Memory usage
            axes[0, 1].plot(timestamps, memory_data, "r-", linewidth=2)
            axes[0, 1].set_title("Memory Usage (%)")
            axes[0, 1].set_ylabel("Memory %")
            axes[0, 1].grid(True)
            axes[0, 1].set_ylim(0, 100)

            # Plot Cache size
            axes[1, 0].plot(timestamps, cache_data, "g-", linewidth=2)
            axes[1, 0].set_title("Cache Size")
            axes[1, 0].set_ylabel("Cache Entries")
            axes[1, 0].grid(True)

            # Plot Error rate
            axes[1, 1].plot(timestamps, error_rate_data, "orange", linewidth=2)
            axes[1, 1].set_title("Error Rate (%)")
            axes[1, 1].set_ylabel("Error %")
            axes[1, 1].grid(True)
            axes[1, 1].set_ylim(0, 10)

            # Format x-axis
            for ax in axes.flat:
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
                ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
                plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)

            plt.tight_layout()

        # Create animation
        ani = FuncAnimation(fig, update_plot, interval=5000, blit=False)

        plt.show()

    def run_text_dashboard(self, refresh_interval: int = 5):
        """Run the text-based dashboard."""
        try:
            while True:
                metrics = self.get_current_metrics()
                self.update_metrics_history(metrics)
                self.print_text_dashboard(metrics)
                time.sleep(refresh_interval)
        except KeyboardInterrupt:
            print("\nDashboard stopped by user")

    def run_plot_dashboard(self):
        """Run the matplotlib-based dashboard."""
        if HAS_PLOTTING:
            self.create_plot_dashboard()
        else:
            print("Matplotlib not available. Install matplotlib to use plot dashboard.")

    def export_metrics(self, output_file: str, hours: int = 24):
        """Export metrics to a file."""
        try:
            # Get performance summary
            performance = self.production_manager.monitor.get_performance_summary(
                hours=hours
            )

            # Get recent alerts
            alerts = self.production_manager.monitor.get_recent_alerts(hours=hours)

            # Get system status
            status = self.production_manager.get_system_status()

            export_data = {
                "export_timestamp": time.time(),
                "export_period_hours": hours,
                "environment": self.config.environment,
                "performance_summary": performance,
                "recent_alerts": alerts,
                "system_status": status,
                "configuration": self.config.get_environment_summary(),
            }

            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2)

            print(f"Metrics exported to {output_file}")

        except Exception as e:
            print(f"Failed to export metrics: {e}")


def main():
    """Main monitoring dashboard function."""
    parser = argparse.ArgumentParser(
        description="GraphRAG Production Monitoring Dashboard"
    )
    parser.add_argument(
        "--environment",
        choices=["development", "staging", "production"],
        default=os.getenv("GRAPHRAG_ENVIRONMENT", "development"),
        help="Target environment",
    )
    parser.add_argument(
        "--mode", choices=["text", "plot"], default="text", help="Dashboard mode"
    )
    parser.add_argument(
        "--refresh-interval",
        type=int,
        default=5,
        help="Refresh interval in seconds (text mode only)",
    )
    parser.add_argument("--export", type=str, help="Export metrics to file")
    parser.add_argument(
        "--export-hours", type=int, default=24, help="Hours of data to export"
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = load_config_from_env(args.environment)

        # Create dashboard
        dashboard = GraphRAGMonitoringDashboard(config)

        # Export metrics if requested
        if args.export:
            dashboard.export_metrics(args.export, args.export_hours)
            return

        # Run dashboard
        if args.mode == "text":
            dashboard.run_text_dashboard(args.refresh_interval)
        elif args.mode == "plot":
            dashboard.run_plot_dashboard()

    except Exception as e:
        print(f"Dashboard failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
