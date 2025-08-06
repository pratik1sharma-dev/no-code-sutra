const API_BASE_URL = 'http://localhost:8000';

export interface WorkflowGenerationRequest {
  prompt: string;
  user_id?: string;
  context?: Record<string, any>;
}

export interface WorkflowGenerationResponse {
  workflow: {
    name: string;
    description: string;
    nodes: any[];
    edges: any[];
    metadata: {
      title: string;
      description: string;
      estimated_cost: string;
      required_integrations: string[];
      auth_requirements: string[];
      complexity: 'simple' | 'medium' | 'complex';
      estimated_time: string;
    };
  };
  suggestions: string[];
  questions: string[];
  metadata: any;
  generated_at: string;
}

export interface WorkflowExecutionRequest {
  workflow: any;
  input_data: Record<string, any>;
  user_id?: string;
}

export interface NodeExecutionRequest {
  node_type: string;
  node_config: Record<string, any>;
  input_data: Record<string, any>;
  user_id?: string;
}

export interface WorkflowExecutionResponse {
  success: boolean;
  data: any;
  execution_time: number;
  timestamp: string;
}

export interface AgentInfo {
  id: string;
  name: string;
  description: string;
  capabilities: string[];
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const defaultOptions: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await fetch(url, { ...defaultOptions, ...options });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Workflow Generation
  async generateWorkflow(request: WorkflowGenerationRequest): Promise<WorkflowGenerationResponse> {
    return this.request<WorkflowGenerationResponse>('/api/workflows/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Workflow Execution
  async executeWorkflow(request: WorkflowExecutionRequest): Promise<WorkflowExecutionResponse> {
    return this.request<WorkflowExecutionResponse>('/api/workflows/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // Node Execution
  async executeNode(request: NodeExecutionRequest): Promise<WorkflowExecutionResponse> {
    return this.request<WorkflowExecutionResponse>('/api/nodes/execute', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getWorkflowStatus(workflowId: string): Promise<WorkflowExecutionResponse> {
    return this.request<WorkflowExecutionResponse>(`/api/workflows/${workflowId}/status`);
  }

  // Available Agents
  async getAvailableAgents(): Promise<{ agents: AgentInfo[] }> {
    return this.request<{ agents: AgentInfo[] }>('/api/agents/available');
  }

  // Health Check
  async healthCheck(): Promise<{ status: string; service: string }> {
    return this.request<{ status: string; service: string }>('/health');
  }
}

// Create singleton instance
export const apiService = new ApiService();

// Export for use in components
export default apiService; 