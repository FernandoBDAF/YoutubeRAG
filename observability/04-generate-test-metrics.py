#!/usr/bin/env python3
################################################################################
# Generate Test Metrics
#
# Purpose: Generate sample metrics for testing Prometheus scraping
# Usage: python3 observability/04-generate-test-metrics.py
#
# This script starts a metrics server on http://localhost:9091/metrics
# and generates test metrics every 5 seconds.
################################################################################

import time
import random
import sys
from prometheus_client import Counter, Gauge, Histogram, start_http_server

# Color codes for output
GREEN = "\033[0;32m"
BLUE = "\033[0;34m"
YELLOW = "\033[1;33m"
NC = "\033[0m"

# Create test metrics
test_counter = Counter(
    "test_metric_total", "Test counter metric for validation", ["label", "environment"]
)

test_gauge = Gauge("test_gauge", "Test gauge metric for validation")

test_histogram = Histogram(
    "test_histogram_seconds",
    "Test histogram metric for validation",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0],
)

# Additional application-like metrics
pipeline_duration = Histogram(
    "pipeline_duration_seconds", "Mock pipeline execution duration", ["stage"]
)

documents_processed = Counter("documents_processed_total", "Mock documents processed", ["stage"])

stage_errors = Counter("stage_errors_total", "Mock stage errors", ["stage", "error_type"])


def generate_metrics():
    """Generate test metrics every 5 seconds."""
    print()
    print(f"{BLUE}════════════════════════════════════════════════════════════${NC}")
    print(f"{BLUE}  Test Metrics Generator${NC}")
    print(f"{BLUE}════════════════════════════════════════════════════════════${NC}")
    print()
    print(f"{GREEN}✅ Started metrics server on http://localhost:9091/metrics${NC}")
    print(f"{YELLOW}ℹ️  Metrics are generated every 5 seconds${NC}")
    print()
    print("Generating metrics...")
    print()

    counter_value = 0
    iteration = 0

    try:
        while True:
            iteration += 1

            # Increment counters
            test_counter.labels(label="test", environment="validation").inc()
            counter_value += 1

            # Set gauge to random value
            test_gauge.set(random.randint(0, 100))

            # Record histogram values
            test_histogram.observe(random.uniform(0.1, 2.0))

            # Simulate pipeline metrics
            for stage in ["extraction", "resolution", "construction", "detection"]:
                pipeline_duration.labels(stage=stage).observe(random.uniform(0.5, 5.0))
                documents_processed.labels(stage=stage).inc(random.randint(1, 10))

                # Occasionally add errors
                if random.random() < 0.1:
                    stage_errors.labels(stage=stage, error_type="timeout").inc()

            # Print status
            print(f"  Iteration {iteration:4d}: Generated metrics")
            print(f"    - Counter: {counter_value}")
            print(f"    - Gauge: {test_gauge._value.get():.0f}")
            print(
                f"    - Histogram entries: {counter_value * 3}"
            )  # 3 histogram values per iteration

            # Wait 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print()
        print()
        print(f"{GREEN}✅ Metrics generation stopped${NC}")
        sys.exit(0)


def main():
    """Main entry point."""
    try:
        # Start Prometheus metrics server on port 9091
        start_http_server(9091)

        # Generate metrics
        generate_metrics()

    except Exception as e:
        print(f"{YELLOW}❌ Error: {e}${NC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
