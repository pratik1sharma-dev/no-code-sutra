import React from 'react';
import { NodeProps } from 'reactflow';
import { Bot, Settings, Play } from 'lucide-react';
import { BaseNode } from './BaseNode';
import { WorkflowNodeData } from '../../../types/workflow';
import { useWorkflowStore } from '../../../stores/workflowStore';

export const AIAgentNode: React.FC<NodeProps<WorkflowNodeData>> = (props) => {
  const { data } = props;
  const { updateNode } = useWorkflowStore();

  // Add null checks for data and config
  if (!data) {
    console.warn('AIAgentNode: data is undefined', props);
    return null;
  }

  const config = data.config || {};
  const model = config?.model || 'GPT-4';
  const temperature = config?.temperature || 0.7;

  return (
    <BaseNode
      {...props}
      icon={<Bot className="w-4 h-4" />}
      color="primary"
      className="min-w-[250px]"
    >
      <div className="space-y-2">
        {/* Model Info */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium">Model:</span>
          <span className="text-xs bg-primary-100 px-2 py-1 rounded">
            {model}
          </span>
        </div>

        {/* Temperature */}
        <div className="flex items-center justify-between">
          <span className="text-xs font-medium">Temperature:</span>
          <span className="text-xs bg-secondary-100 px-2 py-1 rounded">
            {temperature}
          </span>
        </div>

        {/* Prompt Preview */}
        {config?.prompt && (
          <div className="mt-2">
            <span className="text-xs font-medium block mb-1">Prompt:</span>
            <div className="text-xs bg-gray-50 p-2 rounded border max-h-16 overflow-y-auto">
              {config.prompt.length > 100 
                ? `${config.prompt.substring(0, 100)}...`
                : config.prompt
              }
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-1 mt-3">
          <button
            className="flex-1 btn btn-sm btn-primary"
            onClick={() => {
              // TODO: Implement node testing
              console.log('Test AI Agent node');
            }}
          >
            <Play className="w-3 h-3 mr-1" />
            Test
          </button>
          <button
            className="btn btn-sm btn-outline"
            onClick={() => {
              // TODO: Open configuration modal
              console.log('Configure AI Agent node');
            }}
          >
            <Settings className="w-3 h-3" />
          </button>
        </div>
      </div>
    </BaseNode>
  );
}; 