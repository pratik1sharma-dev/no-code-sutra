import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useWorkflowStore } from './workflowStore';

// Mock API service
vi.mock('../services/api', () => {
  return {
    apiService: {
      saveWorkflow: vi.fn().mockResolvedValue({ success: true }),
      executeWorkflow: vi.fn().mockResolvedValue({ success: true, data: { execution_id: 'x', status: 'completed' }, timestamp: new Date().toISOString() }),
      saveExecution: vi.fn().mockResolvedValue({ success: true })
    }
  };
});

describe('workflowStore selection and execution stability', () => {
  beforeEach(() => {
    const { setState } = useWorkflowStore as any;
    setState({
      currentWorkflow: {
        id: 'wf1',
        name: 'Test WF',
        description: '',
        nodes: [
          { id: 'n1', type: 'aiAgent', position: { x: 0, y: 0 }, data: { id: 'n1', label: 'Node 1', type: 'aiAgent', config: {}, status: 'idle', executionCount: 0 } }
        ],
        edges: [],
        status: 'draft',
        createdAt: new Date(),
        updatedAt: new Date(),
        executionCount: 0,
        tags: []
      },
      workflows: [],
      isExecuting: false,
      currentExecution: null,
      selectedNode: null,
      selectedEdge: null,
    });
  });

  it('setSelectedNode should be idempotent', () => {
    const { getState } = useWorkflowStore as any;
    const a = useWorkflowStore.getState();
    a.setSelectedNode('n1');
    const s1 = getState().selectedNode;
    a.setSelectedNode('n1');
    const s2 = getState().selectedNode;
    expect(s1).toBe('n1');
    expect(s2).toBe('n1');
  });

  it('setSelectedEdge should be idempotent', () => {
    const a = useWorkflowStore.getState();
    a.setSelectedEdge('e1');
    const s1 = useWorkflowStore.getState().selectedEdge;
    a.setSelectedEdge('e1');
    const s2 = useWorkflowStore.getState().selectedEdge;
    expect(s1).toBe('e1');
    expect(s2).toBe('e1');
  });

  it('executeWorkflow should save then execute without throwing', async () => {
    const a = useWorkflowStore.getState();
    await expect(a.executeWorkflow()).resolves.not.toThrow();
    expect(useWorkflowStore.getState().isExecuting).toBe(false);
    expect(useWorkflowStore.getState().currentExecution?.status).toBe('completed');
  });
});