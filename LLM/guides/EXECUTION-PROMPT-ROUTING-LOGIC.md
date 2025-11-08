# Execution Prompt Routing Logic Specification

**Purpose**: Technical specification for routing natural language prompts to document types and templates  
**Status**: ✅ Complete  
**Created**: 2025-11-09 20:15 UTC  
**Version**: 1.0  
**For**: PLAN 4 (Automation Implementation)

---

## 🎯 Overview

This document specifies the complete routing logic for execution prompts, enabling automation scripts to parse natural language prompts and route them to the correct document type and template.

**Key Components**:
1. **Routing Table**: Action keywords → Document Type → Template
2. **Parsing Algorithm**: 7-step process to extract prompt components
3. **Ambiguity Handling**: Rules for unclear or malformed prompts
4. **Extensibility Design**: How to add new patterns without breaking existing

---

## 📊 Complete Routing Table

### Core Routing (5 Patterns)

| Pattern | Action Keywords | Document Type | Template | Category (if ANALYSIS) |
|---------|----------------|---------------|----------|----------------------|
| **Analysis** | "make an analysis on", "analyze", "investigate", "study", "research" | EXECUTION_ANALYSIS | PLANNING-STRATEGY | Category 5 (Planning & Strategy) |
| **Case Study** | "make a case study on", "document as case study", "create case study", "study in depth" | EXECUTION_CASE-STUDY | CASE-STUDY | N/A |
| **Review** | "review the implementation of", "assess the implementation", "evaluate implementation", "check implementation", "audit implementation" | EXECUTION_ANALYSIS | IMPLEMENTATION-REVIEW | Category 3 (Implementation Review) |
| **Debug** | "debug", "investigate issue", "troubleshoot", "fix", "diagnose" | EXECUTION_ANALYSIS | BUG | Category 1 (Bug/Issue Analysis) |
| **Observation** | "watch", "observe", "monitor", "track", "capture observations", "follow" | EXECUTION_OBSERVATION | OBSERVATION | N/A |

---

### Extended Routing (All Variations)

#### Analysis Pattern Variations

| Action Keyword/Phrase | Routes To | Template | Priority |
|-----------------------|-----------|----------|----------|
| "make an analysis on" | EXECUTION_ANALYSIS | PLANNING-STRATEGY | 1 (highest) |
| "analyze" | EXECUTION_ANALYSIS | PLANNING-STRATEGY | 2 |
| "investigate" | EXECUTION_ANALYSIS | PLANNING-STRATEGY | 3 |
| "study" | EXECUTION_ANALYSIS | PLANNING-STRATEGY | 4 |
| "research" | EXECUTION_ANALYSIS | PLANNING-STRATEGY | 5 |

**Note**: If "investigate" appears with "issue" or "bug", route to Debug pattern instead (higher priority).

---

#### Case Study Pattern Variations

| Action Keyword/Phrase | Routes To | Template | Priority |
|-----------------------|-----------|----------|----------|
| "make a case study on" | EXECUTION_CASE-STUDY | CASE-STUDY | 1 (highest) |
| "document as case study" | EXECUTION_CASE-STUDY | CASE-STUDY | 2 |
| "create case study on" | EXECUTION_CASE-STUDY | CASE-STUDY | 3 |
| "study in depth" | EXECUTION_CASE-STUDY | CASE-STUDY | 4 |

---

#### Review Pattern Variations

| Action Keyword/Phrase | Routes To | Template | Priority |
|-----------------------|-----------|----------|----------|
| "review the implementation of" | EXECUTION_ANALYSIS | IMPLEMENTATION-REVIEW | 1 (highest) |
| "assess the implementation of" | EXECUTION_ANALYSIS | IMPLEMENTATION-REVIEW | 2 |
| "evaluate implementation" | EXECUTION_ANALYSIS | IMPLEMENTATION-REVIEW | 3 |
| "check implementation" | EXECUTION_ANALYSIS | IMPLEMENTATION-REVIEW | 4 |
| "audit implementation" | EXECUTION_ANALYSIS | IMPLEMENTATION-REVIEW | 5 |

---

#### Debug Pattern Variations

