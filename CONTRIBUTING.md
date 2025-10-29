# Contributing to Jiagu Unpacker

Thank you for your interest in contributing to Jiagu Unpacker! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and professional
- Focus on constructive feedback
- Help create a welcoming environment for all contributors

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:

1. **Clear title**: Describe the issue briefly
2. **Environment**: Python version, OS, APK details (if shareable)
3. **Steps to reproduce**: Detailed steps to trigger the bug
4. **Expected behavior**: What should happen
5. **Actual behavior**: What actually happens
6. **Error messages**: Full error output or logs

Example:
```
Title: "XOR decryption fails on classes3.dex"

Environment:
- Python 3.9.7
- Ubuntu 20.04
- APK packed with Jiagu v4.x

Steps:
1. Run: python3 jiagu_unpacker.py -apk test.apk
2. Observe error during DEX #3 extraction

Expected: All DEX files extracted successfully
Actual: XOR decryption produces invalid DEX magic
Error: "Invalid DEX magic: b'xxx'"
```

### Suggesting Features

For feature requests, please describe:

1. **Use case**: Why is this feature needed?
2. **Proposed solution**: How should it work?
3. **Alternatives**: Any other approaches considered?
4. **Additional context**: Screenshots, examples, etc.

### Pull Requests

#### Before You Start

1. **Check existing issues**: Avoid duplicate work
2. **Open an issue first**: Discuss major changes before implementing
3. **Fork the repository**: Work in your own fork

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/Jiagu-unpacker.git
cd Jiagu-unpacker

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest flake8 black
```

#### Making Changes

1. **Create a branch**:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

2. **Write clean code**:
   - Follow PEP 8 style guide
   - Add docstrings to functions/classes
   - Keep functions focused and small
   - Use meaningful variable names

3. **Test your changes**:
   ```bash
   # Run with different APKs
   python3 jiagu_unpacker.py -apk test1.apk
   python3 jiagu_unpacker.py -apk test2.apk

   # Test edge cases
   python3 jiagu_unpacker.py -apk password_protected.apk
   python3 jiagu_unpacker.py -apk multidex_app.apk
   ```

4. **Format code**:
   ```bash
   # Auto-format with black
   black jiagu_unpacker.py zip_decrypt.py

   # Check style
   flake8 jiagu_unpacker.py zip_decrypt.py
   ```

5. **Commit changes**:
   ```bash
   git add .
   git commit -m "feat: Add support for Jiagu v5 encryption"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `refactor:` Code refactoring
   - `test:` Adding tests
   - `chore:` Maintenance tasks

#### Submitting Pull Request

1. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create pull request**:
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the template

3. **PR description should include**:
   - Summary of changes
   - Related issue number (if applicable)
   - Testing performed
   - Screenshots (if UI changes)

Example PR description:
```markdown
## Summary
Adds support for Jiagu v5 encryption scheme which uses different AES keys.

## Changes
- Added detection for Jiagu version in packed DEX
- Implemented v5 key extraction algorithm
- Updated AES decryption to handle both v4 and v5

## Related Issues
Fixes #42

## Testing
- Tested with 5 different v5-packed APKs
- All DEX files extracted successfully
- Backward compatibility with v4 confirmed
```

#### Code Review Process

- Maintainers will review your PR
- Address feedback by pushing new commits
- Once approved, your PR will be merged

## Code Style Guidelines

### Python Style

```python
# Good
def extract_dex_files(self, data: bytes, count: int) -> list:
    """
    Extract multiple DEX files from encrypted data.

    Args:
        data: Encrypted byte data containing DEX files
        count: Number of DEX files to extract

    Returns:
        List of extracted DEX file data as bytes
    """
    dex_files = []
    for i in range(count):
        dex = self._extract_single_dex(data, i)
        dex_files.append(dex)
    return dex_files


# Bad
def extract(d, c):
    # extract dex
    l = []
    for i in range(c):
        x = self.ext(d, i)
        l.append(x)
    return l
```

### Documentation

- Add docstrings to all public functions/classes
- Use Google-style docstrings
- Keep comments up-to-date
- Document complex algorithms

### Error Handling

```python
# Good
try:
    dex_data = self.extract_classes_dex()
    if not dex_data:
        print("[-] No DEX data extracted")
        return False
except FileNotFoundError as e:
    print(f"[-] APK not found: {e}")
    return False
except Exception as e:
    print(f"[-] Unexpected error: {e}")
    return False

# Bad
try:
    dex_data = self.extract_classes_dex()
except:
    pass
```

## Testing

### Manual Testing Checklist

Before submitting PR, test:

- [ ] Normal APK extraction
- [ ] Password-protected APK handling
- [ ] Multidex APK support
- [ ] Invalid/corrupted APK handling
- [ ] Different output directories
- [ ] Command-line arguments
- [ ] Module import and usage

### Test Cases

If adding new features, include test cases:

```python
# Example test structure (for future pytest integration)
def test_xor_decryption():
    unpacker = JiaguUnpacker("test.apk", "output")
    data = b'\x00' * 112
    result = unpacker.xor_decrypt(data)
    assert result == b'\x66' * 112
```

## Documentation

### Updating README

When adding features:
- Update usage examples
- Add to feature list
- Update troubleshooting if needed
- Keep both README.md and README_FA.md in sync

### Code Comments

```python
# Good: Explains WHY
# Clear encryption bit (bit 0) to bypass fake password protection
data[i + 8] = v1 & 0xFE

# Bad: Explains WHAT (obvious from code)
# Set data at index i+8
data[i + 8] = v1 & 0xFE
```

## Release Process

For maintainers:

1. Update version in `jiagu_unpacker.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag -a v1.1.0 -m "Version 1.1.0"`
4. Push tag: `git push origin v1.1.0`
5. Create GitHub release with notes

## Questions?

- Open an issue for questions
- Check existing issues and PRs
- Be patient - maintainers are volunteers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Jiagu Unpacker! 🎉
