# SUBPLAN: Design Prompt Routing Logic

**Type**: SUBPLAN  
**Mother Plan**: PLAN_EXECUTION-PROMPT-SYSTEM.md  
**Plan**: EXECUTION-PROMPT-SYSTEM  
**Achievement Addressed**: Achievement 0.2 (Design Prompt Routing Logic)  
**Achievement**: 0.2  
**Status**: Complete  
**Created**: 2025-11-09 20:15 UTC  
**Completed**: 2025-11-09 21:15 UTC  
**Estimated Effort**: 2-3 hours  
**Actual Effort**: ~1 hour

---

## 🎯 Objective

Design comprehensive routing logic that maps natural language prompts to document types and templates, including action keyword mapping, parsing algorithms, ambiguity handling, and extensibility design. This specification will enable PLAN 4 (automation) to implement prompt parsing and routing.

**Contribution to Mother PLAN**: Provides the technical specification for how prompt patterns (Achievement 0.1) are parsed and routed, forming the foundation for automation implementation and comprehensive guide creation.

---

## 📋 What Needs to Be Created

### Primary Deliverable

**File**: `LLM/guides/EXECUTION-PROMPT-ROUTING-LOGIC.md` (400-500 lines)

**Content**:
- Complete routing table (action keywords → document type → template)
- Parsing algorithm specification (7-step process)
- Action keyword mapping (all variations mapped to patterns)
- Ambiguity handling rules (defaults, suggestions, confirmation)
- Extensibility design (how to add new patterns)
- Implementation guidance for PLAN 4
- Edge case handling
- Error scenarios and recovery

### Routing Table Specifications

**Core Routing Table**:
```
Action Keyword(s)           → Document Type        → Template
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"make an analysis on"       → EXECUTION_ANALYSIS   → PLANNING-STRATEGY (default)
"make a case study on"      → EXECUTION_CASE-STUDY → CASE-STUDY
"review the implementation" → EXECUTION_ANALYSIS   → IMPLEMENTATION-REVIEW
"debug"                     → EXECUTION_ANALYSIS   → BUG
"watch", "observe"          → EXECUTION_OBSERVATION → OBSERVATION
```

**Extended Routing Table** (with variations):
- All pattern variations from Achievement 0.1
- Synonym mapping
- Alternative phrasings
- Complete keyword coverage

### Parsing Algorithm

**7-Step Process**:
1. Extract action phrase (first verb phrase after "Execution:")
2. Extract target (noun phrase after action)
3. Extract optional purpose (after "for")
4. Extract optional method (after "using")
5. Match action to pattern
6. Route to document type
7. Select template based on document type

**Detailed Specification**:
- Input format
- Output format
- Intermediate data structures
- Error handling at each step

### Ambiguity Handling

**Rules**:
- Default to EXECUTION_ANALYSIS if unclear
- Provide suggestions if multiple matches
- User confirmation for ambiguous prompts
- Fallback strategies

**Scenarios**:
- No match found
- Multiple matches
- Partial match
- Malformed prompt

### Extensibility Design

**How to Add New Patterns**:
- Update routing table
- Add action keywords
- Specify document type
- Specify template
- Add examples
- Update parsing logic (if needed)

---

## 📝 Approach

**Strategy**: Design routing logic that is deterministic, extensible, and implementable by automation scripts while handling edge cases gracefully.

**Method**:

1. **Routing Table Design Phase**
   - Create core routing table (5 patterns)
   - Extend with all variations from Achievement 0.1
   - Map synonyms to patterns
   - Document keyword priorities

2. **Parsing Algorithm Design Phase**
   - Specify 7-step parsing process
   - Define input/output formats
   - Design intermediate data structures
   - Document error handling at each step

3. **Ambiguity Handling Design Phase**
   - Define ambiguity scenarios
   - Specify default behaviors
   - Design suggestion system
   - Document confirmation flows

4. **Extensibility Design Phase**
   - Document how to add new patterns
   - Specify update procedures
   - Design backward compatibility
   - Create extension examples

