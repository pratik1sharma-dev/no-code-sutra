import OpenAI from 'openai';
import type { WorkflowNode, WorkflowEdge, NodeType } from '../types/workflow';

interface WorkflowGenerationRequest {
  prompt: string;
  userId?: string;
}

interface WorkflowGenerationResponse {
  workflow: {
    name: string;
    description: string;
    nodes: WorkflowNode[];
    edges: WorkflowEdge[];
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
}

export class AIWorkflowGenerator {
  private openai: OpenAI;

  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  async generateWorkflow(request: WorkflowGenerationRequest): Promise<WorkflowGenerationResponse> {
    try {
      const systemPrompt = this.buildSystemPrompt();
      const userPrompt = this.buildUserPrompt(request.prompt);

      const completion = await this.openai.chat.completions.create({
        model: 'gpt-4',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userPrompt }
        ],
        temperature: 0.7,
        max_tokens: 2000,
      });

      const response = completion.choices[0]?.message?.content;
      if (!response) {
        throw new Error('No response from AI service');
      }

      return this.parseAIResponse(response, request.prompt);
    } catch (error) {
      console.error('Error generating workflow:', error);
      throw new Error('Failed to generate workflow');
    }
  }

  private buildSystemPrompt(): string {
    return `You are an expert AI workflow designer for No Code Sutra, a platform that creates automation workflows from natural language descriptions.

Your task is to analyze user requests and generate structured workflow definitions that can be executed by our platform.

AVAILABLE NODE TYPES:
- aiAgent: AI-powered tasks (research, analysis, content generation)
- email: Send emails via SMTP or email services
- slack: Send messages to Slack channels
- data: Data processing and manipulation
- condition: Conditional logic and branching
- delay: Time delays and scheduling
- schedule: Recurring task scheduling
- blogWriter: Generate blog content
- socialMedia: Post to social media platforms
- imageGenerator: Generate images using AI
- seoOptimizer: SEO optimization tasks

RESPONSE FORMAT:
Return a JSON object with the following structure:
{
  "workflow": {
    "name": "Descriptive workflow name",
    "description": "Clear description of what the workflow does",
    "nodes": [
      {
        "id": "unique_id",
        "type": "node_type",
        "label": "Human readable label",
        "position": {"x": 100, "y": 100},
        "data": {
          "label": "Node label",
          "type": "node_type",
          "config": {},
          "status": "idle",
          "executionCount": 0
        }
      }
    ],
    "edges": [
      {
        "id": "edge_id",
        "source": "source_node_id",
        "target": "target_node_id",
        "type": "default",
        "label": ""
      }
    ],
    "metadata": {
      "title": "Workflow title",
      "description": "Detailed description",
      "estimatedCost": "Free to $50/month",
      "requiredIntegrations": ["LinkedIn", "Email"],
      "authRequirements": ["LinkedIn API Key", "SMTP Credentials"],
      "complexity": "simple|medium|complex",
      "estimatedTime": "5-10 minutes setup"
    }
  },
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "questions": ["Clarifying question 1", "Clarifying question 2"]
}

GUIDELINES:
1. Keep workflows simple and focused
2. Use clear, descriptive node labels
3. Position nodes logically (left to right flow)
4. Include relevant metadata for user understanding
5. Suggest improvements and ask clarifying questions
6. Focus on practical, achievable automations`;
  }

  private buildUserPrompt(userPrompt: string): string {
    return `Please analyze this user request and generate a workflow:

USER REQUEST: "${userPrompt}"

Please create a workflow that accomplishes this goal. Consider:
- What steps are needed?
- What integrations are required?
- What could go wrong?
- How can we make it more robust?

Generate the workflow in the specified JSON format.`;
  }

  private parseAIResponse(response: string, originalPrompt: string): WorkflowGenerationResponse {
    try {
      // Try to extract JSON from the response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (!jsonMatch) {
        throw new Error('No JSON found in response');
      }

      const parsed = JSON.parse(jsonMatch[0]);
      
      // Validate and enhance the response
      return {
        workflow: {
          name: parsed.workflow?.name || this.generateWorkflowName(originalPrompt),
          description: parsed.workflow?.description || originalPrompt,
          nodes: this.validateAndEnhanceNodes(parsed.workflow?.nodes || []),
          edges: this.validateAndEnhanceEdges(parsed.workflow?.edges || []),
          metadata: {
            title: parsed.workflow?.metadata?.title || parsed.workflow?.name || 'Generated Workflow',
            description: parsed.workflow?.metadata?.description || originalPrompt,
            estimatedCost: parsed.workflow?.metadata?.estimatedCost || 'Free to $20/month',
            requiredIntegrations: parsed.workflow?.metadata?.requiredIntegrations || [],
            authRequirements: parsed.workflow?.metadata?.authRequirements || [],
            complexity: parsed.workflow?.metadata?.complexity || 'simple',
            estimatedTime: parsed.workflow?.metadata?.estimatedTime || '5-10 minutes'
          }
        },
        suggestions: parsed.suggestions || [],
        questions: parsed.questions || []
      };
    } catch (error) {
      console.error('Error parsing AI response:', error);
      // Fallback to a simple workflow
      return this.generateFallbackWorkflow(originalPrompt);
    }
  }

  private validateAndEnhanceNodes(nodes: any[]): WorkflowNode[] {
    const validNodeTypes: NodeType[] = [
      'aiAgent', 'email', 'slack', 'data', 'condition', 'delay', 
      'schedule', 'blogWriter', 'socialMedia', 'imageGenerator', 'seoOptimizer'
    ];

    return nodes.map((node, index) => ({
      id: node.id || `node_${index + 1}`,
      type: validNodeTypes.includes(node.type) ? node.type : 'aiAgent',
      label: node.label || `Step ${index + 1}`,
      position: node.position || { x: 100 + (index * 200), y: 100 },
      data: {
        label: node.data?.label || node.label || `Step ${index + 1}`,
        type: validNodeTypes.includes(node.type) ? node.type : 'aiAgent',
        config: node.data?.config || {},
        status: 'idle',
        executionCount: 0
      }
    }));
  }

  private validateAndEnhanceEdges(edges: any[]): WorkflowEdge[] {
    return edges.map((edge, index) => ({
      id: edge.id || `edge_${index + 1}`,
      source: edge.source || '',
      target: edge.target || '',
      type: edge.type || 'default',
      label: edge.label || ''
    }));
  }

  private generateWorkflowName(prompt: string): string {
    const words = prompt.toLowerCase().split(' ');
    const keyWords = words.filter(word => 
      ['find', 'send', 'create', 'process', 'automate', 'generate'].includes(word)
    );
    return keyWords.length > 0 
      ? `${keyWords[0].charAt(0).toUpperCase() + keyWords[0].slice(1)} Workflow`
      : 'Automation Workflow';
  }

  private generateFallbackWorkflow(prompt: string): WorkflowGenerationResponse {
    return {
      workflow: {
        name: this.generateWorkflowName(prompt),
        description: `Automation workflow for: ${prompt}`,
        nodes: [
          {
            id: '1',
            type: 'aiAgent',
            label: 'Process Request',
            position: { x: 100, y: 100 },
            data: {
              label: 'Process Request',
              type: 'aiAgent',
              config: { prompt: prompt },
              status: 'idle',
              executionCount: 0
            }
          }
        ],
        edges: [],
        metadata: {
          title: this.generateWorkflowName(prompt),
          description: `Basic automation for: ${prompt}`,
          estimatedCost: 'Free',
          requiredIntegrations: [],
          authRequirements: [],
          complexity: 'simple',
          estimatedTime: '5 minutes'
        }
      },
      suggestions: [
        'Consider adding more specific steps to make this workflow more robust',
        'You may need to connect external services for full functionality'
      ],
      questions: [
        'What specific outcome are you looking for?',
        'Do you have any existing tools or services you\'d like to integrate?'
      ]
    };
  }
}

export default AIWorkflowGenerator; 