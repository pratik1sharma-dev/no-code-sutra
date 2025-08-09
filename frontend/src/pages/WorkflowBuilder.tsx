import React, { useCallback, useMemo, useEffect } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';
import {
  ReactFlow,
  Controls,
  Background,
  MiniMap,
  addEdge,
  useNodesState,
  useEdgesState,
} from 'reactflow';
import type { Node, Edge, Connection, NodeTypes, EdgeTypes, PanelPosition } from 'reactflow';
import 'reactflow/dist/style.css';
import { DndContext, DragOverlay, useDroppable } from '@dnd-kit/core';
import type { DragEndEvent } from '@dnd-kit/core';
import { v4 as uuidv4 } from 'uuid';
import { Play, Save, Settings, Sparkles } from 'lucide-react';
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
  nodeTypes: NodeTypes;
  nodes: any[];
  edges: any[];
  fitView?: boolean;
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

const WorkflowBuilder: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [searchParams] = useSearchParams(); // Added for generated workflow import
  const { 
    currentWorkflow, 
    setCurrentWorkflow, 
    addNode, 
    addEdge: addWorkflowEdge,
    updateNodePosition,
    executeWorkflow,
    isExecuting,
    currentExecution
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
          // Fallback to new empty workflow if parsing fails
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
      console.log('Syncing React Flow state with workflow:', currentWorkflow);
      
      // Convert backend format to React Flow format
      const reactFlowNodes = currentWorkflow.nodes.map((node: any) => ({
        id: node.id,
        type: node.type,
        position: node.position,
        data: {
          label: node.label || `New ${node.type}`,
          type: node.type,
          config: node.config || {},
          status: node.status || 'idle',
          executionCount: node.executionCount || 0,
          lastExecution: node.lastExecution
        }
      }));
      
      console.log('Setting React Flow nodes:', reactFlowNodes);
      setNodes(reactFlowNodes);
      
      // Convert edges to React Flow format with proper handles
      const reactFlowEdges = currentWorkflow.edges.map((edge: any) => ({
        ...edge,
        sourceHandle: null, // Use default source handle
        targetHandle: null  // Use default target handle
      }));
      
      setEdges(reactFlowEdges);
    }
  }, [currentWorkflow?.id, currentWorkflow?.nodes, currentWorkflow?.edges, setNodes, setEdges]);

  // Node types for React Flow - memoized to prevent recreation
  const nodeTypes: NodeTypes = useMemo(() => {
    const types: NodeTypes = {};
    // Get all available node types from the registry
    const allNodeTypes = Object.keys(NODE_TYPES);
    allNodeTypes.forEach(type => {
      types[type] = getNodeComponent(type as NodeType);
    });
    return types;
  }, [getNodeComponent]);

  // Handle new connections
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

  // Handle drag and drop with proper positioning
  const onDragEnd = useCallback((event: DragEndEvent) => {
    const { active, over } = event;
    
    console.log('Drag end event:', { active, over });
    
    if (active && over && over.id === 'workflow-canvas') {
      const nodeType = active.data?.current?.nodeType as NodeType;
      console.log('Node type to add:', nodeType);
      
      if (nodeType) {
        // Calculate position based on existing nodes
        const existingNodes = currentWorkflow?.nodes || [];
        const baseX = 100;
        const baseY = 100;
        const offsetX = existingNodes.length * 50;
        const offsetY = existingNodes.length * 30;
        
        const newNode: WorkflowNode = {
          id: uuidv4(),
          type: nodeType,
          position: { 
            x: baseX + offsetX, 
            y: baseY + offsetY 
          },
          data: {
            label: `New ${nodeType}`,
            type: nodeType,
            config: {},
            status: 'idle',
            executionCount: 0
          }
        };
        
        console.log('Adding new node:', newNode);
        addNode(newNode);
        console.log('Node added to store');
      }
    }
  }, [addNode, currentWorkflow?.nodes]);

  // Handle node changes from React Flow
  const handleNodesChange = useCallback((changes: any[]) => {
    onNodesChange(changes);
    
    // Update Zustand store with position changes
    changes.forEach(change => {
      if (change.type === 'position' && change.position) {
        updateNodePosition(change.id, change.position);
      }
    });
  }, [onNodesChange, updateNodePosition]);

  // Handle workflow execution
  const handleExecute = useCallback(async () => {
    await executeWorkflow();
  }, [executeWorkflow]);

  // Handle node selection
  const handleNodeSelect = useCallback((nodeType: NodeType) => {
    console.log('Selected node type:', nodeType);
    // TODO: Implement node selection logic
  }, []);

  // Component for displaying generated workflow info
  const GeneratedWorkflowInfo: React.FC<{ workflow: any }> = ({ workflow }) => {
    const metadata = workflow.metadata || {};
    const originalPrompt = workflow.prompt;
    
    return (
      <div className="mb-4 p-6 bg-gradient-to-r from-blue-50 to-purple-50 border border-blue-200 rounded-xl">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-5 h-5 text-blue-600" />
          <h3 className="text-sm font-semibold text-blue-900">
            AI-Generated Workflow
          </h3>
        </div>
        
        <div className="space-y-3">
          {originalPrompt && (
            <div>
              <p className="text-xs font-medium text-blue-700 mb-1">Original Request:</p>
              <p className="text-sm text-blue-800 italic">"{originalPrompt}"</p>
            </div>
          )}
          
          {workflow.description && (
            <div>
              <p className="text-xs font-medium text-blue-700 mb-1">Description:</p>
              <p className="text-sm text-blue-800">{workflow.description}</p>
            </div>
          )}
          
          {metadata.estimatedCost && (
            <div className="flex items-center gap-4 text-xs">
              <span className="text-blue-700">
                <span className="font-medium">Estimated Cost:</span> {metadata.estimatedCost}
              </span>
              {metadata.estimatedTime && (
                <span className="text-blue-700">
                  <span className="font-medium">Setup Time:</span> {metadata.estimatedTime}
                </span>
              )}
            </div>
          )}
          
          {metadata.requiredIntegrations && metadata.requiredIntegrations.length > 0 && (
            <div>
              <p className="text-xs font-medium text-blue-700 mb-1">Required Integrations:</p>
              <div className="flex flex-wrap gap-1">
                {metadata.requiredIntegrations.map((integration: string, index: number) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-orange-100 text-orange-700 rounded-full text-xs border border-orange-200"
                  >
                    {integration}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {metadata.authRequirements && metadata.authRequirements.length > 0 && (
            <div>
              <p className="text-xs font-medium text-blue-700 mb-1">Authentication Required:</p>
              <div className="flex flex-wrap gap-1">
                {metadata.authRequirements.map((auth: string, index: number) => (
                  <span
                    key={index}
                    className="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs border border-red-200"
                  >
                    {auth}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  if (!currentWorkflow) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading workflow...</p>
        </div>
      </div>
    );
  }

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
        {/* Node Palette Sidebar */}
        <NodePalette onNodeSelect={handleNodeSelect} />
        
        {/* Main Canvas Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <div className="bg-white border-b border-gray-200 px-6 py-4">
            {/* Show generated workflow info if available */}
            {searchParams.get('generated') && currentWorkflow && (
              <GeneratedWorkflowInfo workflow={currentWorkflow} />
            )}
            
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <h1 className="text-lg font-semibold text-gray-900">
                  {currentWorkflow.name}
                </h1>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  currentWorkflow.status === 'active' ? 'bg-green-100 text-green-800' :
                  currentWorkflow.status === 'draft' ? 'bg-gray-100 text-gray-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {currentWorkflow.status}
                </span>
              </div>
              
              <div className="flex items-center gap-2">
                <button className="btn btn-outline btn-sm">
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
                <button className="btn btn-outline btn-sm">
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            {/* Execution Status */}
            {currentExecution && (
              <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse"></div>
                    <span className="text-sm font-medium text-blue-900">
                      Execution {currentExecution.status}
                    </span>
                  </div>
                  <span className="text-xs text-blue-700">
                    {currentExecution.steps.filter(s => s.status === 'completed').length} / {currentExecution.steps.length} steps
                  </span>
                </div>
              </div>
            )}
          </div>
          
          {/* React Flow Canvas */}
          <div className="flex-1 min-w-0">
            <DroppableReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={handleNodesChange}
              onEdgesChange={onEdgesChange}
              onConnect={onConnect}
              nodeTypes={nodeTypes}
              fitView
              attributionPosition="bottom-left"
            >
              <Controls />
              <Background />
              <MiniMap />
            </DroppableReactFlow>
          </div>
        </div>
      </div>
    </DndContext>
  );
};

export default WorkflowBuilder; 