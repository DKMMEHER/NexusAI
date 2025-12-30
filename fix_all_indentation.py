#!/usr/bin/env python3
"""Complete fix for test_document_summarization_integration.py"""

import re

file_path = r"tests\integration\test_document_summarization_integration.py"

# Read the entire file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Create the corrected file line by line
corrected_lines = []

i = 0
while i < len(lines):
    line_num = i + 1  # 1-indexed line number
    
    # Skip and replace problematic sections
    if line_num == 136:
        # Replace lines 136-151 with corrected version
        corrected_lines.append("        for model in models:\n")
        corrected_lines.append("            fake_txt = io.BytesIO(f\"Test document for model {model}\".encode())\n")
        corrected_lines.append("            \n")
        corrected_lines.append("            response = client.post(\n")
        corrected_lines.append("                \"/summarize\",\n")
        corrected_lines.append("                files={\"files\": (\"test.txt\", fake_txt, \"text/plain\")},\n")
        corrected_lines.append("                data={\n")
        corrected_lines.append("                    \"model\": model,\n")
        corrected_lines.append("                    \"user_id\": \"test_user_123\"\n")
        corrected_lines.append("                }\n")
        corrected_lines.append("            )\n")
        corrected_lines.append("            \n")
        corrected_lines.append("            assert response.status_code == 200\n")
        corrected_lines.append("            data = response.json()\n")
        corrected_lines.append("            assert \"summary\" in data\n")
        corrected_lines.append("            print(f\"✅ Model {model} works correctly\")\n")
        i += 16  # Skip original lines 136-151
        continue
    
    elif line_num == 214:
        # Keep line 214
        corrected_lines.append(lines[i])
        i += 1
        continue
    
    elif line_num == 215:
        # Replace lines 215-235 with corrected version
        corrected_lines.append("            fake_txt = io.BytesIO(b\"Database integration test document\")\n")
        corrected_lines.append("            \n")
        corrected_lines.append("            response = client.post(\n")
        corrected_lines.append("                \"/summarize\",\n")
        corrected_lines.append("                files={\"files\": (\"test.txt\", fake_txt, \"text/plain\")},\n")
        corrected_lines.append("                data={\"user_id\": \"test_user_123\"}\n")
        corrected_lines.append("            )\n")
        corrected_lines.append("            \n")
        corrected_lines.append("            assert response.status_code == 200\n")
        corrected_lines.append("            \n")
        corrected_lines.append("            # Verify database save was called\n")
        corrected_lines.append("            mock_db.save_job.assert_called_once()\n")
        corrected_lines.append("            \n")
        corrected_lines.append("            # Verify the saved data structure\n")
        corrected_lines.append("            call_args = mock_db.save_job.call_args[0][0]\n")
        corrected_lines.append("            assert \"job_id\" in call_args\n")
        corrected_lines.append("            assert \"user_id\" in call_args\n")
        corrected_lines.append("            assert call_args[\"user_id\"] == \"test_user_123\"\n")
        corrected_lines.append("            assert \"type\" in call_args\n")
        corrected_lines.append("            \n")
        corrected_lines.append("            print(\"✅ Database integration works correctly\")\n")
        i += 21  # Skip original lines 215-235
        continue
    
    elif line_num == 241:
        # Replace lines 241-247 with corrected version
        corrected_lines.append("        def make_request(i):\n")
        corrected_lines.append("            fake_txt = io.BytesIO(f\"Concurrent document {i} with content to summarize.\".encode())\n")
        corrected_lines.append("            return client.post(\n")
        corrected_lines.append("                \"/summarize\",\n")
        corrected_lines.append("                files={\"files\": (f\"doc{i}.txt\", fake_txt, \"text/plain\")},\n")
        corrected_lines.append("                data={\"user_id\": f\"user_{i}\"}\n")
        corrected_lines.append("            )\n")
        i += 7  # Skip original lines 241-247
        continue
    
    else:
        # Keep all other lines as-is
        corrected_lines.append(lines[i])
        i += 1

# Write the corrected file
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(corrected_lines)

print("✅ Successfully fixed all indentation issues!")
print("Fixed sections:")
print("  - Lines 136-151 (test_summarize_with_different_models)")
print("  - Lines 215-235 (test_database_integration)")
print("  - Lines 241-247 (test_concurrent_summarization_requests)")
