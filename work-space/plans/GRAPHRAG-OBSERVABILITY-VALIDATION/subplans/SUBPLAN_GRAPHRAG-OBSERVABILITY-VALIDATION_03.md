# SUBPLAN: GraphRAG Observability Validation - Environment Variables Configured

**Objective**: Set up and validate all required environment variables for GraphRAG observability infrastructure, ensuring proper configuration for transformation logging, intermediate data collection, quality metrics, and pipeline settings.

**Achievement**: 0.3: Environment Variables Configured  
**Parent PLAN**: PLAN_GRAPHRAG-OBSERVABILITY-VALIDATION.md  
**Priority**: CRITICAL  
**Estimated Effort**: 1-2 hours

---

## 🎯 Deliverables

1. **`.env.observability` Template File**:

   - Complete environment variable template with all observability settings
   - All variables documented with descriptions
   - Default values specified
   - Required vs. optional variables clearly marked
   - Location: Root directory or docs folder

2. **Environment Variable Documentation**:

   - Comprehensive guide explaining each variable
   - Purpose, expected values, defaults
   - Dependencies between variables
   - How variables affect observability behavior
   - Troubleshooting guide for common issues

3. **Validation Checklist**:
   - List of all variables to configure
   - Validation steps for each variable
   - Testing procedures to verify correct reading
   - Results from validation run

---

## 📖 Context & Prerequisites

**Parent Work Complete**:

- Achievement 0.1: Transformation Logging Infrastructure (complete)
- Achievement 0.2: Collection Name Compatibility (complete)
- Achievement 0.2: Configuration Compatibility (complete)

**Existing Infrastructure**:

- `core/config/graphrag.py` - Reads environment variables
- `core/models/config.py` - BaseStageConfig with trace_id
- `business/pipelines/graphrag.py` - Pipeline execution with trace_id propagation
- Environment variable handling already implemented

**Goal**: Document and validate all observability-related environment variables to ensure pipeline can be properly configured for observability validation run.

---

## 🎯 Objective & Approach

**Objective**:
Create comprehensive environment variable configuration for GraphRAG observability pipeline, document all variables, validate they're read correctly, and provide template for reproducible observability validation runs.

**Approach**:

1. **Audit Existing Variables**: Review current environment variable handling in codebase
2. **Document Variables**: Create comprehensive documentation of all observability variables
3. **Create Template**: Build `.env.observability` template with all variables
4. **Test Variables**: Validate each variable is read correctly by pipeline
5. **Verify Defaults**: Test that defaults work when variables not set
6. **Create Validation Checklist**: Document validation procedures

---

## 📋 Execution Strategy

**Single EXECUTION_TASK approach** (sequential):

- Configuration audit (identify all variables)
- Documentation creation (explain each variable)
- Template generation (create `.env.observability`)
- Variable testing (validate each is read correctly)
- Validation run (test pipeline with variables)

**Total Estimated Time**: 1-2 hours

- Variable audit: 15-20 minutes
- Documentation: 30-40 minutes
- Template creation: 15-20 minutes
- Testing: 20-30 minutes

---

## 🔧 Detailed Approach

### Phase 1: Environment Variable Audit (15-20 min)

**Steps**:

1. Review `core/config/graphrag.py` for environment variable usage
2. Review `core/config/paths.py` for collection name variables
3. Review `business/pipelines/graphrag.py` for runtime variables
4. Check `.env.example` (if exists) for reference
5. Document all variables found:
   - Variable name
   - Where it's used
   - Default value
   - Type (string, boolean, int, float)
   - Required or optional

**Variables to Find**:

- Observability feature flags (GRAPHRAG_TRANSFORMATION_LOGGING, GRAPHRAG_SAVE_INTERMEDIATE_DATA, GRAPHRAG_QUALITY_METRICS)
- Pipeline settings (GRAPHRAG_USE_TPM_TRACKING, GRAPHRAG_TARGET_TPM, GRAPHRAG_TARGET_RPM)
- Database (MONGODB_URI, DB_NAME, READ_DB_NAME, WRITE_DB_NAME)
- OpenAI (OPENAI_API_KEY, GRAPHRAG_MODEL, GRAPHRAG_TEMPERATURE, GRAPHRAG_MAX_TOKENS)
- Extraction (GRAPHRAG_EXTRACTION_CONCURRENCY, GRAPHRAG_MAX_ENTITIES_PER_CHUNK, GRAPHRAG_MIN_ENTITY_CONFIDENCE)
- Resolution (GRAPHRAG_ENTITY_RESOLUTION_THRESHOLD, GRAPHRAG_MAX_ALIASES_PER_ENTITY)
- Construction (GRAPHRAG_MAX_RELATIONSHIPS_PER_ENTITY)
- Detection (GRAPHRAG_COMMUNITY_ALGORITHM, GRAPHRAG_MAX_CLUSTER_SIZE)

### Phase 2: Documentation Creation (30-40 min)

**Document Structure**:

