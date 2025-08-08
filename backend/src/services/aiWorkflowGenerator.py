import openai
import json
import logging
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_community.llms import HuggingFaceEndpoint
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseLanguageModel
import asyncio

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AIWorkflowGenerator:
    def __init__(self):
        logger.info("Initializing AIWorkflowGenerator")
        self.llm = self._initialize_llm()
        self.client = None  # Keep for backward compatibility
        logger.info(f"AIWorkflowGenerator initialized with LLM: {type(self.llm).__name__ if self.llm else 'None'}")

    def _initialize_llm(self) -> Optional[BaseLanguageModel]:
        """Initialize the best available LLM based on environment configuration"""
        logger.info("Initializing LLM provider")
        
        # Priority 1: Ollama (local, free)
        if os.getenv("USE_OLLAMA", "false").lower() == "true":
            logger.info("Attempting to initialize Ollama LLM")
            try:
                model_name = os.getenv("OLLAMA_MODEL", "llama3.1")
                logger.info(f"Using Ollama model: {model_name}")
                llm = ChatOllama(
                    model=model_name,
                    temperature=0.5,  # Lower for faster responses
                    timeout=30,  # 30 second timeout
                    num_ctx=2048,  # Limit context window for speed
                    num_predict=500  # Limit response length
                )
                logger.info("Ollama LLM initialized successfully")
                return llm
            except Exception as e:
                logger.warning(f"Ollama not available: {e}")
        
        # Priority 2: Hugging Face (free tier)
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if hf_token:
            logger.info("Attempting to initialize Hugging Face LLM")
            try:
                model_id = os.getenv("HF_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct")
                logger.info(f"Using Hugging Face model: {model_id}")
                llm = HuggingFaceEndpoint(
                    endpoint_url=f"https://api-inference.huggingface.co/models/{model_id}",
                    huggingfacehub_api_token=hf_token,
                    task="text-generation",
                    model_kwargs={"temperature": 0.7}
                )
                logger.info("Hugging Face LLM initialized successfully")
                return llm
            except Exception as e:
                logger.warning(f"Hugging Face not available: {e}")
        
        # Priority 3: OpenAI (fallback)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            logger.info("Attempting to initialize OpenAI LLM")
            try:
                llm = ChatOpenAI(
                    model="gpt-4",
                    temperature=0.7,
                    api_key=api_key
                )
                logger.info("OpenAI LLM initialized successfully")
                return llm
            except Exception as e:
                logger.warning(f"OpenAI not available: {e}")
        
        # Priority 4: Together AI (very cheap alternative)
        together_api_key = os.getenv("TOGETHER_API_KEY")
        if together_api_key:
            logger.info("Attempting to initialize Together AI LLM")
            try:
                llm = ChatOpenAI(
                    model="meta-llama/Llama-3.1-8B-Instruct",
                    temperature=0.7,
                    api_key=together_api_key,
                    base_url="https://api.together.xyz/v1"
                )
                logger.info("Together AI LLM initialized successfully")
                return llm
            except Exception as e:
                logger.warning(f"Together AI not available: {e}")
        
        logger.warning("No LLM provider configured, using fallback workflow generation")
        return None

    async def generateWorkflow(self, request: Dict[str, Any]) -> Dict[str, Any]:
        prompt = request.get('prompt', '')
        logger.info(f"Starting workflow generation for prompt: '{prompt[:50]}...'")
        
        try:
            # Check if LLM is available
            if self.llm is None:
                logger.warning("No LLM provider configured, using fallback workflow")
                return self._generate_fallback_workflow(prompt)
            
            logger.info("Building prompts for LLM")
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(prompt)

            # Use LangChain for better integration with LangGraph
            logger.info("Creating LangChain template and chain")
            template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", user_prompt)
            ])
            
            chain = template | self.llm
            logger.info("Invoking LLM chain")
            try:
                response = await asyncio.wait_for(
                    chain.ainvoke({"prompt": prompt}),
                    timeout=180.0  # 45 second timeout
                )
            except asyncio.TimeoutError:
                logger.error("Ollama request timed out after 45 seconds")
                raise Exception('LLM request timed out')

            if not response.content:
                logger.error("No response content from AI service")
                raise Exception('No response from AI service')

            logger.info(f"Received response from LLM (length: {len(response.content)})")
            logger.info(f"LLM response: {response.content}")
            
            result = self._parse_ai_response(response.content, prompt)
            logger.info("Workflow generation completed successfully")
            return result
            
        except Exception as error:
            logger.error(f'Error generating workflow: {error}', exc_info=True)
            # Return fallback workflow instead of raising exception
            logger.info("Returning fallback workflow due to error")
            return self._generate_fallback_workflow(prompt)

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
        "label": ""
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
        logger.info("Parsing AI response")
        try:
            # Try to extract JSON from the response
            json_match = response.find('{')
            if json_match == -1:
                logger.error("No JSON found in response")
                raise Exception('No JSON found in response')

            logger.info(f"Found JSON start at position {json_match}")
            # Find the closing brace by counting braces
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
            
            json_str = response[json_match:end_pos]
            logger.info(f"Extracted JSON string (length: {len(json_str)})")
            logger.debug(f"JSON string: {json_str[:200]}...")
            
            parsed = json.loads(json_str)
            logger.info("JSON parsed successfully")
            
            # Validate and enhance the response
            logger.info("Validating and enhancing parsed response")
            result = {
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
            logger.info(f"Response validation completed. Workflow: {result['workflow']['name']}, Nodes: {len(result['workflow']['nodes'])}, Edges: {len(result['workflow']['edges'])}")
            return result
        except Exception as error:
            logger.error(f'Error parsing AI response: {error}', exc_info=True)
            # Fallback to a simple workflow
            logger.info("Falling back to simple workflow due to parsing error")
            return self._generate_fallback_workflow(original_prompt)

    def _validate_and_enhance_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Validating and enhancing {len(nodes)} nodes")
        valid_node_types = [
            'aiAgent', 'email', 'slack', 'data', 'condition', 'delay', 
            'schedule', 'blogWriter', 'socialMedia', 'imageGenerator', 'seoOptimizer'
        ]

        enhanced_nodes = []
        for index, node in enumerate(nodes):
            original_type = node.get('type', 'unknown')
            if original_type not in valid_node_types:
                logger.warning(f"Invalid node type '{original_type}' for node {index + 1}, defaulting to 'aiAgent'")
            
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
            logger.debug(f"Enhanced node {index + 1}: {enhanced_node['type']} - {enhanced_node['label']}")

        logger.info(f"Node validation completed. Enhanced {len(enhanced_nodes)} nodes")
        return enhanced_nodes

    def _validate_and_enhance_edges(self, edges: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Validating and enhancing {len(edges)} edges")
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
            logger.debug(f"Enhanced edge {index + 1}: {enhanced_edge['source']} -> {enhanced_edge['target']}")

        logger.info(f"Edge validation completed. Enhanced {len(enhanced_edges)} edges")
        return enhanced_edges

    def _generate_workflow_name(self, prompt: str) -> str:
        logger.debug(f"Generating workflow name from prompt: '{prompt[:50]}...'")
        words = prompt.lower().split()
        key_words = [word for word in words if word in ['find', 'send', 'create', 'process', 'automate', 'generate']]
        name = f"{key_words[0].capitalize()} Workflow" if key_words else 'Automation Workflow'
        logger.debug(f"Generated workflow name: {name}")
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
        