5. **Implementation Guidance Phase**
   - Write guidance for PLAN 4 automation
   - Specify data structures
   - Document algorithms
   - Provide pseudocode examples

**Key Considerations**:

- **Determinism**: Same prompt → same routing (predictable)
- **Completeness**: All pattern variations covered
- **Clarity**: Unambiguous specifications for implementation
- **Robustness**: Graceful handling of edge cases
- **Extensibility**: Easy to add new patterns without breaking existing
- **Implementation-Ready**: PLAN 4 can implement directly from spec
- **User-Friendly**: Ambiguity handling provides helpful feedback

---

## 🔄 Execution Strategy

**Execution Count**: Single

**Rationale**:
- Routing logic is cohesive specification work
- All components (routing, parsing, ambiguity, extensibility) are interdependent
- Single execution ensures consistency across all specifications
- Estimated 2-3 hours fits within single execution scope
- No benefit to splitting into multiple executions

**EXECUTION_TASK**: `EXECUTION_TASK_EXECUTION-PROMPT-SYSTEM_02_01.md`

---

## 🧪 Tests

**Type**: Design Validation (Specification Review)

**Validation Approach**:

1. **Completeness Check**
   - [ ] Routing table covers all 5 patterns + variations
   - [ ] Parsing algorithm has all 7 steps specified
   - [ ] Ambiguity handling covers all scenarios
   - [ ] Extensibility design is complete
   - [ ] Implementation guidance is clear

2. **Determinism Validation**
   - [ ] Each action keyword maps to exactly one pattern
   - [ ] No overlapping keywords
   - [ ] Priority rules clear for conflicts
   - [ ] Same input → same output

3. **Implementability Check**
   - [ ] Specifications are clear enough for PLAN 4
   - [ ] Algorithms are well-defined
   - [ ] Data structures are specified
   - [ ] Edge cases are documented

4. **Usability Test** (Manual)
   - Select 10 prompts (5 clear, 5 ambiguous)
   - Apply routing logic manually
   - Verify correct routing for clear prompts
   - Verify helpful feedback for ambiguous prompts

**Expected Results**:
- Complete routing logic specification
- Clear parsing algorithm
- Robust ambiguity handling
- Extensible design
- Implementation-ready for PLAN 4

---

## 📚 Dependencies

**Upstream (Must Complete First)**:
- ✅ Achievement 0.1: Design 5 Core Prompt Patterns (provides patterns to route)

**Downstream (Depends on This)**:
- Achievement 0.3: Document Prompt-to-Type Mapping (uses routing logic)
- Achievement 1.1: Create Comprehensive Guide (incorporates routing logic)
- PLAN 4: Automation scripts (implements routing logic)

**Related Work**:
- `LLM/guides/EXECUTION-PROMPT-PATTERNS.md` - Patterns to route
- `LLM/guides/EXECUTION-TAXONOMY.md` - Document types and templates
- `LLM/templates/EXECUTION_*-TEMPLATE.md` - Target templates

---

## 📊 Success Criteria

**Must Have**:
- [ ] Complete routing table (all patterns + variations)
- [ ] 7-step parsing algorithm specified
- [ ] Action keyword mapping complete
- [ ] Ambiguity handling rules documented
- [ ] Extensibility design complete
- [ ] Implementation guidance for PLAN 4

**Should Have**:
- [ ] Edge case handling documented
- [ ] Error scenarios covered
- [ ] Pseudocode examples provided
- [ ] Data structure specifications

**Nice to Have**:
- [ ] Performance considerations
- [ ] Optimization opportunities
- [ ] Testing strategy for PLAN 4

---

## 🔄 Iteration Strategy

**Expected Iterations**: 1

**Iteration 1** (Design & Specification):
- Create routing table with all variations
- Specify 7-step parsing algorithm
- Document ambiguity handling rules
- Design extensibility approach
- Write implementation guidance

**Completion Criteria**:
- All success criteria met
- Specifications are clear and implementable
- Ready for Achievement 0.3 (mapping table)
- Ready for PLAN 4 (automation implementation)

