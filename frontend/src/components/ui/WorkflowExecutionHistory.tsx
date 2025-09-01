import React, { useState, useEffect } from 'react';
import { 
  WorkflowExecutionHistoryItem, 
  WorkflowExecutionDetail 
} from '../../services/api';
import apiService from '../../services/api';
import { 
  Clock, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  ChevronRight, 
  ChevronDown, 
  Trash2,
  RefreshCw
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

interface WorkflowExecutionHistoryProps {
  workflowId: string;
  onRefresh?: () => void;
}

const WorkflowExecutionHistory: React.FC<WorkflowExecutionHistoryProps> = ({ 
  workflowId,
  onRefresh 
}) => {
  const [executions, setExecutions] = useState<WorkflowExecutionHistoryItem[]>([]);
  const [selectedExecution, setSelectedExecution] = useState<string | null>(null);
  const [executionDetail, setExecutionDetail] = useState<WorkflowExecutionDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [total, setTotal] = useState<number>(0);
  const [page, setPage] = useState<number>(0);
  const [limit] = useState<number>(10);

  const loadExecutions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiService.getWorkflowExecutions(workflowId, {
        limit,
        offset: page * limit
      });
      setExecutions(response.executions);
      setTotal(response.total);
    } catch (err) {
      setError('Failed to load execution history');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadExecutionDetail = async (executionId: string) => {
    try {
      const detail = await apiService.getWorkflowExecutionDetail(executionId);
      setExecutionDetail(detail);
    } catch (err) {
      console.error('Failed to load execution details:', err);
    }
  };

  const handleDeleteExecution = async (executionId: string, event: React.MouseEvent) => {
    event.stopPropagation();
    if (window.confirm('Are you sure you want to delete this execution record?')) {
      try {
        await apiService.deleteWorkflowExecution(executionId);
        loadExecutions();
        if (selectedExecution === executionId) {
          setSelectedExecution(null);
          setExecutionDetail(null);
        }
        if (onRefresh) onRefresh();
      } catch (err) {
        console.error('Failed to delete execution:', err);
      }
    }
  };

  const handleExecutionClick = (executionId: string) => {
    if (selectedExecution === executionId) {
      setSelectedExecution(null);
      setExecutionDetail(null);
    } else {
      setSelectedExecution(executionId);
      loadExecutionDetail(executionId);
    }
  };

  const handleRefresh = () => {
    loadExecutions();
    if (onRefresh) onRefresh();
  };

  useEffect(() => {
    if (workflowId) {
      loadExecutions();
    }
  }, [workflowId, page, limit]);

  const getStatusIcon = (status: string, hasError: boolean) => {
    switch (status) {
      case 'completed':
        return hasError ? <AlertTriangle className="text-yellow-500" /> : <CheckCircle className="text-green-500" />;
      case 'failed':
        return <XCircle className="text-red-500" />;
      case 'running':
        return <RefreshCw className="text-blue-500 animate-spin" />;
      default:
        return <Clock className="text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (e) {
      return dateString;
    }
  };

  const formatDuration = (ms?: number) => {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };

  if (loading && executions.length === 0) {
    return <div className="p-4 text-center">Loading execution history...</div>;
  }

  if (error) {
    return <div className="p-4 text-center text-red-500">{error}</div>;
  }

  if (executions.length === 0) {
    return (
      <div className="p-4 text-center text-gray-500">
        No execution history found for this workflow
      </div>
    );
  }

  return (
    <div className="bg-white rounded-md shadow">
      <div className="flex justify-between items-center p-4 border-b">
        <h3 className="text-lg font-medium">Execution History</h3>
        <button 
          onClick={handleRefresh}
          className="p-1 rounded hover:bg-gray-100"
          title="Refresh"
        >
          <RefreshCw size={18} />
        </button>
      </div>
      
      <div className="divide-y">
        {executions.map((execution) => (
          <div key={execution.id} className="cursor-pointer">
            <div 
              className="p-4 hover:bg-gray-50 flex items-center justify-between"
              onClick={() => handleExecutionClick(execution.id)}
            >
              <div className="flex items-center space-x-3">
                {selectedExecution === execution.id ? 
                  <ChevronDown size={18} /> : 
                  <ChevronRight size={18} />
                }
                {getStatusIcon(execution.status, execution.has_error)}
                <div>
                  <div className="font-medium">
                    {execution.status.charAt(0).toUpperCase() + execution.status.slice(1)}
                    {execution.has_error && <span className="text-yellow-600"> (with warnings)</span>}
                  </div>
                  <div className="text-sm text-gray-500">
                    {formatDate(execution.started_at)}
                    {execution.completed_at && ` • ${formatDuration(execution.duration_ms)}`}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <button
                  onClick={(e) => handleDeleteExecution(execution.id, e)}
                  className="p-1 rounded hover:bg-gray-200 text-gray-500"
                  title="Delete execution"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
            
            {selectedExecution === execution.id && executionDetail && (
              <div className="p-4 bg-gray-50 border-t">
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <div className="text-sm font-medium text-gray-500">Started</div>
                    <div>{new Date(executionDetail.started_at).toLocaleString()}</div>
                  </div>
                  {executionDetail.completed_at && (
                    <div>
                      <div className="text-sm font-medium text-gray-500">Completed</div>
                      <div>{new Date(executionDetail.completed_at).toLocaleString()}</div>
                    </div>
                  )}
                  <div>
                    <div className="text-sm font-medium text-gray-500">Duration</div>
                    <div>{formatDuration(executionDetail.duration_ms)}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-500">Nodes Executed</div>
                    <div>{executionDetail.node_count || 'N/A'}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-500">User</div>
                    <div>{executionDetail.user_id || 'Anonymous'}</div>
                  </div>
                </div>
                
                {executionDetail.error && (
                  <div className="mb-4">
                    <div className="text-sm font-medium text-gray-500 mb-1">Error</div>
                    <div className="p-3 bg-red-50 text-red-700 rounded border border-red-200 whitespace-pre-wrap">
                      {executionDetail.error}
                    </div>
                  </div>
                )}
                
                {executionDetail.input_data && (
                  <div className="mb-4">
                    <div className="text-sm font-medium text-gray-500 mb-1">Input Data</div>
                    <pre className="p-3 bg-gray-100 rounded border border-gray-200 overflow-auto text-sm">
                      {JSON.stringify(executionDetail.input_data, null, 2)}
                    </pre>
                  </div>
                )}
                
                {executionDetail.results && (
                  <div>
                    <div className="text-sm font-medium text-gray-500 mb-1">Results</div>
                    <pre className="p-3 bg-gray-100 rounded border border-gray-200 overflow-auto text-sm">
                      {JSON.stringify(executionDetail.results, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {total > limit && (
        <div className="p-4 border-t flex justify-between items-center">
          <button 
            onClick={() => setPage(Math.max(0, page - 1))}
            disabled={page === 0}
            className={`px-3 py-1 rounded ${page === 0 ? 'text-gray-400' : 'text-blue-600 hover:bg-blue-50'}`}
          >
            Previous
          </button>
          <span className="text-sm text-gray-500">
            Page {page + 1} of {Math.ceil(total / limit)}
          </span>
          <button 
            onClick={() => setPage(Math.min(Math.ceil(total / limit) - 1, page + 1))}
            disabled={page >= Math.ceil(total / limit) - 1}
            className={`px-3 py-1 rounded ${page >= Math.ceil(total / limit) - 1 ? 'text-gray-400' : 'text-blue-600 hover:bg-blue-50'}`}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
};

export default WorkflowExecutionHistory;
