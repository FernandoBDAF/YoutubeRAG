#!/bin/bash
#
# Run Full GraphRAG Pipeline with Optimized TPM Configuration
#
# This script runs all 4 GraphRAG stages with validated settings:
# - 300 workers for maximum parallelization
# - 950k TPM (95% of 1M limit)
# - 20k RPM (validated with your tier)
# - Dynamic batch sizing (600 chunks per batch)
#
# Expected time for 13,069 chunks: ~45 minutes total
# vs Sequential: 66.5 hours (90x speedup!)
#

echo "================================================================================"
echo "GraphRAG Full Pipeline - Optimized Configuration"
echo "================================================================================"
echo ""
echo "Configuration:"
echo "  - Chunks: 13,069"
echo "  - Workers: 300"
echo "  - TPM: 950,000"
echo "  - RPM: 20,000"
echo "  - Batch size: 600 (dynamic)"
echo "  - Database: validation_db"
echo ""
echo "Expected time: ~45 minutes"
echo "================================================================================"
echo ""

# All optimizations are now default:
# - TPM tracking: enabled
# - Concurrency: 300 workers  
# - RPM: 20,000
# - Batch size: 600 (dynamic)
# - Log file: auto-generated with timestamp

python -m app.cli.graphrag \
  --max 13069 \
  --read-db-name validation_db \
  --write-db-name validation_db \
  --verbose
# Note: --concurrency defaults to 300, no need to specify!

echo ""
echo "================================================================================"
echo "Pipeline Complete!"
echo "================================================================================"
echo ""
echo "Check results:"
echo "  - Log: logs/graphrag_full_13k_optimized.log"
echo "  - Database: validation_db"
echo ""
echo "Analyze results:"
echo "  python -c \"
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv('MONGODB_URI'))
db = client['validation_db']

print('Results:')
print(f'  Entities: {db.entities.count_documents({}):,}')
print(f'  Relations: {db.relations.count_documents({}):,}')
print(f'  Communities: {db.communities.count_documents({}):,}' if 'communities' in db.list_collection_names() else '  Communities: 0')
print(f'  Processed chunks: {db.video_chunks.count_documents({\"graphrag_construction.status\": \"completed\"}):,}')
\""
echo ""

