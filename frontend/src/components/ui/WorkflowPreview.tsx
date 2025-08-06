import React from 'react';
import { CheckCircle, Clock, DollarSign, Settings, ArrowRight, Zap } from 'lucide-react';

interface WorkflowPreviewProps {
  workflow: any;
  onCustomize: () => void;
  onRegenerate?: () => void;
}

const WorkflowPreview: React.FC<WorkflowPreviewProps> = ({
  workflow,
  onCustomize,
  onRegenerate
}) => {
  const metadata = workflow.metadata || {};
  const nodes = workflow.nodes || [];
  const edges = workflow.edges || [];

  const getNodeIcon = (type: string) => {
    switch (type) {
      case 'aiAgent':
        return <Zap className="w-4 h-4 text-purple-600" />;
      case 'email':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'slack':
        return <Settings className="w-4 h-4 text-blue-600" />;
      case 'data':
        return <Settings className="w-4 h-4 text-gray-600" />;
      default:
        return <Settings className="w-4 h-4 text-gray-600" />;
    }
  };

  const getNodeColor = (type: string) => {
    switch (type) {
      case 'aiAgent':
        return 'bg-purple-50 border-purple-200';
      case 'email':
        return 'bg-green-50 border-green-200';
      case 'slack':
        return 'bg-blue-50 border-blue-200';
      case 'data':
        return 'bg-gray-50 border-gray-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto bg-white rounded-2xl shadow-lg border border-gray-200">
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-xl font-semibold text-gray-900">
              {metadata.title || workflow.name || 'Generated Workflow'}
            </h3>
            <p className="text-gray-600 mt-1">
              {metadata.description || workflow.description}
            </p>
          </div>
          <div className="flex items-center gap-2 text-sm text-green-600">
            <CheckCircle className="w-4 h-4" />
            Ready to customize
          </div>
        </div>
      </div>

      <div className="p-6">
        {/* Workflow Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="flex items-center gap-3 p-4 bg-blue-50 rounded-xl">
            <Settings className="w-5 h-5 text-blue-600" />
            <div>
              <p className="text-sm text-gray-600">Steps</p>
              <p className="font-semibold text-gray-900">{nodes.length}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-4 bg-green-50 rounded-xl">
            <Clock className="w-5 h-5 text-green-600" />
            <div>
              <p className="text-sm text-gray-600">Setup Time</p>
              <p className="font-semibold text-gray-900">
                {metadata.estimatedTime || '5-10 minutes'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-3 p-4 bg-purple-50 rounded-xl">
            <DollarSign className="w-5 h-5 text-purple-600" />
            <div>
              <p className="text-sm text-gray-600">Estimated Cost</p>
              <p className="font-semibold text-gray-900">
                {metadata.estimatedCost || 'Free'}
              </p>
            </div>
          </div>
        </div>

        {/* Workflow Steps */}
        <div className="mb-6">
          <h4 className="text-lg font-medium text-gray-900 mb-4">Workflow Steps</h4>
          <div className="space-y-3">
            {nodes.map((node: any, index: number) => (
              <div
                key={node.id}
                className={`flex items-center gap-4 p-4 rounded-xl border ${getNodeColor(node.type)}`}
              >
                <div className="flex items-center justify-center w-8 h-8 bg-white rounded-full border-2 border-gray-200 text-sm font-medium text-gray-600">
                  {index + 1}
                </div>
                <div className="flex items-center gap-3 flex-1">
                  {getNodeIcon(node.type)}
                  <div>
                    <p className="font-medium text-gray-900">
                      {node.data?.label || node.label || `Step ${index + 1}`}
                    </p>
                    <p className="text-sm text-gray-600 capitalize">
                      {node.type} • {node.type === 'aiAgent' ? 'AI Processing' : 'Action'}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Required Integrations */}
        {metadata.requiredIntegrations && metadata.requiredIntegrations.length > 0 && (
          <div className="mb-6">
            <h4 className="text-lg font-medium text-gray-900 mb-4">Required Integrations</h4>
            <div className="flex flex-wrap gap-2">
              {metadata.requiredIntegrations.map((integration: string, index: number) => (
                <span
                  key={index}
                  className="px-3 py-1 bg-orange-50 text-orange-700 rounded-full text-sm border border-orange-200"
                >
                  {integration}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4">
          <button
            onClick={onCustomize}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <Settings className="w-4 h-4" />
            Customize Workflow
            <ArrowRight className="w-4 h-4" />
          </button>
          
          {onRegenerate && (
            <button
              onClick={onRegenerate}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors"
            >
              Regenerate
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default WorkflowPreview; 