import pytest
import uuid
import json
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.main import app
from src.services.models import Execution as ExecutionModel
from src.models.workflow import Workflow as WorkflowModel
from src.models.workflow import WorkflowPermission

# Test client
client = TestClient(app)

# Mock user data
TEST_USER_ID = "test_user_123"
TEST_OTHER_USER_ID = "other_user_456"
TEST_ADMIN_USER_ID = "admin_user_789"

# Mock auth header
def get_auth_header(user_id):
    return {"Authorization": f"Bearer test_token_{user_id}"}

# Test data
def create_test_workflow(db: Session):
    """Create a test workflow in the database"""
    workflow_id = str(uuid.uuid4())
    workflow = WorkflowModel(
        id=workflow_id,
        name="Test Workflow",
        description="Test workflow for execution history",
        user_id=TEST_USER_ID,
        is_public=False,
        version=1,
        data={"nodes": [], "edges": []}
    )
    db.add(workflow)
    db.commit()
    return workflow

def create_test_public_workflow(db: Session):
    """Create a public test workflow in the database"""
    workflow_id = str(uuid.uuid4())
    workflow = WorkflowModel(
        id=workflow_id,
        name="Public Test Workflow",
        description="Public test workflow for execution history",
        user_id=TEST_USER_ID,
        is_public=True,
        version=1,
        data={"nodes": [], "edges": []}
    )
    db.add(workflow)
    db.commit()
    return workflow

def create_test_shared_workflow(db: Session):
    """Create a shared test workflow in the database"""
    workflow_id = str(uuid.uuid4())
    workflow = WorkflowModel(
        id=workflow_id,
        name="Shared Test Workflow",
        description="Shared test workflow for execution history",
        user_id=TEST_USER_ID,
        is_public=False,
        version=1,
        data={"nodes": [], "edges": []}
    )
    db.add(workflow)
    
    # Add permission for other user
    permission = WorkflowPermission(
        workflow_id=workflow_id,
        user_id=TEST_OTHER_USER_ID,
        permission="read"
    )
    db.add(permission)
    db.commit()
    return workflow

def create_test_executions(db: Session, workflow_id: str, count: int = 5):
    """Create test execution records for a workflow"""
    executions = []
    now = datetime.utcnow()
    
    for i in range(count):
        execution_id = f"exec_{uuid.uuid4()}"
        started_at = now - timedelta(hours=i)
        finished_at = started_at + timedelta(minutes=5)
        
        execution = ExecutionModel(
            id=execution_id,
            workflow_id=workflow_id,
            user_id=TEST_USER_ID,
            status="completed" if i % 3 != 0 else "failed",
            result={
                "status": "completed" if i % 3 != 0 else "failed",
                "error": "Test error" if i % 3 == 0 else None,
                "nodes_executed": ["node1", "node2", "node3"],
                "execution_id": execution_id,
                "start_time": started_at.isoformat(),
            },
            nodes_executed=3,
            started_at=started_at,
            finished_at=finished_at
        )
        db.add(execution)
        executions.append(execution)
    
    db.commit()
    return executions

# Tests
def test_get_workflow_executions_owner(db: Session):
    """Test getting workflow executions as the workflow owner"""
    # Create test data
    workflow = create_test_workflow(db)
    executions = create_test_executions(db, workflow.id, 5)
    
    # Make request
    response = client.get(
        f"/api/workflows/{workflow.id}/executions",
        headers=get_auth_header(TEST_USER_ID)
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "executions" in data
    assert len(data["executions"]) == 5
    assert data["total"] == 5
    
    # Verify execution data
    first_execution = data["executions"][0]
    assert "id" in first_execution
    assert "workflow_id" in first_execution
    assert "user_id" in first_execution
    assert first_execution["user_id"] == TEST_USER_ID
    assert "status" in first_execution
    assert "started_at" in first_execution
    assert "finished_at" in first_execution
    assert "duration_ms" in first_execution

def test_get_workflow_executions_public(db: Session):
    """Test getting workflow executions for a public workflow"""
    # Create test data
    workflow = create_test_public_workflow(db)
    executions = create_test_executions(db, workflow.id, 3)
    
    # Make request as different user
    response = client.get(
        f"/api/workflows/{workflow.id}/executions",
        headers=get_auth_header(TEST_OTHER_USER_ID)
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "executions" in data
    assert len(data["executions"]) == 3

def test_get_workflow_executions_shared(db: Session):
    """Test getting workflow executions for a shared workflow"""
    # Create test data
    workflow = create_test_shared_workflow(db)
    executions = create_test_executions(db, workflow.id, 2)
    
    # Make request as user with permission
    response = client.get(
        f"/api/workflows/{workflow.id}/executions",
        headers=get_auth_header(TEST_OTHER_USER_ID)
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "executions" in data
    assert len(data["executions"]) == 2

def test_get_workflow_executions_unauthorized(db: Session):
    """Test getting workflow executions without permission"""
    # Create test data
    workflow = create_test_workflow(db)
    executions = create_test_executions(db, workflow.id, 1)
    
    # Make request as different user without permission
    response = client.get(
        f"/api/workflows/{workflow.id}/executions",
        headers=get_auth_header(TEST_OTHER_USER_ID)
    )
    
    # Verify response
    assert response.status_code == 403

def test_get_workflow_executions_with_status_filter(db: Session):
    """Test getting workflow executions with status filter"""
    # Create test data
    workflow = create_test_workflow(db)
    executions = create_test_executions(db, workflow.id, 6)  # Will create 2 failed executions
    
    # Make request with status filter
    response = client.get(
        f"/api/workflows/{workflow.id}/executions?status=failed",
        headers=get_auth_header(TEST_USER_ID)
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "executions" in data
    assert len(data["executions"]) == 2
    assert all(exec["status"] == "failed" for exec in data["executions"])

def test_get_execution_details(db: Session):
    """Test getting execution details"""
    # Create test data
    workflow = create_test_workflow(db)
    executions = create_test_executions(db, workflow.id, 1)
    execution_id = executions[0].id
    
    # Make request
    response = client.get(
        f"/api/executions/{execution_id}",
        headers=get_auth_header(TEST_USER_ID)
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == execution_id
    assert data["workflow_id"] == workflow.id
    assert data["user_id"] == TEST_USER_ID
    assert "status" in data
    assert "started_at" in data
    assert "finished_at" in data
    assert "duration_ms" in data
    assert "result" in data

def test_delete_execution(db: Session):
    """Test deleting an execution"""
    # Create test data
    workflow = create_test_workflow(db)
    executions = create_test_executions(db, workflow.id, 1)
    execution_id = executions[0].id
    
    # Make request
    response = client.delete(
        f"/api/executions/{execution_id}",
        headers=get_auth_header(TEST_USER_ID)
    )
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    
    # Verify execution is deleted
    response = client.get(
        f"/api/executions/{execution_id}",
        headers=get_auth_header(TEST_USER_ID)
    )
    assert response.status_code == 404

def test_delete_execution_unauthorized(db: Session):
    """Test deleting an execution without permission"""
    # Create test data
    workflow = create_test_workflow(db)
    executions = create_test_executions(db, workflow.id, 1)
    execution_id = executions[0].id
    
    # Make request as different user
    response = client.delete(
        f"/api/executions/{execution_id}",
        headers=get_auth_header(TEST_OTHER_USER_ID)
    )
    
    # Verify response
    assert response.status_code == 403
