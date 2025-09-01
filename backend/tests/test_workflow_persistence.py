import os
import sys
import json
import unittest
import requests
from datetime import datetime

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from config.settings import get_settings
from models.workflow import Workflow
from database.session import get_db

class TestWorkflowPersistence(unittest.TestCase):
    """Test the workflow persistence functionality"""
    
    def setUp(self):
        """Set up the test environment"""
        self.settings = get_settings()
        self.base_url = f"http://localhost:{self.settings.PORT}/api"
        
        # Test user credentials
        self.test_user = {
            "username": "test_user",
            "password": "test_password"
        }
        
        # Login and get auth token
        self.auth_token = self._get_auth_token()
        
        # Test workflow data
        self.test_workflow = {
            "name": "Test Workflow",
            "description": "A test workflow for persistence testing",
            "nodes": [
                {
                    "id": "node1",
                    "type": "start",
                    "position": {"x": 100, "y": 100},
                    "data": {}
                },
                {
                    "id": "node2",
                    "type": "end",
                    "position": {"x": 300, "y": 100},
                    "data": {}
                }
            ],
            "edges": [
                {
                    "id": "edge1",
                    "source": "node1",
                    "target": "node2"
                }
            ],
            "is_public": False,
            "version": 1
        }
        
        # Clean up any existing test workflows
        self._cleanup_test_workflows()
    
    def tearDown(self):
        """Clean up after tests"""
        self._cleanup_test_workflows()
    
    def _get_auth_token(self):
        """Get authentication token for test user"""
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json=self.test_user
            )
            response.raise_for_status()
            return response.json()["access_token"]
        except requests.exceptions.RequestException as e:
            print(f"Failed to get auth token: {e}")
            print("Make sure the backend server is running and a test user exists")
            return None
    
    def _cleanup_test_workflows(self):
        """Clean up test workflows"""
        if not self.auth_token:
            return
            
        try:
            # Get all workflows
            response = requests.get(
                f"{self.base_url}/workflows",
                headers={"Authorization": f"Bearer {self.auth_token}"}
            )
            
            if response.status_code == 200:
                workflows = response.json().get("workflows", [])
                
                # Delete test workflows
                for workflow in workflows:
                    if workflow["name"] == self.test_workflow["name"]:
                        requests.delete(
                            f"{self.base_url}/workflows/{workflow['id']}?delete_all_versions=true",
                            headers={"Authorization": f"Bearer {self.auth_token}"}
                        )
        except Exception as e:
            print(f"Error cleaning up test workflows: {e}")
    
    def test_workflow_creation(self):
        """Test creating a new workflow"""
        if not self.auth_token:
            self.skipTest("No auth token available")
        
        # Create workflow
        response = requests.post(
            f"{self.base_url}/workflows",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=self.test_workflow
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["workflow_id"])
        
        # Store workflow ID for other tests
        self.workflow_id = data["workflow_id"]
        
        # Get the workflow to verify it was created
        response = requests.get(
            f"{self.base_url}/workflows/{self.workflow_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        workflow = response.json()
        self.assertEqual(workflow["name"], self.test_workflow["name"])
        self.assertEqual(workflow["version"], 1)
        self.assertEqual(workflow["is_public"], False)
    
    def test_workflow_versioning(self):
        """Test workflow versioning"""
        if not self.auth_token:
            self.skipTest("No auth token available")
        
        # Create initial workflow
        response = requests.post(
            f"{self.base_url}/workflows",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=self.test_workflow
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        workflow_id = data["workflow_id"]
        
        # Update workflow to create a new version
        updated_workflow = self.test_workflow.copy()
        updated_workflow["description"] = "Updated description for version 2"
        updated_workflow["nodes"].append({
            "id": "node3",
            "type": "process",
            "position": {"x": 200, "y": 200},
            "data": {"process_type": "test"}
        })
        
        response = requests.put(
            f"{self.base_url}/workflows/{workflow_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=updated_workflow
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        
        # Get workflow versions
        response = requests.get(
            f"{self.base_url}/workflows/{workflow_id}/versions",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        versions = response.json()["versions"]
        self.assertEqual(len(versions), 2)
        self.assertEqual(versions[0]["version"], 2)
        self.assertEqual(versions[1]["version"], 1)
        
        # Get specific version
        response = requests.get(
            f"{self.base_url}/workflows/{workflow_id}?version=1",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        workflow_v1 = response.json()
        self.assertEqual(workflow_v1["version"], 1)
        self.assertEqual(len(workflow_v1["nodes"]), 2)
        
        response = requests.get(
            f"{self.base_url}/workflows/{workflow_id}?version=2",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        workflow_v2 = response.json()
        self.assertEqual(workflow_v2["version"], 2)
        self.assertEqual(len(workflow_v2["nodes"]), 3)
        self.assertEqual(workflow_v2["description"], "Updated description for version 2")
    
    def test_workflow_sharing(self):
        """Test workflow sharing functionality"""
        if not self.auth_token:
            self.skipTest("No auth token available")
        
        # Create private workflow
        response = requests.post(
            f"{self.base_url}/workflows",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=self.test_workflow
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        workflow_id = data["workflow_id"]
        
        # Update workflow to make it public
        updated_workflow = self.test_workflow.copy()
        updated_workflow["is_public"] = True
        
        response = requests.put(
            f"{self.base_url}/workflows/{workflow_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=updated_workflow
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Get the workflow to verify it's public
        response = requests.get(
            f"{self.base_url}/workflows/{workflow_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        workflow = response.json()
        self.assertTrue(workflow["is_public"])
        
        # List workflows with public filter
        response = requests.get(
            f"{self.base_url}/workflows?include_public=true",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        workflows = response.json()["workflows"]
        public_workflows = [w for w in workflows if w["is_public"]]
        self.assertGreaterEqual(len(public_workflows), 1)
    
    def test_workflow_deletion(self):
        """Test workflow deletion"""
        if not self.auth_token:
            self.skipTest("No auth token available")
        
        # Create workflow
        response = requests.post(
            f"{self.base_url}/workflows",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=self.test_workflow
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        workflow_id = data["workflow_id"]
        
        # Update workflow to create a new version
        updated_workflow = self.test_workflow.copy()
        updated_workflow["description"] = "Updated description for version 2"
        
        response = requests.put(
            f"{self.base_url}/workflows/{workflow_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            json=updated_workflow
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Delete specific version
        response = requests.delete(
            f"{self.base_url}/workflows/{workflow_id}?version=1",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Check that only one version remains
        response = requests.get(
            f"{self.base_url}/workflows/{workflow_id}/versions",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        versions = response.json()["versions"]
        self.assertEqual(len(versions), 1)
        self.assertEqual(versions[0]["version"], 2)
        
        # Delete all versions
        response = requests.delete(
            f"{self.base_url}/workflows/{workflow_id}?delete_all_versions=true",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify workflow is deleted
        response = requests.get(
            f"{self.base_url}/workflows/{workflow_id}",
            headers={"Authorization": f"Bearer {self.auth_token}"}
        )
        
        self.assertEqual(response.status_code, 404)

if __name__ == "__main__":
    unittest.main()
