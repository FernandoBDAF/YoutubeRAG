# SUBPLAN: Design 5 Core Prompt Patterns

**Type**: SUBPLAN  
**Mother Plan**: PLAN_EXECUTION-PROMPT-SYSTEM.md  
**Plan**: EXECUTION-PROMPT-SYSTEM  
**Achievement Addressed**: Achievement 0.1 (Design 5 Core Prompt Patterns)  
**Achievement**: 0.1  
**Status**: Complete  
**Created**: 2025-11-09 19:00 UTC  
**Completed**: 2025-11-09 20:00 UTC  
**Estimated Effort**: 3-4 hours  
**Actual Effort**: ~1 hour

---

## 🎯 Objective

Design standardized natural language prompt patterns for all 5 execution work types (Analysis, Case Study, Review, Debug, Observation), specifying syntax, routing logic, and comprehensive examples. This establishes the foundation for natural language initiation of execution work and enables future automation (PLAN 4).

**Contribution to Mother PLAN**: Provides the core prompt patterns that users will use to initiate execution work, forming the foundation for the comprehensive guide (Priority 1) and protocol integration (Priority 2).

---

## 📋 What Needs to Be Created

### Primary Deliverable

**File**: `LLM/guides/EXECUTION-PROMPT-PATTERNS.md` (300-400 lines)

**Content**:

- 5 core prompt patterns with full specifications
- Syntax definitions for each pattern
- Routing logic (prompt → document type → template)
- 3+ examples per pattern (15+ total)
- Extended pattern support ("for <PURPOSE>", "using <METHOD>")
- Pattern variations (alternative phrasings)
- Quick reference table

### Pattern Specifications (5 Required)

**Pattern 1: Analysis**

- Syntax: "Execution: make an analysis on <TARGET> [for <PURPOSE>]"
- Routes to: EXECUTION_ANALYSIS (Category 5: Planning & Strategy)
- Template: EXECUTION_ANALYSIS-PLANNING-STRATEGY-TEMPLATE.md
- Examples: 3+ covering different domains

**Pattern 2: Case Study**

- Syntax: "Execution: make a case study on <TARGET> [for <PURPOSE>]"
- Routes to: EXECUTION_CASE-STUDY
- Template: EXECUTION_CASE-STUDY-TEMPLATE.md
- Examples: 3+ covering different scenarios

**Pattern 3: Review**

- Syntax: "Execution: review the implementation of <TARGET> [for <PURPOSE>]"
- Routes to: EXECUTION_ANALYSIS (Category 3: Implementation Review)
- Template: EXECUTION_ANALYSIS-IMPLEMENTATION-REVIEW-TEMPLATE.md
- Examples: 3+ covering different implementations

**Pattern 4: Debug**

- Syntax: "Execution: debug <ISSUE> [in <CONTEXT>]"
- Routes to: EXECUTION_ANALYSIS (Category 1: Bug/Issue Analysis)
- Template: EXECUTION_ANALYSIS-BUG-TEMPLATE.md
- Examples: 3+ covering different bug types

**Pattern 5: Observation**

- Syntax: "Execution: watch <TARGET> to get <FEEDBACK_TYPE>" or "Execution: observe <TARGET> for <INSIGHTS>"
- Routes to: EXECUTION_OBSERVATION
- Template: EXECUTION_OBSERVATION-TEMPLATE.md
- Examples: 3+ covering different observation scenarios

### Supporting Content

**Extended Pattern Support**:

- "for <PURPOSE>" clause specification
- "using <METHOD>" clause specification
- Examples of extended patterns

**Pattern Variations**:

- Alternative phrasings for each pattern
- Synonym mapping (e.g., "analyze" vs "make an analysis")
- Natural language flexibility guidelines

**Quick Reference**:

- One-page table format
- Pattern → Syntax → Routes To → Template
- Printable/copyable format

---

## 📝 Approach

**Strategy**: Design patterns that are natural, intuitive, and unambiguous while maintaining clear routing to specific document types and templates.

**Method**:

1. **Pattern Definition Phase**

   - Define syntax for each of 5 patterns
   - Specify routing logic (prompt → type → template)
   - Create 3+ examples per pattern
   - Document extended pattern support

2. **Variation Design Phase**

   - Identify alternative phrasings for each pattern
   - Map synonyms and natural language variations
   - Ensure variations route to same destination
   - Document flexibility guidelines

