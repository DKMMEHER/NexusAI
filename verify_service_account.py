#!/usr/bin/env python3
"""Verify and prepare service account key for GitHub Secret"""

import json
import sys

def verify_service_account_key(filename='serviceAccountKey.json'):
    """Verify the service account key JSON is valid and complete."""
    
    print("🔍 Verifying Service Account Key JSON...\n")
    
    try:
        # Read the file
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if it's valid JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON Decode Error at position {e.pos}:")
            print(f"   {e.msg}")
            print(f"\n   Content around error:")
            start = max(0, e.pos - 50)
            end = min(len(content), e.pos + 50)
            print(f"   ...{content[start:end]}...")
            return False
        
        # Check required fields
        required_fields = {
            'type': 'service_account',
            'project_id': str,
            'private_key_id': str,
            'private_key': str,
            'client_email': str,
            'client_id': str,
            'auth_uri': str,
            'token_uri': str,
            'auth_provider_x509_cert_url': str,
            'client_x509_cert_url': str
        }
        
        print("✅ JSON is valid!\n")
        print("📋 Checking required fields:\n")
        
        all_fields_present = True
        for field, expected_type in required_fields.items():
            if field not in data:
                print(f"   ❌ Missing field: {field}")
                all_fields_present = False
            else:
                if expected_type == str and not isinstance(data[field], str):
                    print(f"   ⚠️  Field '{field}' should be a string")
                elif field == 'type' and data[field] != 'service_account':
                    print(f"   ⚠️  Field 'type' should be 'service_account', got '{data[field]}'")
                else:
                    # Show first 50 chars of the value
                    value_preview = str(data[field])[:50]
                    if len(str(data[field])) > 50:
                        value_preview += "..."
                    print(f"   ✅ {field}: {value_preview}")
        
        if not all_fields_present:
            print("\n❌ Some required fields are missing!")
            return False
        
        # Check private key format
        if not data['private_key'].startswith('-----BEGIN PRIVATE KEY-----'):
            print("\n⚠️  Warning: private_key doesn't start with '-----BEGIN PRIVATE KEY-----'")
        
        if not data['private_key'].endswith('-----END PRIVATE KEY-----\n'):
            print("\n⚠️  Warning: private_key doesn't end with '-----END PRIVATE KEY-----\\n'")
        
        # Check project ID
        print(f"\n📊 Service Account Details:")
        print(f"   Project ID: {data['project_id']}")
        print(f"   Email: {data['client_email']}")
        print(f"   Type: {data['type']}")
        
        # Calculate JSON size
        json_size = len(content)
        print(f"\n📏 JSON Size: {json_size} characters")
        
        if json_size < 1000:
            print("   ⚠️  Warning: JSON seems too small, might be incomplete")
        
        # Final validation
        print("\n" + "="*60)
        print("✅ SERVICE ACCOUNT KEY IS VALID!")
        print("="*60)
        print("\n📋 Next Steps:")
        print("   1. Copy the ENTIRE content of this file")
        print("   2. Go to: https://github.com/DKMMEHER/NexusAI/settings/secrets/actions")
        print("   3. Delete the old GCP_SA_KEY secret")
        print("   4. Add a new secret named: GCP_SA_KEY")
        print("   5. Paste the content (all {} characters)".format(json_size))
        print("   6. Click 'Add secret'")
        
        # Offer to copy to clipboard (Windows only)
        try:
            import subprocess
            response = input("\n❓ Copy JSON to clipboard? (y/n): ")
            if response.lower() == 'y':
                subprocess.run(['clip'], input=content.encode('utf-8'), check=True)
                print("✅ JSON copied to clipboard! Ready to paste into GitHub.")
        except:
            print("\n💡 Tip: Use this command to copy to clipboard:")
            print(f"   Get-Content {filename} -Raw | Set-Clipboard")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {filename}")
        print(f"\n💡 Make sure '{filename}' is in the current directory")
        print(f"   Current directory: {sys.path[0]}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    import os
    
    # Check if file exists
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'serviceAccountKey.json'
    
    if not os.path.exists(filename):
        print(f"❌ File '{filename}' not found in current directory\n")
        print("📁 Current directory:", os.getcwd())
        print("\n💡 Usage:")
        print(f"   python verify_service_account.py [filename]")
        print(f"   python verify_service_account.py serviceAccountKey.json")
        sys.exit(1)
    
    success = verify_service_account_key(filename)
    sys.exit(0 if success else 1)
