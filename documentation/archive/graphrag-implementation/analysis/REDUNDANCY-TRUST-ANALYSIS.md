# Redundancy & Trust Stage Analysis

## Overview

Analysis of redundancy and trust stages based on actual MongoDB document data from the `video_chunks` collection.

---

## Sample Data Analysis

### Document Samples (from `ZA-tUyM_y7s` video)

#### Chunk 1: `629529fb-34ce-4744-9e8e-853b5636bcd9`

- **Content**: Introduction to the algorithms course by Jason Ku
- **Redundancy**:
  - `is_redundant`: `false`
  - `redundancy_score`: `0.897` (cosine similarity)
  - `redundancy_method`: `"cosine"`
  - `duplicate_of`: `null`
- **Trust**:
  - `trust_score`: `0.0607`
  - `trust_method`: `"heuristic"`

#### Chunk 2: `d3913463-be87-4cf6-8cf2-b71e75792158`

- **Content**: Discussion about proving correctness and communication
- **Redundancy**:
  - `is_redundant`: `false`
  - `redundancy_score`: `0.897` (cosine similarity)
  - `redundancy_method`: `"cosine"`
  - `duplicate_of`: `null`
- **Trust**:
  - `trust_score`: `0.0607`
  - `trust_method`: `"heuristic"`

#### Chunk 3: `32ba2690-6c9b-4614-91a5-c41b25b1cd84` (PRIMARY)

- **Content**: Binary relation and bipartite graph explanation
- **Redundancy**:
  - `is_redundant`: `false` ✅ (marked as primary)
  - `redundancy_score`: `0.926` (cosine similarity)
  - `redundancy_method`: `"cosine"`
  - `duplicate_of`: `null`
- **Trust**:
  - `trust_score`: `0.0607`
  - `trust_method`: `"heuristic"`

#### Chunk 4: `f1423039-2263-47a8-b720-128791af656a` (DUPLICATE)

- **Content**: Similar content about bipartite graphs and predicates
- **Redundancy**:
  - `is_redundant`: `true` ✅ (correctly identified as duplicate)
  - `redundancy_score`: `0.926` (cosine similarity - matches chunk 3)
  - `redundancy_method`: `"cosine"`
  - `duplicate_of`: `"32ba2690-6c9b-4614-91a5-c41b25b1cd84"` ✅ (correctly references primary)
  - `redundancy_reason`: `"high_sim"`
- **Trust**:
  - `trust_score`: `0.0607`
  - `trust_method`: `"heuristic"`

#### Chunk 5: `86e9fad9-3fb1-40eb-a22a-61f7e43f5fff`

- **Content**: Birthday problem and pigeonhole principle
- **Redundancy**:
  - `is_redundant`: `false`
  - `redundancy_score`: `0.903` (cosine similarity)
  - `redundancy_method`: `"cosine"`
  - `duplicate_of`: `null`
- **Trust**:
  - `trust_score`: `0.0607`
  - `trust_method`: `"heuristic"`

---

## Findings

### ✅ Redundancy Stage - Working Correctly

1. **Threshold Detection**:

   - Default threshold: `0.92` (from `REDUNDANCY_THRESHOLD` environment variable or config)
   - Chunk 3 + 4: Score `0.926` → **Above threshold** → Correctly marked as duplicate
   - Chunks 1, 2, 5: Scores `0.897`, `0.897`, `0.903` → **Below threshold** → Correctly marked as non-redundant

2. **Primary Selection**:

   - Chunk 3 (`32ba2690-...`) is lexicographically smaller than Chunk 4 (`f1423039-...`)
   - ✅ **Correct behavior**: Chunk 3 marked as primary (`is_redundant=false`), Chunk 4 references it

3. **Duplicate Linking**:

   - ✅ Chunk 4 correctly references Chunk 3 via `duplicate_of` field
   - ✅ `redundancy_reason` set to `"high_sim"` for high similarity cases

4. **Method Assignment**:
   - All chunks using `"cosine"` method (embedding-based similarity)
   - No LLM calls observed (likely `use_llm=false` or no borderline cases)

### ⚠️ Trust Stage - Potential Issues

1. **Identical Trust Scores**:

   - **All 5 chunks have identical trust scores**: `0.0607`
   - This is suspicious - different content should produce different trust scores
   - **Possible causes**:
     - All chunks from the same video/channel may have similar metadata
     - Heuristic scoring function may be too simplistic
     - Age, channel, or other factors are identical across chunks

2. **Low Trust Scores**:

   - Score of `0.0607` is quite low (scale appears to be 0.0-1.0)
   - All chunks marked with `trust_method: "heuristic"` (no LLM scoring used)
   - **Possible reasons**:
     - Video age: `age_days: 1500` (~4 years old) may lower score
     - Channel factor may be neutral
     - No code present (`code_present: false`)
     - Heuristic may weight certain factors heavily

