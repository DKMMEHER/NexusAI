#!/usr/bin/env python3
"""Fix service account key for GitHub Actions"""

import json
import sys

def fix_service_account_key(input_file='serviceAccountKey.json', output_file='serviceAccountKey_fixed.json'):
    """Fix the service account key by ensuring proper formatting."""
    
    print("🔧 Fixing Service Account Key for GitHub Actions...\n")
    
    try:
        # Read the original file
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ Successfully loaded JSON\n")
        
        # The issue is usually with the private_key field
        # GitHub Actions expects the \n to be literal characters, not actual newlines
        
        # Check current format
        private_key = data.get('private_key', '')
        
        print("📋 Current private_key format:")
        if '\\n' in private_key:
            print("   ✅ Has escaped newlines (\\n) - CORRECT for GitHub")
        elif '\n' in private_key:
            print("   ⚠️  Has actual newlines - needs fixing")
            # Convert actual newlines to escaped newlines
            data['private_key'] = private_key.replace('\n', '\\n')
            print("   ✅ Fixed: Converted to escaped newlines")
        else:
            print("   ❌ No newlines found - this is wrong!")
        
        # Ensure the JSON is compact (no extra whitespace)
        # GitHub Actions works best with compact JSON
        compact_json = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
        
        # Save the fixed version
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(compact_json)
        
        print(f"\n✅ Fixed JSON saved to: {output_file}")
        print(f"📏 Size: {len(compact_json)} characters")
        
        # Verify the fixed JSON
        with open(output_file, 'r', encoding='utf-8') as f:
            verify_data = json.load(f)
        
        print("\n✅ Verification: Fixed JSON is valid")
        
        # Show the difference
        print("\n📊 Comparison:")
        print(f"   Original size: {len(json.dumps(data))} chars")
        print(f"   Fixed size: {len(compact_json)} chars")
        
        # Copy to clipboard
        try:
            import subprocess
            response = input("\n❓ Copy fixed JSON to clipboard? (y/n): ")
            if response.lower() == 'y':
                subprocess.run(['clip'], input=compact_json.encode('utf-8'), check=True)
                print("✅ Fixed JSON copied to clipboard!")
                print("\n📋 Next steps:")
                print("   1. Go to: https://github.com/DKMMEHER/NexusAI/settings/secrets/actions")
                print("   2. Delete the old GCP_SA_KEY secret")
                print("   3. Add new secret: GCP_SA_KEY")
                print("   4. Paste the fixed JSON (Ctrl+V)")
                print("   5. Save the secret")
        except:
            print("\n💡 To copy to clipboard, run:")
            print(f"   Get-Content {output_file} -Raw | Set-Clipboard")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ File not found: {input_file}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = fix_service_account_key()
    
    if success:
        print("\n" + "="*60)
        print("✅ SERVICE ACCOUNT KEY FIXED!")
        print("="*60)
        print("\nThe fixed JSON is ready to use in GitHub Secrets.")
        print("It has been formatted specifically for GitHub Actions.")
    
    sys.exit(0 if success else 1)
