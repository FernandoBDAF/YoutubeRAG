"""
Derive ontology from GraphRAG extraction data.

Mines existing graphrag_extraction.data to produce:
- ontology/predicates.yml → canonical predicates, synonyms, symmetry, allowed (src_type, tgt_type) pairs
- ontology/entity_types.yml → observed types + recommended merges/aliases

Usage:
    python scripts/derive_ontology.py [--db DB_NAME] [--coll COLLECTION_NAME]

Environment variables:
    MIN_REL_FREQ: Minimum frequency for predicate (default: 15)
    MIN_REL_DOCS: Minimum document count for predicate (default: 8)
    MIN_TYPE_FREQ: Minimum frequency for entity type (default: 50)
    MIN_REL_CONF: Minimum confidence threshold (default: 0.6)
"""

import os
import re
import sys
import json
import math
import argparse
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Any

from pymongo import MongoClient
from unidecode import unidecode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ---- Config ----
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DEFAULT_DB = os.getenv("MONGODB_DB", "mongo_hack")
DEFAULT_COLL = "video_chunks"  # from core.config.paths.COLL_CHUNKS

MIN_REL_FREQ = int(os.getenv("MIN_REL_FREQ", "15"))
MIN_REL_DOCS = int(os.getenv("MIN_REL_DOCS", "8"))
MIN_TYPE_FREQ = int(os.getenv("MIN_TYPE_FREQ", "50"))
LOWER_BOUND_CONF = float(os.getenv("MIN_REL_CONF", "0.6"))

CANON_TYPES = {
    "PERSON",
    "ORGANIZATION",
    "CONCEPT",
    "METHOD",
    "TECHNOLOGY",
    "PROCESS",
    "TASK",
    "THEORY",
    "LAW",
    "FORMULA",
    "EXPERIMENT",
    "DATASTRUCTURE",
    "ALGORITHM",
    "MODEL",
    "METRIC",
    "COURSE",
    "EVENT",
    "LOCATION",
    "MATERIAL",
    "OTHER",
}


def norm_pred(p: str) -> str:
    """
    Simple normalize/lemma for predicates: lower, snake_case, strip gerunds.

    Args:
        p: Raw predicate string

    Returns:
        Normalized predicate string
    """
    p = unidecode(p.strip().lower())
    p = re.sub(r"[^a-z0-9]+", "_", p)
    p = re.sub(r"_+", "_", p).strip("_")
    # Crude lemma: teaches/teaching -> teach ; includes -> include ; uses -> use
    p = re.sub(r"(ing|es|s)$", "", p)
    return p


