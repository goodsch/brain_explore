#!/bin/bash
# Check extraction progress

echo "=== Running Processes ==="
ps aux | grep "python scripts/extract_single.py" | grep -v grep | wc -l
echo "extraction processes"
echo

echo "=== Graph Stats ==="
python scripts/extract_entities.py --stats

echo
echo "=== Recent Log Activity ==="
tail -1 /tmp/extract_*.log 2>/dev/null | head -20
