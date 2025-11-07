#!/usr/bin/env python3
"""
Metrics Summary

Query and summarize metrics from Prometheus export.
"""

import argparse
import json
import os
import sys
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from core.libraries.metrics import MetricRegistry, export_prometheus_text
from core.libraries.error_handling.decorators import handle_errors


@handle_errors(log_traceback=True, reraise=True)
def generate_metrics_summary(format: str = "table", output: Optional[str] = None) -> None:
    """Generate metrics summary from Prometheus export."""
    # Export metrics
    export = export_prometheus_text()

    # Parse metrics
    metrics_data: Dict[str, Any] = {
        "stage_metrics": {},
        "agent_metrics": {},
        "service_metrics": {},
        "pipeline_metrics": {},
    }

    lines = export.split("\n")
    for line in lines:
        if line.startswith("#") or not line.strip():
            continue

        # Parse Prometheus format: metric_name{labels} value
        if "{" in line:
            parts = line.split("{")
            metric_name = parts[0].strip()
            rest = "}".join(parts[1:])
            if "}" in rest:
                value_part = rest.split("}")[1].strip()
                try:
                    value = float(value_part)
                except ValueError:
                    continue
            else:
                continue
        else:
            parts = line.split()
            if len(parts) >= 2:
                metric_name = parts[0]
                try:
                    value = float(parts[1])
                except ValueError:
                    continue
            else:
                continue

        # Categorize metrics
        if "stage_" in metric_name:
            metrics_data["stage_metrics"][metric_name] = value
        elif "agent_" in metric_name:
            metrics_data["agent_metrics"][metric_name] = value
        elif "service_" in metric_name or "rag_" in metric_name or "graphrag_" in metric_name:
            metrics_data["service_metrics"][metric_name] = value
        elif "pipeline_" in metric_name:
            metrics_data["pipeline_metrics"][metric_name] = value

    # Format output
    if format == "json":
        output_data = json.dumps(metrics_data, indent=2, default=str)
    else:  # table
        lines = ["\n📊 Metrics Summary", "=" * 80]

        if metrics_data["stage_metrics"]:
            lines.append("\n🎯 Stage Metrics:")
            for name, value in sorted(metrics_data["stage_metrics"].items()):
                lines.append(f"  {name}: {value}")

        if metrics_data["agent_metrics"]:
            lines.append("\n🤖 Agent Metrics:")
            for name, value in sorted(metrics_data["agent_metrics"].items()):
                lines.append(f"  {name}: {value}")

        if metrics_data["service_metrics"]:
            lines.append("\n⚙️  Service Metrics:")
            for name, value in sorted(metrics_data["service_metrics"].items()):
                lines.append(f"  {name}: {value}")

        if metrics_data["pipeline_metrics"]:
            lines.append("\n🔄 Pipeline Metrics:")
            for name, value in sorted(metrics_data["pipeline_metrics"].items()):
                lines.append(f"  {name}: {value}")

        if not any(metrics_data.values()):
            lines.append("\n⚠️  No metrics found (may need to run pipeline stages first)")

        lines.append("=" * 80)
        output_data = "\n".join(lines)

    if output:
        with open(output, "w") as f:
            f.write(output_data)
        print(f"✅ Metrics summary saved to {output}")
    else:
        print(output_data)


def main():
    parser = argparse.ArgumentParser(description="Generate metrics summary")
    parser.add_argument(
        "--format", choices=["table", "json"], default="table", help="Output format"
    )
    parser.add_argument("--output", help="Output file path")

    args = parser.parse_args()
    generate_metrics_summary(format=args.format, output=args.output)


if __name__ == "__main__":
    main()
