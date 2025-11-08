#!/bin/bash

# IDE Performance Diagnostic Script
# Helps identify why IDE slows down after 1 hour of use
# Usage: bash LLM/scripts/diagnostics/ide_performance_check.sh

echo "🔍 IDE Performance Diagnostic Report"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Timestamp: $(date)"
echo ""

# Check 1: IDE Memory Usage
echo "┌─ CHECK 1: IDE Memory Usage"
echo "│"
echo "│  (Cursor/VS Code process memory)"
ps aux | grep -E "Cursor|code|cursor" | grep -v grep | while read line; do
    memory=$(echo "$line" | awk '{print $6}')
    memory_mb=$((memory / 1024))
    pid=$(echo "$line" | awk '{print $2}')
    command=$(echo "$line" | awk '{$1=$2=$3=$4=$5=$6=""; print $0}' | xargs)
    
    if [ "$memory_mb" -gt 300 ]; then
        echo "│  ⚠️  PID $pid: ${memory_mb} MB - $command"
    else
        echo "│  ✅ PID $pid: ${memory_mb} MB - $command"
    fi
done
echo "│"
echo "│  Expected: 300-500 MB (fresh), 1-2 GB (1 hour), >2 GB (problem)"
echo ""

# Check 2: Git Status Speed
echo "┌─ CHECK 2: Git Operations Performance"
echo "│"
echo "│  Measuring 'git status' execution time..."
echo "│"

start_time=$(date +%s%N)
git status > /dev/null 2>&1
end_time=$(date +%s%N)
elapsed=$((($end_time - $start_time) / 1000000))
elapsed_ms=$((elapsed / 1000))

echo "│  Git status took: ${elapsed_ms} ms"

if [ "$elapsed_ms" -lt 1000 ]; then
    echo "│  ✅ FAST (optimal)"
elif [ "$elapsed_ms" -lt 3000 ]; then
    echo "│  ⚠️  ACCEPTABLE"
else
    echo "│  ❌ SLOW (likely IDE culprit)"
fi

file_count=$(git ls-files | wc -l)
echo "│  Files tracked by Git: $file_count"
echo "│"
echo "│  Expected: <1s for this repo size"
echo ""

# Check 3: System Memory
echo "┌─ CHECK 3: System Memory Pressure"
echo "│"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    memory_info=$(vm_stat | grep "Pages free\|Pages active\|Pages wired" | head -3)
    echo "│  macOS Memory Stats:"
    echo "$memory_info" | while read line; do
        echo "│    $line"
    done
    
    # Check swap
    swap_info=$(sysctl vm.swapusage 2>/dev/null | head -1)
    if [[ "$swap_info" == *"used = "* ]]; then
        echo "│    Swap: $swap_info"
    fi
elif [[ "$OSTYPE" == "linux"* ]]; then
    # Linux
    free -h | tail -2 | while read line; do
        echo "│    $line"
    done
fi
echo "│"
echo "│  Watch for: High swap usage, memory >80% used"
echo ""

# Check 4: Large Files
echo "┌─ CHECK 4: Largest Files in Workspace"
echo "│"
echo "│  Top 5 largest files (may slow indexing):"
find . -type f \( -name "*.md" -o -name "*.py" \) -not -path "./documentation/archive/*" -not -path "./.git/*" -not -path "*/__pycache__/*" | while read f; do
    size=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null)
    echo "$size $f"
done | sort -rn | head -5 | while read size f; do
    size_kb=$((size / 1024))
    if [ "$size_kb" -gt 500 ]; then
        echo "│  ⚠️  ${f}: ${size_kb} KB (large, may impact indexing)"
    else
        echo "│  ✅ ${f}: ${size_kb} KB"
    fi
done
echo ""

# Check 5: .gitignore Optimization
echo "┌─ CHECK 5: .gitignore Optimization"
echo "│"
patterns_to_check=("__pycache__" ".pytest_cache" "*.pyc" "node_modules" ".DS_Store" "venv" ".venv")
echo "│  Checking if these patterns are in .gitignore:"
for pattern in "${patterns_to_check[@]}"; do
    if grep -q "$pattern" .gitignore 2>/dev/null; then
        echo "│  ✅ $pattern"
    else
        echo "│  ⚠️  $pattern (missing - add to .gitignore)"
    fi
done
echo "│"
echo "│  Total patterns in .gitignore: $(wc -l < .gitignore 2>/dev/null || echo "0")"
echo ""

# Check 6: Directory Tree Depth
echo "┌─ CHECK 6: Directory Structure"
echo "│"
dir_count=$(find . -type d -not -path "*/\.*" -not -path "*/__pycache__/*" | wc -l)
echo "│  Total directories: $dir_count"
deepest=$(find . -type d -not -path "*/\.*" | awk -F/ '{print NF}' | sort -n | tail -1)
echo "│  Deepest nesting level: $deepest"
echo "│"
echo "│  Expected: <1000 dirs, <10 nesting (for optimal performance)"
echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
echo "📊 DIAGNOSTIC SUMMARY"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next Steps:"
echo "1. If IDE memory > 2 GB:"
echo "   ✅ Use Fix 1: Restart IDE every hour"
echo "   ✅ Use Fix 2: Fresh chat windows"
echo ""
echo "2. If git status > 3s:"
echo "   ✅ Use Fix 3: Optimize .gitignore"
echo "   Run: git add .gitignore && git commit -m 'Optimize gitignore'"
echo ""
echo "3. If top 5 files > 500 KB each:"
echo "   ✅ Use Fix 5: Exclude from indexing"
echo "   Edit: .vscode/settings.json"
echo ""
echo "See: EXECUTION_ANALYSIS_IDE-PERFORMANCE-DEGRADATION.md for full guide"
echo ""