3. **Quick Reference Creation**

   - Design one-page table format
   - Include all 5 patterns with key info
   - Make printable and copyable
   - Test for clarity and completeness

4. **Documentation Assembly**
   - Combine all specifications into single guide
   - Organize for readability and reference
   - Add navigation and structure
   - Verify completeness against requirements

**Key Considerations**:

- **Clarity**: Patterns must be unambiguous (no confusion about which type to create)
- **Naturalness**: Syntax should feel like natural language, not commands
- **Consistency**: All patterns follow similar structure ("Execution: <action> <target>")
- **Extensibility**: Support for optional clauses ("for <PURPOSE>", "using <METHOD>")
- **Routing Precision**: Each pattern maps to exactly one document type and template
- **Example Quality**: Examples must cover diverse domains and scenarios
- **Foundation for Automation**: Patterns designed for future script parsing (PLAN 4)

---

## 🔄 Execution Strategy

**Execution Count**: Single

**Rationale**:

- Design work is cohesive and interdependent (patterns should be consistent)
- All 5 patterns share common structure and principles
- Single execution ensures consistency across all patterns
- No benefit to splitting into multiple executions
- Estimated 3-4 hours fits within single execution scope

**EXECUTION_TASK**: `EXECUTION_TASK_EXECUTION-PROMPT-SYSTEM_01_01.md`

---

## 🧪 Tests

**Type**: Design Validation (Documentation Review)

**Validation Approach**:

1. **Completeness Check**

   - [ ] All 5 patterns documented with syntax
   - [ ] Each pattern has 3+ examples
   - [ ] Routing logic specified for each pattern
   - [ ] Extended pattern support documented
   - [ ] Pattern variations documented
   - [ ] Quick reference table created

2. **Clarity Validation**

   - [ ] Syntax is unambiguous (no confusion about which pattern to use)
   - [ ] Examples are diverse and representative
   - [ ] Routing logic is clear and precise
   - [ ] Quick reference is readable and useful

3. **Consistency Check**

   - [ ] All patterns follow similar structure
   - [ ] Syntax conventions consistent across patterns
   - [ ] Example format consistent
   - [ ] Documentation structure consistent

4. **Usability Test** (Manual)
   - Select 5 random scenarios
   - Use patterns to formulate prompts
   - Verify prompt maps to correct document type
   - Measure clarity (should be obvious which pattern to use)

**Expected Results**:

- All 5 patterns fully specified
- 15+ examples covering diverse scenarios
- Clear routing logic for each pattern
- Usable quick reference
- Foundation ready for comprehensive guide (Achievement 1.1)

---

## 📚 Dependencies

**Upstream (Must Complete First)**:

- ✅ PLAN 1 (EXECUTION-TAXONOMY-AND-WORKSPACE) complete
  - Provides stable taxonomy (6 types: TASK + 5 WORK types)
  - Defines document types and templates
  - Establishes routing targets

**Downstream (Depends on This)**:

- Achievement 0.2: Design Prompt Routing Logic (uses these patterns)
- Achievement 0.3: Create Prompt-to-Template Mapping (uses these patterns)
- Achievement 1.1: Create Comprehensive Guide (incorporates these patterns)
- PLAN 4: Automation scripts (parses these patterns)

**Related Work**:

- `LLM/guides/EXECUTION-TAXONOMY.md` - Document type definitions
- `LLM/templates/EXECUTION_ANALYSIS-*-TEMPLATE.md` - Target templates
- `LLM/templates/EXECUTION_CASE-STUDY-TEMPLATE.md` - Target template
- `LLM/templates/EXECUTION_OBSERVATION-TEMPLATE.md` - Target template

---

## 📊 Success Criteria

**Must Have**:

- [ ] 5 patterns documented (Analysis, Case Study, Review, Debug, Observation)
- [ ] Syntax specified for each pattern
- [ ] Routing logic clear (prompt → type → template)
- [ ] 15+ examples (3+ per pattern)
- [ ] Extended pattern support ("for <PURPOSE>", "using <METHOD>")
- [ ] Pattern variations documented
- [ ] Quick reference table created

**Should Have**:

- [ ] Examples cover diverse domains (GraphRAG, methodology, code quality, etc.)
- [ ] Variations include common synonyms
- [ ] Quick reference is one-page and printable
- [ ] Documentation is well-structured and navigable