3. **Heuristic Calculation**:
   Based on `compute_trust_score()` function, the score depends on:

   - Video age (older = lower score)
   - Channel quality/trustworthiness
   - Presence of code
   - Other metadata factors

   Since all chunks share the same video, channel, and metadata, identical scores make sense.

---

## Technical Details

### Redundancy Threshold

```python
# From redundancy.py config
threshold = _getf(["REDUNDANCY_THRESHOLD", "DEDUP_THRESHOLD"], 0.92)
```

- **Default**: `0.92` (92% cosine similarity)
- **Above threshold** (`≥ 0.92`): Marked as redundant
- **Below threshold** (`< 0.92`): Marked as non-redundant

### Primary Selection Logic

```python
# Lexicographic ordering ensures consistent primary selection
primary_chunk_id = min(chunk_id_a, chunk_id_b)
```

- Ensures deterministic primary chunk selection
- Primary chunk always has `is_redundant=false`
- Duplicate chunks reference primary via `duplicate_of`

### Trust Score Calculation

The heuristic trust score considers:

1. **Video age**: Older videos may have lower scores
2. **Channel metadata**: Channel reputation/quality
3. **Code presence**: Technical content may have different weights
4. **Other factors**: Additional metadata signals

**Current behavior**: All chunks from same video/channel → Same trust score

---

## Recommendations

### 1. Redundancy Stage - ✅ No Changes Needed

The redundancy detection is working correctly:

- Threshold properly separates duplicates from unique content
- Primary selection is deterministic and correct
- Duplicate linking is accurate

**Optional Enhancements**:

- Consider logging similarity scores for chunks just below threshold (0.85-0.92) for manual review
- Add LLM-based verification for borderline cases if needed

### 2. Trust Stage - Consider Improvements

#### Issue: Low Differentiation

**Problem**: All chunks have identical trust scores, making it difficult to distinguish high-quality from low-quality content.

**Potential Solutions**:

1. **Content-Based Trust Signals**:

   - Factor in chunk text quality (length, structure, coherence)
   - Consider embedding quality (vector norm, similarity to neighbors)
   - Use enrichment data (summary quality, entity extraction quality)

2. **Relative Trust Scoring**:

   - Normalize trust scores within a video/channel
   - Weight chunks by their position in video (intros/conclusions may be different)
   - Consider chunk-level metadata (cross-links, relations, concepts)

3. **Enable LLM Trust Scoring**:

   - For chunks with high similarity or unusual patterns, use LLM-based trust scoring
   - Currently all chunks use heuristic only (`trust_method: "heuristic"`)

4. **Trust Score Granularity**:
   - Current heuristic may be too coarse
   - Consider adding more factors: chunk length, timestamp position, enrichment completeness

#### Issue: Low Absolute Scores

**Problem**: All scores are `0.0607`, which seems low for educational MIT content.

**Investigation Needed**:

1. Check if `age_days: 1500` is heavily penalizing scores
2. Verify channel trust factor for MIT OpenCourseWare
3. Review if code absence is penalizing too much

**Potential Fix**:

- Adjust age weighting (educational content may retain value longer)
- Add channel whitelist/trust boost for known educational channels
- Consider content type in scoring (educational vs. entertainment)

---

## Data Quality Metrics

### Redundancy Metrics (from sample)

- **Duplicate Detection Rate**: 1 duplicate out of 5 chunks (20%)
- **False Positive Rate**: 0% (no false duplicates detected)
- **False Negative Rate**: Unknown (would need manual review)
- **Threshold Effectiveness**: ✅ Correctly separating 0.897/0.903 (non-duplicates) from 0.926 (duplicate)

### Trust Metrics (from sample)

- **Trust Score Range**: `0.0607` (very narrow, all identical)
- **Trust Method Distribution**: 100% heuristic (0% LLM)
- **Score Variation**: None (all chunks identical)

---

## Conclusion

✅ **Redundancy Stage**: Working as designed

- Correctly identifies duplicates using cosine similarity threshold
- Properly links duplicates to primary chunks
- Deterministic primary selection via lexicographic ordering

⚠️ **Trust Stage**: Functional but needs enhancement

- Correctly computes trust scores, but lacks differentiation
- All chunks from same video have identical scores (expected given current heuristic)
- Low absolute scores may indicate overly conservative scoring or missing quality signals
- Consider adding content-based or chunk-specific factors to improve granularity

---

## Next Steps

1. ✅ **Redundancy**: Monitor and validate threshold effectiveness over larger dataset
2. ⚠️ **Trust**: Investigate trust score calculation to add chunk-level differentiation
3. ⚠️ **Trust**: Review age/channel weighting factors for educational content
4. 🔄 **Future**: Consider LLM-based trust scoring for borderline or high-value chunks
