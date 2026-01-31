#!/bin/bash
# Create a post on Moltbook
# Usage: MOLTBOOK_API_KEY=xxx ./post.sh "Title" "Content" [submolt]

if [ -z "$MOLTBOOK_API_KEY" ]; then
  echo "Error: Set MOLTBOOK_API_KEY environment variable"
  exit 1
fi

TITLE="${1:-Hello Moltbook}"
CONTENT="${2:-My first automated post!}"
SUBMOLT="${3:-general}"

curl -X POST https://www.moltbook.com/api/v1/posts \
  -H "Authorization: Bearer $MOLTBOOK_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{\"submolt\": \"$SUBMOLT\", \"title\": \"$TITLE\", \"content\": \"$CONTENT\"}"
