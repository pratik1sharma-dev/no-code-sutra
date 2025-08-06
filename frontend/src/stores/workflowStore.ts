import { create } from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import { apiService } from '../services/api';
import type {
  WorkflowStore,
  WorkflowState,
  WorkflowNode,
  WorkflowEdge,
  WorkflowNodeData,
  WorkflowExecution,
  ExecutionStep
} from '../types/workflow';

export const useWorkflowStore = create<WorkflowStore>((set, get) => ({
  // Initial state
  currentWorkflow: null,
  workflows: [],
  isExecuting: false,
  currentExecution: null,
  selectedNode: null,
  selectedEdge: null,

  // Actions
  setCurrentWorkflow: (workflow) => {
    set({ currentWorkflow: workflow });
  },

  addNode: (node) => {
    const { currentWorkflow } = get();
    if (!currentWorkflow) return;

    // Create a new workflow with the added node
    const updatedWorkflow = {
      ...currentWorkflow,
      nodes: [...currentWorkflow.nodes, node],
      updatedAt: new Date()
    };

    // Update only the current workflow
    set({ currentWorkflow: updatedWorkflow });
  },

  updateNode: (nodeId, updates) => {
    const { currentWorkflow } = get();
    if (!currentWorkflow) return;

    const updatedWorkflow = {
      ...currentWorkflow,
      nodes: currentWorkflow.nodes.map(node =>
        node.id === nodeId ? { ...node, data: { ...node.data, ...updates } } : node
      ),
      updatedAt: new Date()
    };

    set({ currentWorkflow: updatedWorkflow });
  },

  updateNodePosition: (nodeId, position) => {
    const { currentWorkflow } = get();
    if (!currentWorkflow) return;

    const updatedWorkflow = {
      ...currentWorkflow,
      nodes: currentWorkflow.nodes.map(node =>
        node.id === nodeId ? { ...node, position } : node
      ),
      updatedAt: new Date()
    };

    set({ currentWorkflow: updatedWorkflow });
  },

  removeNode: (nodeId) => {
    const { currentWorkflow } = get();
    if (!currentWorkflow) return;

    const updatedWorkflow = {
      ...currentWorkflow,
      nodes: currentWorkflow.nodes.filter(node => node.id !== nodeId),
      edges: currentWorkflow.edges.filter(edge =>
        edge.source !== nodeId && edge.target !== nodeId
      ),
      updatedAt: new Date()
    };

    set({ currentWorkflow: updatedWorkflow });
  },

  addEdge: (edge) => {
    const { currentWorkflow } = get();
    if (!currentWorkflow) return;

    const updatedWorkflow = {
      ...currentWorkflow,
      edges: [...currentWorkflow.edges, edge],
      updatedAt: new Date()
    };

    set({ currentWorkflow: updatedWorkflow });
  },

  removeEdge: (edgeId) => {
    const { currentWorkflow } = get();
    if (!currentWorkflow) return;

    const updatedWorkflow = {
      ...currentWorkflow,
      edges: currentWorkflow.edges.filter(edge => edge.id !== edgeId),
      updatedAt: new Date()
    };

    set({ currentWorkflow: updatedWorkflow });
  },

  updateWorkflow: (updates) => {
    const { currentWorkflow } = get();
    if (!currentWorkflow) return;

    const updatedWorkflow = {
      ...currentWorkflow,
      ...updates,
      updatedAt: new Date()
    };

    set({ currentWorkflow: updatedWorkflow });
  },

  executeWorkflow: async () => {
    const { currentWorkflow } = get();
    if (!currentWorkflow) return;

    const executionId = uuidv4();
    const execution: WorkflowExecution = {
      id: executionId,
      workflowId: currentWorkflow.id,
      status: 'running',
      startTime: new Date(),
      steps: currentWorkflow.nodes.map(node => ({
        nodeId: node.id,
        status: 'pending'
      }))
    };

    set({
      isExecuting: true,
      currentExecution: execution
    });

    try {
      // Execute workflow using LangGraph
      const result = await apiService.executeWorkflow({
        workflow: currentWorkflow,
        input_data: {},
        user_id: 'demo-user'
      });

      // Update execution with real results
      set(state => ({
        currentExecution: state.currentExecution ? {
          ...state.currentExecution,
          status: result.success ? 'completed' : 'failed',
          endTime: new Date(),
          result: result.data,
          error: result.success ? undefined : 'Workflow execution failed'
        } : null,
        isExecuting: false
      }));

      if (result.success) {
        get().updateWorkflow({
          executionCount: currentWorkflow.executionCount + 1,
          lastExecuted: new Date()
        });
      }
    } catch (error) {
      set(state => ({
        currentExecution: state.currentExecution ? {
          ...state.currentExecution,
          status: 'failed',
          endTime: new Date(),
          error: error instanceof Error ? error.message : 'Unknown error'
        } : null,
        isExecuting: false
      }));
    }
  },

  clearExecution: () => {
    set({
      isExecuting: false,
      currentExecution: null
    });
  }
})); 