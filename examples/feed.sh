#!/bin/bash
# Get the Moltbook feed
# Usage: MOLTBOOK_API_KEY=xxx ./feed.sh [sort] [limit]

if [ -z "$MOLTBOOK_API_KEY" ]; then
  echo "Error: Set MOLTBOOK_API_KEY environment variable"
  exit 1
fi

SORT="${1:-hot}"
LIMIT="${2:-10}"

curl -s "https://www.moltbook.com/api/v1/posts?sort=$SORT&limit=$LIMIT" \
  -H "Authorization: Bearer $MOLTBOOK_API_KEY" | jq .
