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
	
	def _initialize_llm_client(self, provider: str = "bedrock"):
		"""Initialize the appropriate LLM client based on provider."""
		if provider == "bedrock" and os.getenv("AWS_BEARER_TOKEN_BEDROCK"):
			if BedrockClient:
				system_prompt = self._build_system_prompt()
				return BedrockClient(system_prompt=system_prompt)
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
			logger.info("Invoking LLM client")
			# Run blocking call in thread to keep FastAPI happy if used async
			response_content = await asyncio.to_thread(self.llm_client.generate, prompt)
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
		# Force reload of node_registry to get latest contracts
		import importlib
		from . import node_registry as nr_module
		importlib.reload(nr_module)
		node_registry = nr_module.node_registry
		# Build node types list dynamically
		node_types_list = []
		for node_type, metadata in node_registry._nodes.items():
			if metadata.is_active:
				output_keys = list(metadata.output_schema.get('properties', {}).keys())
				node_types_list.append(f"- {node_type}: {metadata.description}\n  - outputs: {output_keys}")
		node_types_text = "\n".join(node_types_list)
		node_count = node_registry.get_node_count()
		header = f"""You are an expert AI workflow designer for No Code Sutra, a platform that creates automation workflows from natural language descriptions.

Your task is to analyze user requests and generate structured workflow definitions that can be executed by our platform.

AVAILABLE NODE TYPES ({node_count} Core Types):
{node_types_text}

"""
		body = """CRITICAL: You MUST use the EXACT node type names listed above. Do not create variations or use camelCase versions. For example:
- Use "instagram_post" (not "instagramPost")
- Use "textOverlay" (not "text_overlay") 
- Use "imageUpload" (not "image_upload")
- Use "aiAgent" (not "ai_agent")

CRITICAL WORKFLOW RULES:
1. EVERY node must be connected in execution order
2. Each node (except the first) must have at least one incoming edge
3. Each node (except the last) must have at least one outgoing edge
4. Workflows must form a complete execution chain from start to finish
5. No disconnected or orphaned nodes allowed
6. Parallel branches must be properly connected to main flow

RESPONSE FORMAT (STRICT):
You MUST return ONLY a valid JSON object with this exact structure (no prose):
{
  "workflow": {
    "name": "Descriptive workflow name",
    "description": "Clear description of what the workflow does",
    "entry": "node_id_of_entry",
    "nodes": [
      {
        "id": "unique_id",
        "type": "node_type",
        "label": "Human readable label",
        "position": {"x": 100, "y": 100},
        "reads": ["input.prompt", "node123.output"],
        "writes": ["structured_data"],
        "version": "v1",
        "data": {
          "label": "Node label",
          "type": "node_type",
          "config": {}
        }
      }
    ],
    "edges": [
      {"id": "edge_id", "source": "source_node_id", "target": "target_node_id", "type": "default", "label": ""}
    ],
    "conditions": [
      {"source": "node_id", "guards": [{"if": "content_type == 'image'", "target": "node_id"}]}
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

CRITICAL: Return ONLY the JSON object. No other text, explanations, or formatting.

            GUIDELINES:
            1. Keep workflows simple and focused
            2. Use clear, descriptive node labels
            3. Position nodes logically (left to right flow)
            4. ENSURE ALL NODES ARE CONNECTED IN EXECUTION ORDER AND DECLARE READS/WRITES
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

   **POST TYPE DETECTION:**
   First, analyze the user request to determine the optimal post type:
   - 'single': Simple messages, tips, announcements (1 main point)
   - 'carousel': Multi-step processes, lists, comparisons (2-5 key points)
   - 'video_reel': Demonstrations, tutorials, dynamic content
   - 'story': Time-sensitive, behind-the-scenes content

   **INSTAGRAM WITH TEXT OVERLAY (ENHANCED):**
   "Create Instagram content optimized for modern visual overlay. Generate:
   - Headline (max 35 chars): Clear, impactful main message
   - Subhead (max 50 chars): Supporting description OR key point
   - Bullet points (1-2 items, max 20 chars each): Key insights (optional)
   - Caption (max 200 chars): Engaging caption for Instagram (goes in caption field)
   - Hashtags (5-8): Relevant, trending hashtags (goes in caption field)
   - Recommended template: Choose from minimal|bold|gradient|split_screen|quote
   
   Content must be VISUAL, ENGAGING, and MOBILE-OPTIMIZED for Instagram. Use modern, professional tone.
   Focus on ONE main message with ONE supporting element. Keep it simple and impactful.
   Return JSON: {\"headline\": \"...\", \"subhead\": \"...\", \"bullets\": [...], \"caption\": \"...\", \"hashtags\": [...], \"recommended_template\": \"minimal\"}"

   **INSTAGRAM CAROUSEL:**
   "Create Instagram carousel content (2-5 slides). Generate:
   - Headline (max 35 chars): Main carousel title
   - Subhead (max 50 chars): Supporting description
   - Slides array (2-5 items):
     - Title (max 25 chars): Slide title
     - Content (max 80 chars): Slide content
     - Stats (max 30 chars): Key metric or stat (optional)
     - image_search_terms (array): 3 relevant image search terms for background image
   - Caption (max 200 chars): Engaging caption
   - Hashtags (5-8): Relevant hashtags
   - Recommended template: Choose from minimal|bold|gradient|split_screen|quote
   
   Each slide should be self-contained but connected to the main theme.
   For image_search_terms, provide 3 visual, descriptive terms that would find good background images.
   Return JSON: {\"headline\": \"...\", \"subhead\": \"...\", \"slides\": [...], \"caption\": \"...\", \"hashtags\": [...], \"recommended_template\": \"split_screen\"}"

   **INSTAGRAM VIDEO REEL:**
   "Create Instagram video reel content. Generate:
   - Headline (max 35 chars): Main reel title
   - Subhead (max 50 chars): Supporting description
   - Script (max 200 chars): Video script or description
   - Key points (3-5 items, max 30 chars each): Main talking points
   - Caption (max 200 chars): Engaging caption
   - Hashtags (5-8): Relevant hashtags
   - Recommended template: Choose from minimal|bold|gradient|split_screen|quote
   
   Content should be engaging and suitable for video format.
   Return JSON: {\"headline\": \"...\", \"subhead\": \"...\", \"script\": \"...\", \"key_points\": [...], \"caption\": \"...\", \"hashtags\": [...], \"recommended_template\": \"bold\"}"

   **INSTAGRAM STORY:**
   "Create Instagram story content. Generate:
   - Headline (max 25 chars): Story title
   - Content (max 100 chars): Story content
   - Call to action (max 30 chars): Action prompt
   - Caption (max 100 chars): Story caption
   - Hashtags (3-5): Relevant hashtags
   - Recommended template: Choose from minimal|bold|gradient|split_screen|quote
   
   Content should be time-sensitive and engaging for stories.
   Return JSON: {\"headline\": \"...\", \"content\": \"...\", \"call_to_action\": \"...\", \"caption\": \"...\", \"hashtags\": [...], \"recommended_template\": \"minimal\"}"

4. TEMPLATE RECOMMENDATION GUIDELINES:
   Choose the appropriate template based on content type:
   - "quote": For inspirational quotes, testimonials, wisdom, love content
   - "minimal": For business, professional, corporate, clean content
   - "bold": For motivational, promotional, urgent messages, announcements
   - "gradient": For tech, lifestyle, creative, modern content
   - "split_screen": For educational, tutorials, features, step-by-step content

5. CONFIGURATION STRUCTURE:
   For AI Agent nodes, include in config:
   {
     "prompt": "Your dynamically generated contextual prompt here",
     "model": "gpt-4",
     "temperature": 0.7,
     "max_tokens": 1000
   }

6. WORKFLOW CHAIN AWARENESS:
   - If AI Agent → textOverlay: Generate content suitable for modern image overlay (hero, headlines, bullets, quotes, stats)
   - If AI Agent → instagram_post: Generate Instagram-optimized content with hashtags
   - If AI Agent → email: Generate professional email content
   - If AI Agent → slack: Generate concise, team-friendly messages

6. DECLARE DATA FLOW VIA READS/WRITES:
   - Do NOT use edge-level data_mapping.
   - Each node must declare what it reads (e.g., "input.prompt", "node123.image_url") and what it writes (e.g., "structured_data", "image_url").

CRITICAL: Use your intelligence to generate appropriate prompts based on the user's specific needs. Don't use generic prompts - make them contextual and platform-specific. Consider the entire workflow chain when generating AI Agent prompts.

IMAGE GENERATION WORKFLOW PATTERNS:

🚨 CRITICAL INSTAGRAM WORKFLOW ORDER 🚨
For Instagram posts with dynamic backgrounds, use this MANDATORY pattern:
1. aiAgent → imageGenerator → textOverlay → imageUpload → instagram_post

⚠️ ABSOLUTE REQUIREMENT: imageGenerator MUST ALWAYS come BEFORE textOverlay for Instagram templates to work properly.
⚠️ THIS IS NON-NEGOTIABLE - Templates cannot render without a background image first.

This pattern provides:
- AI-generated content (hero, headlines, bullets, quotes, stats)
- Dynamic background images from public sources (Unsplash, Pexels, Lorem Picsum)
- Modern text overlay with professional styling and Instagram-optimized fonts
- Cloudinary hosting for public Instagram URLs
- Direct Instagram posting with properly styled overlays

🚫 NEVER EVER USE: aiAgent → textOverlay → imageGenerator (this breaks Instagram templates)
🚫 WRONG ORDER WILL CAUSE TEMPLATE FAILURES

For other social media with images:
1. aiAgent → imageGenerator → textOverlay → imageUpload → [social_media_node]

IMAGE GENERATOR CONFIGURATION:
- The imageGenerator node automatically extracts keywords from AI content
- It searches multiple free APIs in order: Unsplash → Pexels → Lorem Picsum
- No configuration needed - it works automatically with AI content
- Optional: Add "prompt" or "style" for specific image preferences

WORKFLOW VALIDATION:
Before returning the response, verify:
- All nodes are connected in a logical sequence
- No orphaned or disconnected nodes exist
- The workflow forms a complete execution chain
- Parallel branches are properly connected to main flow
- Every node has appropriate incoming and outgoing connections
- AI Agent nodes have contextual, platform-specific prompts
- Image workflows include imageGenerator for dynamic backgrounds
- 🚨 FOR INSTAGRAM: imageGenerator comes BEFORE textOverlay (mandatory for templates) 🚨
- Check execution order: dependencies must be satisfied before dependent nodes"""
		return header + body
	
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
		logger.info(f"Full LLM response: {response}")
		try:
			# Prefer fenced JSON blocks if present
			import re
			code_block = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", response, re.IGNORECASE)
			candidate = code_block.group(1) if code_block else None
			json_match = (candidate or response).find('{')
			if json_match == -1:
				logger.error("No JSON found in response")
				raise Exception('No JSON found in response')
			text = candidate or response
			brace_count = 0
			end_pos = json_match
			for i, char in enumerate(text[json_match:], json_match):
				if char == '{':
					brace_count += 1
				elif char == '}':
					brace_count -= 1
					if brace_count == 0:
						end_pos = i + 1
						break
			json_str = text[json_match:end_pos].strip()
			# Sanitize common issues: backticks, smart quotes, control chars, trailing commas
			json_str = json_str.replace('```', '')
			json_str = json_str.replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'")
			json_str = json_str.replace('“', '"').replace('”', '"').replace('’', "'")
			# Remove invalid control characters except standard whitespace
			json_str = re.sub(r"[\x00-\x08\x0B-\x0C\x0E-\x1F]", " ", json_str)
			# Remove trailing commas before closing braces/brackets
			json_str = re.sub(r",\s*(\}|\])", r"\1", json_str)
			try:
				parsed = json.loads(json_str)
			except json.JSONDecodeError as e:
				logger.warning(f"JSON parsing failed, attempting to fix common issues: {e}")
				last_brace = json_str.rfind('}')
				if last_brace != -1:
					json_str = json_str[:last_brace + 1]
					parsed = json.loads(json_str)
			wf = parsed.get('workflow', {})
			result = {
				"name": wf.get('name') or self._generate_workflow_name(original_prompt),
				"description": wf.get('description') or original_prompt,
				"entry": wf.get('entry') or (wf.get('nodes', [{}])[0].get('id') if wf.get('nodes') else None),
				"nodes": self._validate_and_enhance_nodes(wf.get('nodes', [])),
				"edges": self._validate_and_enhance_edges(wf.get('edges', [])),
				"conditions": wf.get('conditions', []),
				"metadata": {
					"title": wf.get('metadata', {}).get('title') or wf.get('name') or 'Generated Workflow',
					"description": wf.get('metadata', {}).get('description') or original_prompt,
					"estimatedCost": wf.get('metadata', {}).get('estimatedCost') or 'Free to $20/month',
					"requiredIntegrations": wf.get('metadata', {}).get('requiredIntegrations') or [],
					"authRequirements": wf.get('metadata', {}).get('authRequirements') or [],
					"complexity": wf.get('metadata', {}).get('complexity') or 'simple',
					"estimatedTime": wf.get('metadata', {}).get('estimatedTime') or '5-10 minutes'
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
			
			# Validate node type (AI should now generate correct names)
			
			if original_type not in valid_node_types:
				logger.warning(f"Invalid node type '{original_type}' for node {index + 1}, defaulting to 'aiAgent'")
				original_type = 'aiAgent'

			# Get the authoritative writes from the node registry
			node_metadata = node_registry.get_node_metadata(original_type)
			writes_from_contract = []
			if node_metadata:
				writes_from_contract = list(node_metadata.output_schema.get('properties', {}).keys())

			enhanced_node = {
				"id": node.get('id') or f"node_{index + 1}",
				"type": original_type,
				"label": node.get('label') or f"Step {index + 1}",
				"position": node.get('position') or {"x": 100 + (index * 200), "y": 100},
				"reads": node.get('reads') or [],
				"writes": writes_from_contract, # Overwrite with authoritative keys
				"version": node.get('version') or 'v1',
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
				"label": edge.get('label') or ''
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
		flattened = {
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
		return flattened 