# Workflow Execution History API

This document describes the API endpoints for managing workflow execution history.

## Endpoints

### Get Workflow Executions

Retrieves execution history for a specific workflow with filtering options.

**URL**: `/api/workflows/{workflow_id}/executions`

**Method**: `GET`

**Auth required**: Yes

**Query Parameters**:
- `limit` (optional): Maximum number of executions to return (default: 20)
- `offset` (optional): Pagination offset (default: 0)
- `status` (optional): Filter by execution status (e.g., "completed", "failed", "running")

**Permissions**:
- User must own the workflow, or
- Workflow must be public, or
- User must have explicit read/write/admin/execute permission on the workflow

**Success Response**:
```json
{
  "executions": [
    {
      "id": "exec_123",
      "workflow_id": "workflow_456",
      "user_id": "user_789",
      "status": "completed",
      "nodes_executed": 5,
      "started_at": "2025-08-31T12:00:00.000Z",
      "finished_at": "2025-08-31T12:01:30.000Z",
      "duration_ms": 90000,
      "result_summary": {
        "success": true,
        "error": null
      }
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0,
  "status_filter": "completed"
}
```

### Get Execution Details

Retrieves detailed information about a specific workflow execution.

**URL**: `/api/executions/{execution_id}`

**Method**: `GET`

**Auth required**: Yes

**Permissions**:
- User must own the execution, or
- User must own the associated workflow, or
- Associated workflow must be public, or
- User must have explicit read/write/admin/execute permission on the associated workflow

**Success Response**:
```json
{
  "id": "exec_123",
  "workflow_id": "workflow_456",
  "user_id": "user_789",
  "status": "completed",
  "nodes_executed": 5,
  "started_at": "2025-08-31T12:00:00.000Z",
  "finished_at": "2025-08-31T12:01:30.000Z",
  "duration_ms": 90000,
  "result": {
    "status": "completed",
    "nodes_executed": ["node1", "node2", "node3", "node4", "node5"],
    "execution_id": "exec_123",
    "start_time": "2025-08-31T12:00:00.000Z",
    "outputs": {
      "node1": { "result": "value1" },
      "node2": { "result": "value2" }
    }
  }
}
```

### Delete Execution

Deletes a specific workflow execution record.

**URL**: `/api/executions/{execution_id}`

**Method**: `DELETE`

**Auth required**: Yes

**Permissions**:
- User must own the execution, or
- User must own the associated workflow, or
- User must have admin permission on the associated workflow

**Success Response**:
```json
{
  "success": true,
  "message": "Execution record deleted successfully"
}
```

## Data Models

### Execution Model

```python
class Execution(Base):
    __tablename__ = "executions"
    id = Column(String, primary_key=True)
    workflow_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    status = Column(String, default="running", index=True)
    result = Column(JSONB)
    nodes_executed = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    finished_at = Column(DateTime)
    
    # Indexes for common query patterns
    __table_args__ = (
        Index('idx_execution_workflow_user', 'workflow_id', 'user_id'),
        Index('idx_execution_status_time', 'status', 'started_at'),
    )
```

## Security Considerations

- All endpoints require authentication
- Rate limiting is applied to prevent abuse
- Permission checks ensure users can only access executions they are authorized to view
- Execution results are stored as JSONB in PostgreSQL for efficient storage and querying
- Sensitive data in execution results should be handled according to data privacy policies
