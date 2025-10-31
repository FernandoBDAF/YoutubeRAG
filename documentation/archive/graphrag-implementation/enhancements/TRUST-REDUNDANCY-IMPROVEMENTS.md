# Trust & Redundancy Stage Improvements

## Overview

This document outlines proposed improvements for the Trust and Redundancy stages based on analysis of actual pipeline execution data. These improvements aim to enhance score granularity, content differentiation, and overall system quality.

**Status**: Planning/Backlog  
**Priority**: Medium  
**Last Updated**: 2025-10-30

---

## Current State Analysis

### Redundancy Stage ✅

- **Status**: Working correctly
- **Threshold**: 0.92 (92% cosine similarity)
- **Method**: Cosine similarity on embeddings + optional LLM verification
- **Primary Selection**: Lexicographic ordering (deterministic)
- **Findings**: Correctly identifies duplicates, properly links to primary chunks

### Trust Stage ⚠️

- **Status**: Functional but limited differentiation
- **Method**: Heuristic-based scoring (default), optional LLM scoring
- **Current Issues**:
  1. **Identical Scores**: All chunks from same video/channel have identical trust scores
  2. **Low Absolute Scores**: Scores appear low for high-quality educational content
  3. **Limited Granularity**: No chunk-level differentiation beyond redundancy status

---

## Proposed Improvements

### 1. Enhanced Trust Score Differentiation

#### Problem

Currently, all chunks from the same video have identical trust scores because the heuristic only considers:

- Video-level metadata (age, channel)
- Redundancy status
- Engagement (if available)
- Code presence

This means chunks with different content quality, completeness, or value cannot be distinguished.

#### Solution A: Content-Based Trust Signals

**Add chunk-level quality indicators**:

1. **Text Quality Metrics**:

   ```python
   def compute_text_quality_score(chunk: Dict) -> float:
       text = chunk.get("chunk_text", "")

       # Length factor (too short = lower quality)
       length_score = min(1.0, len(text) / 500)  # Normalize to 500 chars

       # Structure factor (paragraphs, sentences)
       paragraph_count = len([p for p in text.split("\n\n") if p.strip()])
       structure_score = min(1.0, paragraph_count / 3)  # Normalize to 3 paragraphs

       # Coherence factor (repetition detection)
       words = text.lower().split()
       unique_ratio = len(set(words)) / max(1, len(words))
       coherence_score = max(0.5, unique_ratio)  # Penalize excessive repetition

       return 0.4 * length_score + 0.3 * structure_score + 0.3 * coherence_score
   ```

2. **Enrichment Quality Score**:

   ```python
   def compute_enrichment_quality_score(chunk: Dict) -> float:
       score = 0.0

       # Summary quality (presence and length)
       summary = chunk.get("summary", "")
       if summary:
           summary_score = min(1.0, len(summary) / 200)  # Normalize to 200 chars
           score += 0.3 * summary_score

       # Entity extraction quality
       entities = chunk.get("entities", [])
       entity_score = min(1.0, len(entities) / 5)  # Normalize to 5 entities
       score += 0.25 * entity_score

       # Concept extraction quality
       concepts = chunk.get("concepts", [])
       concept_score = min(1.0, len(concepts) / 5)  # Normalize to 5 concepts
       score += 0.25 * concept_score

       # Relations quality
       relations = chunk.get("relations", [])
       relation_score = min(1.0, len(relations) / 3)  # Normalize to 3 relations
       score += 0.2 * relation_score

       return score
   ```

3. **Embedding Quality Score**:

   ```python
   def compute_embedding_quality_score(chunk: Dict) -> float:
       embedding = chunk.get("embedding", [])

       if not embedding:
           return 0.0

       # Vector norm (should be close to 1.0 for normalized vectors)
       norm = sum(x * x for x in embedding) ** 0.5
       norm_score = 1.0 - abs(1.0 - norm)  # Closer to 1.0 = better

       # Embedding dimension consistency
       expected_dim = chunk.get("embedding_dim", 1024)
       dim_score = 1.0 if len(embedding) == expected_dim else 0.5

       return 0.7 * norm_score + 0.3 * dim_score
   ```

