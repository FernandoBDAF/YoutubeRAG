0) North-star for extraction (what “good” looks like)

Only extract entities explicitly present in the chunk.

Only keep relations with typed predicates from a whitelist.

Every relation has evidence spans (start/end or sentence ids).

Normalize names and types (PERSON, ORG, CONCEPT, COURSE, LOCATION, EVENT, METHOD, THEOREM, DATASTRUCTURE, METRIC, OTHER).

Confidence-weighted output with min thresholds (entity ≥0.5, relation ≥0.6 by default).

Deterministic: fixed temperature, fixed system prompt, few-shot examples.

TASK 1 — Tighten the system prompt + add few-shot examples

Modify extraction agent prompt to be strict, typed, and evidence-backed

Files:

business/agents/graphrag/extraction.py

Goals:

Replace self.system_prompt with a strict, minimal prompt that enforces: (a) in-chunk only, (b) predicate whitelist, (c) evidence spans, (d) confidence rules, (e) canonical types, (f) no reverse/bidirectional auto-expansion.

Add 2 few-shot examples (one the MIT chunk below; one negative example with “don’t infer unseen entities”).

Exact changes:

Overwrite self.system_prompt with:

You extract entities and typed relations **only** from the provided transcript chunk.
DO NOT invent entities or relations not explicitly present. DO NOT generalize across chunks.

## Types (strict)
PERSON | ORGANIZATION | TECHNOLOGY | CONCEPT | COURSE | LOCATION | EVENT | METHOD | THEOREM | DATASTRUCTURE | METRIC | OTHER

## Predicate whitelist (one of):
teaches, member_of, works_at, focuses_on, includes, emphasizes, is_a, subtype_of, part_of, located_in, related_to, uses, requires, depends_on, explained_by, authored_by

## Evidence (required)
For every relation, return `evidence`: { sentence_index_start, sentence_index_end } or { char_start, char_end } from the given chunk.

## Confidence
- Entities: omit entities with confidence < 0.50
- Relations: omit relations with confidence < 0.60

## Rules
- No bidirectional expansion. Emit only the **forward** predicate you saw.
- Normalize course names and proper nouns (e.g., “Introduction to Algorithms”).
- Prefer `COURSE` over `CONCEPT` when it’s clearly a course title.
- If unsure between types, choose the more general (`CONCEPT`) and lower confidence.

Return JSON that matches the `KnowledgeModel` schema exactly.


Add two few-shot messages to messages (before the user content):

Positive example built from the MIT chunk to show COURSE, teaches, focuses_on, includes, with evidence spans.

Negative example where a chunk mentions “algorithms” but does not mention a person—model must not invent instructors.

Acceptance criteria:

Running extraction on your provided MIT chunk yields:

Entities: Jason Ku (PERSON), Eric Demaine (PERSON), Justin Solomon (PERSON), Introduction to Algorithms (COURSE), Computational Problems (CONCEPT), Communication (CONCEPT)

Relations only from the whitelist, each with evidence spans; no reverse duplicates; confidences ≥ thresholds.

Temperature stays at 0.0–0.1.

