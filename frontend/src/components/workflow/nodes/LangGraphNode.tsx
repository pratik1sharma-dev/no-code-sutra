import React, { useState, useEffect } from 'react';
import { NodeProps } from 'reactflow';
import { Bot, Play, Settings, CheckCircle, AlertCircle, Clock } from 'lucide-react';
import { BaseNode } from './BaseNode';
import { WorkflowNodeData } from '../../../types/workflow';

interface LangGraphNodeData extends WorkflowNodeData {
  config: {
    workflow_type?: string;
    input_data?: Record<string, any>;
    node_type?: 'research' | 'analyze' | 'score' | 'route';
  };
  execution_result?: {
    success: boolean;
    data: Record<string, any>;
    execution_time: number;
    timestamp: string;
  };
}

export const LangGraphNode: React.FC<NodeProps<LangGraphNodeData>> = (props) => {
  const { data } = props;
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionStatus, setExecutionStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');

  const config = data?.config || {};
  const result = data?.execution_result;

  const getNodeIcon = () => {
    switch (config.node_type) {
      case 'research':
        return <Bot className="w-4 h-4 text-blue-500" />;
      case 'analyze':
        return <Bot className="w-4 h-4 text-green-500" />;
      case 'score':
        return <Bot className="w-4 h-4 text-yellow-500" />;
      case 'route':
        return <Bot className="w-4 h-4 text-purple-500" />;
      default:
        return <Bot className="w-4 h-4" />;
    }
  };

  const getNodeTitle = () => {
    switch (config.node_type) {
      case 'research':
        return 'Research Company';
      case 'analyze':
        return 'Analyze Lead';
      case 'score':
        return 'Score Lead';
      case 'route':
        return 'Route Lead';
      default:
        return 'AI Agent';
    }
  };

  const getNodeDescription = () => {
    switch (config.node_type) {
      case 'research':
        return 'AI-powered company research';
      case 'analyze':
        return 'AI analyzes lead quality';
      case 'score':
        return 'AI scores lead (0-100)';
      case 'route':
        return 'AI routes lead to appropriate path';
      default:
        return 'AI-powered processing';
    }
  };

  const handleExecute = async () => {
    if (!config.workflow_type || !config.input_data) {
      alert('Please configure the node with workflow type and input data');
      return;
    }

    setIsExecuting(true);
    setExecutionStatus('running');

    try {
      const response = await fetch('/api/langgraph/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          workflow_type: config.workflow_type,
          input_data: config.input_data
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to execute workflow');
      }

      const result = await response.json();
      setExecutionStatus(result.success ? 'completed' : 'error');
      
      // Update node data with result (this would typically be handled by the workflow store)
      console.log('Execution result:', result);
      
    } catch (error) {
      console.error('Execution failed:', error);
      setExecutionStatus('error');
    } finally {
      setIsExecuting(false);
    }
  };

  const renderExecutionResult = () => {
    if (!result) return null;

    return (
      <div className="space-y-2 mt-3">
        <div className="flex items-center gap-2">
          {result.success ? (
            <CheckCircle className="w-4 h-4 text-green-500" />
          ) : (
            <AlertCircle className="w-4 h-4 text-red-500" />
          )}
          <span className="text-xs font-medium">
            {result.success ? 'Completed' : 'Failed'}
          </span>
        </div>
        
        {result.execution_time && (
          <div className="text-xs text-gray-600">
            Execution time: {result.execution_time.toFixed(2)}s
          </div>
        )}
        
        {result.data && (
          <div className="text-xs">
            <div className="font-medium mb-1">Results:</div>
            <div className="bg-gray-50 p-2 rounded max-h-20 overflow-y-auto">
              <pre className="text-xs">
                {JSON.stringify(result.data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <BaseNode
      {...props}
      icon={getNodeIcon()}
      color="primary"
      className="min-w-[300px]"
    >
      <div className="space-y-3">
        {/* Node Info */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">{getNodeTitle()}</span>
            <span className="text-xs bg-primary-100 px-2 py-1 rounded">
              {config.node_type || 'ai'}
            </span>
          </div>
          
          <div className="text-xs text-gray-600">
            {getNodeDescription()}
          </div>
        </div>

        {/* Configuration */}
        {config.workflow_type && (
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium">Workflow:</span>
              <span className="text-xs bg-secondary-100 px-2 py-1 rounded">
                {config.workflow_type}
              </span>
            </div>
          </div>
        )}

        {/* Input Data Preview */}
        {config.input_data && (
          <div className="space-y-1">
            <span className="text-xs font-medium">Input:</span>
            <div className="text-xs bg-gray-50 p-2 rounded max-h-16 overflow-y-auto">
              <pre className="text-xs">
                {JSON.stringify(config.input_data, null, 2)}
              </pre>
            </div>
          </div>
        )}

        {/* Status Indicator */}
        <div className="flex items-center gap-2">
          {executionStatus === 'idle' && <div className="w-2 h-2 bg-gray-300 rounded-full" />}
          {executionStatus === 'running' && <Clock className="w-4 h-4 text-blue-500 animate-spin" />}
          {executionStatus === 'completed' && <CheckCircle className="w-4 h-4 text-green-500" />}
          {executionStatus === 'error' && <AlertCircle className="w-4 h-4 text-red-500" />}
          
          <span className="text-xs text-gray-600">
            {executionStatus === 'idle' && 'Ready'}
            {executionStatus === 'running' && 'Executing...'}
            {executionStatus === 'completed' && 'Completed'}
            {executionStatus === 'error' && 'Error'}
          </span>
        </div>

        {/* Execution Results */}
        {renderExecutionResult()}

        {/* Action Buttons */}
        <div className="flex gap-2">
          <button
            className="flex-1 btn btn-sm btn-primary"
            onClick={handleExecute}
            disabled={isExecuting || !config.workflow_type}
          >
            <Play className="w-3 h-3 mr-1" />
            {isExecuting ? 'Executing...' : 'Execute'}
          </button>
          
          <button
            className="btn btn-sm btn-outline"
            onClick={() => {
              // Open configuration modal
              console.log('Configure LangGraph node');
            }}
          >
            <Settings className="w-3 h-3" />
          </button>
        </div>
      </div>
    </BaseNode>
  );
}; 