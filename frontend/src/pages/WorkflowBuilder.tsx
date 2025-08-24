import React, { useCallback, useMemo, useEffect, useState, useRef } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
  useReactFlow,
} from 'reactflow';
import type { Node, Edge, Connection, NodeTypes, EdgeTypes, PanelPosition } from 'reactflow';
import 'reactflow/dist/style.css';
import { DndContext, DragOverlay, useDroppable } from '@dnd-kit/core';
import type { DragEndEvent } from '@dnd-kit/core';
import { v4 as uuidv4 } from 'uuid';
import { Play, Save, Settings, Sparkles, ZoomIn, ZoomOut, Maximize2, Grid, LayoutGrid } from 'lucide-react';
import { useWorkflowStore } from '../stores/workflowStore';
import { useNodeRegistry, NODE_TYPES } from '../components/workflow/nodes/NodeRegistry';
import { NodePalette } from '../components/workflow/NodePalette';
import type { WorkflowNodeData, WorkflowNode, WorkflowEdge, NodeType } from '../types/workflow';

// Droppable React Flow wrapper
const DroppableReactFlow: React.FC<{
  children: React.ReactNode;
  onNodesChange: any;
  onEdgesChange: any;
  onConnect: any;
  onNodeClick?: any;
  onSelectionChange?: any;
  nodeTypes: NodeTypes;
  nodes: any[];
  edges: any[];
  fitView?: boolean;
  snapToGrid?: boolean;
  snapGrid?: [number, number];
  attributionPosition?: PanelPosition;
}> = ({ children, fitView, attributionPosition, ...props }) => {
  const { setNodeRef } = useDroppable({
    id: 'workflow-canvas',
  });

  return (
    <div ref={setNodeRef} className="w-full h-full">
      <ReactFlow {...props} fitView={fitView} attributionPosition={attributionPosition}>
        {children}
      </ReactFlow>
    </div>
  );
};

// Canvas Controls Component
const CanvasControls: React.FC<{ 
  showGrid: boolean; 
  onToggleGrid: () => void;
  onArrangeNodes: () => void;
}> = ({ 
  showGrid, 
  onToggleGrid,
  onArrangeNodes
}) => {
  const { zoomIn, zoomOut, fitView } = useReactFlow();

  return (
    <div className="absolute right-3 top-3 z-10 flex items-center gap-1 bg-white/80 backdrop-blur border border-gray-200 rounded-md p-1">
      <button 
        className="icon-btn" 
        onClick={() => fitView()} 
        title="Fit to view"
      >
        <Maximize2 className="w-4 h-4" />
      </button>
      <button 
        className="icon-btn" 
        onClick={() => zoomIn()} 
        title="Zoom in"
      >
        <ZoomIn className="w-4 h-4" />
      </button>
      <button 
        className="icon-btn" 
        onClick={() => zoomOut()} 
        title="Zoom out"
      >
        <ZoomOut className="w-4 h-4" />
      </button>
      <button 
        className={`icon-btn ${showGrid ? 'bg-gray-100' : ''}`} 
        onClick={onToggleGrid} 
        title="Toggle grid"
      >
        <Grid className="w-4 h-4" />
      </button>
      <button 
        className="icon-btn" 
        onClick={onArrangeNodes} 
        title="Arrange nodes in grid"
      >
        <LayoutGrid className="w-4 h-4" />
      </button>
    </div>
  );
};

const InspectorPanel: React.FC = () => {
  const { currentWorkflow, selectedNode, updateNode } = useWorkflowStore();
  const node = useMemo(() => currentWorkflow?.nodes.find(n => n.id === selectedNode), [currentWorkflow, selectedNode]);
  const [label, setLabel] = useState('');
  const [configText, setConfigText] = useState('');

  useEffect(() => {
    setLabel(node?.data.label || '');
    setConfigText(JSON.stringify(node?.data.config || {}, null, 2));
  }, [node?.id]);

  if (!node) {
    return (
      <div className="w-80 border-l border-gray-100 bg-white p-4 text-xs text-gray-600">Select a node to edit</div>
    );
  }

  return (
    <div className="w-80 border-l border-gray-100 bg-white p-4 space-y-3">
      <div>
        <div className="text-[11px] text-gray-500 mb-1">Label</div>
        <input
          value={label}
          onChange={(e) => setLabel(e.target.value)}
          onBlur={() => updateNode(node.id, { label })}
          className="w-full rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900/5 focus:bg-white"
        />
      </div>
      <div>
        <div className="text-[11px] text-gray-500 mb-1">Type</div>
        <div className="text-sm text-gray-900">{node.data.type}</div>
      </div>
      <div>
        <div className="text-[11px] text-gray-500 mb-1">Config (JSON)</div>
        <textarea
          value={configText}
          onChange={(e) => setConfigText(e.target.value)}
          onBlur={() => {
            try { updateNode(node.id, { config: JSON.parse(configText || '{}') }); } catch {}
          }}
          className="w-full h-40 rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-xs text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-900/5 focus:bg-white font-mono"
        />
      </div>
    </div>
  );
};