| Action Keyword/Phrase | Routes To | Template | Priority |
|-----------------------|-----------|----------|----------|
| "debug" | EXECUTION_ANALYSIS | BUG | 1 (highest) |
| "investigate" + ("issue"\|"bug"\|"error"\|"failure") | EXECUTION_ANALYSIS | BUG | 2 |
| "troubleshoot" | EXECUTION_ANALYSIS | BUG | 3 |
| "fix" | EXECUTION_ANALYSIS | BUG | 4 |
| "diagnose" | EXECUTION_ANALYSIS | BUG | 5 |

---

#### Observation Pattern Variations

| Action Keyword/Phrase | Routes To | Template | Priority |
|-----------------------|-----------|----------|----------|
| "watch" | EXECUTION_OBSERVATION | OBSERVATION | 1 (highest) |
| "observe" | EXECUTION_OBSERVATION | OBSERVATION | 2 |
| "monitor" | EXECUTION_OBSERVATION | OBSERVATION | 3 |
| "track" | EXECUTION_OBSERVATION | OBSERVATION | 4 |
| "capture observations" | EXECUTION_OBSERVATION | OBSERVATION | 5 |
| "follow" | EXECUTION_OBSERVATION | OBSERVATION | 6 |

---

## 🔄 Parsing Algorithm (7 Steps)

### Step 1: Extract Action Phrase

**Input**: Full prompt string (e.g., "Execution: make an analysis on database selection")

**Process**:
1. Remove "Execution:" prefix
2. Trim whitespace
3. Extract first verb phrase (up to first noun or "on"/"of")

**Output**: Action phrase (e.g., "make an analysis on")

**Error Handling**:
- If no "Execution:" prefix → Error: "Invalid prompt format"
- If no verb phrase found → Default to "analyze"

**Examples**:
- "Execution: make an analysis on X" → "make an analysis on"
- "Execution: debug the issue" → "debug"
- "Execution: watch X to get feedback" → "watch"

---

### Step 2: Extract Target

**Input**: Remaining prompt after action phrase

**Process**:
1. Extract noun phrase after action
2. Stop at "for", "using", or end of string
3. Trim whitespace

**Output**: Target string (e.g., "database selection")

**Error Handling**:
- If no target found → Error: "Missing target"
- If target is empty → Error: "Target cannot be empty"

**Examples**:
- "database selection for architecture decision" → "database selection"
- "entity resolution" → "entity resolution"
- "the GraphRAG pipeline execution" → "the GraphRAG pipeline execution"

---

### Step 3: Extract Optional Purpose

**Input**: Remaining prompt after target

**Process**:
1. Look for "for" keyword
2. Extract everything after "for" until "using" or end
3. Trim whitespace

**Output**: Purpose string or None

**Error Handling**:
- If no "for" found → Return None (not an error)
- If "for" found but nothing after → Return None

**Examples**:
- "for architecture decision" → "architecture decision"
- "for quality assurance using metrics" → "quality assurance"
- (no "for") → None

---

### Step 4: Extract Optional Method

**Input**: Remaining prompt after purpose

**Process**:
1. Look for "using" keyword
2. Extract everything after "using" until end
3. Trim whitespace

**Output**: Method string or None

**Error Handling**:
- If no "using" found → Return None (not an error)
- If "using" found but nothing after → Return None

**Examples**:
- "using profiling data" → "profiling data"
- "using reproduction steps" → "reproduction steps"
- (no "using") → None

---

### Step 5: Match Action to Pattern

**Input**: Action phrase from Step 1

**Process**:
1. Normalize action phrase (lowercase, remove extra spaces)
2. Check against routing table (in priority order)
3. First match wins
4. Apply special rules (e.g., "investigate" + "issue" → Debug)

**Output**: Pattern name (Analysis, Case Study, Review, Debug, Observation)

**Error Handling**:
- If no match → Default to "Analysis" pattern
- Log warning for unmatched action

**Examples**:
- "make an analysis on" → Analysis
- "debug" → Debug
- "watch" → Observation
- "investigate issue" → Debug (special rule)
- "unknown action" → Analysis (default)

---

### Step 6: Route to Document Type

**Input**: Pattern name from Step 5

**Process**:
1. Look up pattern in routing table
2. Get document type
3. Get category (if EXECUTION_ANALYSIS)

**Output**: Document type and category