**Nice to Have**:

- [ ] Usage guidance (when to use which pattern)
- [ ] Anti-patterns (what NOT to do)
- [ ] Edge case handling (ambiguous prompts)

---

## 🔄 Iteration Strategy

**Expected Iterations**: 1-2

**Iteration 1** (Design & Documentation):

- Define syntax for all 5 patterns
- Create 3+ examples per pattern
- Document routing logic
- Create quick reference
- Assemble documentation

**Iteration 2** (Refinement - if needed):

- Refine syntax based on clarity review
- Add more examples if coverage insufficient
- Improve quick reference format
- Enhance documentation structure

**Completion Criteria**:

- All success criteria met
- Patterns are clear and unambiguous
- Examples are diverse and representative
- Quick reference is usable
- Ready for Achievement 0.2 (routing logic)

---

## 📝 Design Principles

**Principle 1: Natural Language First**

- Patterns should feel like natural language, not commands
- Use conversational phrasing ("make an analysis on" vs "analyze")
- Support natural variations (synonyms, alternative phrasings)

**Principle 2: Unambiguous Routing**

- Each pattern maps to exactly one document type
- No overlap between patterns (clear boundaries)
- Routing logic is deterministic (same prompt → same type)

**Principle 3: Consistent Structure**

- All patterns start with "Execution:"
- All patterns follow <action> <target> structure
- Optional clauses use consistent syntax

**Principle 4: Extensible Design**

- Support for optional clauses ("for <PURPOSE>", "using <METHOD>")
- Room for future pattern additions
- Compatible with automation parsing (PLAN 4)

**Principle 5: Example-Driven**

- Examples demonstrate pattern usage
- Examples cover diverse domains
- Examples show optional clause usage

---

## 🎯 Pattern Design Specifications

### Pattern Structure Template

For each pattern, document:

1. **Name**: Pattern identifier
2. **Syntax**: Formal syntax specification
3. **Action Keywords**: Key words that trigger this pattern
4. **Routes To**: Document type and template
5. **Required Elements**: What must be in the prompt
6. **Optional Elements**: What can be added
7. **Examples**: 3+ diverse examples
8. **Variations**: Alternative phrasings
9. **Use Cases**: When to use this pattern

### Routing Logic Template

For each pattern, specify:

1. **Trigger**: What keywords/structure activates this pattern
2. **Document Type**: What type of document to create
3. **Template**: Which template to use
4. **Category** (if EXECUTION_ANALYSIS): Which of 5 categories
5. **Location**: Where to create the file

### Example Format Template

For each example, provide:

1. **Prompt**: The natural language prompt
2. **Context**: When/why you'd use this prompt
3. **Routes To**: What document type/template
4. **Result**: What gets created

---

## 📚 Active EXECUTION_TASKs

- [x] **EXECUTION_TASK_01_01**: Status: Complete

---

## 📝 Execution Log

- **EXECUTION_TASK_01_01**: Created 2025-11-09, Completed 2025-11-09, Status: Complete

---

## 📈 Summary Statistics

**Total Iterations**: 1  
**Time Spent**: ~1 hour  
**Efficiency**: Ahead of estimate (estimated 3-4 hours, actual 1 hour)

---

## 📝 Learning Summary

**Technical Learnings**:

- Natural language pattern design requires balance between flexibility and precision
- Quick reference tables and decision trees significantly improve usability
- Examples covering diverse domains demonstrate pattern applicability
- Anti-patterns documentation prevents common mistakes

**Process Learnings**:

- Comprehensive examples and variations improve pattern adoption
- One-page quick reference format makes patterns accessible
- Extended pattern support ("for <PURPOSE>") adds value without complexity
- Starting with syntax, then examples, then variations creates logical flow

**Design Insights**:

- Consistent structure across patterns improves learnability
- Optional clauses increase expressiveness without sacrificing clarity
- Variations enable natural language flexibility with deterministic routing
- Domain-specific examples help users apply patterns to their work

---

## 🔮 Future Work Discovered

None - patterns are complete and ready for Achievement 0.2 (routing logic)

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
**Next**: Update PLAN to reflect Achievement 0.1 completion  
**Parent PLAN**: PLAN_EXECUTION-PROMPT-SYSTEM.md
