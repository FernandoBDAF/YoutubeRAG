# Configuration Troubleshooting Guide

**Achievement**: 4.3 - Configuration Integration Validated  
**Date**: 2025-11-14  
**Purpose**: Diagnose and resolve configuration issues with GraphRAG observability

---

## Quick Troubleshooting Checklist

Before diving into specific issues, run through this checklist:

- [ ] Environment variables are set correctly
- [ ] `.env` file exists and is loaded
- [ ] Variable names are spelled correctly
- [ ] Values are valid ("true" or "false" for booleans)
- [ ] MongoDB is running and accessible
- [ ] Database name is correct
- [ ] Python environment is activated
- [ ] `python-dotenv` is installed

---

## Common Issues

### Issue 1: Environment Variables Not Being Respected

**Symptoms**:
- Set `GRAPHRAG_TRANSFORMATION_LOGGING=true` but no logs appear
- Set `GRAPHRAG_QUALITY_METRICS=true` but no metrics collected
- Configuration changes have no effect

**Possible Causes**:

#### Cause A: .env File Not Loaded

**Check**:
```bash
# Verify .env file exists
ls -la .env

# Check if python-dotenv is installed
pip list | grep python-dotenv
```

**Solution**:
```bash
# Install python-dotenv
pip install python-dotenv

# Ensure .env is in project root
# Ensure pipeline loads .env (check business/pipelines/graphrag.py)
```

#### Cause B: Variable Name Typo

**Check**:
```bash
# List all environment variables
env | grep GRAPHRAG

# Compare with correct names:
# GRAPHRAG_TRANSFORMATION_LOGGING
# GRAPHRAG_SAVE_INTERMEDIATE_DATA
# GRAPHRAG_QUALITY_METRICS
```

**Solution**:
Fix typos in variable names (case-sensitive).

#### Cause C: Shell Not Exporting Variables

**Check**:
```bash
# Check if variable is set
echo $GRAPHRAG_TRANSFORMATION_LOGGING

# If empty, variable not exported
```

**Solution**:
```bash
# Use 'export' to set variables
export GRAPHRAG_TRANSFORMATION_LOGGING=true

# Or add to .env file instead
```

#### Cause D: Wrong Shell or Session

**Check**:
```bash
# Check current shell
echo $SHELL

# Variables set in one terminal won't affect another
```

**Solution**:
- Set variables in the same terminal where you run the pipeline
- Or use `.env` file (recommended)
- Or add to shell profile (~/.bashrc, ~/.zshrc)

---

### Issue 2: Collections Not Being Created

**Symptoms**:
- Expected collections don't appear in MongoDB
- `transformation_logs` collection missing
- `quality_metrics` collection missing
- Intermediate data collections missing

**Diagnosis**:

#### Step 1: Verify Configuration

```bash
# Check environment variables
echo "Logging: $GRAPHRAG_TRANSFORMATION_LOGGING"
echo "Intermediate: $GRAPHRAG_SAVE_INTERMEDIATE_DATA"
echo "Metrics: $GRAPHRAG_QUALITY_METRICS"
```

#### Step 2: Check Pipeline Logs

```bash
# Look for these messages in pipeline output:
# "Quality metrics collection: enabled" or "disabled"
# "Transformation logging: enabled" or "disabled"
```

#### Step 3: Verify MongoDB Connection

```bash
# Test MongoDB connection
mongo $MONGO_URI --eval "db.stats()"

# List collections
mongo $MONGO_URI --eval "db.getCollectionNames()"
```

**Solutions**:

**If variables are "false"**:
```bash
# Enable the features
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true
```

**If MongoDB not accessible**:
```bash
# Check MongoDB is running
systemctl status mongod  # Linux
brew services list | grep mongodb  # macOS

# Start MongoDB if needed
systemctl start mongod  # Linux
brew services start mongodb-community  # macOS
```

**If pipeline hasn't run yet**:
```bash
# Collections are created when pipeline runs
# Run pipeline to create collections
python business/pipelines/graphrag.py
```

---

### Issue 3: Invalid Values Silently Ignored

**Symptoms**:
- Set `GRAPHRAG_TRANSFORMATION_LOGGING=yes` but logging not enabled
- Set `GRAPHRAG_QUALITY_METRICS=1` but metrics not collected
- No error messages about invalid values

