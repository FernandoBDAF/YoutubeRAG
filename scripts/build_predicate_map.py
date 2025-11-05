"""
Build a canonicalization table for predicates (synonyms → canonical).

Reads predicates.yml, scans all relations again, and outputs:
- ontology/predicate_map.yml with entries mapping variants to canonical predicates

Heuristic:
- Normalize (norm_pred) then string-similarity (Jaro-Winkler) against canonical set
- Use type constraints: if a predicate mostly appears as (PERSON→COURSE), map to teaches
- Only auto-map if similarity ≥ 0.88 and type-pair compatibility is high
- Otherwise emit to review list for manual decision

Usage:
    python scripts/build_predicate_map.py [--db DB_NAME] [--coll COLLECTION_NAME] [--predicates-file PATH]
    
Environment variables:
    MIN_SIMILARITY: Minimum Jaro-Winkler similarity (default: 0.88)
    MIN_TYPE_COMPAT: Minimum type-pair compatibility (default: 0.7)
"""

import os
import re
import sys
import argparse
from collections import Counter, defaultdict
from typing import Dict, List, Set, Tuple, Any, Optional

from pymongo import MongoClient
from unidecode import unidecode
from dotenv import load_dotenv

try:
    # Try different possible import names for jaro-winkler
    try:
        from jaro_winkler import jaro_winkler_similarity
    except ImportError:
        try:
            from jarowinkler import jarowinkler_similarity as jaro_winkler_similarity
        except ImportError:
            # Use jellyfish as alternative
            from jellyfish import jaro_winkler_similarity
except ImportError:
    # Fallback to difflib if jaro-winkler/jellyfish not available
    from difflib import SequenceMatcher
    
    def jaro_winkler_similarity(s1: str, s2: str) -> float:
        """Fallback similarity using SequenceMatcher."""
        return SequenceMatcher(None, s1, s2).ratio()

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML not installed. Install with: pip install pyyaml")
    sys.exit(1)

# Load environment variables
load_dotenv()

# ---- Config ----
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DEFAULT_DB = os.getenv("MONGODB_DB", "mongo_hack")
DEFAULT_COLL = "video_chunks"
DEFAULT_PREDICATES_FILE = "ontology/predicates.yml"

MIN_SIMILARITY = float(os.getenv("MIN_SIMILARITY", "0.88"))
MIN_TYPE_COMPAT = float(os.getenv("MIN_TYPE_COMPAT", "0.7"))


