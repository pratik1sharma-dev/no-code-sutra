import openai
import json
import logging
import boto3
from typing import Dict, Any, List, Optional
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEndpoint
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
        
        # Priority 1: Amazon Bedrock (fastest & most reliable)
        bedrock_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        if bedrock_token:
            logger.info("Attempting to initialize Amazon Bedrock LLM")
            try:
                model_id = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-1-8b-instruct-v1:0")
                region = os.getenv("AWS_DEFAULT_REGION", "ap-southeast-1")
                logger.info(f"Using Bedrock model: {model_id} in region: {region}")
                
                # Set the Bearer token as environment variable for Bedrock
                os.environ['AWS_BEARER_TOKEN_BEDROCK'] = bedrock_token
                
                # Create a simple object to identify this as a Bedrock client
                llm = type('BedrockClient', (), {'converse': True})()
                logger.info("Amazon Bedrock LLM initialized successfully")
                return llm
            except Exception as e:
                logger.warning(f"Amazon Bedrock not available: {e}")
        
        # Priority 2: Ollama (local, free)
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
                    num_predict=1200  # Limit response length
                )
                logger.info("Ollama LLM initialized successfully")
                return llm
            except Exception as e:
                logger.warning(f"Ollama not available: {e}")
        
        # Priority 3: Hugging Face (free tier)
        hf_token = os.getenv("HUGGINGFACE_API_TOKEN")
        if hf_token:
            logger.info("Attempting to initialize Hugging Face LLM")
            try:
                model_id = os.getenv("HF_MODEL_ID", "meta-llama/Llama-3.1-8B-Instruct:novita")
                logger.info(f"Using Hugging Face model: {model_id}")
                llm = HuggingFaceEndpoint(
                    endpoint_url=f"https://api-inference.huggingface.co/models/{model_id}",
                    huggingfacehub_api_token=hf_token,
                    task="text-generation",
                    temperature=0.7
                )
                logger.info("Hugging Face LLM initialized successfully")
                return llm
            except Exception as e:
                logger.warning(f"Hugging Face not available: {e}")
        
        # Priority 4: OpenAI (fallback)
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
        
        # Priority 5: Together AI (very cheap alternative)
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

            # Create the full prompt
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            logger.info("Invoking LLM")
            try:
                # Use simple boto3 approach
                if hasattr(self.llm, 'converse'):  # Bedrock client
                    messages = [{"role": "user", "content": [{"text": full_prompt}]}]
                    
                    # Use requests library for API key authentication as per AWS docs
                    import requests
                    bedrock_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
                    region = os.getenv("AWS_DEFAULT_REGION", "ap-southeast-1")
                    model_id = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-1-8b-instruct-v1:0")
                    
                    url = f"https://bedrock-runtime.{region}.amazonaws.com/model/{model_id}/converse"
                    
                    payload = {"messages": messages}
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {bedrock_token}"
                    }
                    
                    response = await asyncio.to_thread(
                        requests.post,
                        url,
                        json=payload,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        logger.info(f"Bedrock response structure: {list(response_data.keys())}")
                        
                        # Handle different response structures
                        if 'content' in response_data:
                            response_content = response_data['content'][0]['text']
                        elif 'message' in response_data:
                            response_content = response_data['message']['content'][0]['text']
                        elif 'output' in response_data and 'message' in response_data['output']:
                            response_content = response_data['output']['message']['content'][0]['text']
                        elif 'generation' in response_data:
                            response_content = response_data['generation']
                        else:
                            # Log the full response for debugging
                            logger.error(f"Unexpected response structure: {response_data}")
                            raise Exception(f"Unexpected response structure from Bedrock API")
                    else:
                        raise Exception(f"Bedrock API error: {response.status_code} - {response.text}")
                else:  # Other LLM providers
                    response_content = await asyncio.wait_for(
                        self.llm._acall(full_prompt),
                        timeout=30.0
                    )
            except asyncio.TimeoutError:
                logger.error("LLM request timed out after 30 seconds")
                raise Exception('LLM request timed out')

            if not response_content:
                logger.error("No response content from AI service")
                raise Exception('No response from AI service')

            logger.info(f"Received response from LLM (length: {len(response_content)})")
            logger.info(f"LLM response: {response_content[100:]}")
            
            result = self._parse_ai_response(response_content, prompt)
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

AVAILABLE NODE TYPES (16 Core Types):
- aiAgent: AI-powered tasks (research, analysis, content generation, image generation, SEO optimization)
- webScraper: Extract data from websites and web pages
- email: Send emails via SMTP or email services
- slack: Send messages to Slack channels
- notification: Send notifications (push, SMS, in-app)
- data: Data processing, storage, and manipulation
- fileOperation: File operations (read, write, move, delete)
- database: Database operations (query, insert, update, delete)
- apiCall: External API integrations (social media, third-party services)
- condition: Conditional logic and branching
- delay: Time delays and scheduling
- schedule: Recurring task scheduling
- transform: Data transformation (CSV↔JSON, format conversion)
- filter: Data filtering based on conditions
- aggregate: Data aggregation (group, sum, count, average)
- errorHandler: Error handling and recovery

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

CRITICAL: Return ONLY the JSON object. No other text, explanations, or formatting.

GUIDELINES:
1. Keep workflows simple and focused
2. Use clear, descriptive node labels
3. Position nodes logically (left to right flow)
4. ENSURE ALL NODES ARE CONNECTED IN EXECUTION ORDER
5. Include relevant metadata for user understanding
6. Suggest improvements and ask clarifying questions
7. Focus on practical, achievable automations

WORKFLOW VALIDATION:
Before returning the response, verify:
- All nodes are connected in a logical sequence
- No orphaned or disconnected nodes exist
- The workflow forms a complete execution chain
- Parallel branches are properly connected to main flow
- Every node has appropriate incoming and outgoing connections"""

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
            
            # Clean up the JSON string - remove any trailing content after the closing brace
            json_str = json_str.strip()
            
            # Try to parse the JSON
            try:
                parsed = json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed, attempting to fix common issues: {e}")
                # Try to fix common JSON issues
                # Remove any trailing text after the last closing brace
                last_brace = json_str.rfind('}')
                if last_brace != -1:
                    json_str = json_str[:last_brace + 1]
                    try:
                        parsed = json.loads(json_str)
                    except json.JSONDecodeError:
                        logger.error(f"Failed to fix JSON: {json_str}")
                        raise
            logger.info("JSON parsed successfully")
            
            # Validate and enhance the response
            logger.info("Validating and enhancing parsed response")
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
            # Fallback to a simple workflow
            logger.info("Falling back to simple workflow due to parsing error")
            return self._generate_fallback_workflow(original_prompt)

    def _validate_and_enhance_nodes(self, nodes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        logger.info(f"Validating and enhancing {len(nodes)} nodes")
        
        # Consolidated valid node types
        valid_node_types = [
            'aiAgent', 'webScraper', 'email', 'slack', 'notification', 'data',
            'fileOperation', 'database', 'apiCall', 'condition', 'delay', 'schedule',
            'transform', 'filter', 'aggregate', 'errorHandler'
        ]

        enhanced_nodes = []
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
        