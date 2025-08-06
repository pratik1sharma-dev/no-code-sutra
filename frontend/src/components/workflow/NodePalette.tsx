import React, { useState } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { ChevronDown, ChevronRight } from 'lucide-react';
import { useNodeRegistry, NODE_TYPES } from './nodes/NodeRegistry';
import type { NodeType } from '../../types/workflow';

interface NodePaletteProps {
  onNodeSelect?: (nodeType: NodeType) => void;
}

export const NodePalette: React.FC<NodePaletteProps> = ({ onNodeSelect }) => {
  const { getNodeTypesByCategory } = useNodeRegistry();
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>(() => {
    // Expand all categories by default so users can see draggable nodes
    const categories = getNodeTypesByCategory();
    const expanded: Record<string, boolean> = {};
    Object.keys(categories).forEach(category => {
      expanded[category] = true;
    });
    return expanded;
  });
  
  const categories = getNodeTypesByCategory();

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  return (
    <div className="w-64 bg-white border-r border-gray-200 p-4">
      <div className="mb-4">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">Node Library</h3>
        <p className="text-xs text-gray-600">
          Drag nodes to the canvas to build your workflow
        </p>
      </div>

      <div className="space-y-2">
        {Object.entries(categories).map(([category, nodes]) => (
          <div key={category} className="border border-gray-200 rounded-lg">
            <button
              className="w-full px-3 py-2 text-left text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center justify-between"
              onClick={() => toggleCategory(category)}
            >
              <span>{category}</span>
              {expandedCategories[category] ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
            
            {expandedCategories[category] && (
              <div className="border-t border-gray-200 p-2 space-y-1">
                {nodes.map((nodeType) => (
                  <DraggableNodeItem
                    key={nodeType.type}
                    nodeType={nodeType}
                    onNodeSelect={onNodeSelect}
                  />
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

interface DraggableNodeItemProps {
  nodeType: typeof NODE_TYPES[keyof typeof NODE_TYPES];
  onNodeSelect?: (nodeType: NodeType) => void;
}

const DraggableNodeItem: React.FC<DraggableNodeItemProps> = ({ nodeType, onNodeSelect }) => {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({
    id: `node-${nodeType.type}`,
    data: {
      type: 'node',
      nodeType: nodeType.type
    }
  });

  const style = {
    transform: CSS.Translate.toString(transform),
    opacity: isDragging ? 0.5 : 1,
  };

  const Icon = nodeType.icon;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className="flex items-center gap-2 p-2 text-xs text-gray-700 hover:bg-gray-100 rounded cursor-move transition-colors"
      onClick={() => onNodeSelect?.(nodeType.type)}
    >
      <Icon className="w-4 h-4 text-gray-500" />
      <div className="flex-1 min-w-0">
        <div className="font-medium truncate">{nodeType.label}</div>
        <div className="text-gray-500 truncate">{nodeType.description}</div>
      </div>
    </div>
  );
}; 