def norm_pred(p: str) -> str:
    """
    Normalize predicate: lower, snake_case, strip gerunds.
    
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


def compute_type_compatibility(
    pred_type_pairs: Counter,
    canon_type_pairs: List[List[str]],
) -> float:
    """
    Compute compatibility score between predicate's type pairs and canonical's.
    
    Args:
        pred_type_pairs: Counter of (src_type, tgt_type) pairs for this predicate
        canon_type_pairs: List of allowed [src_type, tgt_type] pairs for canonical
        
    Returns:
        Compatibility score (0.0 to 1.0)
    """
    if not pred_type_pairs or not canon_type_pairs:
        return 0.0
    
    canon_set = set(tuple(p) for p in canon_type_pairs)
    total = sum(pred_type_pairs.values())
    
    if total == 0:
        return 0.0
    
    # Count how many of this predicate's pairs match canonical
    matches = sum(
        cnt for (src, tgt), cnt in pred_type_pairs.items()
        if (src, tgt) in canon_set
    )
    
    return matches / total


def find_best_canonical_match(
    pred: str,
    pred_type_pairs: Counter,
    canonical_preds: List[str],
    pred_type_constraints: Dict[str, List[List[str]]],
    min_similarity: float = MIN_SIMILARITY,
    min_type_compat: float = MIN_TYPE_COMPAT,
) -> Optional[Tuple[str, float, float]]:
    """
    Find best canonical match for a predicate.
    
    Args:
        pred: Normalized predicate to match
        pred_type_pairs: Type pairs seen for this predicate
        canonical_preds: List of canonical predicates
        pred_type_constraints: Type constraints for canonical predicates
        min_similarity: Minimum similarity threshold
        min_type_compat: Minimum type compatibility threshold
        
    Returns:
        Tuple of (canonical_pred, similarity_score, type_compat_score) or None
    """
    best_match = None
    best_sim = 0.0
    best_compat = 0.0
    
    for canon in canonical_preds:
        # Compute string similarity
        sim = jaro_winkler_similarity(pred, canon)
        
        if sim < min_similarity:
            continue
        
        # Compute type compatibility
        canon_types = pred_type_constraints.get(canon, [])
        compat = compute_type_compatibility(pred_type_pairs, canon_types)
        
        if compat < min_type_compat:
            continue
        
        # Combined score (weighted)
        combined = (sim * 0.6) + (compat * 0.4)
        
        if best_match is None or combined > (best_sim * 0.6 + best_compat * 0.4):
            best_match = canon
            best_sim = sim
            best_compat = compat
    
    if best_match:
        return (best_match, best_sim, best_compat)
    return None


def main(
    db_name: str = None,
    coll_name: str = None,
    predicates_file: str = None,
):
    """
    Main function to build predicate canonicalization map.
    
    Args:
        db_name: Database name
        coll_name: Collection name
        predicates_file: Path to predicates.yml file
    """
    db_name = db_name or DEFAULT_DB
    coll_name = coll_name or DEFAULT_COLL
    predicates_file = predicates_file or DEFAULT_PREDICATES_FILE
    
    print("=" * 80)
    print(f"Building predicate canonicalization map")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  Database: {db_name}")
    print(f"  Collection: {coll_name}")
    print(f"  Predicates file: {predicates_file}")
    print(f"  MIN_SIMILARITY: {MIN_SIMILARITY}")
    print(f"  MIN_TYPE_COMPAT: {MIN_TYPE_COMPAT}")
    print()
    
    # Load predicates.yml
    if not os.path.exists(predicates_file):
        print(f"ERROR: Predicates file not found: {predicates_file}")
        print("Run scripts/derive_ontology.py first to generate predicates.yml")
        return 1
    
    with open(predicates_file, "r") as f:
        predicates_data = yaml.safe_load(f)
    
    canonical_preds = predicates_data.get("canonical_predicates", [])
    pred_type_constraints = predicates_data.get("predicate_type_constraints", {})
    
    print(f"Loaded {len(canonical_preds)} canonical predicates")
    print()
    
    # Connect to MongoDB
    mc = MongoClient(MONGO_URI)
    coll = mc[db_name][coll_name]
    
    # Collect all predicates and their type pairs
    print("Scanning all predicates in database...")
    all_preds = Counter()  # Count of normalized predicates
    pred_type_pairs_map = defaultdict(lambda: Counter())  # pred -> Counter of (src, tgt) pairs
    pred_raw_map = defaultdict(set)  # normalized -> set of raw variants
    
    query = {
        "graphrag_extraction.status": "completed",
    }
    
    cursor = coll.find(
        query,
        {"graphrag_extraction.data": 1, "_id": 0}
    )
    
    doc_count = 0
    for doc in cursor:
        doc_count += 1
        extraction_data = doc.get("graphrag_extraction", {}).get("data", {})
        
        if not extraction_data:
            continue
        
        rels = extraction_data.get("relationships", [])
        
        for r in rels:
            p_raw = r.get("relation", "")
            if not p_raw:
                continue
            
            p_norm = norm_pred(p_raw)
            all_preds[p_norm] += 1
            pred_raw_map[p_norm].add(p_raw)
            
            source_entity = r.get("source_entity", {})
            target_entity = r.get("target_entity", {})
            
            src_t = source_entity.get("type", "OTHER")
            tgt_t = target_entity.get("type", "OTHER")
            
            pred_type_pairs_map[p_norm][(src_t, tgt_t)] += 1
        
        if doc_count % 100 == 0:
            print(f"  Processed {doc_count} documents...", end="\r")
    
    print(f"\n  Processed {doc_count} documents")
    print(f"  Found {len(all_preds)} unique normalized predicates")
    print()
    
    # Build canonicalization map
    print("Building canonicalization map...")
    auto_mapped = {}
    review_list = []
    
    for pred, count in all_preds.most_common():
        # Skip if already canonical
        if pred in canonical_preds:
            continue
        
        # Find best match
        pred_type_pairs = pred_type_pairs_map[pred]
        match = find_best_canonical_match(
            pred,
            pred_type_pairs,
            canonical_preds,
            pred_type_constraints,
            min_similarity=MIN_SIMILARITY,
            min_type_compat=MIN_TYPE_COMPAT,
        )
        
        if match:
            canon, sim, compat = match
            auto_mapped[pred] = {
                "canonical": canon,
                "similarity": round(sim, 3),
                "type_compatibility": round(compat, 3),
                "count": int(count),
                "raw_variants": sorted(list(pred_raw_map[pred]))[:10],  # Top 10 variants
            }
        else:
            # Add to review list
            review_list.append({
                "predicate": pred,
                "count": int(count),
                "type_pairs": dict(pred_type_pairs.most_common(5)),
                "raw_variants": sorted(list(pred_raw_map[pred]))[:10],
            })
    
    print(f"  Auto-mapped: {len(auto_mapped)} predicates")
    print(f"  Needs review: {len(review_list)} predicates")
    print()
    
    # Build output
    output = {
        "auto_mapped": auto_mapped,
        "review_list": review_list,
        "stats": {
            "total_unique_predicates": len(all_preds),
            "canonical_predicates": len(canonical_preds),
            "auto_mapped_count": len(auto_mapped),
            "review_count": len(review_list),
        },
    }
    
    # Write YAML
    os.makedirs("ontology", exist_ok=True)
    
    output_file = "ontology/predicate_map.yml"
    with open(output_file, "w") as f:
        yaml.safe_dump(
            output,
            f,
            sort_keys=False,
            default_flow_style=False,
            allow_unicode=True,
        )
    
    print("=" * 80)
    print(f"✅ Successfully generated: {output_file}")
    print(f"  Auto-mapped: {len(auto_mapped)} predicates")
    print(f"  Review needed: {len(review_list)} predicates")
    print("=" * 80)
    
    if review_list:
        print("\n⚠️  Predicates needing manual review:")
        for item in review_list[:10]:  # Show first 10
            print(f"  - {item['predicate']} (count: {item['count']})")
        if len(review_list) > 10:
            print(f"  ... and {len(review_list) - 10} more")
    
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Build predicate canonicalization map"
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
    parser.add_argument(
        "--predicates-file",
        type=str,
        default=None,
        help=f"Path to predicates.yml (default: {DEFAULT_PREDICATES_FILE})",
    )
    
    args = parser.parse_args()
    sys.exit(main(db_name=args.db, coll_name=args.coll, predicates_file=args.predicates_file))

