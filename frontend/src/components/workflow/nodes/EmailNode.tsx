import React from 'react';
import { NodeProps } from 'reactflow';
import { Mail, Settings, Play, User } from 'lucide-react';
import { BaseNode } from './BaseNode';
import { WorkflowNodeData } from '../../../types/workflow';

export const EmailNode: React.FC<NodeProps<WorkflowNodeData>> = (props) => {
  const { data } = props;
  
  // Add null checks for data and config
  if (!data) {
    console.warn('EmailNode: data is undefined', props);
    return null;
  }

  const config = data.config || {};

  return (
    <BaseNode
      {...props}
      icon={<Mail className="w-4 h-4" />}
      color="success"
      className="min-w-[250px]"
    >
      <div className="space-y-2">
        {/* Recipient */}
        <div className="flex items-center gap-2">
          <User className="w-3 h-3 text-gray-500" />
          <span className="text-xs font-medium">To:</span>
          <span className="text-xs bg-success-100 px-2 py-1 rounded truncate max-w-[120px]">
            {config?.to || 'Not set'}
          </span>
        </div>

        {/* Subject */}
        {config?.subject && (
          <div className="mt-2">
            <span className="text-xs font-medium block mb-1">Subject:</span>
            <div className="text-xs bg-gray-50 p-2 rounded border max-h-12 overflow-y-auto">
              {config.subject.length > 50 
                ? `${config.subject.substring(0, 50)}...`
                : config.subject
              }
            </div>
          </div>
        )}

        {/* Template Info */}
        {config?.template && (
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium">Template:</span>
            <span className="text-xs bg-secondary-100 px-2 py-1 rounded">
              {config.template}
            </span>
          </div>
        )}

        {/* Variables */}
        {config?.variables && Object.keys(config.variables).length > 0 && (
          <div className="mt-2">
            <span className="text-xs font-medium block mb-1">Variables:</span>
            <div className="text-xs text-gray-600">
              {Object.keys(config.variables).slice(0, 2).join(', ')}
              {Object.keys(config.variables).length > 2 && '...'}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-1 mt-3">
          <button
            className="flex-1 btn btn-sm btn-success"
            onClick={() => {
              // TODO: Implement email testing
              console.log('Test Email node');
            }}
          >
            <Play className="w-3 h-3 mr-1" />
            Test
          </button>
          <button
            className="btn btn-sm btn-outline"
            onClick={() => {
              // TODO: Open configuration modal
              console.log('Configure Email node');
            }}
          >
            <Settings className="w-3 h-3" />
          </button>
        </div>
      </div>
    </BaseNode>
  );
}; 