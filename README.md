# Jiagu Unpacker

A Python tool to unpack and extract original DEX files from Android APKs protected by the Jiagu (加固) packer. This tool automatically handles both standard and password-protected ZIP archives.

## Features

- **Automatic DEX Extraction**: Extracts original `classes.dex` files from Jiagu-packed APKs
- **AES & XOR Decryption**: Handles both AES-CBC and XOR encryption layers
- **ZIP Password Bypass**: Automatically detects and removes fake ZIP encryption flags
- **Multiple DEX Support**: Extracts all DEX files (classes.dex, classes2.dex, etc.)
- **Application Name Recovery**: Retrieves the original Application class name
- **Shell DEX Isolation**: Separates the packer's shell DEX from original code

## What is Jiagu?

Jiagu (加固) is a popular Android application packer used to protect APKs from reverse engineering. It:
- Encrypts the original DEX files using AES-CBC and XOR
- Wraps the app with a protective shell DEX
- Sometimes uses fake ZIP encryption flags to prevent standard extraction

**This unpacker is designed for APKs packed with the [Jiagu packer](https://github.com/Frezrik/Jiagu).**

This tool reverses the packing process to recover the original application code.

## Installation

### Requirements

- Python 3.6+
- `pycryptodome` library

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/Jiagu-unpacker.git
cd Jiagu-unpacker

# Install dependencies
pip3 install pycryptodome
```

## Usage

### Basic Usage

```bash
python3 jiagu_unpacker.py -apk packed.apk
```

This will create an `unpacked` directory containing:
- `classes.dex` - Original DEX file(s)
- `classes2.dex`, `classes3.dex`, etc. - Additional DEX files (if multidex)
- `shell.dex` - The Jiagu packer's shell DEX
- `original_application.txt` - Original Application class name

### Custom Output Directory

```bash
python3 jiagu_unpacker.py -apk packed.apk -out extracted
```

### Handling Password-Protected ZIPs

The tool **automatically detects** when an APK has fake ZIP encryption flags and applies the decryption method. No manual intervention needed!

```bash
# This works for both regular and "password-protected" APKs
python3 jiagu_unpacker.py -apk protected.apk
```

Output example:
```
[*] Extracting classes.dex from protected.apk...
[!] ZIP encryption detected: File is encrypted
[*] Attempting to extract using ZIP decryption method...
[+] Successfully extracted classes.dex using decryption, size: 1234567 bytes
```

## How It Works

### Unpacking Process

1. **DEX Extraction**:
   - Tries standard ZIP extraction first
   - If password error occurs, automatically uses `zip_decrypt.py` to remove fake encryption flags

2. **Structure Parsing**:
   - Reads shell DEX length from last 4 bytes
   - Separates shell DEX from encrypted payload

3. **AES Decryption**:
   - First 512 bytes are AES-CBC encrypted with hardcoded key
   - Uses PKCS5 padding removal

4. **Application Name Recovery**:
   - First byte = length of original Application class name
   - Extracts UTF-8 encoded name

5. **DEX File Extraction**:
   - Each DEX has 4-byte size header (big-endian)
   - First DEX (classes.dex) is unmodified
   - Additional DEX files have XOR encryption on first 112 bytes

6. **XOR Decryption** (for classes2.dex and beyond):
   - XOR key: `0x66`
   - Applied to first 112 bytes

### Encryption Constants

```python
AES_KEY = b"bajk3b4j3bvuoa3h"
AES_IV = b"mers46ha35ga23hn"
XOR_KEY = 0x66
XOR_LENGTH = 112
```

### ZIP Decryption Method

The `zip_decrypt.py` module works by:
1. Scanning for Central Directory File Header (CDFH) signatures (`PK\x01\x02`)
2. Clearing the encryption bit (bit 0) in the general purpose bit flag
3. Creating a cleaned temporary file that can be extracted normally

## File Structure

```
Jiagu-unpacker/
├── jiagu_unpacker.py      # Main unpacker script
├── zip_decrypt.py         # ZIP encryption flag removal
├── README.md              # English documentation
├── README_FA.md           # Persian documentation
├── requirements.txt       # Python dependencies
├── LICENSE                # MIT License
└── examples/              # Example usage scripts
    └── batch_unpack.sh    # Batch processing script
```

## Output Files

After unpacking, you'll get:

- **`classes.dex`**: Original primary DEX file
- **`classes2.dex`, `classes3.dex`, ...**: Additional DEX files (multidex apps)
- **`shell.dex`**: Jiagu packer's shell DEX (can be discarded)
- **`original_application.txt`**: Original Application class name for AndroidManifest.xml

## Rebuilding the Original APK

To reconstruct a working APK:

1. **Extract the packed APK**:
   ```bash
   apktool d packed.apk -o unpacked_apk
   ```

2. **Replace DEX files**:
   ```bash
   cp unpacked/classes*.dex unpacked_apk/
   ```

3. **Restore Application name**:
   Edit `AndroidManifest.xml`:
   ```xml
   <application android:name="com.example.OriginalApplication" ...>
   ```
   Use the name from `original_application.txt`

4. **Remove Jiagu libraries**:
   ```bash
   rm -rf unpacked_apk/assets/libjiagu*.so
   rm -rf unpacked_apk/lib/*/libjiagu*.so
   ```

5. **Repack and sign**:
   ```bash
   apktool b unpacked_apk -o rebuilt.apk
   jarsigner -keystore my.keystore rebuilt.apk mykey
   zipalign -v 4 rebuilt.apk final.apk
   ```

## Advanced Usage

### Batch Processing

```bash
#!/bin/bash
# Process all APKs in a directory
for apk in *.apk; do
    echo "Processing: $apk"
    python3 jiagu_unpacker.py -apk "$apk" -out "extracted_$(basename "$apk" .apk)"
done
```

### Integration as a Module

```python
from jiagu_unpacker import JiaguUnpacker

# Create unpacker instance
unpacker = JiaguUnpacker("packed.apk", "output_dir")

# Run unpacking
success = unpacker.unpack()

if success:
    print("Unpacking completed successfully!")
```

## Troubleshooting

### "pycryptodome is required"
```bash
pip3 install pycryptodome
```

### "classes.dex not found in APK"
- The APK may not be packed with Jiagu
- Try extracting manually with `unzip` or `apktool`

### "Invalid DEX magic"
- The unpacking may have failed partially
- Check if the APK is using a different Jiagu version
- Open an issue with the APK details (if shareable)

### "ZIP encryption detected" but still fails
- The APK may have real password protection (not fake flags)
- Try using `zip_decrypt.py` standalone:
  ```bash
  python3 zip_decrypt.py packed.apk
  ```

## Limitations

- Only tested with Jiagu packer versions using these specific encryption keys
- May not work with newer Jiagu versions that use different encryption schemes
- Requires the APK to be a valid ZIP file structure

## Security & Legal Notice

**This tool is for educational and security research purposes only.**

- Only use on applications you own or have permission to analyze
- Respect intellectual property rights and local laws
- Do not use for piracy or malicious purposes
- The authors are not responsible for misuse

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

- [Android DEX Format](https://source.android.com/docs/core/runtime/dex-format)
- [ZIP File Format Specification](https://pkware.cachefly.net/webdocs/casestudies/APPNOTE.TXT)
- [Jiagu Packer Analysis](https://github.com/topics/jiagu)

## Changelog

### Version 1.0.0 (2024)
- Initial release
- AES-CBC and XOR decryption support
- Automatic ZIP password bypass
- Multiple DEX file extraction
- Application name recovery

## Author

Created for security researchers and Android developers who need to analyze packed applications.

## Acknowledgments

- Thanks to the Android security research community
- Inspired by various Jiagu unpacking tools and research papers

---

**Star this repo if you find it useful!** ⭐
