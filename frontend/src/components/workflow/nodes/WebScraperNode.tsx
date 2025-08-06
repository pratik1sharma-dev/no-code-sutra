import React from 'react';
import { NodeProps } from 'reactflow';
import { Globe, Settings, Play, Search } from 'lucide-react';
import { BaseNode } from './BaseNode';
import { WorkflowNodeData } from '../../../types/workflow';

export const WebScraperNode: React.FC<NodeProps<WorkflowNodeData>> = (props) => {
  const { data } = props;
  
  // Add null checks for data and config
  if (!data) {
    console.warn('WebScraperNode: data is undefined', props);
    return null;
  }

  const config = data.config || {};

  return (
    <BaseNode
      {...props}
      icon={<Globe className="w-4 h-4" />}
      color="primary"
      className="min-w-[250px]"
    >
      <div className="space-y-2">
        {/* Search Terms */}
        <div className="flex items-center gap-2">
          <Search className="w-3 h-3 text-gray-500" />
          <span className="text-xs font-medium">Search:</span>
          <span className="text-xs bg-primary-100 px-2 py-1 rounded truncate max-w-[120px]">
            {config?.searchTerms || 'Not set'}
          </span>
        </div>

        {/* Sources */}
        {config?.sources && (
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium">Sources:</span>
            <span className="text-xs bg-secondary-100 px-2 py-1 rounded">
              {Array.isArray(config.sources) ? config.sources.join(', ') : config.sources}
            </span>
          </div>
        )}

        {/* Results Count */}
        {config?.maxResults && (
          <div className="flex items-center justify-between">
            <span className="text-xs font-medium">Max Results:</span>
            <span className="text-xs bg-success-100 px-2 py-1 rounded">
              {config.maxResults}
            </span>
          </div>
        )}

        {/* Filters */}
        {config?.filters && Object.keys(config.filters).length > 0 && (
          <div className="mt-2">
            <span className="text-xs font-medium block mb-1">Filters:</span>
            <div className="text-xs text-gray-600">
              {Object.keys(config.filters).slice(0, 2).join(', ')}
              {Object.keys(config.filters).length > 2 && '...'}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-1 mt-3">
          <button
            className="flex-1 btn btn-sm btn-primary"
            onClick={() => {
              console.log('Test Web Scraper node');
            }}
          >
            <Play className="w-3 h-3 mr-1" />
            Test
          </button>
          <button
            className="btn btn-sm btn-outline"
            onClick={() => {
              console.log('Configure Web Scraper node');
            }}
          >
            <Settings className="w-3 h-3" />
          </button>
        </div>
      </div>
    </BaseNode>
  );
}; 