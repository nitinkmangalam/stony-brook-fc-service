#!/bin/bash
set -e

echo "🔄 Running black to fix formatting..."
black .

echo "🔄 Running isort to fix imports..."
isort .

echo "⚠️  Remaining flake8 issues:"
flake8 . || true

echo "
✅ Auto-fixing complete!

Note:
- Formatting issues have been automatically fixed by black and isort
- Any remaining flake8 issues (like missing docstrings) will need manual fixes
- Run this script again after making manual fixes to verify
"
