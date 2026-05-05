#!/bin/bash

echo "=== Lang-Assist API Testing ==="
echo ""

echo "Waiting for services to be ready..."
sleep 5

echo ""
echo "=== Test 1: Successful request with correct key ==="
curl -s -w "\nHTTP_CODE:%{http_code}\n" -X POST http://localhost:8000/api/v1/simplify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: test-key-123" \
  -d '{"text":"我酷爱钻研艰深的语言学理论","hsk_level":4}'

echo ""
echo "=== Test 2: Request without API key ==="
curl -s -w "\nHTTP_CODE:%{http_code}\n" -X POST http://localhost:8000/api/v1/simplify \
  -H "Content-Type: application/json" \
  -d '{"text":"任何文本","hsk_level":1}'

echo ""
echo "=== Test 3: Request with invalid API key ==="
curl -s -w "\nHTTP_CODE:%{http_code}\n" -X POST http://localhost:8000/api/v1/simplify \
  -H "Content-Type: application/json" \
  -H "X-API-Key: wrong-key" \
  -d '{"text":"任何文本","hsk_level":1}'

echo ""
echo "=== Test 4: Rate limiting (6 requests) ==="
for i in {1..6}; do
  echo "Request $i:"
  curl -s -w "\nHTTP_CODE:%{http_code}\n" -X POST http://localhost:8000/api/v1/simplify \
    -H "Content-Type: application/json" \
    -H "X-API-Key: test-key-123" \
    -d '{"text":"我","hsk_level":2}'
  sleep 1
done

echo ""
echo "=== Test 5: Healthcheck ==="
curl -s -w "\nHTTP_CODE:%{http_code}\n" http://localhost:8000/health

echo ""
echo "=== Tests completed ==="