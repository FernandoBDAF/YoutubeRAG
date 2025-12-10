# Data Ingestion & Setup

Scripts for fetching and preparing data from external sources.

## Directory Structure

```
data/
├── ingestion/          # Data fetching scripts
│   ├── fetch_playlist_transcripts.py   # YouTube playlist ingestion
│   ├── transcribe_missing.py           # AWS Transcribe backfill
│   └── generate_db_with_raw_videos.py  # Database migration
└── setup/              # Database setup scripts
    ├── setup_validation_db.py          # Validation database setup
    └── copy_chunks_to_validation_db.py # Data copying utilities
```

## Ingestion Scripts

### `fetch_playlist_transcripts.py`
Fetches transcripts from YouTube playlists and stores them in MongoDB.

**Usage:**
```bash
python -m data.ingestion.fetch_playlist_transcripts --playlist-id <id>
```

### `transcribe_missing.py`
Uses AWS Transcribe to generate transcripts for videos that don't have them.

**Usage:**
```bash
python -m data.ingestion.transcribe_missing --db-name <database>
```

### `generate_db_with_raw_videos.py`
Migrates raw video data into the database format expected by the ingestion pipeline.

**Usage:**
```bash
python -m data.ingestion.generate_db_with_raw_videos
```

## Setup Scripts

### `setup_validation_db.py`
Creates and configures a validation database for testing purposes.

**Usage:**
```bash
python -m data.setup.setup_validation_db --target-db <name>
```

### `copy_chunks_to_validation_db.py`
Copies chunk data between databases for validation testing.

**Usage:**
```bash
python -m data.setup.copy_chunks_to_validation_db --source <db> --target <db>
```

## Environment Variables

- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB` - Default database name
- `YOUTUBE_API_KEY` - YouTube Data API key (for playlist fetching)
- `AWS_ACCESS_KEY_ID` - AWS credentials (for transcription)
- `AWS_SECRET_ACCESS_KEY` - AWS credentials (for transcription)

