#!/bin/bash
# Test script to verify unpacker works correctly

echo "=========================================="
echo "Jiagu Unpacker - Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Test counter
passed=0
failed=0

# Test 1: Check dependencies
echo "[TEST 1] Checking dependencies..."
if python3 -c "from Crypto.Cipher import AES" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}: pycryptodome installed"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}: pycryptodome not installed"
    failed=$((failed + 1))
fi
echo ""

# Test 2: Check if scripts are executable
echo "[TEST 2] Checking file permissions..."
if [ -x "jiagu_unpacker.py" ]; then
    echo -e "${GREEN}✓ PASS${NC}: jiagu_unpacker.py is executable"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}: jiagu_unpacker.py is not executable"
    failed=$((failed + 1))
fi
echo ""

# Test 3: Check help output
echo "[TEST 3] Testing help command..."
if python3 jiagu_unpacker.py -h > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}: Help command works"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}: Help command failed"
    failed=$((failed + 1))
fi
echo ""

# Test 4: Module import
echo "[TEST 4] Testing module import..."
if python3 -c "from jiagu_unpacker import JiaguUnpacker" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}: Module can be imported"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}: Module import failed"
    failed=$((failed + 1))
fi
echo ""

# Test 5: ZIP decrypt module
echo "[TEST 5] Testing zip_decrypt module..."
if python3 -c "from zip_decrypt import remove_encryption_flag, get_dex_data" 2>/dev/null; then
    echo -e "${GREEN}✓ PASS${NC}: zip_decrypt module works"
    passed=$((passed + 1))
else
    echo -e "${RED}✗ FAIL${NC}: zip_decrypt module failed"
    failed=$((failed + 1))
fi
echo ""

# Summary
echo "=========================================="
echo "Test Results"
echo "=========================================="
echo "Total: $((passed + failed))"
echo -e "${GREEN}Passed: $passed${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo ""

if [ $failed -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed. Please check above.${NC}"
    exit 1
fi
