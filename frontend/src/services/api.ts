import { config } from '../config/environment';
import { authService } from './auth';

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

// Scheduler Types
export interface CreateRecurringScheduleRequest {
	workflow_id: string;
	name: string;
	cron_expression: string;
	timezone?: string;
	description?: string;
	metadata?: Record<string, any>;
}

export interface CreateOneTimeScheduleRequest {
	workflow_id: string;
	name: string;
	run_at: string; // ISO string
	description?: string;
	metadata?: Record<string, any>;
}

export interface ScheduleResponse {
	success: boolean;
	schedule_id?: string;
	backend_job_id?: string;
	message: string;
	next_run_time?: string;
	run_at?: string;
}

export interface ScheduleListItem {
	schedule_id: string;
	workflow_id: string;
	name: string;
	description?: string;
	cron_expression: string;
	timezone: string;
	is_active: boolean;
	backend_type: string;
	created_at: string;
	last_execution_at?: string;
	next_execution_at?: string;
	execution_count: number;
	metadata?: Record<string, any>;
}

export interface ExecutionHistoryItem {
	execution_id: string;
	workflow_id: string;
	execution_type: string;
	status: string;
	success?: boolean;
	started_at: string;
	completed_at?: string;
	duration_seconds?: number;
	error_message?: string;
	node_results_count: number;
}

export interface SchedulerStatusResponse {
	backend: string;
	is_distributed: boolean;
	active_schedules: number;
	executions_24h: number;
	success_rate_24h: number;
	status: string;
	error?: string;
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
				...authService.getAuthHeaders(),
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

	// Scheduler API Methods
	async createRecurringSchedule(
		request: CreateRecurringScheduleRequest, 
		userId: string = 'default_user'
	): Promise<ScheduleResponse> {
		return this.request<ScheduleResponse>('/api/scheduler/recurring', {
			method: 'POST',
			body: JSON.stringify(request),
			headers: {
				'Content-Type': 'application/json',
				'X-User-ID': userId, // TODO: Replace with proper auth
			},
		});
	}

	async createOneTimeSchedule(
		request: CreateOneTimeScheduleRequest, 
		userId: string = 'default_user'
	): Promise<ScheduleResponse> {
		return this.request<ScheduleResponse>('/api/scheduler/one-time', {
			method: 'POST',
			body: JSON.stringify(request),
			headers: {
				'Content-Type': 'application/json',
				'X-User-ID': userId, // TODO: Replace with proper auth
			},
		});
	}

	async listUserSchedules(userId: string = 'default_user'): Promise<ScheduleListItem[]> {
		return this.request<ScheduleListItem[]>(`/api/scheduler/?user_id=${userId}`);
	}

	async pauseSchedule(scheduleId: string, userId: string = 'default_user'): Promise<{ success: boolean; message: string }> {
		return this.request<{ success: boolean; message: string }>(`/api/scheduler/${scheduleId}/pause`, {
			method: 'POST',
			headers: {
				'X-User-ID': userId, // TODO: Replace with proper auth
			},
		});
	}

	async resumeSchedule(scheduleId: string, userId: string = 'default_user'): Promise<{ success: boolean; message: string }> {
		return this.request<{ success: boolean; message: string }>(`/api/scheduler/${scheduleId}/resume`, {
			method: 'POST',
			headers: {
				'X-User-ID': userId, // TODO: Replace with proper auth
			},
		});
	}

	async deleteSchedule(scheduleId: string, userId: string = 'default_user'): Promise<{ success: boolean; message: string; backend_removal_success: boolean }> {
		return this.request<{ success: boolean; message: string; backend_removal_success: boolean }>(`/api/scheduler/${scheduleId}`, {
			method: 'DELETE',
			headers: {
				'X-User-ID': userId, // TODO: Replace with proper auth
			},
		});
	}

	async getExecutionHistory(
		workflowId: string, 
		userId: string = 'default_user', 
		limit: number = 50
	): Promise<ExecutionHistoryItem[]> {
		return this.request<ExecutionHistoryItem[]>(`/api/scheduler/${workflowId}/history?user_id=${userId}&limit=${limit}`);
	}

	async getSchedulerStatus(): Promise<SchedulerStatusResponse> {
		return this.request<SchedulerStatusResponse>('/api/scheduler/status');
	}
}

// Create singleton instance
export const apiService = new ApiService();

// Export for use in components
export default apiService; 