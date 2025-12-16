
import os
from dotenv import load_dotenv
import inspect

# Mock genai if needed or try to import real one
try:
    import google.genai as genai
    from google.genai import types
    print("SDK imported successfully")
except ImportError:
    print("SDK not found")
    exit(1)

load_dotenv()

def inspect_sdk():
    print("\n--- Inspecting google.genai.types.GenerateVideosConfig ---")
    if hasattr(types, "GenerateVideosConfig"):
        cfg = types.GenerateVideosConfig
        print(f"Class: {cfg}")
        try:
            print(f"Fields: {cfg.model_fields.keys()}")
        except:
            print("No model_fields found")
            try:
                print(f"Signature: {inspect.signature(cfg)}")
            except:
                pass
    else:
        print("GenerateVideosConfig not found in types")

    print("\n--- Inspecting client.models.generate_videos ---")
    try:
        api_key = os.getenv("GEMINI_API_KEY") # Ensure this is set in env or use placeholder if just inspecting signatures (might fail init)
        # We try to create client securely
        if api_key:
            client = genai.Client(api_key=api_key)
            if hasattr(client.models, "generate_videos"):
                sig = inspect.signature(client.models.generate_videos)
                print(f"Signature: {sig}")
            else:
                print("client.models.generate_videos not found")
        else:
            print("No API key, cannot init client to inspect methods")
    except Exception as e:
        print(f"Client init failed: {e}")

if __name__ == "__main__":
    inspect_sdk()
