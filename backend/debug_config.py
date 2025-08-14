#!/usr/bin/env python3
"""
Debug script to test configuration passing
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor

def debug_config_passing():
    """Debug configuration passing step by step"""
    print("🔍 Debugging Configuration Passing")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Load the test workflow
    with open('test_workflow_real_instagram.json', 'r') as f:
        workflow_data = json.load(f)
    
    print(f"Workflow: {workflow_data['workflow_name']}")
    
    # Check the Instagram node specifically
    instagram_node = None
    for node in workflow_data['nodes']:
        if node['type'] == 'instagram_post':
            instagram_node = node
            break
    
    if instagram_node:
        print(f"\n📱 Instagram Node Found:")
        print(f"  ID: {instagram_node['id']}")
        print(f"  Type: {instagram_node['type']}")
        print(f"  Config: {instagram_node.get('config', {})}")
        print(f"  Access Token in Config: {instagram_node.get('config', {}).get('access_token', 'NOT_FOUND')}")
    else:
        print("❌ No Instagram node found!")
        return
    
    # Test the executor's configuration extraction
    executor = LangGraphWorkflowExecutor()
    
    # Simulate what happens in execute_workflow
    node_data = instagram_node
    node_config = node_data.get('config', {})
    
    print(f"\n🔧 Configuration Extraction:")
    print(f"  node_data.get('config', {{}}): {node_config}")
    print(f"  access_token from config: {node_config.get('access_token', 'NOT_FOUND')}")
    
    # Test the execute_node method directly
    print(f"\n🧪 Testing execute_node method:")
    
    # Create a mock state
    mock_state = {
        'workflow_id': 'test',
        'start_time': '2025-01-20T10:00:00Z',
        'result': 'Test content from previous node',
        'content': 'Test content'
    }
    
    # Call execute_node directly
    try:
        result = executor.execute_node(
            node_data['type'],
            node_config,
            mock_state
        )
        print(f"  ✅ execute_node completed")
        print(f"  Status: {result.get('status', 'unknown')}")
    except Exception as e:
        print(f"  ❌ execute_node failed: {e}")
    
    # Test environment variable resolution
    print(f"\n🔑 Testing Environment Variable Resolution:")
    env_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    print(f"  Environment variable: {env_token[:10] + '...' if env_token else 'NOT_FOUND'}")
    
    # Test the resolution method
    test_value = "${INSTAGRAM_ACCESS_TOKEN}"
    resolved = executor.nodes._resolve_environment_variables(test_value)
    print(f"  Resolving '{test_value}' -> '{resolved[:10] + '...' if resolved else 'None'}'")

if __name__ == "__main__":
    debug_config_passing()
