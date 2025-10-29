"""
ZIP Decryption Utility
Removes fake encryption flags from APK/ZIP files to bypass password protection

This module is used automatically by jiagu_unpacker.py when it encounters
password-protected ZIP files.
"""

import sys
import logging
import os
import tempfile
import zipfile
from io import BytesIO

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("ZIP_DECRYPT")

# Central Directory File Header signature
CDFH_SIGNATURE = bytes([0x50, 0x4B, 0x01, 0x02])  # PK\x01\x02


def read_file_fully(file_path: str) -> bytes:
    """
    Read an entire file into a byte array.

    Args:
        file_path: Path to the file to read

    Returns:
        Bytes content of the file
    """
    with open(file_path, "rb") as f:
        return f.read()


def remove_encryption_flag(file_path: str) -> str:
    """
    Remove encryption flags from ZIP file entries by clearing the encryption bit
    in the Central Directory File Header.

    Args:
        file_path: Path to the APK/ZIP file

    Returns:
        Path to the cleaned temporary file
    """
    # Read the entire file
    data = bytearray(read_file_fully(file_path))

    # Create a temporary file
    fd, temp_file = tempfile.mkstemp(suffix=".apk", prefix="cleaned_apk_")

    try:
        # Scan for CDFH signatures and clear encryption flag
        for i in range(len(data) - 3):
            if (data[i] == CDFH_SIGNATURE[0] and
                data[i + 1] == CDFH_SIGNATURE[1] and
                data[i + 2] == CDFH_SIGNATURE[2] and
                data[i + 3] == CDFH_SIGNATURE[3]):

                # Read the general purpose bit flag (at offset +8 from CDFH signature)
                v1 = (data[i + 8] & 0xFF) | ((data[i + 9] & 0xFF) << 8)

                # Clear the encryption bit (bit 0)
                data[i + 8] = v1 & 0xFE
                data[i + 9] = ((v1 & 0xFFFFFFFE) >> 8) & 0xFF

        # Write the modified data to the temporary file
        os.write(fd, bytes(data))
    finally:
        os.close(fd)

    return temp_file


def get_dex_data(file_path: str) -> bytes:
    """
    Extract DEX data from an APK file by removing encryption flags and
    reading the classes.dex entry.

    Args:
        file_path: Path to the APK file

    Returns:
        Byte array containing the DEX file data
    """
    output = BytesIO()
    cleaned_file = None

    try:
        # Remove encryption flags from the APK
        cleaned_file = remove_encryption_flag(file_path)

        # Open the cleaned APK as a ZIP file
        with zipfile.ZipFile(cleaned_file, "r") as zip_file:
            # Look for classes.dex entry
            for entry_name in zip_file.namelist():
                if entry_name == "classes.dex":
                    # Read the DEX file in chunks
                    with zip_file.open(entry_name) as dex_stream:
                        chunk_size = 0x2000  # 8192 bytes
                        while True:
                            chunk = dex_stream.read(chunk_size)
                            if not chunk:
                                break
                            output.write(chunk)
                    break

        return output.getvalue()

    except IOError as e:
        logger.error(f"getDexData error: {e}")
        return output.getvalue()

    finally:
        # Clean up the temporary file
        if cleaned_file and os.path.exists(cleaned_file):
            try:
                os.remove(cleaned_file)
            except OSError as e:
                logger.error(f"Error removing temporary file: {e}")


# Standalone usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 zip_decrypt.py <apk_file>")
        sys.exit(1)

    apk_path = sys.argv[1]
    if not os.path.exists(apk_path):
        print(f"Error: File not found: {apk_path}")
        sys.exit(1)

    print(f"[*] Removing encryption flags from: {apk_path}")
    cleaned_file = remove_encryption_flag(apk_path)
    print(f"[+] Cleaned file created: {cleaned_file}")
    print("[*] Note: Temporary file will be cleaned up automatically")
