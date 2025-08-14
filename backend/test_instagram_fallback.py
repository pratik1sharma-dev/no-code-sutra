#!/usr/bin/env python3
"""
Test script to verify Instagram access token fallback behavior
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor

def test_instagram_fallback():
    """Test Instagram access token fallback behavior"""
    print("🔍 Testing Instagram Access Token Fallback")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Create executor
    executor = LangGraphWorkflowExecutor()
    
    # Test Case 1: No access token in config (should use environment variable)
    print("\n📋 Test Case 1: No access token in config")
    print("-" * 30)
    
    config_no_token = {
        'post': 'Test post content'
    }
    
    mock_state = {
        'workflow_id': 'test',
        'start_time': '2025-01-20T10:00:00Z'
    }
    
    try:
        result = executor.execute_node('instagram_post', config_no_token, mock_state)
        print(f"✅ Test completed")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Access token used: {result.get('access_token', 'None')[:10] + '...' if result.get('access_token') else 'None'}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test Case 2: Access token in config (should use config value)
    print("\n📋 Test Case 2: Access token in config")
    print("-" * 30)
    
    config_with_token = {
        'access_token': 'test_token_from_config',
        'post': 'Test post content'
    }
    
    try:
        result = executor.execute_node('instagram_post', config_with_token, mock_state)
        print(f"✅ Test completed")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Access token used: {result.get('access_token', 'None')[:10] + '...' if result.get('access_token') else 'None'}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Test Case 3: Environment variable reference in config
    print("\n📋 Test Case 3: Environment variable reference in config")
    print("-" * 30)
    
    config_env_ref = {
        'access_token': '${INSTAGRAM_ACCESS_TOKEN}',
        'post': 'Test post content'
    }
    
    try:
        result = executor.execute_node('instagram_post', config_env_ref, mock_state)
        print(f"✅ Test completed")
        print(f"Status: {result.get('status', 'unknown')}")
        print(f"Access token used: {result.get('access_token', 'None')[:10] + '...' if result.get('access_token') else 'None'}")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    
    # Environment variable check
    print("\n🔑 Environment Variable Check")
    print("-" * 30)
    env_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    if env_token:
        print(f"✅ INSTAGRAM_ACCESS_TOKEN found: {env_token[:10]}...")
    else:
        print("❌ INSTAGRAM_ACCESS_TOKEN not found in environment")
        print("💡 Set it in your .env file to test real Instagram posting")

if __name__ == "__main__":
    test_instagram_fallback()
