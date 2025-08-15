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
  const { selectedNode } = useWorkflowStore();

  if (!data) return null;

  const isSelected = selected || selectedNode === data.id;

  return (
    <div
      className={`
        relative min-w-[220px] max-w-[280px] p-3 rounded-lg border shadow-sm bg-white
        border-gray-200 hover:shadow-md transition-all duration-150
        ${isSelected ? 'ring-2 ring-gray-900/5 ring-offset-1' : ''}
        ${className}
      `}
    >
      {/* Input Handle */}
      <Handle
        type="target"
        position={Position.Left}
        id="target"
        className="w-2.5 h-2.5 bg-gray-800 border-2 border-white rounded-full"
      />

      {/* Node Header */}
      <div className="flex items-center gap-2 mb-1.5">
        {icon && (
          <div className="w-4 h-4 text-gray-800">
            {icon}
          </div>
        )}
        <h3 className="text-[13px] font-semibold text-gray-900 truncate">
          {data.label}
        </h3>
        <span 
          className="ml-2 px-1.5 py-0.5 text-[10px] font-medium bg-gray-100 text-gray-700 rounded"
          title={`Node Type: ${data.type}`}
        >
          {data.type}
        </span>
        <div className="ml-auto">
          <StatusIndicator status={data.status} />
        </div>
      </div>

      {/* Node Content */}
      <div className="text-[11px] text-gray-700 leading-relaxed">
        {children}
      </div>

      {/* Meta */}
      {(data.executionCount || 0) > 0 && (
        <div className="mt-2 text-[10px] text-gray-500">
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
        className="w-2.5 h-2.5 bg-gray-800 border-2 border-white rounded-full"
      />
    </div>
  );
};

const StatusIndicator: React.FC<{ status?: WorkflowNodeData['status'] }> = ({ status }) => {
  const statusConfig = {
    idle: { color: 'bg-gray-300', label: 'Idle' },
    running: { color: 'bg-blue-500 animate-pulse', label: 'Running' },
    success: { color: 'bg-green-500', label: 'Success' },
    error: { color: 'bg-red-500', label: 'Error' }
  } as const;

  const config = statusConfig[status || 'idle'];

  return (
    <div className="flex items-center gap-1">
      <div className={`w-2 h-2 rounded-full ${config.color}`} />
      <span className="text-[10px] text-gray-600">{config.label}</span>
    </div>
  );
}; 