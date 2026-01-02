"""
Quick Start Script for LangSmith Integration
Run this to verify your LangSmith setup is working correctly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if required environment variables are set"""
    print("=" * 60)
    print("LangSmith Setup Verification")
    print("=" * 60)
    
    # Check LANGSMITH_API_KEY
    api_key = os.getenv("LANGSMITH_API_KEY")
    if api_key:
        print("✅ LANGSMITH_API_KEY is set")
        print(f"   Key: {api_key[:10]}...{api_key[-4:]}")
    else:
        print("❌ LANGSMITH_API_KEY is NOT set")
        print("   Please add it to your .env file:")
        print("   LANGSMITH_API_KEY=your_api_key_here")
        return False
    
    # Check LANGSMITH_PROJECT
    project = os.getenv("LANGSMITH_PROJECT", "NexusAI")
    print(f"✅ LANGSMITH_PROJECT: {project}")
    
    # Check LANGSMITH_WORKSPACE_ID (optional, but needed for org-scoped keys)
    workspace_id = os.getenv("LANGSMITH_WORKSPACE_ID")
    if workspace_id:
        print(f"✅ LANGSMITH_WORKSPACE_ID is set: {workspace_id[:8]}...")
    else:
        print("ℹ️  LANGSMITH_WORKSPACE_ID is NOT set (optional, needed for org-scoped API keys)")
    
    # Check GEMINI_API_KEY
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print("✅ GEMINI_API_KEY is set")
    else:
        print("⚠️  GEMINI_API_KEY is NOT set (required for LLM calls)")
    
    return True

def test_langsmith_import():
    """Test if LangSmith SDK is installed"""
    print("\n" + "=" * 60)
    print("Testing LangSmith SDK Installation")
    print("=" * 60)
    
    try:
        import langsmith
        print(f"✅ langsmith installed (version: {langsmith.__version__})")
    except ImportError:
        print("❌ langsmith not installed")
        print("   Run: pip install langsmith")
        return False
    
    try:
        import langchain
        print(f"✅ langchain installed")
    except ImportError:
        print("❌ langchain not installed")
        print("   Run: pip install langchain")
        return False
    
    return True

def test_langsmith_connection():
    """Test connection to LangSmith"""
    print("\n" + "=" * 60)
    print("Testing LangSmith Connection")
    print("=" * 60)
    
    try:
        from langsmith import Client
        
        client = Client()
        
        # Try to list projects
        projects = list(client.list_projects(limit=1))
        print(f"✅ Successfully connected to LangSmith")
        print(f"   Found {len(projects)} project(s)")
        
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ Failed to connect to LangSmith: {e}")
        
        # Check if it's an org-scoped API key issue
        if "org-scoped" in error_str or "X-Tenant-ID" in error_str or "403" in error_str:
            print("\n⚠️  Your API key is organization-scoped!")
            print("   You need to add your workspace/tenant ID to .env:")
            print("")
            print("   1. Go to https://smith.langchain.com/")
            print("   2. Look at the URL when viewing your project")
            print("   3. The URL will be: https://smith.langchain.com/o/YOUR_ORG/projects/p/YOUR_PROJECT")
            print("   4. Copy YOUR_ORG value")
            print("   5. Add to .env: LANGSMITH_WORKSPACE_ID=YOUR_WORKSPACE_ID")
            print("")
            print("   Example:")
            print("   LANGSMITH_WORKSPACE_ID=abc123-def456-ghi789")
            print("")
        
        return False

def test_tracing():
    """Test basic tracing functionality"""
    print("\n" + "=" * 60)
    print("Testing Tracing Functionality")
    print("=" * 60)
    
    try:
        from langsmith_config import trace_llm_call, token_tracker
        from langsmith import traceable
        
        # Test decorator
        @traceable(name="test_function", run_type="chain")
        def test_function(x: int, y: int):
            return x + y
        
        result = test_function(5, 3)
        print(f"✅ Tracing decorator works (result: {result})")
        
        # Test token tracker
        token_tracker.log_usage(
            service="Test",
            operation="test_operation",
            model="gemini-2.5-flash",
            input_tokens=100,
            output_tokens=200,
            user_id="test_user",
            job_id="test_job"
        )
        
        summary = token_tracker.get_summary(user_id="test_user")
        print(f"✅ Token tracker works")
        print(f"   Total tokens: {summary['total_tokens']}")
        print(f"   Total cost: ${summary['total_cost_usd']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Tracing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cost_calculation():
    """Test cost calculation"""
    print("\n" + "=" * 60)
    print("Testing Cost Calculation")
    print("=" * 60)
    
    try:
        from langsmith_config import calculate_cost
        
        # Test different models
        models = [
            ("gemini-2.5-flash", 1000, 2000),
            ("gemini-3-pro-preview", 1000, 2000),
            ("gemini-2.0-flash-exp", 1000, 2000),
        ]
        
        for model, input_tokens, output_tokens in models:
            cost = calculate_cost(model, input_tokens, output_tokens)
            print(f"✅ {model}:")
            print(f"   Input: {input_tokens} tokens, Output: {output_tokens} tokens")
            print(f"   Cost: ${cost:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Cost calculation test failed: {e}")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n" + "=" * 60)
    print("Next Steps")
    print("=" * 60)
    
    print("""
1. View your traces in LangSmith:
   → https://smith.langchain.com/

2. Integrate tracing into your services:
   → See ImageGeneration/langsmith_integration_example.py
   → See LANGSMITH_GUIDE.md for detailed instructions

3. Add analytics endpoints to your services:
   → Import analytics_api.py router
   → Add to your FastAPI app

4. Test with a real LLM call:
   → Run one of your services (e.g., ImageGeneration)
   → Make a request
   → Check LangSmith dashboard for the trace

5. Monitor costs:
   → Use /analytics/token-usage endpoint
   → Use /analytics/cost-breakdown endpoint
   → Set up alerts in LangSmith

For detailed instructions, see LANGSMITH_GUIDE.md
""")

def main():
    """Run all tests"""
    print("\n🚀 LangSmith Quick Start\n")
    
    all_passed = True
    
    # Run tests
    if not check_environment():
        all_passed = False
    
    if not test_langsmith_import():
        all_passed = False
    
    if not test_langsmith_connection():
        all_passed = False
    
    if not test_tracing():
        all_passed = False
    
    if not test_cost_calculation():
        all_passed = False
    
    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    
    if all_passed:
        print("✅ All tests passed! LangSmith is ready to use.")
        show_next_steps()
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        print("\nCommon issues:")
        print("1. Missing LANGSMITH_API_KEY in .env")
        print("2. LangSmith SDK not installed (run: pip install -r requirements.txt)")
        print("3. Invalid API key")
        print("\nSee LANGSMITH_GUIDE.md for help.")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