**Integration**:

```python
def compute_trust_score_enhanced(chunk: Dict[str, Any]) -> float:
    # Original heuristic score
    base_score = compute_trust_score(chunk)

    # Content-based scores
    text_quality = compute_text_quality_score(chunk)
    enrichment_quality = compute_enrichment_quality_score(chunk)
    embedding_quality = compute_embedding_quality_score(chunk)

    # Weighted combination
    content_score = (
        0.5 * text_quality +
        0.3 * enrichment_quality +
        0.2 * embedding_quality
    )

    # Final score: 60% base (video/channel factors) + 40% content quality
    final_score = 0.6 * base_score + 0.4 * content_score

    return max(0.0, min(1.0, final_score))
```

#### Solution B: Relative Trust Scoring

**Normalize scores within video/channel context**:

```python
def compute_relative_trust_score(chunk: Dict, video_chunks: List[Dict]) -> float:
    # Compute base scores for all chunks
    base_scores = [compute_trust_score(c) for c in video_chunks]

    # Normalize to 0-1 range within video
    min_score = min(base_scores) if base_scores else 0.0
    max_score = max(base_scores) if base_scores else 1.0
    score_range = max(0.001, max_score - min_score)

    current_score = compute_trust_score(chunk)
    normalized = (current_score - min_score) / score_range

    # Blend absolute and relative (70% absolute, 30% relative)
    return 0.7 * current_score + 0.3 * normalized
```

#### Solution C: Position-Based Weighting

**Weight chunks by their position in the video**:

```python
def compute_position_weight(chunk: Dict) -> float:
    metadata = chunk.get("metadata", {})
    chunk_index = metadata.get("chunk_index", 0)
    chunk_count = metadata.get("chunk_count", 1)

    if chunk_count <= 1:
        return 1.0

    position = chunk_index / chunk_count

    # Intro chunks (first 10%) may have lower value
    # Middle chunks (10-90%) have highest value
    # Conclusion chunks (last 10%) have medium value
    if position < 0.1:
        return 0.8  # Intro
    elif position > 0.9:
        return 0.9  # Conclusion
    else:
        return 1.0  # Main content
```

---

### 2. Age Weighting Adjustment for Educational Content

#### Problem

Educational content (like MIT courses) retains value over time, but the current age penalty (`age_days: 1500` ≈ 4 years) heavily reduces trust scores.

#### Solution: Content-Type Aware Age Weighting

```python
def compute_recency_component_enhanced(chunk: Dict, age_days: float) -> float:
    # Detect educational content
    channel_name = chunk.get("channel_name", "").lower()
    video_title = chunk.get("video_title", "").lower()
    is_educational = any(keyword in channel_name or keyword in video_title
                        for keyword in ["course", "lecture", "education", "tutorial",
                                       "mit", "stanford", "harvard", "university"])

    # Educational content: slower decay (half-life of 5 years vs 6 months)
    if is_educational:
        recency_component = sigmoid(max(-6.0, min(6.0, (730.0 - age_days) / 365.0)))
    else:
        # Standard content: original decay
        recency_component = sigmoid(max(-6.0, min(6.0, (180.0 - age_days) / 60.0)))

    return recency_component
```

**Alternative: Channel Whitelist**:

```python
EDUCATIONAL_CHANNELS = {
    "mit opencourseware",
    "stanford",
    "harvard",
    "khan academy",
    # ... add more
}

def is_educational_channel(chunk: Dict) -> bool:
    channel = chunk.get("channel_name", "").lower()
    return channel in EDUCATIONAL_CHANNELS or any(
        edu in channel for edu in ["courseware", "lecture", "university"]
    )
```

---

