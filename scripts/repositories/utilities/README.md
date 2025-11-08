# Utility Scripts

Utility scripts for database maintenance, data checking, and setup operations.

## Scripts

### check_data.py

Check GraphRAG data across all databases. Scans all databases and reports:

- Entities count
- Relations count
- Entity mentions count
- Communities count

**Usage**:

```bash
python scripts/repositories/utilities/check_data.py
```

**Purpose**: Quickly check which databases have GraphRAG data

---

### full_cleanup.py

**⚠️ WARNING: DESTRUCTIVE OPERATION**

Full GraphRAG data cleanup. This script:

1. Drops all GraphRAG collections (entities, relations, communities, entity_mentions)
2. Removes GraphRAG metadata from video_chunks
3. Verifies cleanup completion

**Usage**:

```bash
python scripts/repositories/utilities/full_cleanup.py
```

**Use Cases**:

- Starting fresh with GraphRAG pipeline
- Cleaning up after failed runs
- Preparing for full pipeline re-run

---

### seed_indexes.py

Seed database indexes for optimal query performance. Creates indexes on:

- Entities collection
- Relations collection
- Communities collection
- Entity mentions collection

**Usage**:

```bash
python scripts/repositories/utilities/seed_indexes.py
```

**Purpose**: Ensure optimal database performance for GraphRAG queries

---

## Safety Notes

- **full_cleanup.py** is destructive - use with caution
- Always backup data before running cleanup scripts
- Test in development environment first

---

**Created**: November 7, 2025  
**Source**: Consolidated from app/scripts/utilities/  
**Purpose**: Database maintenance and setup operations