**Explanation**:
This is **by design**. The configuration system only recognizes "true" (case-insensitive) as enabling a feature. All other values are treated as "false" with no warnings.

**Valid Values**:
- ✅ `"true"` (any case: TRUE, True, true)
- ❌ `"false"` (any case: FALSE, False, false)
- ❌ `"yes"` (not recognized, treated as false)
- ❌ `"1"` (not recognized, treated as false)
- ❌ `"on"` (not recognized, treated as false)
- ❌ Any other value (treated as false)

**Solution**:
```bash
# Use "true" or "false" only
export GRAPHRAG_TRANSFORMATION_LOGGING=true  # ✅ Correct
export GRAPHRAG_TRANSFORMATION_LOGGING=yes   # ❌ Wrong (treated as false)
```

**Verification**:
```bash
# After setting variables, check pipeline logs for:
# "Quality metrics collection: enabled"
# "Transformation logging: enabled"
```

---

### Issue 4: High Storage Usage

**Symptoms**:
- MongoDB database growing rapidly
- Disk space running low
- Collections very large

**Diagnosis**:

#### Check Collection Sizes

```bash
mongo mongo_hack --eval "
  db.getCollectionNames().forEach(function(col) {
    var stats = db[col].stats();
    print(col + ': ' + (stats.size / 1024 / 1024).toFixed(2) + ' MB');
  });
"
```

**Common Culprits**:
- `transformation_logs`: Can be large if logging enabled
- `*_intermediate`: Intermediate data collections
- `quality_metrics`: Usually small

**Solutions**:

#### Solution A: Disable Intermediate Data

```bash
# Intermediate data can be very large
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
```

#### Solution B: Reduce TTL

```bash
# Cleanup intermediate data faster
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=1
```

#### Solution C: Manual Cleanup

```bash
# Drop intermediate collections
mongo mongo_hack --eval "
  db.getCollectionNames().forEach(function(col) {
    if (col.includes('_intermediate')) {
      db[col].drop();
      print('Dropped: ' + col);
    }
  });
"

# Drop old transformation logs
mongo mongo_hack --eval "
  db.transformation_logs.deleteMany({
    timestamp: { \$lt: new Date(Date.now() - 7*24*60*60*1000) }
  });
"
```

#### Solution D: Use Experiment Databases

```bash
# Write to separate database for testing
python business/pipelines/graphrag.py \
  --read-db-name mongo_hack \
  --write-db-name mongo_hack_test

# Drop test database when done
mongo mongo_hack_test --eval "db.dropDatabase()"
```

---

### Issue 5: Performance Degradation

**Symptoms**:
- Pipeline running slower than expected
- High CPU or memory usage
- Long execution times

**Diagnosis**:

#### Check Observability Overhead

```bash
# Test with all observability disabled
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=false

time python business/pipelines/graphrag.py

# Test with observability enabled
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true

time python business/pipelines/graphrag.py

# Compare execution times
```

**Expected Overhead**:
- Logging only: ~2-3%
- Metrics only: ~3-5%
- Intermediate data: ~5-10%
- All enabled: ~10-15%

**Solutions**:

#### Solution A: Disable Intermediate Data

```bash
# Biggest performance impact
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
```

#### Solution B: Selective Observability

```bash
# Keep metrics, disable logging
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_QUALITY_METRICS=true
```

#### Solution C: Production Configuration

```bash
# Minimal overhead
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=true
```

---

### Issue 6: Experiment Mode Not Working

**Symptoms**:
- `--experiment-id` not recognized
- `--read-db-name` not working
- `--write-db-name` not working
- Data written to wrong database

**Diagnosis**:

#### Check CLI Arguments

```bash
# Verify arguments are accepted
python business/pipelines/graphrag.py --help | grep -E "experiment-id|read-db-name|write-db-name"
```

**Expected Output**:
```
--experiment-id EXPERIMENT_ID
--read-db-name READ_DB_NAME
--write-db-name WRITE_DB_NAME
```

**Solutions**:

#### Solution A: Check Argument Spelling

```bash
# Correct usage
python business/pipelines/graphrag.py \
  --experiment-id test-001 \
  --read-db-name mongo_hack \
  --write-db-name mongo_hack_test

# Common mistakes:
# --experiment_id (underscore instead of hyphen) ❌
# --read_db_name (underscore instead of hyphen) ❌
# --write_db_name (underscore instead of hyphen) ❌
```

