#!/usr/bin/env python3
"""
Simple test script to test workflow execution with fixed configuration
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor

def test_workflow_execution():
    """Test workflow execution with Instagram posting"""
    print("🔍 Testing Workflow Execution")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Load the test workflow
    with open('test_workflow_real_instagram.json', 'r') as f:
        workflow_data = json.load(f)
    
    print(f"Workflow: {workflow_data['workflow_name']}")
    print(f"Nodes: {[node['type'] for node in workflow_data['nodes']]}")
    
    # Check node configurations
    for i, node in enumerate(workflow_data['nodes']):
        print(f"Node {i+1} ({node['type']}): config = {node.get('config', {})}")
    
    # Initialize executor
    executor = LangGraphWorkflowExecutor()
    
    # Execute workflow
    input_data = {}
    result = executor.execute_workflow(workflow_data, input_data)
    
    print(f"\n✅ Workflow execution completed")
    print(f"Status: {result.get('status', 'unknown')}")
    
    # Check if Instagram posting was successful
    if 'instagram_post' in result:
        instagram_data = result['instagram_post']
        print(f"Instagram Post ID: {instagram_data.get('post_id', 'N/A')}")
        print(f"Real Post: {instagram_data.get('real_post', False)}")
        print(f"Content Length: {len(str(instagram_data.get('content', '')))}")
    
    return result

if __name__ == "__main__":
    test_workflow_execution()