**Error Handling**:
- Pattern not in table → Error: "Invalid pattern" (should not happen if Step 5 works)

**Examples**:
- Analysis → EXECUTION_ANALYSIS (Category 5: Planning & Strategy)
- Case Study → EXECUTION_CASE-STUDY
- Review → EXECUTION_ANALYSIS (Category 3: Implementation Review)
- Debug → EXECUTION_ANALYSIS (Category 1: Bug Analysis)
- Observation → EXECUTION_OBSERVATION

---

### Step 7: Select Template

**Input**: Document type and category from Step 6

**Process**:
1. Look up template in routing table
2. Construct full template path

**Output**: Template file path

**Error Handling**:
- Template not found → Error: "Template missing"

**Examples**:
- EXECUTION_ANALYSIS (Planning & Strategy) → `LLM/templates/EXECUTION_ANALYSIS-PLANNING-STRATEGY-TEMPLATE.md`
- EXECUTION_CASE-STUDY → `LLM/templates/EXECUTION_CASE-STUDY-TEMPLATE.md`
- EXECUTION_ANALYSIS (Implementation Review) → `LLM/templates/EXECUTION_ANALYSIS-IMPLEMENTATION-REVIEW-TEMPLATE.md`
- EXECUTION_ANALYSIS (Bug Analysis) → `LLM/templates/EXECUTION_ANALYSIS-BUG-TEMPLATE.md`
- EXECUTION_OBSERVATION → `LLM/templates/EXECUTION_OBSERVATION-TEMPLATE.md`

---

## 📋 Complete Parsing Example

**Input Prompt**:
```
Execution: make an analysis on database selection for architecture decision using comparison matrix
```

**Step-by-Step**:

1. **Extract Action**: "make an analysis on"
2. **Extract Target**: "database selection"
3. **Extract Purpose**: "architecture decision"
4. **Extract Method**: "comparison matrix"
5. **Match Action**: Analysis pattern
6. **Route to Type**: EXECUTION_ANALYSIS (Category 5: Planning & Strategy)
7. **Select Template**: `LLM/templates/EXECUTION_ANALYSIS-PLANNING-STRATEGY-TEMPLATE.md`

**Output**:
```json
{
  "pattern": "Analysis",
  "action": "make an analysis on",
  "target": "database selection",
  "purpose": "architecture decision",
  "method": "comparison matrix",
  "document_type": "EXECUTION_ANALYSIS",
  "category": "Planning & Strategy",
  "template": "LLM/templates/EXECUTION_ANALYSIS-PLANNING-STRATEGY-TEMPLATE.md",
  "location": "work-space/analyses/EXECUTION_ANALYSIS_DATABASE-SELECTION.md"
}
```

---

## ⚠️ Ambiguity Handling

### Scenario 1: No Action Match

**Trigger**: Action phrase doesn't match any known pattern

**Example**: "Execution: explore the codebase"

**Detection**: Step 5 returns no match

**Behavior**:
1. Default to Analysis pattern
2. Log warning: "Unknown action 'explore', defaulting to Analysis"
3. Continue with Analysis routing

**User Feedback** (optional):
```
⚠️  Unknown action 'explore'. Defaulting to EXECUTION_ANALYSIS.
Did you mean:
  • "make an analysis on the codebase"
  • "investigate the codebase"
```

---

### Scenario 2: Multiple Potential Matches

**Trigger**: Action phrase could match multiple patterns

**Example**: "Execution: investigate the performance issue"

**Detection**: "investigate" matches both Analysis and Debug patterns

**Behavior**:
1. Apply priority rules (Debug > Analysis if "issue" present)
2. Route to Debug pattern
3. Log decision: "Matched Debug pattern (priority over Analysis due to 'issue')"

**User Feedback** (optional):
```
✓ Routing to EXECUTION_ANALYSIS (Bug Analysis) due to 'issue' keyword.
```

---

### Scenario 3: Missing Target

**Trigger**: No target extracted in Step 2

**Example**: "Execution: make an analysis"

**Detection**: Step 2 returns empty target

**Behavior**:
1. Error: "Missing target"
2. Prompt user for target
3. Do not proceed until target provided

**User Feedback**:
```
❌ Error: Missing target.
Please specify what you want to analyze.
Example: "Execution: make an analysis on database selection"
```

