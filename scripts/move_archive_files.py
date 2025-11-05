#!/usr/bin/env python3
"""
Move documentation files to archive directories.

This script moves implementation documentation files from root to their
appropriate archive directories as specified in DOCUMENTATION-ARCHIVING-PLAN.md
"""

import os
import shutil
from pathlib import Path


def main():
    root = Path(".")

    # Define all file moves
    moves = [
        # Experiment Infrastructure
        (
            "EXPERIMENT-INFRASTRUCTURE-COMPLETE.md",
            "documentation/archive/experiment-infrastructure-nov-2025/implementation/",
        ),
        (
            "CHECKPOINT-EXPERIMENT-INFRASTRUCTURE.md",
            "documentation/archive/experiment-infrastructure-nov-2025/implementation/",
        ),
        (
            "EXPERIMENT-MVP-READY.md",
            "documentation/archive/experiment-infrastructure-nov-2025/summaries/",
        ),
        (
            "QUICK-REFERENCE-EXPERIMENTS.md",
            "documentation/archive/experiment-infrastructure-nov-2025/summaries/",
        ),
        # Ontology Planning
        (
            "NORMALIZATION-FIX-PLAN.md",
            "documentation/archive/ontology-implementation-nov-2025/planning/",
        ),
        (
            "NORMALIZATION-LLM-IMPLEMENTATION-PLAN.md",
            "documentation/archive/ontology-implementation-nov-2025/planning/",
        ),
        (
            "GraphRAG_Ontology_Feedback_Prompt.md",
            "documentation/archive/ontology-implementation-nov-2025/planning/",
        ),
        (
            "REFRACTOR_PROMPT__ONTOLOGY_INJECTION.md",
            "documentation/archive/ontology-implementation-nov-2025/planning/",
        ),
        # Ontology Implementation
        (
            "ONTOLOGY-REFACTOR-REVIEW-COMPLETE.md",
            "documentation/archive/ontology-implementation-nov-2025/implementation/",
        ),
        (
            "NORMALIZATION-FIX-COMPLETE.md",
            "documentation/archive/ontology-implementation-nov-2025/implementation/",
        ),
        (
            "NORMALIZATION-SIMPLIFIED-COMPLETE.md",
            "documentation/archive/ontology-implementation-nov-2025/implementation/",
        ),
        (
            "NORMALIZATION-TEST-FIX-COMPLETE.md",
            "documentation/archive/ontology-implementation-nov-2025/implementation/",
        ),
        (
            "NORMALIZATION-PREDICATE-MAP-FIX.md",
            "documentation/archive/ontology-implementation-nov-2025/implementation/",
        ),
        (
            "ONTOLOGY-TESTS-REFACTOR-COMPLETE.md",
            "documentation/archive/ontology-implementation-nov-2025/implementation/",
        ),
        # Ontology Analysis
        (
            "NORMALIZATION-ANALYSIS.md",
            "documentation/archive/ontology-implementation-nov-2025/analysis/",
        ),
        (
            "NORMALIZATION-AMBIGUOUS-CASES.md",
            "documentation/archive/ontology-implementation-nov-2025/analysis/",
        ),
        (
            "NORMALIZATION-DEBUG-REPORT.md",
            "documentation/archive/ontology-implementation-nov-2025/analysis/",
        ),
        (
            "NORMALIZATION-ISSUE-ANALYSIS.md",
            "documentation/archive/ontology-implementation-nov-2025/analysis/",
        ),
        (
            "NORMALIZATION-LLM-ANALYSIS.md",
            "documentation/archive/ontology-implementation-nov-2025/analysis/",
        ),
        (
            "SOFT-KEEP-ANALYSIS.md",
            "documentation/archive/ontology-implementation-nov-2025/analysis/",
        ),
        (
            "SYMMETRIC-NORMALIZATION-DEBUG-REVIEW.md",
            "documentation/archive/ontology-implementation-nov-2025/analysis/",
        ),
        # Extraction Optimization
        (
            "EXTRACTION-REFACTOR.md",
            "documentation/archive/extraction-optimization-nov-2025/planning/",
        ),
        (
            "EXTRACTION-IMPROVEMENTS-SUMMARY.md",
            "documentation/archive/extraction-optimization-nov-2025/implementation/",
        ),
        (
            "GRAPHRAG_EXTRACTION_REFACTOR.md",
            "documentation/archive/extraction-optimization-nov-2025/implementation/",
        ),
        (
            "EXTRACTION-RUN-ANALYSIS.md",
            "documentation/archive/extraction-optimization-nov-2025/analysis/",
        ),
        (
            "COST-ANALYSIS-AND-TEST-STATUS.md",
            "documentation/archive/extraction-optimization-nov-2025/analysis/",
        ),
        # Community Detection
        (
            "LOUVAIN-IMPLEMENTATION-COMPLETE.md",
            "documentation/archive/community-detection-nov-2025/implementation/",
        ),
        # Concurrency Optimization
        (
            "CONCURRENCY-REFACTOR-COMPLETE.md",
            "documentation/archive/concurrency-optimization-nov-2025/implementation/",
        ),
        # Session Summaries
        (
            "SESSION-COMPLETE-NOV-4-2025.md",
            "documentation/archive/session-summaries-nov-2025/summaries/",
        ),
        (
            "SESSION-SUMMARY-NOV-4-2025-COMPLETE.md",
            "documentation/archive/session-summaries-nov-2025/summaries/",
        ),
        (
            "HANDOFF-TO-QUALITY-IMPROVEMENTS.md",
            "documentation/archive/session-summaries-nov-2025/summaries/",
        ),
        # Testing & Validation
        (
            "TEST-EXECUTION-EXPLANATION.md",
            "documentation/archive/testing-validation-nov-2025/implementation/",
        ),
        (
            "TEST-STATUS-AND-ANSWERS.md",
            "documentation/archive/testing-validation-nov-2025/summaries/",
        ),
        (
            "ANSWERS-AND-TEST-STATUS.md",
            "documentation/archive/testing-validation-nov-2025/summaries/",
        ),
        # General Refactoring
        (
            "REFACTORING-COMPLETE-FINAL.md",
            "documentation/archive/graphrag-optimization-nov-2025/implementation/",
        ),
    ]

    moved = 0
    not_found = []
    errors = []

    for filename, dest_dir in moves:
        src = root / filename
        if src.exists():
            try:
                dest = Path(dest_dir)
                dest.mkdir(parents=True, exist_ok=True)
                dest_path = dest / filename
                shutil.move(str(src), str(dest_path))
                moved += 1
                print(f"✓ Moved: {filename}")
            except Exception as e:
                errors.append((filename, str(e)))
                print(f"✗ Error moving {filename}: {e}")
        else:
            not_found.append(filename)
            print(f"⚠ Not found: {filename}")

    print(f'\n{"="*60}')
    print(f"Summary:")
    print(f"  Moved: {moved}/{len(moves)}")
    if not_found:
        print(f"  Not found: {len(not_found)}")
    if errors:
        print(f"  Errors: {len(errors)}")
    print(f'{"="*60}')

    if not_found:
        print(f"\nFiles not found (may have been moved already):")
        for f in not_found:
            print(f"  - {f}")

    if errors:
        print(f"\nErrors encountered:")
        for f, e in errors:
            print(f"  - {f}: {e}")


if __name__ == "__main__":
    main()