#### Solution B: Check Pipeline Version

```bash
# Experiment mode added in Achievement 4.1
# Verify pipeline has the arguments
grep -n "experiment-id" business/pipelines/graphrag.py
```

#### Solution C: Verify Database Isolation

```bash
# Check which database was used
mongo --eval "
  db.getMongo().getDBNames().forEach(function(dbName) {
    print(dbName);
  });
"

# Verify data in correct database
mongo mongo_hack_test --eval "db.getCollectionNames()"
```

---

## Configuration Validation Checklist

Use this checklist to verify your configuration is correct:

### Basic Configuration

- [ ] `.env` file exists in project root
- [ ] `python-dotenv` is installed
- [ ] Environment variables are set
- [ ] Variable names are spelled correctly
- [ ] Values are "true" or "false" (for booleans)

### MongoDB Configuration

- [ ] MongoDB is running
- [ ] MongoDB is accessible
- [ ] Database name is correct
- [ ] Connection string is valid
- [ ] Sufficient disk space available

### Observability Configuration

- [ ] `GRAPHRAG_TRANSFORMATION_LOGGING` set to "true" or "false"
- [ ] `GRAPHRAG_SAVE_INTERMEDIATE_DATA` set to "true" or "false"
- [ ] `GRAPHRAG_QUALITY_METRICS` set to "true" or "false"
- [ ] `GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS` is a positive integer (if used)

### Verification

- [ ] Run pipeline and check logs for configuration messages
- [ ] Verify expected collections are created
- [ ] Check collection sizes are reasonable
- [ ] Monitor performance overhead
- [ ] Test experiment mode (if using)

---

## Debugging Steps

### Step 1: Verify Environment Variables

```bash
# Print all GRAPHRAG variables
env | grep GRAPHRAG

# Expected output:
# GRAPHRAG_TRANSFORMATION_LOGGING=true
# GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
# GRAPHRAG_QUALITY_METRICS=true
# GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=7
```

### Step 2: Check Pipeline Initialization

```bash
# Run pipeline with verbose logging
python business/pipelines/graphrag.py --verbose

# Look for these messages:
# "Quality metrics collection: enabled" or "disabled"
# "Transformation logging: enabled" or "disabled"
```

### Step 3: Verify MongoDB Collections

```bash
# List all collections
mongo mongo_hack --eval "db.getCollectionNames()"

# Expected collections (if enabled):
# - transformation_logs (if TRANSFORMATION_LOGGING=true)
# - quality_metrics (if QUALITY_METRICS=true)
# - *_intermediate (if SAVE_INTERMEDIATE_DATA=true)
```

### Step 4: Check Collection Content

```bash
# Check transformation logs
mongo mongo_hack --eval "db.transformation_logs.count()"

# Check quality metrics
mongo mongo_hack --eval "db.quality_metrics.count()"

# Check intermediate data
mongo mongo_hack --eval "db.entity_resolution_intermediate.count()"
```

### Step 5: Test Configuration Changes

```bash
# Disable all observability
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=false

# Run pipeline
python business/pipelines/graphrag.py

# Verify no observability collections created

# Enable all observability
export GRAPHRAG_TRANSFORMATION_LOGGING=true
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=true
export GRAPHRAG_QUALITY_METRICS=true

# Run pipeline
python business/pipelines/graphrag.py

# Verify all observability collections created
```

---

## Error Messages and Solutions

### Error: "ModuleNotFoundError: No module named 'dotenv'"

**Solution**:
```bash
pip install python-dotenv
```

### Error: "pymongo.errors.ServerSelectionTimeoutError"

**Solution**:
```bash
# Check MongoDB is running
systemctl status mongod  # Linux
brew services list | grep mongodb  # macOS

# Start MongoDB
systemctl start mongod  # Linux
brew services start mongodb-community  # macOS

# Verify connection string
echo $MONGO_URI
```

### Error: "Database 'mongo_hack' not found"

**Solution**:
```bash
# Database is created automatically when pipeline runs
# Just run the pipeline
python business/pipelines/graphrag.py
```

### Warning: "Quality metrics collection: disabled"

**Explanation**: This is informational, not an error.

**Solution** (if you want metrics enabled):
```bash
export GRAPHRAG_QUALITY_METRICS=true
```

---

## FAQ

### Q: How do I know if my configuration is working?

