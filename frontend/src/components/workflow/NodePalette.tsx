import React, { useState, useMemo } from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import { ChevronDown, ChevronRight, Search } from 'lucide-react';
import { useNodeRegistry, NODE_TYPES } from './nodes/NodeRegistry';
import type { NodeType } from '../../types/workflow';

interface NodePaletteProps {
  onNodeSelect?: (nodeType: NodeType) => void;
}

export const NodePalette: React.FC<NodePaletteProps> = ({ onNodeSelect }) => {
  const { getNodeTypesByCategory } = useNodeRegistry();
  const [expandedCategories, setExpandedCategories] = useState<Record<string, boolean>>(() => {
    const categories = getNodeTypesByCategory();
    const expanded: Record<string, boolean> = {};
    Object.keys(categories).forEach(category => {
      expanded[category] = true;
    });
    return expanded;
  });
  const [query, setQuery] = useState('');
  
  const categories = getNodeTypesByCategory();

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return categories;
    const result: Record<string, typeof NODE_TYPES[keyof typeof NODE_TYPES][]> = {};
    Object.entries(categories).forEach(([cat, nodes]) => {
      const matches = nodes.filter(n =>
        n.label.toLowerCase().includes(q) ||
        n.description.toLowerCase().includes(q) ||
        n.type.toLowerCase().includes(q)
      );
      if (matches.length) result[cat] = matches;
    });
    return result;
  }, [categories, query]);

  const toggleCategory = (category: string) => {
    setExpandedCategories(prev => ({
      ...prev,
      [category]: !prev[category]
    }));
  };

  return (
    <div className="w-72 bg-white border-r border-gray-100 p-4">
      <div className="sticky top-0 z-10 bg-white pb-3">
        <h3 className="text-xs font-semibold text-gray-900 mb-2 tracking-wide">Node Library</h3>
        <div className="relative">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search nodes…"
            className="w-full rounded-md border border-gray-200 bg-gray-50 px-8 py-1.5 text-xs text-gray-900 placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-900/5 focus:bg-white"
          />
          <Search className="absolute left-2 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        </div>
      </div>

      <div className="space-y-2">
        {Object.entries(filtered).map(([category, nodes]) => (
          <div key={category} className="border border-gray-100 rounded-lg overflow-hidden">
            <button
              className="w-full px-3 py-2 text-left text-xs font-medium text-gray-700 hover:bg-gray-50 flex items-center justify-between"
              onClick={() => toggleCategory(category)}
            >
              <span className="truncate">{category}</span>
              {expandedCategories[category] ? (
                <ChevronDown className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
            {expandedCategories[category] && (
              <div className="border-t border-gray-100 p-1.5 space-y-1">
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
        {Object.keys(filtered).length === 0 && (
          <div className="text-[11px] text-gray-500 px-1.5">No nodes found</div>
        )}
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
  } as React.CSSProperties;

  const Icon = nodeType.icon;

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className="flex items-center gap-2 p-2 text-[11px] text-gray-700 hover:bg-gray-50 rounded-md cursor-move transition-colors"
      onClick={() => onNodeSelect?.(nodeType.type)}
      title={nodeType.description}
    >
      <Icon className="w-4 h-4 text-gray-400" />
      <div className="flex-1 min-w-0">
        <div className="font-medium truncate text-gray-900">{nodeType.label}</div>
        <div className="text-gray-500 truncate">{nodeType.description}</div>
      </div>
    </div>
  );
}; 