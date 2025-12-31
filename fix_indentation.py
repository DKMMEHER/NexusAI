#!/usr/bin/env python3
"""Fix indentation issues in test_document_summarization_integration.py"""

import re

file_path = r"tests\integration\test_document_summarization_integration.py"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix 1: Lines 139-151 - indent into for loop
# Lines 139-150 need to be indented by 4 spaces
for i in range(138, 150):  # Lines 139-150 (0-indexed: 138-149)
    if lines[i].strip():  # Only indent non-empty lines
        lines[i] = '    ' + lines[i]

# Fix line 151 - remove extra indentation before print
if '            print(f"✅ Model' in lines[150]:
    lines[150] = lines[150].replace('            print(f"✅ Model', '            print(f"✅ Model')

# Fix 2: Lines 217-235 - indent into with block  
# Lines 217-235 need to be indented by 4 spaces
for i in range(216, 235):  # Lines 217-235 (0-indexed: 216-234)
    if lines[i].strip():  # Only indent non-empty lines
        lines[i] = '    ' + lines[i]

# Fix 3: Lines 243-246 - indent into function
# Lines 243-246 need to be indented by 4 spaces
for i in range(242, 246):  # Lines 243-246 (0-indexed: 242-245)
    if lines[i].strip():  # Only indent non-empty lines
        lines[i] = '    ' + lines[i]

# Write the fixed file
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ Fixed indentation issues in test_document_summarization_integration.py")
print("Fixed sections:")
print("  - Lines 139-151 (test_summarize_with_different_models)")
print("  - Lines 217-235 (test_database_integration)")
print("  - Lines 243-246 (test_concurrent_summarization_requests)")