---

## 📝 Design Principles

**Principle 1: Deterministic Routing**
- Same prompt always routes to same destination
- No ambiguity in action keyword matching
- Clear priority rules for conflicts

**Principle 2: Complete Coverage**
- All pattern variations mapped
- All synonyms handled
- All edge cases documented

**Principle 3: Graceful Degradation**
- Ambiguous prompts get helpful suggestions
- Malformed prompts get clear error messages
- Unknown patterns default to EXECUTION_ANALYSIS

**Principle 4: Implementation-Ready**
- Specifications clear enough to implement directly
- Algorithms well-defined
- Data structures specified
- No ambiguity in requirements

**Principle 5: Extensible Design**
- Easy to add new patterns
- Backward compatible
- No breaking changes to existing routing
- Clear extension procedures

---

## 🎯 Routing Logic Specifications

### Action Keyword Mapping Structure

For each pattern, document:

1. **Primary Keywords**: Main action phrases
2. **Variations**: Alternative phrasings
3. **Synonyms**: Words with same meaning
4. **Priority**: If multiple matches, which takes precedence
5. **Document Type**: What type to create
6. **Template**: Which template to use
7. **Category** (if EXECUTION_ANALYSIS): Which of 5 categories

### Parsing Algorithm Structure

For each step, document:

1. **Input**: What data comes in
2. **Process**: What happens
3. **Output**: What data comes out
4. **Error Handling**: What if it fails
5. **Edge Cases**: Special scenarios
6. **Examples**: Concrete examples

### Ambiguity Handling Structure

For each scenario, document:

1. **Scenario**: What causes ambiguity
2. **Detection**: How to detect it
3. **Default Behavior**: What to do automatically
4. **User Interaction**: What to ask user (if needed)
5. **Resolution**: How to resolve
6. **Examples**: Concrete examples

---

## 📚 Active EXECUTION_TASKs

- [x] **EXECUTION_TASK_02_01**: Status: Complete

---

## 📝 Execution Log

- **EXECUTION_TASK_02_01**: Created 2025-11-09, Completed 2025-11-09, Status: Complete

---

## 📈 Summary Statistics

**Total Iterations**: 1  
**Time Spent**: ~1 hour  
**Efficiency**: Ahead of estimate (estimated 2-3 hours, actual 1 hour)

---

## 📝 Learning Summary

**Technical Learnings**:
- Routing logic requires clear priority rules to handle overlapping keywords
- 7-step parsing algorithm provides systematic approach to prompt decomposition
- Data structure specifications (dataclasses) make implementation requirements explicit
- Ambiguity handling needs both automatic defaults and user feedback options

**Process Learnings**:
- Specification work benefits from concrete examples at each step
- Implementation checklists ensure nothing is missed in PLAN 4
- Testing strategy should be defined during design, not after
- Extensibility design prevents breaking changes when adding features

**Design Insights**:
- Deterministic routing (same input → same output) is critical for predictability
- Graceful degradation (helpful errors) improves user experience
- Special rules (e.g., "investigate" + "issue" → Debug) handle edge cases elegantly
- Backward compatibility guarantees enable safe extension

---

## 🔮 Future Work Discovered

None - routing logic is complete and ready for Achievement 0.3 (mapping table) and PLAN 4 (automation)

---

## ✅ Completion Status

- [ ] All tests passing (if code work) - N/A (documentation work)
- [ ] All code commented with learnings (if code work) - N/A (documentation work)
- [x] Subplan objectives met
- [x] Execution result: Success
- [ ] If Abandoned: N/A
- [x] Future work extracted
- [x] Ready for archive

**Total Iterations**: 1  
**Total Time**: ~1 hour  
**Final Status**: ✅ Success

---

**Status**: ✅ Complete  
**Next**: Update PLAN to reflect Achievement 0.2 completion  
**Parent PLAN**: PLAN_EXECUTION-PROMPT-SYSTEM.md

