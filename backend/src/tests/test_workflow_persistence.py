import sys
import os
import json
import uuid
from datetime import datetime
import requests

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Test configuration
BASE_URL = "http://localhost:8000"  # Change if your API runs on a different port
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "password123"

def get_auth_token():
    """Get authentication token for API requests"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    )
    if response.status_code != 200:
        print(f"Failed to authenticate: {response.text}")
        return None
    return response.json().get("access_token")

def test_workflow_persistence():
    """Test workflow persistence functionality"""
    token = get_auth_token()
    if not token:
        print("Authentication failed, skipping tests")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: Create a new workflow
    workflow_id = str(uuid.uuid4())
    workflow_data = {
        "id": workflow_id,
        "name": "Test Workflow",
        "description": "A test workflow for persistence",
        "data": {
            "nodes": [
                {"id": "node1", "type": "start", "position": {"x": 100, "y": 100}},
                {"id": "node2", "type": "end", "position": {"x": 300, "y": 100}}
            ],
            "edges": [
                {"id": "edge1", "source": "node1", "target": "node2"}
            ]
        },
        "is_public": False,
        "version": 1
    }
    
    print("\n1. Creating new workflow...")
    response = requests.post(
        f"{BASE_URL}/api/workflows/save",
        json=workflow_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to create workflow: {response.text}")
        return False
    
    print(f"Workflow created: {response.json()}")
    
    # Test 2: Retrieve the workflow
    print("\n2. Retrieving workflow...")
    response = requests.get(
        f"{BASE_URL}/api/workflows/{workflow_id}",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to retrieve workflow: {response.text}")
        return False
    
    retrieved_workflow = response.json()
    print(f"Retrieved workflow: {json.dumps(retrieved_workflow, indent=2)}")
    
    # Test 3: Update the workflow (create a new version)
    print("\n3. Creating a new version of the workflow...")
    workflow_data["name"] = "Test Workflow v2"
    workflow_data["description"] = "An updated test workflow"
    workflow_data["version"] = 2
    
    response = requests.post(
        f"{BASE_URL}/api/workflows/save",
        json=workflow_data,
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to update workflow: {response.text}")
        return False
    
    updated_workflow_id = response.json().get("workflow_id")
    print(f"Updated workflow: {response.json()}")
    
    # Test 4: List all workflows
    print("\n4. Listing all workflows...")
    response = requests.get(
        f"{BASE_URL}/api/workflows",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to list workflows: {response.text}")
        return False
    
    workflows = response.json()
    print(f"Found {workflows.get('total')} workflows")
    
    # Test 5: Get workflow versions
    print("\n5. Getting workflow versions...")
    response = requests.get(
        f"{BASE_URL}/api/workflows/{workflow_id}/versions",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to get workflow versions: {response.text}")
        return False
    
    versions = response.json()
    print(f"Workflow versions: {json.dumps(versions, indent=2)}")
    
    # Test 6: Delete the workflow
    print("\n6. Deleting workflow...")
    response = requests.delete(
        f"{BASE_URL}/api/workflows/{workflow_id}?delete_versions=true",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to delete workflow: {response.text}")
        return False
    
    print(f"Workflow deleted: {response.json()}")
    
    print("\nAll tests passed successfully!")
    return True

if __name__ == "__main__":
    print("Testing workflow persistence functionality...")
    test_workflow_persistence()
