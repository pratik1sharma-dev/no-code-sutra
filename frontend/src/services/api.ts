import { config } from '../config/environment';

const API_BASE_URL = config.apiBaseUrl;

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
			estimatedCost: string;
			requiredIntegrations: string[];
			authRequirements: string[];
			complexity: 'simple' | 'medium' | 'complex';
			estimatedTime: string;
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
	execution_time?: number;
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

	async request<T>(
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

	// Save Workflow
	async saveWorkflow(workflow: any): Promise<{ success: boolean; error?: string }> {
		const payload = {
			id: workflow.id,
			name: workflow.name,
			description: workflow.description || '',
			data: workflow,
		};
		return this.request<{ success: boolean; error?: string }>('/api/workflows/save', {
			method: 'POST',
			body: JSON.stringify(payload),
		});
	}

	// Save Execution Result
	async saveExecution(result: any): Promise<{ success: boolean; error?: string }> {
		return this.request<{ success: boolean; error?: string }>('/api/executions/save', {
			method: 'POST',
			body: JSON.stringify(result),
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

	// Generic HTTP methods for Instagram OAuth
	async get<T>(endpoint: string): Promise<T> {
		return this.request<T>(endpoint, { method: 'GET' });
	}

	async post<T>(endpoint: string, data?: any): Promise<T> {
		return this.request<T>(endpoint, {
			method: 'POST',
			body: data ? JSON.stringify(data) : undefined,
		});
	}

	async put<T>(endpoint: string, data?: any): Promise<T> {
		return this.request<T>(endpoint, {
			method: 'PUT',
			body: data ? JSON.stringify(data) : undefined,
		});
	}

	async delete<T>(endpoint: string): Promise<T> {
		return this.request<T>(endpoint, { method: 'DELETE' });
	}
}

// Create singleton instance
export const apiService = new ApiService();

// Export for use in components
export default apiService; 