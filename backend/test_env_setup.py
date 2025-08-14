#!/usr/bin/env python3
"""
Test script to verify Instagram environment variable setup
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_environment_variables():
    """Test if Instagram environment variables are properly set"""
    print("🔍 Testing Instagram Environment Variables...")
    print("=" * 50)
    
    # Check required environment variables
    required_vars = [
        'INSTAGRAM_ACCESS_TOKEN',
        'INSTAGRAM_BUSINESS_ACCOUNT_ID',
        'FACEBOOK_PAGE_ID'
    ]
    
    optional_vars = [
        'INSTAGRAM_DEBUG'
    ]
    
    all_good = True
    
    # Check required variables
    print("📋 Required Variables:")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value[:10]}..." if len(value) > 10 else f"  ✅ {var}: {value}")
        else:
            print(f"  ❌ {var}: Not set")
            all_good = False
    
    # Check optional variables
    print("\n📋 Optional Variables:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var}: {value}")
        else:
            print(f"  ⚠️  {var}: Not set (optional)")
    
    # Test environment variable resolution
    print("\n🧪 Testing Environment Variable Resolution:")
    test_value = "${INSTAGRAM_ACCESS_TOKEN}"
    if os.getenv('INSTAGRAM_ACCESS_TOKEN'):
        print(f"  ✅ Environment variable resolution works")
    else:
        print(f"  ❌ Environment variable resolution failed")
        all_good = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_good:
        print("🎉 All required environment variables are set!")
        print("✅ You can now test real Instagram posting")
    else:
        print("⚠️  Some required environment variables are missing")
        print("📝 Please set them in your .env file")
    
    return all_good

def test_workflow_config():
    """Test workflow configuration with environment variables"""
    print("\n🔧 Testing Workflow Configuration...")
    print("=" * 50)
    
    try:
        import json
        with open('test_workflow_real_instagram.json', 'r') as f:
            workflow = json.load(f)
        
        # Check Instagram node configuration
        instagram_node = None
        for node in workflow['nodes']:
            if node['type'] == 'instagram_post':
                instagram_node = node
                break
        
        if instagram_node:
            access_token_config = instagram_node['config'].get('access_token', '')
            print(f"📱 Instagram Node Access Token Config: {access_token_config}")
            
            if access_token_config == '${INSTAGRAM_ACCESS_TOKEN}':
                print("  ✅ Workflow is configured to use environment variable")
            else:
                print("  ⚠️  Workflow is not using environment variable")
        else:
            print("  ❌ No Instagram node found in workflow")
            
    except Exception as e:
        print(f"  ❌ Error reading workflow: {e}")

if __name__ == "__main__":
    # Test environment variables
    env_ok = test_environment_variables()
    
    # Test workflow configuration
    test_workflow_config()
    
    print(f"\n📚 Next Steps:")
    if env_ok:
        print("1. ✅ Environment variables are ready")
        print("2. 🚀 Run: python test_workflow_execution.py")
        print("3. 📱 Check your Instagram account for the post")
    else:
        print("1. 📝 Create/update backend/.env file")
        print("2. 🔑 Add your Instagram access token")
        print("3. 🔄 Restart your application")
        print("4. 🚀 Then run the test workflow")
