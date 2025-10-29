#!/usr/bin/env python3
"""
Jiagu Unpacker - Python Version
Extracts original DEX files from APKs packed with Jiagu packer

Usage: python3 jiagu_unpacker.py -apk packed.apk -out output_dir
"""

import sys
import struct
import zipfile
import os
from pathlib import Path

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad
except ImportError:
    print("[-] Error: pycryptodome is required")
    print("    Install with: pip3 install pycryptodome")
    sys.exit(1)


class JiaguUnpacker:
    """Unpacker for Jiagu-protected Android applications"""

    # Encryption constants
    AES_KEY = b"bajk3b4j3bvuoa3h"
    AES_IV = b"mers46ha35ga23hn"
    AES_ENCRYPTED_LENGTH = 512
    XOR_KEY = 0x66
    XOR_LENGTH = 112

    def __init__(self, apk_path, output_dir="unpacked", use_zip_decrypt=False):
        self.apk_path = apk_path
        self.output_dir = output_dir
        self.use_zip_decrypt = use_zip_decrypt
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def extract_classes_dex(self):
        """Extract classes.dex from APK with optional ZIP decryption"""
        print(f"[*] Extracting classes.dex from {self.apk_path}...")

        try:
            # Try normal extraction first
            with zipfile.ZipFile(self.apk_path, 'r') as zf:
                if 'classes.dex' not in zf.namelist():
                    print("[-] classes.dex not found in APK")
                    return None

                dex_data = zf.read('classes.dex')
                print(f"[+] Extracted classes.dex, size: {len(dex_data)} bytes")
                return dex_data

        except RuntimeError as e:
            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                print(f"[!] ZIP encryption detected: {e}")
                print("[*] Attempting to extract using ZIP decryption method...")

                # Import and use zip_decrypt module
                try:
                    from zip_decrypt import get_dex_data
                    dex_data = get_dex_data(self.apk_path)
                    if dex_data and len(dex_data) > 0:
                        print(f"[+] Successfully extracted classes.dex using decryption, size: {len(dex_data)} bytes")
                        return dex_data
                    else:
                        print("[-] ZIP decryption failed to extract DEX data")
                        return None
                except ImportError:
                    print("[-] zip_decrypt module not found. Please ensure zip_decrypt.py is in the same directory.")
                    return None
                except Exception as decrypt_error:
                    print(f"[-] ZIP decryption error: {decrypt_error}")
                    return None
            else:
                print(f"[-] Error extracting DEX: {e}")
                return None

        except Exception as e:
            print(f"[-] Error extracting DEX: {e}")
            return None

    def bytes_to_int(self, data, offset):
        """Convert 4 bytes to int (big-endian)"""
        return struct.unpack('>I', data[offset:offset+4])[0]

    def aes_decrypt(self, encrypted_data):
        """Decrypt data using AES-CBC"""
        cipher = AES.new(self.AES_KEY, AES.MODE_CBC, self.AES_IV)
        decrypted = cipher.decrypt(encrypted_data)
        # Remove PKCS5 padding
        return unpad(decrypted, AES.block_size)

    def xor_decrypt(self, data):
        """Apply XOR decryption to first 112 bytes"""
        result = bytearray(data)
        for i in range(min(self.XOR_LENGTH, len(result))):
            result[i] ^= self.XOR_KEY
        return bytes(result)

    def verify_dex_magic(self, dex_data):
        """Check if data has valid DEX magic bytes"""
        return dex_data[:4] == b'dex\n'

    def unpack(self):
        """Main unpacking routine"""
        print(f"[*] Starting Jiagu unpacker")
        print(f"[*] APK: {self.apk_path}")
        print(f"[*] Output: {self.output_dir}")
        print()

        # Step 1: Extract classes.dex
        packed_dex = self.extract_classes_dex()
        if not packed_dex:
            return False

        # Step 2: Parse structure
        print("[*] Parsing packed DEX structure...")

        # Read shell DEX length from last 4 bytes
        shell_dex_length = self.bytes_to_int(packed_dex, len(packed_dex) - 4)
        print(f"[+] Shell DEX length: {shell_dex_length} bytes")

        # Extract shell DEX
        shell_dex = packed_dex[:shell_dex_length]
        shell_path = os.path.join(self.output_dir, "shell.dex")
        with open(shell_path, 'wb') as f:
            f.write(shell_dex)
        print(f"[+] Saved shell DEX to: {shell_path}")

        # Extract encrypted data
        encrypted_data = packed_dex[shell_dex_length:-4]
        print(f"[+] Encrypted data length: {len(encrypted_data)} bytes")

        # Step 3: AES decryption
        print("[*] Decrypting AES-encrypted section...")

        aes_encrypted_size = self.AES_ENCRYPTED_LENGTH + 16  # +16 for padding
        if len(encrypted_data) < aes_encrypted_size:
            print("[-] Encrypted data too small for AES decryption")
            return False

        aes_encrypted_part = encrypted_data[:aes_encrypted_size]
        aes_decrypted = self.aes_decrypt(aes_encrypted_part)
        print(f"[+] AES decryption complete, size: {len(aes_decrypted)} bytes")

        # Reconstruct full decrypted data
        decrypted_data = aes_decrypted + encrypted_data[aes_encrypted_size:]

        # Step 4: Parse application name
        app_name_length = decrypted_data[0]
        app_name = decrypted_data[1:1+app_name_length].decode('utf-8')
        print(f"[+] Original Application name: {app_name}")

        # Save application name
        app_name_path = os.path.join(self.output_dir, "original_application.txt")
        with open(app_name_path, 'w') as f:
            f.write(app_name)

        # Step 5: Extract DEX files
        print("[*] Extracting original DEX files...")

        dex_files = []
        index = 1 + app_name_length
        dex_count = 0

        while index + 4 <= len(decrypted_data):
            # Read DEX size
            dex_size = self.bytes_to_int(decrypted_data, index)
            index += 4

            if index + dex_size > len(decrypted_data):
                print(f"[-] Warning: DEX size exceeds remaining data, stopping")
                break

            # Extract DEX data
            dex_data = bytearray(decrypted_data[index:index+dex_size])

            # Apply XOR decryption for DEX2+
            if dex_count > 0:
                dex_data = self.xor_decrypt(dex_data)
                print(f"[+] Applied XOR decryption to DEX #{dex_count + 1}")

            # Verify DEX magic
            if self.verify_dex_magic(dex_data):
                print(f"[+] Valid DEX file detected (#{dex_count + 1}), size: {dex_size} bytes")
            else:
                magic = dex_data[:4]
                print(f"[-] Warning: DEX #{dex_count + 1} has invalid magic: {magic}")

            dex_files.append(bytes(dex_data))
            index += dex_size
            dex_count += 1

        # Step 6: Save DEX files
        print(f"[*] Saving {len(dex_files)} DEX file(s)...")

        for i, dex_data in enumerate(dex_files):
            if i == 0:
                dex_filename = "classes.dex"
            else:
                dex_filename = f"classes{i+1}.dex"

            dex_path = os.path.join(self.output_dir, dex_filename)
            with open(dex_path, 'wb') as f:
                f.write(dex_data)
            print(f"[+] Saved: {dex_path}")

        # Summary
        print()
        print("[*] Unpacking complete!")
        print("[*] Summary:")
        print(f"    - Original Application: {app_name}")
        print(f"    - Shell DEX: {shell_path}")
        print(f"    - Extracted DEX files: {len(dex_files)}")
        print(f"    - Output directory: {self.output_dir}")
        print()
        print("[*] To rebuild the original APK:")
        print("    1. Extract the packed APK completely")
        print("    2. Replace classes.dex (and classes2.dex, etc.) with extracted files")
        print(f"    3. Modify AndroidManifest.xml to restore original Application: {app_name}")
        print("    4. Remove assets/libjiagu*.so files")
        print("    5. Repack and sign the APK")

        return True


def main():
    """Command-line interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Jiagu Unpacker - Extract original DEX files from packed APK',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 jiagu_unpacker.py -apk packed.apk
  python3 jiagu_unpacker.py -apk app.apk -out extracted

For more information, see README.md
        '''
    )

    parser.add_argument('-apk', required=True, help='Path to packed APK file')
    parser.add_argument('-out', default='unpacked', help='Output directory (default: unpacked)')

    args = parser.parse_args()

    # Check if APK exists
    if not os.path.exists(args.apk):
        print(f"[-] Error: APK file not found: {args.apk}")
        sys.exit(1)

    # Run unpacker
    unpacker = JiaguUnpacker(args.apk, args.out)
    success = unpacker.unpack()

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
