"""
API endpoints for workflow execution history
"""

from flask import Blueprint, request, jsonify, g
from sqlalchemy import desc
from sqlalchemy.orm import Session

from ..models.workflow import WorkflowExecution, Workflow
from ..middleware.auth import auth_required
from ..middleware.rate_limiter import rate_limit
from ..services.db import get_db_session

workflow_executions_bp = Blueprint('workflow_executions', __name__)


@workflow_executions_bp.route('/api/workflows/<workflow_id>/executions', methods=['GET'])
@auth_required
@rate_limit()
def list_workflow_executions(workflow_id):
    """
    List execution history for a specific workflow
    
    Parameters:
    - workflow_id: ID of the workflow
    
    Query Parameters:
    - limit: Maximum number of executions to return (default: 10)
    - offset: Offset for pagination (default: 0)
    - status: Filter by status (optional: 'pending', 'running', 'completed', 'failed')
    
    Returns:
    - List of workflow executions
    """
    user_id = g.user.get('user_id')
    limit = int(request.args.get('limit', 10))
    offset = int(request.args.get('offset', 0))
    status = request.args.get('status')
    
    session: Session = get_db_session()
    
    # Check if user has access to the workflow
    workflow = session.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not workflow:
        return jsonify({"error": "Workflow not found"}), 404
    
    # Check if user has permission to view this workflow's executions
    if workflow.user_id != user_id and not workflow.is_public:
        return jsonify({"error": "You don't have permission to view this workflow's executions"}), 403
    
    # Build query
    query = session.query(WorkflowExecution).filter(WorkflowExecution.workflow_id == workflow_id)
    
    # Apply status filter if provided
    if status:
        query = query.filter(WorkflowExecution.status == status)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination and order by most recent first
    executions = query.order_by(desc(WorkflowExecution.started_at)).limit(limit).offset(offset).all()
    
    # Format response
    result = {
        "executions": [
            {
                "id": execution.id,
                "workflow_id": execution.workflow_id,
                "status": execution.status,
                "started_at": execution.started_at.isoformat() if execution.started_at else None,
                "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
                "duration_ms": execution.duration_ms,
                "node_count": execution.node_count,
                "has_error": bool(execution.error)
            } for execution in executions
        ],
        "total": total_count,
        "limit": limit,
        "offset": offset
    }
    
    return jsonify(result)


@workflow_executions_bp.route('/api/workflow-executions/<execution_id>', methods=['GET'])
@auth_required
@rate_limit()
def get_workflow_execution(execution_id):
    """
    Get details of a specific workflow execution
    
    Parameters:
    - execution_id: ID of the workflow execution
    
    Returns:
    - Workflow execution details including results
    """
    user_id = g.user.get('user_id')
    
    session: Session = get_db_session()
    
    # Get the execution
    execution = session.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
    if not execution:
        return jsonify({"error": "Workflow execution not found"}), 404
    
    # Get the workflow to check permissions
    workflow = session.query(Workflow).filter(Workflow.id == execution.workflow_id).first()
    if not workflow:
        return jsonify({"error": "Associated workflow not found"}), 404
    
    # Check if user has permission to view this execution
    if execution.user_id != user_id and workflow.user_id != user_id and not workflow.is_public:
        return jsonify({"error": "You don't have permission to view this execution"}), 403
    
    # Format response
    result = {
        "id": execution.id,
        "workflow_id": execution.workflow_id,
        "workflow_name": workflow.name,
        "user_id": execution.user_id,
        "status": execution.status,
        "started_at": execution.started_at.isoformat() if execution.started_at else None,
        "completed_at": execution.completed_at.isoformat() if execution.completed_at else None,
        "duration_ms": execution.duration_ms,
        "node_count": execution.node_count,
        "input_data": execution.input_data,
        "results": execution.results,
        "error": execution.error
    }
    
    return jsonify(result)


@workflow_executions_bp.route('/api/workflow-executions/<execution_id>', methods=['DELETE'])
@auth_required
@rate_limit()
def delete_workflow_execution(execution_id):
    """
    Delete a specific workflow execution
    
    Parameters:
    - execution_id: ID of the workflow execution
    
    Returns:
    - Success message
    """
    user_id = g.user.get('user_id')
    
    session: Session = get_db_session()
    
    # Get the execution
    execution = session.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
    if not execution:
        return jsonify({"error": "Workflow execution not found"}), 404
    
    # Check if user has permission to delete this execution
    if execution.user_id != user_id:
        return jsonify({"error": "You don't have permission to delete this execution"}), 403
    
    # Delete the execution
    session.delete(execution)
    session.commit()
    
    return jsonify({"success": True, "message": "Workflow execution deleted successfully"})