- Header with overview
- Table of all variables (name, type, default, required/optional)
- Detailed description for each variable:
  - Purpose
  - Where it's used
  - Expected values
  - Default value
  - Example values
  - Impact on observability
- Categories:
  - Core Settings (MONGODB_URI, DB_NAME, OPENAI_API_KEY)
  - Observability Features (GRAPHRAG_TRANSFORMATION_LOGGING, etc.)
  - Extraction Settings (GRAPHRAG_EXTRACTION_CONCURRENCY, etc.)
  - Resolution Settings
  - Construction Settings
  - Detection Settings
  - Advanced Settings

### Phase 3: Template File Creation (15-20 min)

**`.env.observability` Template**:

- Comments explaining each section
- All variables with default or example values
- Clear marking of required vs optional
- Examples of different use cases (dev vs. production)
- Instructions at top for how to use

### Phase 4: Variable Testing & Validation (20-30 min)

**Testing Approach**:

1. Create test script to import configs and check values
2. Test reading each variable from environment
3. Verify defaults work when variable not set
4. Verify type conversions work correctly
5. Test with sample `.env.observability` file
6. Document any issues found

**Test Cases**:

- All variables present → values used
- Some variables missing → defaults used
- Invalid values → appropriate error or fallback
- Boolean values → "true"/"false" strings parsed correctly
- Numeric values → strings converted to proper types

---

## 🧪 Testing Plan

### Test 1: Variable Audit Completeness (5 min)

- **Objective**: Ensure all environment variables are identified
- **Method**: Review codebase for os.getenv() and env.get() calls
- **Expected**: Complete list of all variables used in project

### Test 2: Documentation Accuracy (5 min)

- **Objective**: Verify documentation matches actual code
- **Method**: Cross-reference documentation against code
- **Expected**: Documentation matches actual variable usage

### Test 3: Template Validity (5 min)

- **Objective**: Verify `.env.observability` template is valid
- **Method**: Syntax check, verify all variables documented
- **Expected**: Template is valid and complete

### Test 4: Variable Reading (10 min)

- **Objective**: Test each variable is read correctly by pipeline
- **Method**: Set variables in environment and verify pipeline reads them
- **Expected**: All variables read correctly

### Test 5: Default Values (5 min)

- **Objective**: Verify defaults work when variables not set
- **Method**: Unset variables and verify defaults are used
- **Expected**: Defaults work correctly

### Test 6: Type Conversions (5 min)

- **Objective**: Verify proper type handling
- **Method**: Test bool, int, float conversions
- **Expected**: Types converted correctly

---

## 📊 Expected Results

**Audit Results**:

- Complete inventory of 20-30 environment variables
- Clear categorization by purpose
- Documentation of default values

**Documentation**:

- Comprehensive guide (10-15 KB)
- Clear explanations of each variable
- Examples and use cases
- Troubleshooting section

**Template**:

- Valid `.env.observability` file
- All variables with defaults or examples
- Clear comments and structure
- Ready to copy and customize

**Validation Results**:

- All 6 tests passing
- Verification that variables are read correctly
- Confirmation that defaults work
- Type conversions validated

**No Breaking Changes**: Existing code continues to work with or without `.env.observability` file

---

## 📝 Findings Documentation

During execution, all findings will be documented in the `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_03_01.md` file, including:

- All environment variables identified
- Categorization of variables
- Default values for each
- Examples and use cases
- Testing results
- Any issues encountered
- Verification checklist

---

## ✅ Success Criteria

### Must Have (Required)

- ✅ All environment variables identified and audited
- ✅ Comprehensive documentation created
- ✅ `.env.observability` template generated
- ✅ All variables tested and validated
- ✅ Defaults verified to work correctly
- ✅ Documentation complete and accurate

### Should Have (Important)

- ✅ Categorized variables by purpose
- ✅ Examples provided for each variable
- ✅ Troubleshooting guide included
- ✅ Use cases documented (dev, test, production)

### Nice to Have (Bonus)

- ✅ Validation script for checking configuration
- ✅ Environment variable migration guide
- ✅ Performance tuning recommendations

---

## 📚 References

- `core/config/graphrag.py` - Environment variable reading
- `core/config/paths.py` - Collection name constants
- `core/models/config.py` - BaseStageConfig
- `business/pipelines/graphrag.py` - Pipeline initialization
- `.env.example` (if exists) - Existing env template

---

## ⏱️ Time Breakdown (Estimated)

- **Phase 1: Variable Audit**: 15-20 minutes
- **Phase 2: Documentation**: 30-40 minutes
- **Phase 3: Template Creation**: 15-20 minutes
- **Phase 4: Testing & Validation**: 20-30 minutes
- **Total Estimated Time**: 1-2 hours

---

## ✅ Success Metric

All environment variables required for GraphRAG observability are documented, a valid `.env.observability` template is created, and all variables are verified to be read correctly by the pipeline configuration system.

---

## 🎯 Next Step

**Executor** will create `EXECUTION_TASK_GRAPHRAG-OBSERVABILITY-VALIDATION_03_01.md` and execute the 4 phases according to this SUBPLAN, following the documented approach and testing procedures.
