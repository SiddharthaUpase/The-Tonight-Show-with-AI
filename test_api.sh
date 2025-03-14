#!/bin/bash

# Base URL
BASE_URL="http://localhost"

# Test the GET endpoints
echo "Testing GET /api/health..."
curl -i -X GET "${BASE_URL}/api/health"
echo -e "\n\n"

echo "Testing GET /api/say-hi..."
curl -i -X GET "${BASE_URL}/api/say-hi"
echo -e "\n\n"

echo "Testing GET /api/server-diagnostic-get..."
curl -i -X GET "${BASE_URL}/api/server-diagnostic-get"
echo -e "\n\n"

echo "Testing GET /api/method-test..."
curl -i -X GET "${BASE_URL}/api/method-test"
echo -e "\n\n"

# Test the POST endpoints
echo "Testing POST /api/method-test..."
curl -i -X POST \
  -H "Content-Type: application/json" \
  -d '{}' \
  "${BASE_URL}/api/method-test"
echo -e "\n\n"

echo "Testing POST /api/generate-roast..."
curl -i -X POST \
  -H "Content-Type: application/json" \
  -d '{"linkedin_url": "https://www.linkedin.com/in/example"}' \
  "${BASE_URL}/api/generate-roast"
echo -e "\n\n"

# Test OPTIONS endpoints
echo "Testing OPTIONS /api/method-test..."
curl -i -X OPTIONS "${BASE_URL}/api/method-test"
echo -e "\n\n"

echo "Testing OPTIONS /api/generate-roast..."
curl -i -X OPTIONS "${BASE_URL}/api/generate-roast"
echo -e "\n\n" 