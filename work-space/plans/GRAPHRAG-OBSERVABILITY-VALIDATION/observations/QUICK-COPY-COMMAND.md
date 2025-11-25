# Quick Copy Command - video_chunks Collection

**Date**: 2025-11-12  
**Task**: Copy `video_chunks` from `mongo_hack` to `validation_01`  
**Status**: Ready to copy-paste

---

## 📋 Collection Info

- **Source Database**: `mongo_hack`
- **Source Collection**: `video_chunks`
- **Destination Database**: `validation_01`
- **Destination Collection**: `video_chunks`

---

## ✅ COPY-PASTE THIS COMMAND

### For Smaller Collections (< 100K documents)

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/mongo_hack" \
  --eval "db.video_chunks.find().forEach(doc => { db.getSiblingDB('validation_01').video_chunks.insertOne(doc) })"
```

**What it does**:

- Connects to `mongo_hack` database
- Reads all documents from `video_chunks`
- Inserts them into `validation_01.video_chunks`

**Time**: 1-5 minutes depending on collection size

---

### For Larger Collections (> 100K documents)

**Step 1: Export from mongo_hack**

```bash
mongodump \
  --uri "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/mongo_hack" \
  --collection video_chunks \
  --out /tmp/graphrag-backup
```

**Step 2: Import into validation_01**

```bash
mongorestore \
  --uri "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --collection video_chunks \
  /tmp/graphrag-backup/mongo_hack/video_chunks.bson
```

**Time**: 5-15 minutes depending on collection size

---

## ✅ VERIFY COPY WAS SUCCESSFUL

### Count documents in both databases

```bash
# Count in mongo_hack
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/mongo_hack" \
  --eval "db.video_chunks.countDocuments()"
```

Expected output: `<number of documents>`

```bash
# Count in validation_01
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "db.video_chunks.countDocuments()"
```

Expected output: `<same number as mongo_hack>`

---

### Check collection exists

```bash
mongosh "mongodb+srv://fernandobarrosomz_db_user:vkJV4cC8mx81wJyQ@cluster0.djtttp9.mongodb.net/validation_01" \
  --eval "db.getCollectionNames()"
```

Expected output: Should show `"video_chunks"` in the list

---

## 🎯 Next Steps After Successful Copy

1. ✅ Verify document counts match
2. ✅ Confirm collection exists in `validation_01`
3. ✅ Proceed to Phase 2: Pipeline Execution

---

**Prepared**: 2025-11-12 23:05 UTC  
**Status**: ✅ READY TO EXECUTE
