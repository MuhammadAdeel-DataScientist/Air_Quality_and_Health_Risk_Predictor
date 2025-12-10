"""
Quick fix script for test issues
Run this before running tests
"""
from pathlib import Path
import shutil

print("🔧 Fixing test files...")

# Backup and fix conftest.py
conftest_path = Path("tests/conftest.py")
if conftest_path.exists():
    shutil.copy(conftest_path, "tests/conftest.py.backup")
    print("✓ Backed up conftest.py")

print("\n📝 Manual fixes needed:")
print("1. Replace tests/conftest.py with the fixed version")
print("2. Update the 3 test methods in test_health_risk.py")
print("3. Update test_feature_count_match in test_model_predictions.py")
print("\nAfter fixes, run: pytest tests/ -v")