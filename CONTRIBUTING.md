# Contributing to SmartCatalog Hub

Thank you for your interest in contributing to **SmartCatalog Hub**!

## How Can I Contribute?

### 1. Adding Rules to App Classifier
If a popular application is miscategorized or uncategorized:
1. Open `classifier.py`.
2. Add relevant binary names, package keywords, or product names to the appropriate dictionary inside `CATEGORY_RULES` or `EXACT_DESCRIPTIONS`.
3. Submit a Pull Request.

### 2. Reporting Bugs
- Open an Issue describing the bug.
- Include your Windows version (e.g. Windows 11 23H2), browser version, and reproduction steps.
- Attach log snippets from `service.log` if relevant.

### 3. Submitting Code Changes
1. Fork the repository.
2. Create your feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m 'feat: add amazing feature'`).
4. Run security and regression tests:
   ```bash
   python -m unittest discover tests
   ```
5. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request.

## Code of Conduct
Please maintain a respectful, welcoming, and constructive environment.
