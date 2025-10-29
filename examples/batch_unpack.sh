#!/bin/bash
# Batch Unpacker Script
# Usage: ./batch_unpack.sh [directory_with_apks]

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default directory is current directory
APK_DIR="${1:-.}"

# Counter for statistics
total=0
success=0
failed=0

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Jiagu Unpacker - Batch Processing${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Processing APKs in: $APK_DIR"
echo ""

# Check if directory exists
if [ ! -d "$APK_DIR" ]; then
    echo -e "${RED}Error: Directory not found: $APK_DIR${NC}"
    exit 1
fi

# Process each APK file
for apk in "$APK_DIR"/*.apk; do
    # Check if any APK files exist
    if [ ! -f "$apk" ]; then
        echo -e "${YELLOW}No APK files found in $APK_DIR${NC}"
        exit 0
    fi

    total=$((total + 1))
    apk_name=$(basename "$apk")
    output_dir="extracted_${apk_name%.apk}"

    echo -e "${YELLOW}[$total] Processing: $apk_name${NC}"

    # Run unpacker
    if python3 jiagu_unpacker.py -apk "$apk" -out "$output_dir" 2>&1 | grep -q "Unpacking complete"; then
        echo -e "${GREEN}    ✓ Success: $apk_name${NC}"
        success=$((success + 1))
    else
        echo -e "${RED}    ✗ Failed: $apk_name${NC}"
        failed=$((failed + 1))
    fi

    echo ""
done

# Print summary
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Summary${NC}"
echo -e "${GREEN}========================================${NC}"
echo "Total APKs processed: $total"
echo -e "${GREEN}Successful: $success${NC}"
echo -e "${RED}Failed: $failed${NC}"
echo ""

exit 0
