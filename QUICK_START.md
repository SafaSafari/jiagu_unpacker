# Quick Start Guide

Get started with Jiagu Unpacker in 60 seconds!

## Installation

```bash
git clone https://github.com/yourusername/Jiagu-unpacker.git
cd Jiagu-unpacker
pip3 install pycryptodome
```

## Basic Usage

```bash
# Unpack a Jiagu-protected APK
python3 jiagu_unpacker.py -apk your_app.apk

# Output will be in 'unpacked' directory
ls unpacked/
# classes.dex
# classes2.dex
# shell.dex
# original_application.txt
```

## Common Scenarios

### 1. Password-Protected APK
```bash
# No special flags needed - auto-detected!
python3 jiagu_unpacker.py -apk protected.apk
```

### 2. Custom Output Directory
```bash
python3 jiagu_unpacker.py -apk app.apk -out my_output
```

### 3. Batch Processing
```bash
cd examples
./batch_unpack.sh /path/to/apk/directory
```

## What Gets Extracted?

- **classes.dex** - Original app code
- **classes2.dex, classes3.dex, ...** - Additional DEX files
- **shell.dex** - Jiagu packer shell (can ignore)
- **original_application.txt** - App class name for AndroidManifest.xml

## Rebuilding APK

```bash
# 1. Extract original APK
apktool d packed.apk -o unpacked_apk

# 2. Replace DEX files
cp unpacked/classes*.dex unpacked_apk/

# 3. Edit AndroidManifest.xml - restore Application name from original_application.txt

# 4. Remove Jiagu files
rm -rf unpacked_apk/assets/libjiagu*.so
rm -rf unpacked_apk/lib/*/libjiagu*.so

# 5. Rebuild
apktool b unpacked_apk -o rebuilt.apk
jarsigner -keystore my.keystore rebuilt.apk mykey
zipalign -v 4 rebuilt.apk final.apk
```

## Troubleshooting

**"pycryptodome is required"**
```bash
pip3 install pycryptodome
```

**"classes.dex not found"**
- APK may not be Jiagu-packed
- Try: `unzip -l your_app.apk | grep dex`

**"Invalid DEX magic"**
- Different Jiagu version
- Open an issue with APK details

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check [examples/](examples/) for advanced usage
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

---

Need help? [Open an issue](https://github.com/yourusername/Jiagu-unpacker/issues)
