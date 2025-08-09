#!/usr/bin/env python3
"""
Test script to verify workflow execution with fixed data passing
"""

import json
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.langgraph_workflows.workflow_executor import LangGraphWorkflowExecutor

def test_workflow_execution():
    """Test the workflow execution with the fixed data passing"""
    
    # Load the test workflow
    with open('test_workflow_fixed.json', 'r') as f:
        workflow_data = json.load(f)
    
    print("Testing workflow execution with fixed data passing...")
    print(f"Workflow: {workflow_data['name']}")
    print(f"Nodes: {len(workflow_data['nodes'])}")
    print(f"Edges: {len(workflow_data['edges'])}")
    
    # Initialize the executor
    executor = LangGraphWorkflowExecutor()
    
    # Test input data
    input_data = {
        'test_input': 'This is a test input',
        'platform': 'instagram'
    }
    
    try:
        # Execute the workflow
        print("\nExecuting workflow...")
        result = executor.execute_workflow(workflow_data, input_data)
        
        print("\nWorkflow execution completed!")
        print(f"Status: {result.get('status')}")
        print(f"Execution ID: {result.get('execution_id')}")
        
        # Show node results
        if 'node_results' in result:
            print("\nNode Results:")
            for node_id, node_result in result['node_results'].items():
                print(f"  {node_id}: {node_result.get('status')} - {node_result.get('node_type')}")
                if 'output' in node_result:
                    print(f"    Output: {str(node_result['output'])[:100]}...")
        
        # Show final state
        print(f"\nFinal state keys: {list(result.keys())}")
        
        return result
        
    except Exception as e:
        print(f"Error executing workflow: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_workflow_execution()