### 3. LLM-Based Trust Scoring Enhancement

#### Problem

Currently, LLM trust scoring is only used for borderline cases (`auto_llm=True`, `band_low=0.40`, `band_high=0.70`). Many chunks fall outside this band and never get LLM evaluation.

#### Solution: Strategic LLM Trust Scoring

**Enable LLM scoring for high-value chunks**:

```python
def should_use_llm_trust_scoring(chunk: Dict, config: TrustConfig) -> bool:
    if not config.use_llm and not config.auto_llm:
        return False

    base_score = compute_trust_score(chunk)

    # Original auto-llm logic (borderline cases)
    if config.auto_llm and config.band_low <= base_score <= config.band_high:
        return True

    # NEW: High-value content indicators
    # High similarity chunks (potential duplicates)
    if chunk.get("redundancy_score", 0) >= 0.85:
        return True

    # Chunks with rich enrichment (entities, concepts, relations)
    enrichment_count = (
        len(chunk.get("entities", [])) +
        len(chunk.get("concepts", [])) +
        len(chunk.get("relations", []))
    )
    if enrichment_count >= 10:
        return True

    # Long, structured chunks (likely important content)
    text_length = len(chunk.get("chunk_text", ""))
    if text_length >= 2000:
        return True

    return False
```

---

### 4. Redundancy Stage Enhancements

#### Problem

Redundancy detection works well but could benefit from:

1. Better logging of similarity distributions
2. LLM verification for borderline cases
3. Handling of partial duplicates (substring matches)

#### Solution A: Similarity Distribution Logging

```python
def log_similarity_distribution(self, video_id: str, similarities: List[float]):
    """Log similarity score distribution for analysis."""
    if not similarities:
        return

    sorted_sims = sorted(similarities, reverse=True)
    stats = {
        "mean": sum(similarities) / len(similarities),
        "median": sorted_sims[len(sorted_sims) // 2],
        "p95": sorted_sims[int(len(sorted_sims) * 0.95)],
        "p99": sorted_sims[int(len(sorted_sims) * 0.99)],
        "max": max(similarities),
        "min": min(similarities),
        "above_threshold": len([s for s in similarities if s >= self.config.threshold]),
    }

    self.logger.info(
        f"[redundancy] Similarity distribution for {video_id}: "
        f"mean={stats['mean']:.3f}, median={stats['median']:.3f}, "
        f"above_threshold={stats['above_threshold']}"
    )
```

#### Solution B: Partial Duplicate Detection

**Detect substring/section-level duplicates**:

```python
def detect_partial_duplicates(chunk_a: Dict, chunk_b: Dict, threshold: float = 0.85) -> bool:
    """Detect if one chunk contains substantial content from another."""
    text_a = chunk_a.get("chunk_text", "")
    text_b = chunk_b.get("chunk_text", "")

    if not text_a or not text_b:
        return False

    # Check if significant portion of one chunk appears in another
    min_len = min(len(text_a), len(text_b))
    if min_len < 100:  # Skip very short chunks
        return False

    # Use sequence matching to find longest common substring
    # (simplified - would use more sophisticated algorithm in practice)
    words_a = set(text_a.lower().split())
    words_b = set(text_b.lower().split())

    if len(words_a) == 0 or len(words_b) == 0:
        return False

    overlap_ratio = len(words_a & words_b) / len(words_a | words_b)
    return overlap_ratio >= threshold
```

---

## Implementation Plan

### Phase 1: Content-Based Trust Signals (High Priority)

- **Estimated Effort**: 2-3 days
- **Files to Modify**:
  - `app/stages/trust.py`: Add content quality scoring functions
  - `config/stage_config.py`: Add trust scoring configuration options
- **Testing**: Validate score differentiation on diverse content

### Phase 2: Educational Content Weighting (Medium Priority)

- **Estimated Effort**: 1-2 days
- **Files to Modify**:
  - `app/stages/trust.py`: Update recency calculation
  - Add channel/content-type detection
