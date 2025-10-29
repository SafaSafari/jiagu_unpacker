#!/usr/bin/env python3
"""
Example: Using Jiagu Unpacker as a Python module
"""

import sys
import os

# Add parent directory to path to import jiagu_unpacker
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jiagu_unpacker import JiaguUnpacker


def example_basic_usage():
    """Basic usage example"""
    print("=== Example 1: Basic Usage ===\n")

    apk_path = "packed.apk"
    output_dir = "unpacked_output"

    # Create unpacker instance
    unpacker = JiaguUnpacker(apk_path, output_dir)

    # Run unpacking
    success = unpacker.unpack()

    if success:
        print("\n✓ Unpacking completed successfully!")
        print(f"Check output directory: {output_dir}")
    else:
        print("\n✗ Unpacking failed!")


def example_batch_processing():
    """Batch processing example"""
    print("\n=== Example 2: Batch Processing ===\n")

    apk_files = ["app1.apk", "app2.apk", "app3.apk"]

    for apk_file in apk_files:
        if not os.path.exists(apk_file):
            print(f"Skipping {apk_file} (not found)")
            continue

        output_dir = f"unpacked_{os.path.basename(apk_file).replace('.apk', '')}"

        print(f"\nProcessing: {apk_file}")
        unpacker = JiaguUnpacker(apk_file, output_dir)

        if unpacker.unpack():
            print(f"✓ {apk_file} - Success")
        else:
            print(f"✗ {apk_file} - Failed")


def example_extract_only():
    """Example: Extract DEX without full unpacking"""
    print("\n=== Example 3: Extract DEX Only ===\n")

    apk_path = "packed.apk"
    unpacker = JiaguUnpacker(apk_path, "temp_output")

    # Extract classes.dex
    dex_data = unpacker.extract_classes_dex()

    if dex_data:
        print(f"✓ Extracted DEX, size: {len(dex_data)} bytes")

        # Save to file
        with open("extracted_classes.dex", "wb") as f:
            f.write(dex_data)
        print("✓ Saved to: extracted_classes.dex")
    else:
        print("✗ Failed to extract DEX")


def example_error_handling():
    """Example with error handling"""
    print("\n=== Example 4: Error Handling ===\n")

    apk_path = "packed.apk"
    output_dir = "unpacked"

    try:
        # Check if APK exists
        if not os.path.exists(apk_path):
            raise FileNotFoundError(f"APK not found: {apk_path}")

        # Create unpacker
        unpacker = JiaguUnpacker(apk_path, output_dir)

        # Run unpacking
        if not unpacker.unpack():
            raise Exception("Unpacking failed")

        print("✓ Unpacking successful!")

    except FileNotFoundError as e:
        print(f"✗ Error: {e}")
    except Exception as e:
        print(f"✗ Unpacking error: {e}")


if __name__ == "__main__":
    print("Jiagu Unpacker - Module Usage Examples")
    print("=" * 50)

    # Run examples
    # Uncomment the example you want to run:

    # example_basic_usage()
    # example_batch_processing()
    # example_extract_only()
    # example_error_handling()

    print("\nTo run an example, uncomment it in the __main__ section")