---

### Scenario 4: Malformed Prompt

**Trigger**: Prompt doesn't start with "Execution:"

**Example**: "make an analysis on database selection"

**Detection**: Step 1 fails to find "Execution:" prefix

**Behavior**:
1. Error: "Invalid prompt format"
2. Suggest correct format
3. Do not proceed

**User Feedback**:
```
❌ Error: Invalid prompt format.
Prompts must start with "Execution:"
Example: "Execution: make an analysis on database selection"
```

---

### Scenario 5: Ambiguous Action

**Trigger**: Action phrase is unclear or too generic

**Example**: "Execution: look at entity resolution"

**Detection**: "look at" not in routing table

**Behavior**:
1. Default to Analysis pattern
2. Suggest alternatives
3. Ask for confirmation (optional)

**User Feedback**:
```
⚠️  Unclear action 'look at'. Defaulting to EXECUTION_ANALYSIS.
Did you mean:
  • "make an analysis on entity resolution"
  • "review the implementation of entity resolution"
  • "debug entity resolution"
  • "watch entity resolution to get feedback"
```

---

## 🔧 Extensibility Design

### Adding a New Pattern

**Steps**:

1. **Define Pattern**
   - Name: e.g., "Experiment"
   - Purpose: e.g., "Test hypothesis with A/B comparison"
   - Syntax: e.g., "Execution: experiment with <TARGET> [for <PURPOSE>]"

2. **Update Routing Table**
   - Add action keywords: "experiment with", "test", "compare"
   - Specify document type: e.g., EXECUTION_EXPERIMENT
   - Specify template: e.g., EXPERIMENT-TEMPLATE.md
   - Assign priority: e.g., Priority 1 for "experiment with"

3. **Update Parsing Logic**
   - Add keywords to Step 5 matching
   - Add special rules if needed (e.g., "test" + "hypothesis" → Experiment)
   - Update priority handling

4. **Create Template**
   - Create `LLM/templates/EXECUTION_EXPERIMENT-TEMPLATE.md`
   - Follow template structure conventions

5. **Update Documentation**
   - Add to `EXECUTION-PROMPT-PATTERNS.md`
   - Add examples
   - Update quick reference table

6. **Test**
   - Test all new action keywords
   - Test priority rules
   - Test backward compatibility (existing patterns still work)

---

### Backward Compatibility

**Guarantee**: Adding new patterns MUST NOT break existing patterns

**Rules**:
1. New keywords must not overlap with existing keywords
2. If overlap is unavoidable, use priority rules
3. Existing patterns maintain their priority
4. Default behavior (Analysis) remains unchanged

**Example**:
- Adding "Experiment" pattern with "test" keyword
- "test" might conflict with Debug pattern
- Solution: "test" + "hypothesis" → Experiment, "test" alone → Debug

---

### Extension Example

**New Pattern**: Experiment

**Routing Table Entry**:
```
Action Keyword(s)           → Document Type        → Template
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"experiment with"           → EXECUTION_EXPERIMENT → EXPERIMENT
"test hypothesis"           → EXECUTION_EXPERIMENT → EXPERIMENT
"compare approaches"        → EXECUTION_EXPERIMENT → EXPERIMENT
```

**Parsing Logic Update**:
```python
# Step 5: Match Action to Pattern
if "experiment with" in action:
    return "Experiment"
elif "test" in action and "hypothesis" in prompt:
    return "Experiment"
elif "compare" in action and "approaches" in prompt:
    return "Experiment"
# ... existing patterns ...
```

**Template Creation**:
- Create `LLM/templates/EXECUTION_EXPERIMENT-TEMPLATE.md`
- Include sections: Hypothesis, Approach A, Approach B, Comparison, Conclusion

---

## 📐 Data Structures (for Implementation)

### PromptComponents

```python
@dataclass
class PromptComponents:
    """Parsed components of an execution prompt"""
    action: str              # Action phrase (e.g., "make an analysis on")
    target: str              # Target (e.g., "database selection")
    purpose: Optional[str]   # Purpose (e.g., "architecture decision")
    method: Optional[str]    # Method (e.g., "comparison matrix")
```

### RoutingResult

