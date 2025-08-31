#!/bin/bash

# Test script for workflow persistence functionality
echo "===== Testing Workflow Persistence Functionality ====="

# Set colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Running backend tests${NC}"
cd backend
echo "Running Python unittest for workflow persistence..."
python -m unittest tests/test_workflow_persistence.py
BACKEND_RESULT=$?

if [ $BACKEND_RESULT -eq 0 ]; then
    echo -e "${GREEN}Backend tests passed!${NC}"
else
    echo -e "${RED}Backend tests failed!${NC}"
fi

echo -e "\n${YELLOW}Step 2: Running frontend tests${NC}"
cd ../frontend
echo "Running Jest tests for workflow persistence components..."
npm test -- --testPathPattern=tests/workflow_persistence.test.tsx
FRONTEND_RESULT=$?

if [ $FRONTEND_RESULT -eq 0 ]; then
    echo -e "${GREEN}Frontend tests passed!${NC}"
else
    echo -e "${RED}Frontend tests failed!${NC}"
fi

# Return to project root
cd ..

# Check overall result
if [ $BACKEND_RESULT -eq 0 ] && [ $FRONTEND_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}✅ All workflow persistence tests passed!${NC}"
    echo "The workflow persistence functionality is working correctly."
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed!${NC}"
    echo "Please check the test output above for details."
    exit 1
fi