const WorkflowBuilder: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams(); // Added for generated workflow import
  const [isNodePaletteCollapsed, setIsNodePaletteCollapsed] = useState(false);
  const { 
    currentWorkflow, 
    setCurrentWorkflow, 
    addNode, 
    addEdge: addWorkflowEdge,
    updateNodePosition,
    executeWorkflow,
    isExecuting,
    currentExecution,
    saveCurrentWorkflow,
    setSelectedNode
  } = useWorkflowStore();
  
  const { getNodeComponent } = useNodeRegistry();

  // Initialize workflow if not exists or with generated data
  useEffect(() => {
    if (!currentWorkflow) {
      const generatedWorkflowData = searchParams.get('generated');
      if (generatedWorkflowData) {
        try {
          const workflowData = JSON.parse(decodeURIComponent(generatedWorkflowData));
          
          // Handle both nested and flat workflow structures
          const workflow = workflowData.workflow || workflowData;
          
          setCurrentWorkflow({
            ...workflow,
            id: id || uuidv4(),
            status: 'draft' as const,
            createdAt: new Date(),
            updatedAt: new Date(),
            executionCount: 0,
            tags: []
          });
        } catch (error) {
          console.error('Failed to parse generated workflow:', error);
          setCurrentWorkflow({
            id: id || uuidv4(),
            name: 'New Workflow',
            description: '',
            nodes: [],
            edges: [],
            status: 'draft' as const,
            createdAt: new Date(),
            updatedAt: new Date(),
            executionCount: 0,
            tags: []
          });
        }
      } else {
        const newWorkflow = {
          id: id || uuidv4(),
          name: 'New Workflow',
          description: '',
          nodes: [],
          edges: [],
          status: 'draft' as const,
          createdAt: new Date(),
          updatedAt: new Date(),
          executionCount: 0,
          tags: []
        };
        setCurrentWorkflow(newWorkflow);
      }
    }
  }, [currentWorkflow, id, setCurrentWorkflow, searchParams]);

  // Convert workflow nodes/edges to React Flow format
  const [nodes, setNodes, onNodesChange] = useNodesState(
    currentWorkflow?.nodes || []
  );
  
  const [edges, setEdges, onEdgesChange] = useEdgesState(
    currentWorkflow?.edges || []
  );

  // Sync React Flow state with Zustand store when nodes/edges change
  useEffect(() => {
    if (currentWorkflow) {
      const reactFlowNodes = currentWorkflow.nodes.map((node: any) => ({
        id: node.id,
        type: node.type,
        position: node.position,
        data: {
          id: node.id,
          label: node.label || `New ${node.type}`,
          type: node.type,
          config: node.config || {},
          status: node.status || 'idle',
          executionCount: node.executionCount || 0,
          lastExecution: node.lastExecution
        }
      }));
      setNodes(reactFlowNodes);
      const reactFlowEdges = currentWorkflow.edges.map((edge: any) => ({
        ...edge,
        sourceHandle: null,
        targetHandle: null
      }));
      setEdges(reactFlowEdges);
    }
  }, [currentWorkflow?.id, currentWorkflow?.nodes, currentWorkflow?.edges, setNodes, setEdges]);

  const nodeTypes: NodeTypes = useMemo(() => {
    const types: NodeTypes = {};
    const allNodeTypes = Object.keys(NODE_TYPES);
    allNodeTypes.forEach(type => { types[type] = getNodeComponent(type as NodeType); });
    return types;
  }, [getNodeComponent]);

  const onConnect = useCallback((connection: Connection) => {
    if (connection.source && connection.target) {
      const newEdge: WorkflowEdge = {
        id: uuidv4(),
        source: connection.source,
        target: connection.target,
        type: 'default',
        label: ''
      };
      addWorkflowEdge(newEdge);
    }
  }, [addWorkflowEdge]);

  const onDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;
    if (active && over && over.id === 'workflow-canvas') {
      const nodeType = active.data?.current?.nodeType as NodeType;
      if (nodeType) {
        const existingNodes = currentWorkflow?.nodes || [];
        
        // Grid-based positioning for better visual layout
        const gridSize = { width: 280, height: 120 }; // Node spacing
        const nodesPerRow = 3; // Number of nodes per row
        const rowIndex = Math.floor(existingNodes.length / nodesPerRow);
        const colIndex = existingNodes.length % nodesPerRow;
        
        // Start position with some margin from edges
        const startX = 100;
        const startY = 100;
        
        // Calculate position with alternating row offset for visual interest
        const x = startX + (colIndex * gridSize.width);
        const y = startY + (rowIndex * gridSize.height) + (rowIndex % 2 === 1 ? gridSize.height / 2 : 0);
        
        const nodeId = uuidv4();
        const newNode: WorkflowNode = {
          id: nodeId,
          type: nodeType,
          position: { x, y },
          data: { 
            id: nodeId,
            label: `New ${nodeType}`, 
            type: nodeType, 
            config: {}, 
            status: 'idle', 
            executionCount: 0 
          }
        };
        addNode(newNode);
      }
    }
  }, [addNode, currentWorkflow?.nodes]);

  const handleNodesChange = useCallback((changes: any[]) => {
    onNodesChange(changes);
    changes.forEach(change => {
      if (change.type === 'position' && change.position) {
        updateNodePosition(change.id, change.position);
      }
    });
  }, [onNodesChange, updateNodePosition]);

  // Save / Execute
  const handleSaveDraft = useCallback(async () => { await saveCurrentWorkflow(); }, [saveCurrentWorkflow]);
  const handleExecute = useCallback(async () => { await saveCurrentWorkflow(); await executeWorkflow(); }, [executeWorkflow, saveCurrentWorkflow]);

  // Canvas toolbar controls
  const [showGrid, setShowGrid] = useState(true);

  // Auto-arrange nodes in a grid layout
  const arrangeNodesInGrid = useCallback(() => {
    if (!currentWorkflow?.nodes.length) return;
    
    const gridSize = { width: 280, height: 120 };
    const nodesPerRow = 3;
    const startX = 100;
    const startY = 100;
    
    const updatedNodes = currentWorkflow.nodes.map((node, index) => {
      const rowIndex = Math.floor(index / nodesPerRow);
      const colIndex = index % nodesPerRow;
      const x = startX + (colIndex * gridSize.width);
      const y = startY + (rowIndex * gridSize.height) + (rowIndex % 2 === 1 ? gridSize.height / 2 : 0);
      
      return {
        ...node,
        position: { x, y }
      };
    });
    
    // Update all node positions at once
    updatedNodes.forEach(node => {
      updateNodePosition(node.id, node.position);
    });
  }, [currentWorkflow?.nodes, updateNodePosition]);

  const handleNodeClick = useCallback((_: any, node: any) => {
    setSelectedNode(node?.id || null);
  }, [setSelectedNode]);

  const handleSelectionChange = useCallback((params: any) => {
    const nextId = params?.nodes?.[0]?.id || null;
    if (nextId !== null) setSelectedNode(nextId);
  }, [setSelectedNode]);

  return (
    <DndContext onDragEnd={onDragEnd}>
      <div className="flex h-full w-full">
        <DragOverlay>
          <div className="bg-white border border-gray-300 rounded-lg shadow-lg p-3 opacity-80">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium">Dragging...</span>
            </div>
          </div>
        </DragOverlay>
        
        {/* Collapsible Node Palette Sidebar */}
        <NodePalette 
          isCollapsed={isNodePaletteCollapsed}
          onToggleCollapse={() => setIsNodePaletteCollapsed(!isNodePaletteCollapsed)}
        />
        
        {/* Main Canvas Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <div className="bg-white border-b border-gray-200 px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <h1 className="text-lg font-semibold text-gray-900">
                  {currentWorkflow?.name}
                </h1>
                {currentWorkflow && (
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    currentWorkflow.status === 'active' ? 'bg-green-100 text-green-800' :
                    currentWorkflow.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {currentWorkflow.status}
                  </span>
                )}
              </div>
              <div className="flex items-center gap-2">
                <button className="btn btn-outline btn-sm" onClick={handleSaveDraft}>
                  <Save className="w-4 h-4 mr-1" />
                  Save Draft
                </button>
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={handleExecute}
                  disabled={isExecuting}
                >
                  <Play className="w-4 h-4 mr-1" />
                  {isExecuting ? 'Running...' : 'Save & Run'}
                </button>
              </div>
            </div>
          </div>
          
          {/* Canvas + Inspector */}
          <div className="flex-1 min-w-0 flex">
            <div className="relative flex-1">
              <DroppableReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={handleNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                onNodeClick={handleNodeClick}
                onSelectionChange={handleSelectionChange}
                nodeTypes={nodeTypes}
                fitView
                snapToGrid
                snapGrid={[10, 10]}
                attributionPosition="bottom-left"
              >
                <Controls />
                {showGrid && <Background gap={20} color="#f0f0f0" />}
                <MiniMap />
                <CanvasControls 
                  showGrid={showGrid} 
                  onToggleGrid={() => setShowGrid(v => !v)} 
                  onArrangeNodes={arrangeNodesInGrid}
                />
              </DroppableReactFlow>
            </div>

            {/* Inspector */}
            <InspectorPanel />
          </div>
        </div>
      </div>
    </DndContext>
  );
};

export default WorkflowBuilder; 