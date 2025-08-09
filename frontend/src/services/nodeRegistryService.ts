import { apiService } from './api';

export interface NodeMetadata {
  type: string;
  label: string;
  description: string;
  icon: string;
  color: string;
  category: string;
  required_inputs: string[];
  optional_inputs: string[];
}

export interface NodeRegistryResponse {
  success: boolean;
  nodes: Record<string, NodeMetadata>;
  count: number;
  categories: string[];
}

class NodeRegistryService {
  private cache: NodeRegistryResponse | null = null;
  private lastFetch: number = 0;
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  async getNodeRegistry(): Promise<NodeRegistryResponse> {
    const now = Date.now();
    
    // Return cached data if still valid
    if (this.cache && (now - this.lastFetch) < this.CACHE_DURATION) {
      return this.cache;
    }

    try {
      // Use the apiService to make the request
      const response = await apiService.request<NodeRegistryResponse>('/api/nodes/registry');
      this.cache = response;
      this.lastFetch = now;
      return response;
    } catch (error) {
      console.error('Failed to fetch node registry:', error);
      // Return cached data if available, even if expired
      if (this.cache) {
        return this.cache;
      }
      throw error;
    }
  }

  async getNodeTypes(): Promise<string[]> {
    const registry = await this.getNodeRegistry();
    return Object.keys(registry.nodes);
  }

  async getNodeMetadata(nodeType: string): Promise<NodeMetadata | null> {
    const registry = await this.getNodeRegistry();
    return registry.nodes[nodeType] || null;
  }

  async getNodesByCategory(category: string): Promise<string[]> {
    const registry = await this.getNodeRegistry();
    return Object.entries(registry.nodes)
      .filter(([_, metadata]) => metadata.category === category)
      .map(([type, _]) => type);
  }

  async getCategories(): Promise<string[]> {
    const registry = await this.getNodeRegistry();
    return registry.categories;
  }

  clearCache(): void {
    this.cache = null;
    this.lastFetch = 0;
  }
}

export const nodeRegistryService = new NodeRegistryService();
