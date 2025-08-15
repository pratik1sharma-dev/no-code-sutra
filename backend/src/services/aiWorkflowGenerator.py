import json
import logging
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
	level=logging.INFO,
	format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Prevent duplicate loggers
if logger.handlers:
	logger.handlers.clear()

from .llm.base import LLMClient
from .llm.bedrock_client import BedrockClient
try:
	from .llm.openai_client import OpenAIClient  # Optional fallback
except Exception:  # pragma: no cover
	OpenAIClient = None  # type: ignore


class AIWorkflowGenerator:
	_instance = None
	
	def __new__(cls):
		if cls._instance is None:
			cls._instance = super().__new__(cls)
		return cls._instance
	
	def __init__(self):
		if not hasattr(self, '_initialized'):
			logger.info("Initializing AIWorkflowGenerator")
			self.llm_client: Optional[LLMClient] = self._initialize_llm_client()
			logger.info(f"AIWorkflowGenerator initialized with LLM client: {type(self.llm_client).__name__ if self.llm_client else 'None'}")
			self._initialized = True
	
	def _initialize_llm_client(self) -> Optional[LLMClient]:
		"""Initialize LLM client: prefer Bedrock; fallback to OpenAI if configured; else None."""
		provider = os.getenv("LLM_PROVIDER", "bedrock").lower()
		if provider == "bedrock":
			if os.getenv("AWS_BEARER_TOKEN_BEDROCK"):
				return BedrockClient()
			logger.warning("Bedrock not configured. Falling back to OpenAI if available.")
		if provider == "openai" or not os.getenv("AWS_BEARER_TOKEN_BEDROCK"):
			if OpenAIClient and os.getenv("OPENAI_API_KEY"):
				return OpenAIClient()
			logger.warning("OpenAI not configured.")
		logger.warning("No LLM provider configured. Will use fallback workflow generation.")
		return None
	
	async def generateWorkflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
		prompt = request.get('prompt', '')
		logger.info(f"Starting workflow generation for prompt: '{prompt[:50]}...'")
		try:
			if self.llm_client is None:
				logger.warning("No LLM provider configured, using fallback workflow")
				return self._generate_fallback_workflow(prompt)
			logger.info("Building prompts for LLM")
			system_prompt = self._build_system_prompt()
			user_prompt = self._build_user_prompt(prompt)
			full_prompt = f"{system_prompt}\n\n{user_prompt}"
			logger.info("Invoking LLM client")
			# Run blocking call in thread to keep FastAPI happy if used async
			response_content = await asyncio.to_thread(self.llm_client.generate, full_prompt)
			if not response_content:
				logger.error("No response content from LLM client")
				raise Exception('No response from AI service')
			logger.info(f"Received response from LLM (length: {len(response_content)})")
			result = self._parse_ai_response(response_content, prompt)
			logger.info("Workflow generation completed successfully")
			return result
		except Exception as error:
			logger.error(f'Error generating workflow: {error}', exc_info=True)
			logger.info("Returning fallback workflow due to error")
			return self._generate_fallback_workflow(prompt)
	
	def _build_system_prompt(self) -> str:
		# Import centralized node registry
		from .node_registry import node_registry
		# Build node types list dynamically
		node_types_list = []
		for node_type, metadata in node_registry._nodes.items():
			if metadata.is_active:
				node_types_list.append(f"- {node_type}: {metadata.description}")
		node_types_text = "\n".join(node_types_list)
		node_count = node_registry.get_node_count()
		return f"""You are an expert AI workflow designer for No Code Sutra, a platform that creates automation workflows from natural language descriptions.

Your task is to analyze user requests and generate structured workflow definitions that can be executed by our platform.

AVAILABLE NODE TYPES ({node_count} Core Types):
{node_types_text}

CRITICAL WORKFLOW RULES:
1. EVERY node must be connected in execution order
2. Each node (except the first) must have at least one incoming edge
3. Each node (except the last) must have at least one outgoing edge
4. Workflows must form a complete execution chain from start to finish
5. No disconnected or orphaned nodes allowed
6. Parallel branches must be properly connected to main flow

RESPONSE FORMAT:
You MUST return ONLY a valid JSON object. Do not include any explanatory text before or after the JSON.

The JSON must have this exact structure:
{{
  "workflow": {{
    "name": "Descriptive workflow name",
    "description": "Clear description of what the workflow does",
    "nodes": [
      {{
        "id": "unique_id",
        "type": "node_type",
        "label": "Human readable label",
        "position": {{"x": 100, "y": 100}},
        "data": {{
          "label": "Node label",
          "type": "node_type",
          "config": {{}},
          "status": "idle",
          "executionCount": 0
        }}
      }}
    ],
         "edges": [
       {{
         "id": "edge_id",
         "source": "source_node_id",
         "target": "target_node_id",
         "type": "default",
         "label": "",
         "data_mapping": {{
           "target_field": "source_node.output.field_name"
         }}
       }}
     ],
    "metadata": {{
      "title": "Workflow title",
      "description": "Detailed description",
      "estimatedCost": "Free to $50/month",
      "requiredIntegrations": ["LinkedIn", "Email"],
      "authRequirements": ["LinkedIn API Key", "SMTP Credentials"],
      "complexity": "simple|medium|complex",
      "estimatedTime": "5-10 minutes setup"
    }}
  }},
  "suggestions": ["Suggestion 1", "Suggestion 2"],
  "questions": ["Clarifying question 1", "Clarifying question 2"]
}}

CRITICAL: Return ONLY the JSON object. No other text, explanations, or formatting.

            GUIDELINES:
            1. Keep workflows simple and focused
            2. Use clear, descriptive node labels
            3. Position nodes logically (left to right flow)
            4. ENSURE ALL NODES ARE CONNECTED IN EXECUTION ORDER
            5. Include relevant metadata for user understanding
            6. Suggest improvements and ask clarifying questions
            7. Focus on practical, achievable automations

NODE CONFIGURATION GUIDELINES:

For AI Agent nodes, you must generate contextual prompts based on the user's intent:

1. ANALYZE the user's request to understand:
   - Target platform (Instagram, LinkedIn, Twitter, Email, etc.)
   - Content type (educational, promotional, entertaining, professional, etc.)
   - Audience and tone requirements
   - Specific constraints or requirements
   - Workflow chain context (what comes after this node)

2. GENERATE an appropriate prompt for the AI Agent that:
   - Specifies the platform and content type
   - Includes platform-specific requirements (character limits, hashtags, tone, etc.)
   - Defines output format (JSON structure)
   - Considers workflow chain (if content goes to other nodes like textOverlay, instagram_post, etc.)

3. EXAMPLES of contextual prompt generation:
   - Instagram with image overlay: "Create Instagram content optimized for image overlay. Generate headline (max 40 chars), bullet points (3-4 items, max 20 chars each), engaging caption (max 200 chars), and relevant hashtags. Content must be CRISP and VISUAL for image overlay. Return JSON: {{\"headline\": \"...\", \"bullets\": [...], \"caption\": \"...\", \"hashtags\": [...]}}"
   - LinkedIn: "Write professional LinkedIn post with industry insights and business-focused tone. Include compelling headline, professional content, relevant hashtags, and call-to-action. Return JSON: {{\"headline\": \"...\", \"content\": \"...\", \"hashtags\": [...]}}"
   - Email: "Compose professional email with subject line and body for business communication. Include clear subject, professional greeting, main content, and closing. Return JSON: {{\"subject\": \"...\", \"body\": \"...\"}}"
   - Twitter: "Create engaging tweet with character limit and trending hashtags. Include main message, relevant hashtags, and call-to-action. Return JSON: {{\"tweet\": \"...\", \"hashtags\": [...]}}"

4. CONFIGURATION STRUCTURE:
   For AI Agent nodes, include in config:
   {{
     "prompt": "Your dynamically generated contextual prompt here",
     "model": "gpt-4",
     "temperature": 0.7,
     "max_tokens": 1000
   }}

5. WORKFLOW CHAIN AWARENESS:
   - If AI Agent → textOverlay: Generate content suitable for image overlay (headlines, bullets, not long paragraphs)
   - If AI Agent → instagram_post: Generate Instagram-optimized content with hashtags
   - If AI Agent → email: Generate professional email content
   - If AI Agent → slack: Generate concise, team-friendly messages

6. DATA MAPPING FOR EDGES:
   When creating edges between nodes, include data_mapping to specify how data flows:
   
   For AI Agent → Text Overlay:
   {{
     "data_mapping": {{
       "ai_output": "ai_agent_1.output"
     }}
   }}
   
   For Text Overlay → Image Upload:
   {{
     "data_mapping": {{
       "image_data_url": "text_overlay_1.output.image_url"
     }}
   }}
   
   For AI Agent + Image Upload → Instagram Post:
   {{
     "data_mapping": {{
       "ai_output": "ai_agent_1.output",
       "image_url": "image_upload_1.output.image_url"
     }}
   }}

CRITICAL: Use your intelligence to generate appropriate prompts based on the user's specific needs. Don't use generic prompts - make them contextual and platform-specific. Consider the entire workflow chain when generating AI Agent prompts.

WORKFLOW VALIDATION:
Before returning the response, verify:
- All nodes are connected in a logical sequence
- No orphaned or disconnected nodes exist
- The workflow forms a complete execution chain
- Parallel branches are properly connected to main flow
- Every node has appropriate incoming and outgoing connections
- AI Agent nodes have contextual, platform-specific prompts"""
	
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
		logger.info("Parsing AI response")
		try:
			json_match = response.find('{')
			if json_match == -1:
				logger.error("No JSON found in response")
				raise Exception('No JSON found in response')
			brace_count = 0
			end_pos = json_match
			for i, char in enumerate(response[json_match:], json_match):
				if char == '{':
					brace_count += 1
				elif char == '}':
					brace_count -= 1
					if brace_count == 0:
						end_pos = i + 1
						break
			json_str = response[json_match:end_pos].strip()
			try:
				parsed = json.loads(json_str)
			except json.JSONDecodeError as e:
				logger.warning(f"JSON parsing failed, attempting to fix common issues: {e}")
				last_brace = json_str.rfind('}')
				if last_brace != -1:
					json_str = json_str[:last_brace + 1]
					parsed = json.loads(json_str)
			result = {
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
				},
				"suggestions": parsed.get('suggestions', []),
				"questions": parsed.get('questions', [])
			}
			logger.info(f"Response validation completed. Workflow: {result['name']}, Nodes: {len(result['nodes'])}, Edges: {len(result['edges'])}")
			return result
		except Exception as error:
			logger.error(f'Error parsing AI response: {error}', exc_info=True)
			return self._generate_fallback_workflow(original_prompt)
	
	def _validate_and_enhance_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		logger.info(f"Validating and enhancing {len(nodes)} nodes")
		from .node_registry import node_registry
		valid_node_types = node_registry.get_active_node_types()
		enhanced_nodes: List[Dict[str, Any]] = []
		for index, node in enumerate(nodes):
			original_type = node.get('type', 'unknown')
			if original_type not in valid_node_types:
				logger.warning(f"Invalid node type '{original_type}' for node {index + 1}, defaulting to 'aiAgent'")
				original_type = 'aiAgent'
			enhanced_node = {
				"id": node.get('id') or f"node_{index + 1}",
				"type": original_type,
				"label": node.get('label') or f"Step {index + 1}",
				"position": node.get('position') or {"x": 100 + (index * 200), "y": 100},
				"data": {
					"label": node.get('data', {}).get('label') or node.get('label') or f"Step {index + 1}",
					"type": original_type,
					"config": node.get('data', {}).get('config') or {},
					"status": "idle",
					"executionCount": 0
				}
			}
			enhanced_nodes.append(enhanced_node)
		return enhanced_nodes
	
	def _validate_and_enhance_edges(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
		logger.info(f"Validating and enhancing {len(edges)} edges")
		enhanced_edges: List[Dict[str, Any]] = []
		for index, edge in enumerate(edges):
			enhanced_edge = {
				"id": edge.get('id') or f"edge_{index + 1}",
				"source": edge.get('source') or '',
				"target": edge.get('target') or '',
				"type": edge.get('type') or 'default',
				"label": edge.get('label') or '',
				"data_mapping": edge.get('data_mapping') or {}
			}
			enhanced_edges.append(enhanced_edge)
		return enhanced_edges
	
	def _generate_workflow_name(self, prompt: str) -> str:
		words = prompt.lower().split()
		key_words = [word for word in words if word in ['find', 'send', 'create', 'process', 'automate', 'generate']]
		name = f"{key_words[0].capitalize()} Workflow" if key_words else 'Automation Workflow'
		return name
	
	def _generate_fallback_workflow(self, prompt: str) -> Dict[str, Any]:
		logger.info(f"Generating fallback workflow for prompt: '{prompt[:50]}...'")
		workflow_name = self._generate_workflow_name(prompt)
		fallback_workflow = {
			"workflow": {
				"name": workflow_name,
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
					"title": workflow_name,
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
		logger.info(f"Fallback workflow generated: {workflow_name} with 1 node")
		return fallback_workflow 
        