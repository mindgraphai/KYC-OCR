#!/usr/bin/env bash

API_KEY=f47c1e91-3b6a-4e25-b364-c5cc51f0e799  # <-- Replace with your actual API key

for IMG in 222599-1744115572777.jpeg 237502-1744115450544.jpeg 237631-1744115361089.jpg; do
  echo "Uploading $IMG..."
  TASK_ID=$(curl -s -X POST "http://0.0.0.0:8000/read_text" \
    -H "accept: application/json" \
    -H "api_key: $API_KEY" \
    -F "image=@$IMG" | jq -r '.id')

  echo "Task ID: $TASK_ID"

  # Poll for result
  while : ; do
    STATUS=$(curl -s -X GET "http://0.0.0.0:8000/id?task_id=$TASK_ID" \
      -H "accept: application/json" \
      -H "api_key: $API_KEY")
    echo "$STATUS" | jq .
    if [[ "$STATUS" == *'"status":"Processing"'* ]]; then
      sleep 2
    else
      break
    fi
  done
  echo "-----------------------------------"
done