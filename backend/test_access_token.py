#!/usr/bin/env python3
"""
Test script to check access token resolution
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from services.langgraph_nodes.workflow_nodes import LangGraphWorkflowNodes

def test_access_token_resolution():
    """Test access token resolution"""
    print("🔍 Testing Access Token Resolution")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if environment variable exists
    env_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    print(f"Environment variable: {env_token[:10] + '...' if env_token else 'NOT_FOUND'}")
    
    # Test the resolution method
    nodes = LangGraphWorkflowNodes()
    
    # Test cases
    test_cases = [
        "${INSTAGRAM_ACCESS_TOKEN}",
        "test_token_12345",
        "some_other_token",
        ""
    ]
    
    for test_value in test_cases:
        resolved = nodes._resolve_environment_variables(test_value)
        print(f"Input: '{test_value}' -> Output: '{resolved[:10] + '...' if resolved else 'None'}'")
    
    # Test the condition check
    print("\n🔍 Testing Access Token Validation")
    print("=" * 50)
    
    for test_value in test_cases:
        resolved = nodes._resolve_environment_variables(test_value)
        is_valid = bool(resolved and resolved != 'test_token_12345')
        print(f"Token: '{resolved[:10] + '...' if resolved else 'None'}' -> Valid: {is_valid}")

if __name__ == "__main__":
    test_access_token_resolution()
