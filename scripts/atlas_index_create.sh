#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/atlas_index_create.sh <PROJECT_ID> <CLUSTER_NAME>
PROJECT_ID=${1:-}
CLUSTER_NAME=${2:-}

if [[ -z "$PROJECT_ID" || -z "$CLUSTER_NAME" ]]; then
  echo "Usage: $0 <PROJECT_ID> <CLUSTER_NAME>" >&2
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA_JSON="${SCRIPT_DIR%/scripts}/mongodb_schema.json"

if ! command -v atlas >/dev/null 2>&1; then
  echo "Atlas CLI not found. Install via: brew tap mongodb/brew && brew install mongodb-atlas-cli" >&2
  exit 1
fi

echo "Creating vector index 'embedding_index' on video_chunks..."
atlas clusters search indexes create \
  --projectId "$PROJECT_ID" \
  --clusterName "$CLUSTER_NAME" \
  --db mongo_hack \
  --collection video_chunks \
  --indexName embedding_index \
  --type vectorSearch \
  --definition '{
    "mappings": {
      "dynamic": true,
      "fields": {
        "embedding": {
          "type": "knnVector",
          "dimensions": 1024,
          "similarity": "cosine"
        }
      }
    }
  }'

echo "Done. Check status with: atlas clusters search indexes list --projectId $PROJECT_ID --clusterName $CLUSTER_NAME --db mongo_hack --collection video_chunks"


