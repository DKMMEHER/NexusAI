#!/usr/bin/env python3
"""Fix indentation issues - corrected version"""

file_path = r"tests\integration\test_document_summarization_integration.py"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Lines 225-235 - remove extra indentation (they have 8 extra spaces)
content = content.replace(
    '                # Verify database save was called\r\n                mock_db.save_job.assert_called_once()',
    '            # Verify database save was called\r\n            mock_db.save_job.assert_called_once()'
)

content = content.replace(
    '                # Verify the saved data structure\r\n                call_args',
    '            # Verify the saved data structure\r\n            call_args'
)

content = content.replace(
    '                assert "job_id" in call_args',
    '            assert "job_id" in call_args'
)

content = content.replace(
    '                assert "user_id" in call_args',
    '            assert "user_id" in call_args'
)

content = content.replace(
    '                assert call_args["user_id"] == "test_user_123"',
    '            assert call_args["user_id"] == "test_user_123"'
)

content = content.replace(
    '                assert "type" in call_args',
    '            assert "type" in call_args'
)

content = content.replace(
    '                print("✅ Database integration works correctly")',
    '            print("✅ Database integration works correctly")'
)

# Write the fixed file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed extra indentation in lines 225-235")