**A**: Check pipeline logs for configuration messages:
```bash
python business/pipelines/graphrag.py --verbose 2>&1 | grep -E "metrics|logging|intermediate"
```

Look for:
- "Quality metrics collection: enabled"
- "Transformation logging: enabled"

---

### Q: Why are my environment variables not working?

**A**: Common causes:
1. Variables not exported: Use `export VARIABLE=value`
2. Wrong terminal session: Set variables in same terminal as pipeline
3. Typo in variable name: Check spelling
4. `.env` file not loaded: Install `python-dotenv`

---

### Q: Can I use "yes" or "1" instead of "true"?

**A**: No. Only "true" (case-insensitive) enables features. All other values are treated as "false".

---

### Q: How much storage does observability use?

**A**: Depends on configuration:
- Logging only: ~10-50 MB per run
- Metrics only: ~1-5 MB per run
- Intermediate data: ~50-200 MB per run
- All enabled: ~60-255 MB per run

---

### Q: How much performance overhead does observability add?

**A**: Depends on configuration:
- Logging only: ~2-3%
- Metrics only: ~3-5%
- Intermediate data: ~5-10%
- All enabled: ~10-15%

---

### Q: Can I enable observability temporarily?

**A**: Yes:
```bash
# Enable temporarily
export GRAPHRAG_TRANSFORMATION_LOGGING=true
python business/pipelines/graphrag.py

# Disable after
unset GRAPHRAG_TRANSFORMATION_LOGGING
```

---

### Q: How do I cleanup old observability data?

**A**: Several options:
```bash
# Option 1: Drop specific collections
mongo mongo_hack --eval "db.transformation_logs.drop()"

# Option 2: Drop entire database
mongo mongo_hack --eval "db.dropDatabase()"

# Option 3: Delete old documents
mongo mongo_hack --eval "
  db.transformation_logs.deleteMany({
    timestamp: { \$lt: new Date(Date.now() - 7*24*60*60*1000) }
  });
"

# Option 4: Use TTL (automatic cleanup)
export GRAPHRAG_INTERMEDIATE_DATA_TTL_DAYS=1
```

---

### Q: What's the recommended configuration for production?

**A**: Metrics only (minimal overhead):
```bash
export GRAPHRAG_TRANSFORMATION_LOGGING=false
export GRAPHRAG_SAVE_INTERMEDIATE_DATA=false
export GRAPHRAG_QUALITY_METRICS=true
```

---

### Q: How do I test configuration changes safely?

**A**: Use experiment mode:
```bash
python business/pipelines/graphrag.py \
  --experiment-id test-config \
  --read-db-name mongo_hack \
  --write-db-name mongo_hack_test

# Cleanup after testing
mongo mongo_hack_test --eval "db.dropDatabase()"
```

---

### Q: Can I have different configurations for different stages?

**A**: Not directly. All stages use the same configuration. However, you can:
1. Run stages separately with different configs
2. Use experiment mode for testing
3. Modify code to add stage-specific configuration

---

### Q: What if I need to debug a production issue?

**A**: Enable logging temporarily:
```bash
# Enable logging for one run
export GRAPHRAG_TRANSFORMATION_LOGGING=true
python business/pipelines/graphrag.py

# Disable after debugging
unset GRAPHRAG_TRANSFORMATION_LOGGING
```

Or use experiment mode:
```bash
python business/pipelines/graphrag.py \
  --experiment-id debug-prod-issue \
  --read-db-name mongo_hack \
  --write-db-name mongo_hack_debug

# Investigate in debug database
# Cleanup when done
mongo mongo_hack_debug --eval "db.dropDatabase()"
```

---

## Getting Help

If you're still experiencing issues:

1. **Check Logs**: Review pipeline logs for error messages
2. **Verify Configuration**: Run through the validation checklist
3. **Test Minimal Config**: Try with all observability disabled
4. **Check MongoDB**: Verify MongoDB is accessible
5. **Review Documentation**: Check Configuration-Matrix.md and Recommended-Configurations.md
6. **File Issue**: If problem persists, file an issue with:
   - Configuration used
   - Error messages
   - Pipeline logs
   - MongoDB status

---

**Last Updated**: 2025-11-14  
**Related Documents**:
- Configuration-Matrix.md
- Configuration-Validation-Report.md
- Recommended-Configurations.md


