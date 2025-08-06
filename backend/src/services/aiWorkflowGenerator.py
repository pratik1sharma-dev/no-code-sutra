import openai
import json
from typing import Dict, Any, List
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

class AIWorkflowGenerator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            self.client = openai.OpenAI(api_key=api_key)
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.7,
                api_key=api_key
            )
        else:
            self.client = None
            self.llm = None

    async def generateWorkflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        try:
            # Check if LangChain LLM is available
            if self.llm is None:
                print("OpenAI API key not configured, using fallback workflow")
                return self._generate_fallback_workflow(request.get('prompt', ''))
            
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(request.get('prompt', ''))

            # Use LangChain for better integration with LangGraph
            template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", user_prompt)
            ])
            
            chain = template | self.llm
            response = await chain.ainvoke({"prompt": request.get('prompt', '')})

            if not response.content:
                raise Exception('No response from AI service')

            return self._parse_ai_response(response.content, request.get('prompt', ''))
        except Exception as error:
            print(f'Error generating workflow: {error}')
            # Return fallback workflow instead of raising exception
            return self._generate_fallback_workflow(request.get('prompt', ''))

    def _build_system_prompt(self) -> str:
        return """You are an expert AI workflow designer for No Code Sutra, a platform that creates automation workflows from natural language descriptions.

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
6. Focus on practical, achievable automations"""

    def _build_user_prompt(self, user_prompt: str) -> str:
        return f"""Please analyze this user request and generate a workflow:

USER REQUEST: "{user_prompt}"

Please create a workflow that accomplishes this goal. Consider:
- What steps are needed?
- What integrations are required?
- What could go wrong?
- How can we make it more robust?

Generate the workflow in the specified JSON format."""

    def _parse_ai_response(self, response: str, original_prompt: str) -> Dict[str, Any]:
        try:
            # Try to extract JSON from the response
            json_match = response.find('{')
            if json_match == -1:
                raise Exception('No JSON found in response')

            json_str = response[json_match:]
            parsed = json.loads(json_str)
            
            # Validate and enhance the response
            return {
                "workflow": {
                    "name": parsed.get('workflow', {}).get('name') or self._generate_workflow_name(original_prompt),
                    "description": parsed.get('workflow', {}).get('description') or original_prompt,
                    "nodes": self._validate_and_enhance_nodes(parsed.get('workflow', {}).get('nodes', [])),
                    "edges": self._validate_and_enhance_edges(parsed.get('workflow', {}).get('edges', [])),
                    "metadata": {
                        "title": parsed.get('workflow', {}).get('metadata', {}).get('title') or parsed.get('workflow', {}).get('name') or 'Generated Workflow',
                        "description": parsed.get('workflow', {}).get('metadata', {}).get('description') or original_prompt,
                        "estimatedCost": parsed.get('workflow', {}).get('metadata', {}).get('estimatedCost') or 'Free to $20/month',
                        "requiredIntegrations": parsed.get('workflow', {}).get('metadata', {}).get('requiredIntegrations') or [],
                        "authRequirements": parsed.get('workflow', {}).get('metadata', {}).get('authRequirements') or [],
                        "complexity": parsed.get('workflow', {}).get('metadata', {}).get('complexity') or 'simple',
                        "estimatedTime": parsed.get('workflow', {}).get('metadata', {}).get('estimatedTime') or '5-10 minutes'
                    }
                },
                "suggestions": parsed.get('suggestions', []),
                "questions": parsed.get('questions', [])
            }
        except Exception as error:
            print(f'Error parsing AI response: {error}')
            # Fallback to a simple workflow
            return self._generate_fallback_workflow(original_prompt)

    def _validate_and_enhance_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        valid_node_types = [
            'aiAgent', 'email', 'slack', 'data', 'condition', 'delay', 
            'schedule', 'blogWriter', 'socialMedia', 'imageGenerator', 'seoOptimizer'
        ]

        enhanced_nodes = []
        for index, node in enumerate(nodes):
            enhanced_node = {
                "id": node.get('id') or f"node_{index + 1}",
                "type": node.get('type') if node.get('type') in valid_node_types else 'aiAgent',
                "label": node.get('label') or f"Step {index + 1}",
                "position": node.get('position') or {"x": 100 + (index * 200), "y": 100},
                "data": {
                    "label": node.get('data', {}).get('label') or node.get('label') or f"Step {index + 1}",
                    "type": node.get('type') if node.get('type') in valid_node_types else 'aiAgent',
                    "config": node.get('data', {}).get('config') or {},
                    "status": "idle",
                    "executionCount": 0
                }
            }
            enhanced_nodes.append(enhanced_node)

        return enhanced_nodes

    def _validate_and_enhance_edges(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        enhanced_edges = []
        for index, edge in enumerate(edges):
            enhanced_edge = {
                "id": edge.get('id') or f"edge_{index + 1}",
                "source": edge.get('source') or '',
                "target": edge.get('target') or '',
                "type": edge.get('type') or 'default',
                "label": edge.get('label') or ''
            }
            enhanced_edges.append(enhanced_edge)

        return enhanced_edges

    def _generate_workflow_name(self, prompt: str) -> str:
        words = prompt.lower().split()
        key_words = [word for word in words if word in ['find', 'send', 'create', 'process', 'automate', 'generate']]
        return f"{key_words[0].capitalize()} Workflow" if key_words else 'Automation Workflow'

    def _generate_fallback_workflow(self, prompt: str) -> Dict[str, Any]:
        return {
            "workflow": {
                "name": self._generate_workflow_name(prompt),
                "description": f"Automation workflow for: {prompt}",
                "nodes": [
                    {
                        "id": "1",
                        "type": "aiAgent",
                        "label": "Process Request",
                        "position": {"x": 100, "y": 100},
                        "data": {
                            "label": "Process Request",
                            "type": "aiAgent",
                            "config": {"prompt": prompt},
                            "status": "idle",
                            "executionCount": 0
                        }
                    }
                ],
                "edges": [],
                "metadata": {
                    "title": self._generate_workflow_name(prompt),
                    "description": f"Basic automation for: {prompt}",
                    "estimatedCost": "Free",
                    "requiredIntegrations": [],
                    "authRequirements": [],
                    "complexity": "simple",
                    "estimatedTime": "5 minutes"
                }
            },
            "suggestions": [
                "Consider adding more specific steps to make this workflow more robust",
                "You may need to connect external services for full functionality"
            ],
            "questions": [
                "What specific outcome are you looking for?",
                "Do you have any existing tools or services you'd like to integrate?"
            ]
        } 