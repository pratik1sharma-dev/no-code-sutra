import React from 'react';
import type { NodeProps } from 'reactflow';
import { Instagram } from 'lucide-react';
import type { WorkflowNodeData } from '../../../types/workflow';
import { BaseNode } from './BaseNode';

export const InstagramPostNode: React.FC<NodeProps<WorkflowNodeData>> = (props) => {
  const { data } = props;

  return (
    <BaseNode
      {...props}
      icon={<Instagram className="w-4 h-4" />}
      color="pink"
    >
      <div className="text-xs text-gray-500">
        Post AI-generated content to Instagram Business accounts
      </div>
      
      {/* Configuration Display */}
      {data.config.instagram_credentials && (
        <div className="mt-2 p-2 bg-pink-50 rounded text-xs">
          <div className="font-medium text-pink-700">Instagram Account</div>
          <div className="text-pink-600">
            ID: {data.config.instagram_credentials.instagram_business_account_id}
          </div>
          {data.config.scheduled_time && (
            <div className="text-pink-600">
              Scheduled: {data.config.scheduled_time}
            </div>
          )}
        </div>
      )}
      
      {/* Status Display */}
      <div className="mt-2 flex items-center justify-between text-xs">
        <span className={`px-2 py-1 rounded ${
          data.status === 'success' ? 'bg-green-100 text-green-700' :
          data.status === 'error' ? 'bg-red-100 text-red-700' :
          data.status === 'running' ? 'bg-blue-100 text-blue-700' :
          'bg-gray-100 text-gray-700'
        }`}>
          {data.status}
        </span>
        {data.executionCount > 0 && (
          <span className="text-gray-500">
            {data.executionCount} exec
          </span>
        )}
      </div>
    </BaseNode>
  );
};
