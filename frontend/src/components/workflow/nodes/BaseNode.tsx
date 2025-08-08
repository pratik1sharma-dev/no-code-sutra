import React from 'react';
import { Handle, Position, NodeProps } from 'reactflow';
import { WorkflowNodeData } from '../../../types/workflow';
import { useWorkflowStore } from '../../../stores/workflowStore';

interface BaseNodeProps extends NodeProps<WorkflowNodeData> {
  children?: React.ReactNode;
  className?: string;
  icon?: React.ReactNode;
  color?: string;
}

export const BaseNode: React.FC<BaseNodeProps> = ({
  data,
  selected,
  children,
  className = '',
  icon,
  color = 'primary'
}) => {
  const { selectedNode, updateNode } = useWorkflowStore();

  // Add null check for data
  if (!data) {
    console.warn('BaseNode: data is undefined');
    return null;
  }

  const isSelected = selected || selectedNode === data.id;
  const statusColor = {
    idle: 'border-gray-300',
    running: 'border-blue-500',
    success: 'border-green-500',
    error: 'border-red-500'
  }[data.status || 'idle'];

  const colorClasses = {
    primary: 'bg-primary-50 border-primary-200 text-primary-700',
    secondary: 'bg-secondary-50 border-secondary-200 text-secondary-700',
    success: 'bg-success-50 border-success-200 text-success-700',
    warning: 'bg-warning-50 border-warning-200 text-warning-700',
    danger: 'bg-danger-50 border-danger-200 text-danger-700'
  }[color];

  return (
    <div
      className={`
        relative min-w-[200px] p-4 rounded-lg border-2 shadow-sm
        ${colorClasses}
        ${statusColor}
        ${isSelected ? 'ring-2 ring-primary-500 ring-offset-2' : ''}
        ${className}
        transition-all duration-200 hover:shadow-md
      `}
    >
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        id="target"
        className="w-3 h-3 bg-primary-500 border-2 border-white"
      />

      {/* Node Header */}
      <div className="flex items-center gap-2 mb-2">
        {icon && (
          <div className="w-5 h-5 text-primary-600">
            {icon}
          </div>
        )}
        <h3 className="text-sm font-semibold truncate">
          {data.label}
        </h3>
        {/* Node Type Badge */}
        <span 
          className="ml-2 px-2 py-0.5 text-xs font-medium bg-gray-200 text-gray-700 rounded-full"
          title={`Node Type: ${data.type}`}
        >
          {data.type}
        </span>
        <div className="ml-auto">
          <StatusIndicator status={data.status} />
        </div>
      </div>

      {/* Node Content */}
      <div className="text-xs text-gray-600">
        {children}
      </div>

      {/* Execution Info */}
      {(data.executionCount || 0) > 0 && (
        <div className="mt-2 text-xs text-gray-500">
          Executed {data.executionCount || 0} times
          {data.lastExecution && (
            <div>
              Last: {new Date(data.lastExecution).toLocaleDateString()}
            </div>
          )}
        </div>
      )}

      {/* Output Handle */}
      <Handle
        type="source"
        position={Position.Right}
        className="w-3 h-3 bg-primary-500 border-2 border-white"
      />
    </div>
  );
};

const StatusIndicator: React.FC<{ status?: WorkflowNodeData['status'] }> = ({ status }) => {
  const statusConfig = {
    idle: { color: 'bg-gray-400', label: 'Idle' },
    running: { color: 'bg-blue-500 animate-pulse', label: 'Running' },
    success: { color: 'bg-green-500', label: 'Success' },
    error: { color: 'bg-red-500', label: 'Error' }
  };

  const config = statusConfig[status || 'idle'];

  return (
    <div className="flex items-center gap-1">
      <div className={`w-2 h-2 rounded-full ${config.color}`} />
      <span className="text-xs text-gray-600">{config.label}</span>
    </div>
  );
}; 