```python
@dataclass
class RoutingResult:
    """Result of routing a prompt"""
    pattern: str             # Pattern name (e.g., "Analysis")
    document_type: str       # Document type (e.g., "EXECUTION_ANALYSIS")
    category: Optional[str]  # Category if ANALYSIS (e.g., "Planning & Strategy")
    template: str            # Template path
    location: str            # Where to create file
    components: PromptComponents  # Parsed components
```

### RoutingError

```python
@dataclass
class RoutingError:
    """Error during routing"""
    error_type: str          # Error type (e.g., "MissingTarget")
    message: str             # Error message
    suggestions: List[str]   # Suggested corrections
```

---

## 🧪 Testing Strategy (for PLAN 4)

### Unit Tests

**Test Parsing Steps**:
- Test Step 1: Extract action phrase (10+ test cases)
- Test Step 2: Extract target (10+ test cases)
- Test Step 3: Extract purpose (5+ test cases)
- Test Step 4: Extract method (5+ test cases)
- Test Step 5: Match action (20+ test cases, all patterns)
- Test Step 6: Route to type (10+ test cases)
- Test Step 7: Select template (10+ test cases)

**Test Ambiguity Handling**:
- Test no match scenario (5+ cases)
- Test multiple matches (5+ cases)
- Test missing target (3+ cases)
- Test malformed prompt (5+ cases)
- Test ambiguous action (5+ cases)

---

### Integration Tests

**End-to-End Routing**:
- Test 50+ prompts covering all patterns
- Test all pattern variations
- Test extended patterns ("for", "using")
- Test edge cases
- Test error scenarios

**Expected Results**:
- 100% of clear prompts route correctly
- 100% of ambiguous prompts provide helpful feedback
- 100% of malformed prompts error gracefully
- 0% false positives (wrong routing)

---

## 📊 Priority Rules Summary

**When Multiple Patterns Match**:

1. **Exact phrase match** > Synonym match
2. **Longer phrase** > Shorter phrase
3. **Special rules** > General rules
4. **Pattern-specific keywords** > Generic keywords

**Examples**:
- "investigate issue" → Debug (special rule) > Analysis (general)
- "make an analysis on" → Analysis (exact) > "analyze" (synonym)
- "review the implementation of" → Review (exact) > "review" alone (ambiguous)

---

## 🎯 Implementation Checklist (for PLAN 4)

- [ ] Implement 7-step parsing algorithm
- [ ] Implement routing table lookup
- [ ] Implement priority rules
- [ ] Implement ambiguity handling
- [ ] Implement error handling
- [ ] Create PromptComponents dataclass
- [ ] Create RoutingResult dataclass
- [ ] Create RoutingError dataclass
- [ ] Write unit tests (70+ tests)
- [ ] Write integration tests (50+ prompts)
- [ ] Test all pattern variations
- [ ] Test edge cases
- [ ] Test error scenarios
- [ ] Document implementation
- [ ] Create usage examples

---

## 📚 Related Documentation

- `LLM/guides/EXECUTION-PROMPT-PATTERNS.md` - Prompt patterns (Achievement 0.1)
- `LLM/guides/EXECUTION-TAXONOMY.md` - Document types and templates
- `LLM/templates/EXECUTION_*-TEMPLATE.md` - Target templates
- PLAN 4 documentation (when created) - Automation implementation

---

## 📋 Summary

**Routing Logic Components**:
1. ✅ Complete routing table (5 patterns + all variations)
2. ✅ 7-step parsing algorithm (fully specified)
3. ✅ Ambiguity handling (5 scenarios covered)
4. ✅ Extensibility design (how to add new patterns)
5. ✅ Implementation guidance (data structures, testing, checklist)

**Key Features**:
- **Deterministic**: Same prompt → same routing
- **Complete**: All pattern variations covered
- **Robust**: Graceful error handling
- **Extensible**: Easy to add new patterns
- **Implementation-Ready**: PLAN 4 can implement directly

**Next Steps**:
- Achievement 0.3: Create comprehensive prompt-to-type mapping table
- PLAN 4: Implement routing logic in automation scripts

---

**Version**: 1.0  
**Status**: ✅ Complete  
**Last Updated**: 2025-11-09  
**Ready For**: PLAN 4 (Automation Implementation)




