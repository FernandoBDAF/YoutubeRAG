# Maintenance

Scripts for database cleanup operations.

## Directory Structure

```
maintenance/
└── cleanup/              # Database cleanup scripts
    ├── clean_extraction_status.py   # Reset extraction status fields
    └── clean_graphrag_fields.py     # Remove GraphRAG-specific fields
```

## Cleanup Scripts

### `clean_extraction_status.py`
Resets extraction status fields in documents to allow re-processing.

**Usage:**
```bash
# Reset all documents
python -m maintenance.cleanup.clean_extraction_status --db <database>

# Reset specific collection
python -m maintenance.cleanup.clean_extraction_status --db <database> --collection <name>

# Dry run (show what would be changed)
python -m maintenance.cleanup.clean_extraction_status --db <database> --dry-run
```

**Warning:** This script modifies data. Always use `--dry-run` first.

### `clean_graphrag_fields.py`
Removes GraphRAG-specific fields from documents (e.g., before re-running pipeline).

**Usage:**
```bash
# Clean all GraphRAG fields
python -m maintenance.cleanup.clean_graphrag_fields --db <database>

# Clean specific fields
python -m maintenance.cleanup.clean_graphrag_fields --db <database> --fields entities,relationships

# Dry run
python -m maintenance.cleanup.clean_graphrag_fields --db <database> --dry-run
```

**Warning:** This is destructive. Back up your data first.

## Safety Guidelines

1. **Always backup** before running cleanup scripts
2. **Use --dry-run** to preview changes
3. **Test on staging** before production
4. **Keep audit logs** of cleanup operations

## Environment Variables

- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB` - Target database
