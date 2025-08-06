import type { Node, Edge } from 'reactflow';

// Node Types
export type NodeType = 
  | 'aiAgent'
  | 'langGraph'
  | 'email'
  | 'slack'
  | 'data'
  | 'condition'
  | 'delay'
  | 'schedule'
  | 'blogWriter'
  | 'socialMedia'
  | 'imageGenerator'
  | 'seoOptimizer';

// Edge Types
export type EdgeType = 'default' | 'conditional' | 'data';

// Node Data Interface
export interface WorkflowNodeData {
  label: string;
  type: NodeType;
  config: Record<string, any>;
  status: 'idle' | 'running' | 'success' | 'error';
  executionCount: number;
  lastExecution?: Date;
}

// Custom Node Interface
export type WorkflowNode = Node<WorkflowNodeData> & {
  type: NodeType;
};

// Custom Edge Interface
export type WorkflowEdge = Edge & {
  type: EdgeType;
  label?: string;
  condition?: string;
};

// Workflow State Interface
export interface WorkflowState {
  id: string;
  name: string;
  description: string;
  nodes: WorkflowNode[];
  edges: WorkflowEdge[];
  status: 'draft' | 'active' | 'paused';
  createdAt: Date;
  updatedAt: Date;
  executionCount: number;
  lastExecuted?: Date;
  tags: string[];
}

// Configuration Interfaces
export interface AIAgentConfig {
  model: string;
  temperature: number;
  prompt: string;
  maxTokens?: number;
}

export interface EmailConfig {
  to: string;
  subject: string;
  template: string;
  variables: Record<string, any>;
}

export interface SlackConfig {
  channel: string;
  message: string;
  attachments?: any[];
}

export interface DataConfig {
  source: string;
  query?: string;
  filters?: Record<string, any>;
}

export interface ConditionConfig {
  condition: string;
  operator: 'equals' | 'contains' | 'greater_than' | 'less_than';
  value: any;
}

export interface DelayConfig {
  duration: number;
  unit: 'seconds' | 'minutes' | 'hours' | 'days';
}

export interface ScheduleConfig {
  cron: string;
  timezone: string;
  enabled: boolean;
}

// Execution Interfaces
export interface ExecutionStep {
  nodeId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  startTime?: Date;
  endTime?: Date;
  result?: any;
  error?: string;
}

export interface WorkflowExecution {
  id: string;
  workflowId: string;
  status: 'running' | 'completed' | 'failed';
  startTime: Date;
  endTime?: Date;
  steps: ExecutionStep[];
  error?: string;
}

// Store Interface
export interface WorkflowStore {
  // State
  currentWorkflow: WorkflowState | null;
  workflows: WorkflowState[];
  isExecuting: boolean;
  currentExecution: WorkflowExecution | null;
  selectedNode: string | null;
  selectedEdge: string | null;

  // Actions
  setCurrentWorkflow: (workflow: WorkflowState) => void;
  addNode: (node: WorkflowNode) => void;
  updateNode: (nodeId: string, updates: Partial<WorkflowNodeData>) => void;
  updateNodePosition: (nodeId: string, position: { x: number; y: number }) => void;
  removeNode: (nodeId: string) => void;
  addEdge: (edge: WorkflowEdge) => void;
  removeEdge: (edgeId: string) => void;
  updateWorkflow: (updates: Partial<WorkflowState>) => void;
  executeWorkflow: () => Promise<void>;
  clearExecution: () => void;
} 