- **Testing**: Compare scores for educational vs. entertainment content

### Phase 3: Enhanced LLM Trust Scoring (Medium Priority)

- **Estimated Effort**: 2-3 days
- **Files to Modify**:
  - `app/stages/trust.py`: Expand LLM scoring triggers
  - `agents/trust_agent.py`: Enhance trust scoring prompts
- **Testing**: Validate LLM scores for high-value chunks

### Phase 4: Redundancy Enhancements (Low Priority)

- **Estimated Effort**: 1-2 days
- **Files to Modify**:
  - `app/stages/redundancy.py`: Add similarity distribution logging
  - Consider partial duplicate detection (future enhancement)
- **Testing**: Analyze similarity distributions across videos

---

## Configuration Options

### New Environment Variables

```bash
# Trust scoring enhancements
TRUST_CONTENT_QUALITY_ENABLED=true
TRUST_CONTENT_QUALITY_WEIGHT=0.4  # Weight of content quality vs base score
TRUST_ENRICHMENT_QUALITY_ENABLED=true
TRUST_EMBEDDING_QUALITY_ENABLED=true

# Educational content weighting
TRUST_EDUCATIONAL_DECAY_HALFLIFE=1825  # 5 years in days
TRUST_STANDARD_DECAY_HALFLIFE=180      # 6 months in days
TRUST_EDUCATIONAL_CHANNELS="mit opencourseware,stanford,khan academy"

# LLM trust scoring
TRUST_LLM_ENABLE_HIGH_VALUE=true
TRUST_LLM_HIGH_VALUE_ENRICHMENT_THRESHOLD=10
TRUST_LLM_HIGH_VALUE_TEXT_LENGTH_THRESHOLD=2000

# Redundancy enhancements
REDUNDANCY_LOG_SIMILARITY_DISTRIBUTION=true
REDUNDANCY_PARTIAL_DUPLICATE_THRESHOLD=0.85
```

---

## Expected Outcomes

### Trust Score Improvements

- **Before**: All chunks from same video: `0.0607`
- **After**: Chunks differentiated by:
  - Content quality: `0.35 - 0.75`
  - Enrichment completeness: `+0.1 - 0.3` boost
  - Educational content: `+0.2 - 0.4` boost (age-adjusted)

### Redundancy Improvements

- Better visibility into similarity patterns
- More accurate duplicate detection for edge cases
- Enhanced logging for analysis and tuning

---

## Metrics to Track

1. **Trust Score Distribution**:

   - Mean, median, std dev across all chunks
   - Score range per video/channel
   - Correlation with content quality indicators

2. **Redundancy Accuracy**:

   - False positive rate (non-duplicates marked as redundant)
   - False negative rate (duplicates not detected)
   - Similarity score distribution histograms

3. **Performance Impact**:
   - Time overhead for enhanced scoring
   - LLM call frequency and cost
   - Memory usage for quality calculations

---

## Future Enhancements

1. **Machine Learning-Based Trust Scoring**:

   - Train model on manually labeled high-quality chunks
   - Use features: text quality, enrichment completeness, engagement, etc.

2. **Dynamic Threshold Adjustment**:

   - Adjust redundancy threshold based on content type
   - Educational content may need higher threshold (stricter duplicate detection)

3. **Cross-Video Duplicate Detection**:

   - Detect duplicates across different videos (e.g., reused intros/outros)
   - Requires efficient similarity search across large collections

4. **Trust Score Propagation**:
   - Propagate trust scores to GraphRAG entities
   - Weight entity importance by source chunk trust scores

---

## References

- Current Implementation: `app/stages/trust.py`, `app/stages/redundancy.py`
- Analysis Document: `documentation/REDUNDANCY-TRUST-ANALYSIS.md`
- Configuration: `config/stage_config.py`

---

**Last Updated**: 2025-10-30  
**Status**: Proposed improvements for future implementation