def main(db_name: str = None, coll_name: str = None):
    """
    Main function to derive ontology from MongoDB extraction data.

    Args:
        db_name: Database name (defaults to env var or "mongo_hack")
        coll_name: Collection name (defaults to "video_chunks")
    """
    db_name = db_name or DEFAULT_DB
    coll_name = coll_name or DEFAULT_COLL

    print("=" * 80)
    print(f"Deriving ontology from {db_name}.{coll_name}")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  MIN_REL_FREQ: {MIN_REL_FREQ}")
    print(f"  MIN_REL_DOCS: {MIN_REL_DOCS}")
    print(f"  MIN_TYPE_FREQ: {MIN_TYPE_FREQ}")
    print(f"  MIN_REL_CONF: {LOWER_BOUND_CONF}")
    print()

    mc = MongoClient(MONGO_URI)
    coll = mc[db_name][coll_name]

    # Statistics counters
    pred_counter = Counter()
    pred_docs = defaultdict(set)
    pred_pair_types = defaultdict(lambda: Counter())
    pred_conf_vals = defaultdict(list)
    type_counter = Counter()
    type_name_samples = defaultdict(list)

    # Query for completed extractions
    query = {
        "graphrag_extraction.status": "completed",
    }

    cursor = coll.find(query, {"graphrag_extraction.data": 1, "_id": 0})

    print("Processing documents...")
    doc_id = 0
    processed_count = 0

    for doc in cursor:
        doc_id += 1
        extraction_data = doc.get("graphrag_extraction", {}).get("data", {})

        if not extraction_data:
            continue

        ents = extraction_data.get("entities", [])
        rels = extraction_data.get("relationships", [])

        # Type statistics
        for e in ents:
            t = e.get("type", "OTHER")
            type_counter[t] += 1
            if len(type_name_samples[t]) < 15:
                type_name_samples[t].append(e.get("name", "")[:80])

        # Relation statistics
        for r in rels:
            conf = float(r.get("confidence", 0))
            if conf < LOWER_BOUND_CONF:
                continue

            p_raw = r.get("relation", "")
            if not p_raw:
                continue

            p = norm_pred(p_raw)
            pred_counter[p] += 1
            pred_docs[p].add(doc_id)

            source_entity = r.get("source_entity", {})
            target_entity = r.get("target_entity", {})

            src_t = source_entity.get("type", "OTHER")
            tgt_t = target_entity.get("type", "OTHER")

            pred_pair_types[p][(src_t, tgt_t)] += 1
            pred_conf_vals[p].append(conf)

        processed_count += 1

        if doc_id % 100 == 0:
            print(f"  Processed {doc_id} documents...", end="\r")

    print(f"\n  Processed {processed_count} documents with completed extractions")
    print()

    # Choose whitelist by frequency + document support
    print("Analyzing predicates...")
    whitelist = []
    for p, f in pred_counter.most_common():
        if len(pred_docs[p]) >= MIN_REL_DOCS and f >= MIN_REL_FREQ:
            whitelist.append(p)

    print(f"  Found {len(whitelist)} predicates meeting frequency thresholds")

    # Detect symmetry heuristically: if (A,B) and (B,A) both appear frequently
    print("Detecting symmetric predicates...")
    symmetric = set()
    for p in whitelist:
        pairs = pred_pair_types[p]
        ab = sum(cnt for (a, b), cnt in pairs.items())

        # Count reverse pairs
        ba = sum(cnt for (a, b), cnt in pairs.items() if (b, a) in pairs)

        if ab > 0 and ba / ab > 0.35:  # Tune threshold
            symmetric.add(p)

    print(f"  Found {len(symmetric)} symmetric predicates")

    # Build allowed type pairs per predicate (only top K)
    print("Building predicate type constraints...")
    pred_type_allow = {}
    for p in whitelist:
        pairs = pred_pair_types[p].most_common()
        # Keep pairs covering 80% mass or top 8, whichever first
        total = sum(c for _, c in pairs)
        if total == 0:
            continue

        keep = []
        acc = 0
        for (a, b), c in pairs:
            keep.append([a, b])
            acc += c
            if len(keep) >= 8 or acc / total >= 0.8:
                break
        pred_type_allow[p] = keep

    print(f"  Built constraints for {len(pred_type_allow)} predicates")

    # Entity type recommendations (merge into canonical set)
    print("Analyzing entity types...")
    merges = {}
    for t, cnt in type_counter.most_common():
        if t in CANON_TYPES:
            continue

        # Heuristic: map common variants to CONCEPT/METHOD/COURSE/etc.
        samples_text = " ".join(type_name_samples[t]).lower()
        guess = "CONCEPT"

        if re.search(r"course|class|lecture|syllabus", samples_text):
            guess = "COURSE"
        elif re.search(r"algo|method|procedure|approach|technique", samples_text):
            guess = "METHOD"
        elif re.search(r"person|people|individual|instructor|teacher", samples_text):
            guess = "PERSON"
        elif re.search(r"org|company|institution|university|team", samples_text):
            guess = "ORGANIZATION"
        elif re.search(r"tech|tool|software|framework|language|platform", samples_text):
            guess = "TECHNOLOGY"
        elif re.search(r"location|place|city|country|venue", samples_text):
            guess = "LOCATION"
        elif re.search(r"event|meeting|conference|launch", samples_text):
            guess = "EVENT"

        merges[t] = {
            "suggested": guess,
            "count": int(cnt),
            "samples": type_name_samples[t][:5],  # Top 5 samples
        }

    print(f"  Found {len(merges)} non-canonical types with merge suggestions")
    print()

    # Emit YAML
    try:
        import yaml
    except ImportError:
        print("ERROR: PyYAML not installed. Install with: pip install pyyaml")
        return 1

    out_pred = {
        "canonical_predicates": whitelist,
        "symmetric_predicates": sorted(list(symmetric)),
        "predicate_type_constraints": pred_type_allow,
        "stats": {
            p: {
                "count": int(pred_counter[p]),
                "docs": int(len(pred_docs[p])),
                "avg_conf": float(
                    sum(pred_conf_vals[p]) / max(1, len(pred_conf_vals[p]))
                ),
            }
            for p in whitelist
        },
    }

    out_types = {
        "observed_types": {t: int(n) for t, n in type_counter.items()},
        "canonical_types": sorted(list(CANON_TYPES)),
        "merge_suggestions": merges,
        "samples": {t: type_name_samples[t][:10] for t in type_name_samples},
    }

    # Ensure ontology directory exists
    os.makedirs("ontology", exist_ok=True)

    # Write YAML files
    with open("ontology/predicates.yml", "w") as f:
        yaml.safe_dump(
            out_pred, f, sort_keys=False, default_flow_style=False, allow_unicode=True
        )

    with open("ontology/entity_types.yml", "w") as f:
        yaml.safe_dump(
            out_types, f, sort_keys=False, default_flow_style=False, allow_unicode=True
        )

    print("=" * 80)
    print("✅ Successfully generated ontology files:")
    print(f"  - ontology/predicates.yml ({len(whitelist)} canonical predicates)")
    print(f"  - ontology/entity_types.yml ({len(type_counter)} observed types)")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Derive ontology from GraphRAG extraction data"
    )
    parser.add_argument(
        "--db",
        type=str,
        default=None,
        help=f"Database name (default: {DEFAULT_DB})",
    )
    parser.add_argument(
        "--coll",
        type=str,
        default=None,
        help=f"Collection name (default: {DEFAULT_COLL})",
    )

    args = parser.parse_args()
    sys.exit(main(db_name=args.db, coll_name=args.coll))
