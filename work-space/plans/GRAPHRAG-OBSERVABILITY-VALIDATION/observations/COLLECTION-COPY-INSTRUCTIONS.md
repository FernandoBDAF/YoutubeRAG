# Collection Copy Instructions - Achievement 2.1

**Date**: 2025-11-12  
**Task**: Copy `video_chunks` collection from `mongo_hack` to `validation_01`  
**Status**: Ready to Execute

---

## 📝 Collection Names Verification

From `core/config/paths.py` (line 23):

```python
COLL_CHUNKS: Final[str] = "video_chunks"  # Note: Consider renaming to "document_chunks" in future
```

**Correct Collection Name**: `video_chunks` (NOT `chunks`)

---

## 🔄 Copy Commands

### Method 1: Using `mongosh` (Modern MongoDB Shell)

The `--uri` syntax requires the database to be part of the connection string, not as a separate argument.

```bash
# Connect to mongo_hack and copy video_chunks to validation_01

# Step 1: Dump video_chunks from mongo_hack
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/mongo_hack" \
  --eval "db.video_chunks.find().forEach(doc => { db.getSiblingDB('validation_01').video_chunks.insertOne(doc) })"
```

**What this does**:

- Connects to `mongo_hack` database
- Iterates through all documents in `video_chunks`
- Inserts each document into `validation_01.video_chunks`

---

### Method 2: Using `mongodump` & `mongorestore` (Recommended for Large Collections)

```bash
# Step 1: Dump video_chunks collection from mongo_hack
mongodump \
  --uri "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/mongo_hack" \
  --collection video_chunks \
  --out /tmp/graphrag-backup

# Step 2: Restore to validation_01
mongorestore \
  --uri "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --collection video_chunks \
  /tmp/graphrag-backup/mongo_hack/video_chunks.bson
```

**What this does**:

- Exports `video_chunks` from `mongo_hack` to local file
- Imports that file into `validation_01.video_chunks`
- More reliable for large collections

---

### Method 3: Using MongoDB Compass (GUI)

**Steps**:

1. Connect to your MongoDB cluster in Compass
2. Navigate to `mongo_hack` → `video_chunks`
3. Right-click on `video_chunks` → "Export Collection"
4. Select "Export Full Collection" → Save as `.bson`
5. Navigate to `validation_01` database
6. Right-click on `validation_01` → "Import Collection"
7. Select the `.bson` file you just exported
8. Click "Import"

---

## ✅ Verification Commands

After copying, verify the copy was successful:

### Count documents in both databases

```bash
# Count in mongo_hack
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/mongo_hack" \
  --eval "db.video_chunks.countDocuments()"

# Count in validation_01
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "db.video_chunks.countDocuments()"
```

**Expected**: Both counts should be equal.

---

### Check collection exists in validation_01

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "db.getCollectionNames()"
```

**Expected**: Should include `"video_chunks"` in the list.

---

### Sample a document to verify data integrity

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "db.video_chunks.findOne()" --json canonical
```

**Expected**: Should return a valid document with expected fields.

---

## 📋 Recommended Approach

**For this use case (one-time copy before pipeline execution)**:

1. **Use Method 2 (mongodump/mongorestore)** if collection is large (100K+ documents)
2. **Use Method 1 (mongosh forEach)** if collection is small (< 100K documents)
3. **Use Method 3 (Compass GUI)** if you prefer visual confirmation

---

## 🎯 Next Steps After Copying

1. ✅ Verify counts match between `mongo_hack.video_chunks` and `validation_01.video_chunks`
2. ✅ Check a sample document to ensure data integrity
3. ✅ Confirm `validation_01` database now contains `video_chunks` collection
4. ✅ Proceed to Phase 2: Pipeline Execution

---

## ⚠️ Important Notes

- **Connection String**: Use the full MongoDB Atlas connection string
- **Authentication**: Credentials are embedded in the connection string
- **Database in URL**: The database name comes AFTER the cluster URL in the connection string
- **Collection Name**: Always use `video_chunks`, NOT `chunks`

---

**Prepared**: 2025-11-12 23:00 UTC  
**Status**: ✅ READY TO EXECUTE
