# Workflow Persistence API Documentation

This document describes the API endpoints for workflow persistence in the No-Code Sutra platform.

## Data Models

### Workflow Model

The workflow model has been enhanced with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| id | String | Primary key, unique identifier for the workflow |
| name | String | Name of the workflow |
| description | String | Optional description of the workflow |
| user_id | String | ID of the user who owns this workflow |
| data | JSON | The workflow definition including nodes, edges, and other metadata |
| is_public | Boolean | Whether this workflow is publicly accessible |
| version | Integer | Version number of this workflow |
| parent_id | String | ID of the parent workflow if this is a version |
| created_at | DateTime | When the workflow was created |
| updated_at | DateTime | When the workflow was last updated |

## API Endpoints

### Save Workflow

Saves a new workflow or updates an existing one with versioning support.

**Endpoint:** `POST /api/workflows/save`

**Authentication:** Required

**Request Body:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "data": {},
  "is_public": false,
  "version": 1,
  "parent_id": null
}
```

**Response:**
```json
{
  "success": true,
  "workflow_id": "string",
  "version": 1,
  "parent_id": "string"
}
```

### List Workflows

Lists workflows with filtering options.

**Endpoint:** `GET /api/workflows`

**Authentication:** Optional

**Query Parameters:**
- `user_id` (optional): Filter by owner
- `limit` (optional): Maximum number of workflows to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)
- `include_public` (optional): Include public workflows from other users (default: true)
- `show_versions` (optional): Show all versions (default: false)

**Response:**
```json
{
  "workflows": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "user_id": "string",
      "is_public": false,
      "version": 1,
      "parent_id": "string",
      "created_at": "string",
      "updated_at": "string",
      "node_count": 0,
      "status": "draft"
    }
  ],
  "total": 0,
  "limit": 50,
  "offset": 0,
  "filters": {
    "user_id": "string",
    "include_public": true,
    "show_versions": false
  }
}
```

### Get Workflow

Retrieves a specific workflow by ID with permission checks.

**Endpoint:** `GET /api/workflows/{workflow_id}`

**Authentication:** Optional

**Path Parameters:**
- `workflow_id`: ID of the workflow to retrieve

**Response:**
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "user_id": "string",
  "is_public": false,
  "version": 1,
  "parent_id": "string",
  "data": {},
  "created_at": "string",
  "updated_at": "string",
  "versions": [
    {
      "id": "string",
      "version": 1,
      "updated_at": "string"
    }
  ]
}
```

### Delete Workflow

Deletes a workflow by ID with permission checks.

**Endpoint:** `DELETE /api/workflows/{workflow_id}`

**Authentication:** Required

**Path Parameters:**
- `workflow_id`: ID of the workflow to delete

**Query Parameters:**
- `delete_versions` (optional): If true, also delete all versions of this workflow (default: false)

**Response:**
```json
{
  "success": true,
  "message": "Workflow deleted successfully",
  "deleted_count": 1,
  "deleted_versions": [
    {
      "id": "string",
      "version": 1
    }
  ]
}
```

### Get Workflow Versions

Retrieves version history for a workflow.

**Endpoint:** `GET /api/workflows/{workflow_id}/versions`

**Authentication:** Optional

**Path Parameters:**
- `workflow_id`: ID of the workflow to get versions for

**Query Parameters:**
- `include_data` (optional): If true, include the full workflow data for each version (default: false)

**Response:**
```json
{
  "workflow_id": "string",
  "current_version": 1,
  "total_versions": 1,
  "versions": [
    {
      "id": "string",
      "version": 1,
      "name": "string",
      "description": "string",
      "updated_at": "string",
      "created_at": "string",
      "is_current": true,
      "data": {}
    }
  ]
}
```

## Authentication and Permissions

- Workflows are associated with users via the `user_id` field
- Users can only modify their own workflows
- Users can view public workflows from other users
- Authentication is handled via JWT tokens
- API endpoints use the `get_current_user` dependency for authentication

## Versioning

- When updating a workflow, a new version is created with an incremented version number
- The original workflow is preserved as the parent
- Version history can be retrieved via the `/api/workflows/{workflow_id}/versions` endpoint
- Versions are linked to their parent workflow via the `parent_id` field
