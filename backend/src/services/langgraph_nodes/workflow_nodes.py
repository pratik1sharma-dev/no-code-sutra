from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from ..instagram_service import InstagramService
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import hashlib
import time

class LangGraphWorkflowNodes:
    def __init__(self):
        # Use the same Bedrock implementation as aiWorkflowGenerator
        bedrock_token = os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        if bedrock_token:
            try:
                model_id = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-1-8b-instruct-v1:0")
                region = os.getenv("AWS_DEFAULT_REGION", "ap-southeast-1")
                print(f"Initializing Bedrock for AI Agent with model: {model_id} in region: {region}")
                
                # Set the Bearer token as environment variable for Bedrock
                os.environ['AWS_BEARER_TOKEN_BEDROCK'] = bedrock_token
                
                # Create a simple object to identify this as a Bedrock client
                self.llm = type('BedrockClient', (), {'converse': True})()
                print("Bedrock LLM initialized successfully for AI Agent")
            except Exception as e:
                print(f"Warning: Could not initialize Bedrock for AI Agent: {e}")
                self.llm = None
        else:
            print("Warning: No Bedrock token found, AI Agent will fail")
            self.llm = None
    
    def ai_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """AI Agent node for intelligent processing"""
        try:
            # Check if LLM is available
            if self.llm is None:
                state['status'] = 'failed'
                state['error'] = 'LLM not available - Bedrock configuration required'
                state['timestamp'] = datetime.now().isoformat()
                return state
            
            # Extract prompt from state (this should be the contextual prompt from workflow generator)
            prompt = state.get('prompt', '')
            task = state.get('task', 'generate')
            topic = state.get('topic', 'content generation')
            context = state.get('context', '')
            
            # Use the contextual prompt if provided, otherwise fallback to generic prompts
            if prompt:
                # Use the contextual prompt from workflow generator
                system_prompt = "You are an AI content generation agent. You MUST follow the instructions exactly and return ONLY the requested format. If the instructions ask for JSON, return ONLY valid JSON without any additional text, explanations, or formatting."
                user_prompt = prompt
            else:
                # Fallback to generic prompts (for backward compatibility)
                if task == 'research':
                    system_prompt = f"You are an AI research agent. Research the topic: {topic}"
                    user_prompt = f"Please provide comprehensive research on: {topic}"
                elif task == 'generate':
                    system_prompt = f"You are an AI content generation agent. Generate content about: {topic}"
                    user_prompt = f"Please generate engaging content about: {topic}"
                elif task == 'analyze':
                    system_prompt = f"You are an AI analysis agent. Analyze the topic: {topic}"
                    user_prompt = f"Please provide detailed analysis of: {topic}"
                else:
                    system_prompt = f"You are an intelligent AI agent. Process the given input and provide a helpful response."
                    user_prompt = f"Context: {context}\n\nTask: {prompt}\n\nTopic: {topic}"
            
            # Use the same Bedrock API call as aiWorkflowGenerator
            if hasattr(self.llm, 'converse'):  # Bedrock client
                # Create the full prompt
                full_prompt = f"{system_prompt}\n\n{user_prompt}"
                messages = [{"role": "user", "content": [{"text": full_prompt}]}]
                
                # Use requests library for API key authentication
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
                
                response = requests.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    response_data = response.json()
                    
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
                        raise Exception(f"Unexpected response structure from Bedrock API")
                else:
                    raise Exception(f"Bedrock API error: {response.status_code} - {response.text}")
            else:
                # Fallback to template approach if not Bedrock
                template = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),
                    ("human", user_prompt)
                ])
                
                chain = template | self.llm
                response = chain.invoke({"context": context, "prompt": prompt, "topic": topic})
                response_content = response.content
            parsed_json = None
            
            print(f"AI Agent raw response (first 500 chars): {response_content[:500]}")
            
            try:
                # Look for JSON in the response
                json_start = response_content.find('{')
                json_end = response_content.rfind('}') + 1
                
                if json_start != -1 and json_end > json_start:
                    json_str = response_content[json_start:json_end]
                    print(f"Attempting to parse JSON: {json_str[:200]}...")
                    parsed_json = json.loads(json_str)
                    print(f"Successfully parsed JSON response: {list(parsed_json.keys()) if isinstance(parsed_json, dict) else 'Not a dict'}")
                else:
                    print("No JSON braces found in response")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Could not parse JSON from response: {e}")
                print(f"JSON string that failed: {json_str[:200] if 'json_str' in locals() else 'No json_str'}")
                parsed_json = None
            
            # Store the AI response in multiple formats for flexibility
            if parsed_json:
                # If we have structured JSON, store it
                state['result'] = parsed_json
                state['output'] = parsed_json
                state['content'] = response_content  # Keep original for backward compatibility
                state['structured_data'] = parsed_json
            else:
                # Fallback to plain text
                state['result'] = response_content
                state['output'] = response_content
                state['content'] = response_content
            state['task'] = task
            state['topic'] = topic
            state['status'] = 'completed'
            state['timestamp'] = datetime.now().isoformat()
            
            print(f"AI Agent completed. Generated content length: {len(response.content)}")
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
            state['timestamp'] = datetime.now().isoformat()
            return state
    
    def email_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Email sending node"""
        try:
            to_email = state.get('to_email', '')
            subject = state.get('subject', '')
            body = state.get('body', '')
            
            # For demo purposes, we'll simulate email sending
            # In production, integrate with actual email service (SendGrid, AWS SES, etc.)
            
            email_data = {
                'to': to_email,
                'subject': subject,
                'body': body,
                'sent_at': datetime.now().isoformat()
            }
            
            state['email_data'] = email_data
            state['status'] = 'sent'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
            return state
    
    def slack_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Slack message node"""
        try:
            channel = state.get('channel', '')
            message = state.get('message', '')
            
            # For demo purposes, we'll simulate Slack message
            # In production, integrate with Slack API
            
            slack_data = {
                'channel': channel,
                'message': message,
                'sent_at': datetime.now().isoformat()
            }
            
            state['slack_data'] = slack_data
            state['status'] = 'sent'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
            return state
    
    def data_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Data processing node"""
        try:
            # Handle different input patterns from LLM workflow
            input_source = state.get('input_source', '')
            output_name = state.get('output_name', 'post_data')
            operation = state.get('operation', 'pass_through')
            
            print(f"Data node processing - input_source: {input_source}, output_name: {output_name}")
            print(f"Available state keys: {list(state.keys())}")
            
            # Get input data - improved logic for finding content
            input_data = None
            
            # First, try the specified input source
            if input_source:
                if input_source in state:
                    input_data = state[input_source]
                    print(f"Found input data from specified source '{input_source}': {type(input_data)}")
                else:
                    print(f"Warning: Specified input source '{input_source}' not found in state")
            
            # If no input source specified or found, try common content fields
            if input_data is None:
                # Look for content from previous AI nodes - prioritize AI-generated content
                for key in ['result', 'output', 'content', 'text', 'data']:
                    if key in state and state[key]:
                        input_data = state[key]
                        print(f"Using content from '{key}': {type(input_data)}")
                        break
            
            # If still no data, check for input_data
            if input_data is None and 'input_data' in state:
                input_data = state['input_data']
                print(f"Using input_data from state: {type(input_data)}")
            
            if input_data is None:
                input_data = "No input data available"
                print("Warning: No input data found")
            
            if operation == 'pass_through':
                # Simple pass-through operation (most common for LLM workflows)
                transformed_data = input_data
            elif operation == 'transform':
                # Data transformation
                transformed_data = self._transform_data(input_data)
            elif operation == 'filter':
                # Data filtering
                transformed_data = self._filter_data(input_data, state.get('filter_criteria', {}))
            elif operation == 'aggregate':
                # Data aggregation
                transformed_data = self._aggregate_data(input_data, state.get('aggregation_type', 'sum'))
            else:
                transformed_data = input_data
            
            # Store output with the specified name AND in common fields for easy access
            state[output_name] = transformed_data
            state['output_data'] = transformed_data
            state['content'] = transformed_data  # Make it easily accessible for social media
            state['post_data'] = transformed_data  # Instagram-specific field
            state['operation'] = operation
            state['input_source'] = input_source
            state['output_name'] = output_name
            state['status'] = 'completed'
            state['timestamp'] = datetime.now().isoformat()
            
            print(f"Data node completed. Output stored in '{output_name}': {str(transformed_data)[:100]}...")
            print(f"Content also stored in 'content' and 'post_data' for easy access")
            
            return state
        except Exception as e:
            print(f"Error in data node: {e}")
            state['status'] = 'failed'
            state['error'] = str(e)
            state['timestamp'] = datetime.now().isoformat()
            return state
    
    def condition_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Conditional logic node"""
        try:
            condition = state.get('condition', '')
            input_value = state.get('input_value', '')
            
            # Evaluate condition (simple string-based evaluation for demo)
            result = self._evaluate_condition(condition, input_value)
            
            state['condition_result'] = result
            state['next_step'] = 'branch_a' if result else 'branch_b'
            state['status'] = 'completed'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
            return state
    
    def delay_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Delay/timing node"""
        try:
            delay_seconds = state.get('delay_seconds', 1)
            
            # In production, this would be handled by a proper scheduler
            # For demo, we'll just record the delay
            
            state['delay_seconds'] = delay_seconds
            state['scheduled_for'] = datetime.now().isoformat()
            state['status'] = 'scheduled'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
            return state
    
    def schedule_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Scheduling node"""
        try:
            schedule_type = state.get('schedule_type', 'daily')
            schedule_time = state.get('schedule_time', '09:00')
            
            schedule_data = {
                'type': schedule_type,
                'time': schedule_time,
                'created_at': datetime.now().isoformat()
            }
            
            state['schedule_data'] = schedule_data
            state['status'] = 'scheduled'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
            return state
    
    def blog_writer_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Blog content generation node"""
        try:
            topic = state.get('topic', '')
            style = state.get('style', 'professional')
            length = state.get('length', 'medium')
            
            template = ChatPromptTemplate.from_messages([
                ("system", f"You are a professional blog writer. Write in a {style} style."),
                ("human", "Write a {length} blog post about: {topic}")
            ])
            
            chain = template | self.llm
            response = chain.invoke({"topic": topic, "length": length})
            
            blog_data = {
                'topic': topic,
                'content': response.content,
                'style': style,
                'length': length,
                'generated_at': datetime.now().isoformat()
            }
            
            state['blog_data'] = blog_data
            state['status'] = 'completed'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
            return state
    
    def social_media_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Social media posting node"""
        try:
            platform = state.get('platform', 'instagram')
            content = state.get('content', '')
            access_token = state.get('access_token', '')
            post = state.get('post', '')
            image_url = state.get('image_url', '')
            image = state.get('image', '')
            
            print(f"Social media node - platform: {platform}, content: {content}, post: {post}, image_url: {image_url}")
            print(f"Available state keys: {list(state.keys())}")
            
            # Handle Instagram-specific posting
            if platform == 'instagram' or platform == 'instagram_post':
                # Get post content from various possible sources - prioritize data node output
                if not content:
                    # First, try to get content from data node output
                    for key in ['post_data', 'output_data', 'result', 'output', 'content', 'text']:
                        if key in state and state[key]:
                            content = state[key]
                            print(f"Found content in {key}: {str(content)[:100]}...")
                            break
                
                # If still no content, try the post reference
                if not content and post:
                    # Could be a reference to previous node output
                    if isinstance(post, str) and '.' in post:
                        # Handle "node2.post_data" format
                        parts = post.split('.')
                        if len(parts) == 2 and parts[1] in state:
                            content = state[parts[1]]
                            print(f"Found content from {parts[1]}: {str(content)[:100]}...")
                        else:
                            content = post
                            print(f"Using post reference as content: {content}")
                    else:
                        content = post
                        print(f"Using post as content: {content}")
                
                # Ensure we have an image URL if available in state
                if not image_url and image:
                    # Allow previous nodes to store image in various fields
                    if isinstance(image, dict) and 'image_url' in image:
                        image_url = image.get('image_url')
                    elif isinstance(image, str):
                        image_url = image
                
                # Handle structured content from AI Agent (JSON with caption, hashtags, etc.)
                if isinstance(content, dict):
                    # Extract caption and hashtags from structured data
                    caption = content.get('caption', '')
                    hashtags = content.get('hashtags', [])
                    
                    # Combine caption with hashtags
                    if hashtags:
                        hashtag_text = ' '.join([f"#{tag.replace('#', '')}" for tag in hashtags])
                        content = f"{caption}\n\n{hashtag_text}"
                    else:
                        content = caption
                    
                    print(f"Extracted structured content - Caption: {caption[:100]}..., Hashtags: {hashtags}")
                
                # Final fallback - check if we have any content at all
                if not content:
                    print("ERROR: No content found for Instagram post!")
                    state['status'] = 'failed'
                    state['error'] = 'No content available for Instagram post'
                    state['timestamp'] = datetime.now().isoformat()
                    return state
                
                # Check if we have a valid access token for real Instagram posting
                if access_token and access_token != 'test_token_12345':
                    try:
                        print("Attempting real Instagram posting...")
                        
                        # Initialize Instagram service
                        instagram_service = InstagramService(access_token)
                        
                        # Post content to Instagram
                        # Prefer image posting if image_url available; else fail back to text-only handler which now requires image_url
                        result = instagram_service.post_text_only(str(content), image_url=image_url)
                        
                        if result['status'] == 'success':
                            social_data = {
                                'platform': 'instagram',
                                'content': content,
                                'access_token': access_token[:10] + '...',
                                'posted_at': result['posted_at'],
                                'post_id': result['instagram_post_id'],
                                'creation_id': result['creation_id'],
                                'real_post': True,
                                'api_response': result['api_response']
                            }
                            
                            state['social_data'] = social_data
                            state['instagram_post'] = social_data
                            state['status'] = 'posted'
                            state['timestamp'] = datetime.now().isoformat()
                            
                            print(f"✅ Real Instagram post completed successfully!")
                            print(f"Content length: {len(str(content)) if content else 0}")
                            print(f"Real Post ID: {result['instagram_post_id']}")
                            print(f"Creation ID: {result['creation_id']}")
                            
                        else:
                            # Fallback to simulation if real posting fails
                            print(f"Real Instagram posting failed: {result.get('error', 'Unknown error')}")
                            print("Falling back to simulation mode...")
                            raise Exception(f"Instagram API error: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        print(f"Real Instagram posting failed: {e}")
                        print("Falling back to simulation mode...")
                        # Continue with simulation mode
                
                # Fallback to simulation mode (for testing or when no valid token)
                print("Using Instagram posting simulation mode...")
                social_data = {
                    'platform': 'instagram',
                    'content': content,
                    'access_token': access_token[:10] + '...' if access_token else 'demo_token',
                    'posted_at': datetime.now().isoformat(),
                    'post_id': f"ig_post_{datetime.now().timestamp()}",
                    'real_post': False,
                    'simulation_mode': True,
                    'image_url_used': image_url or 'none'
                }
                
                state['social_data'] = social_data
                state['instagram_post'] = social_data
                state['status'] = 'posted'
                state['timestamp'] = datetime.now().isoformat()
                
                print(f"Instagram post simulation completed successfully!")
                print(f"Content length: {len(str(content)) if content else 0}")
                print(f"Simulated Post ID: {social_data['post_id']}")
                
                return state
            
            # Handle other platforms
            else:
                social_data = {
                    'platform': platform,
                    'content': content,
                    'posted_at': datetime.now().isoformat()
                }
                
                state['social_data'] = social_data
                state['status'] = 'posted'
                state['timestamp'] = datetime.now().isoformat()
                
                return state
                
        except Exception as e:
            print(f"Error in social media node: {e}")
            state['status'] = 'failed'
            state['error'] = str(e)
            state['timestamp'] = datetime.now().isoformat()
            return state
    
    def image_generator_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Image generation node"""
        try:
            prompt = state.get('prompt', '')
            style = state.get('style', 'realistic')
            
            # For demo purposes, we'll simulate image generation
            # In production, integrate with DALL-E, Midjourney, or similar APIs
            
            image_url = f"https://picsum.photos/seed/{int(datetime.now().timestamp())}/1080/1080"
            image_data = {
                'prompt': prompt,
                'style': style,
                'image_url': image_url,
                'generated_at': datetime.now().isoformat()
            }
            
            # Store in multiple convenient locations for downstream nodes
            state['image_data'] = image_data
            state['image_url'] = image_url
            state['image'] = image_data
            state['status'] = 'completed'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
            return state
    
    def seo_optimizer_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """SEO optimization node"""
        try:
            content = state.get('content', '')
            target_keywords = state.get('target_keywords', [])
            
            template = ChatPromptTemplate.from_messages([
                ("system", "You are an SEO expert. Optimize the given content for search engines."),
                ("human", "Optimize this content for SEO with target keywords: {keywords}\n\nContent: {content}")
            ])
            
            chain = template | self.llm
            response = chain.invoke({
                "keywords": ", ".join(target_keywords),
                "content": content
            })
            
            seo_data = {
                'original_content': content,
                'optimized_content': response.content,
                'target_keywords': target_keywords,
                'optimized_at': datetime.now().isoformat()
            }
            
            state['seo_data'] = seo_data
            state['status'] = 'completed'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
            return state
    
    def text_overlay_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create an image with overlaid text and return a data URL as image_url.
        - If image_url is provided in state, use it as background.
        - Otherwise, use a generated solid/gradient background.
        - Reads text from overlay_text, or falls back to content/result.
        """
        try:
            # Get text to overlay - use structured_data from AI Agent
            overlay_text = state.get('overlay_text') or state.get('structured_data')
            if overlay_text:
                print(f"Text overlay using: {type(overlay_text)}")
            
            # Handle structured data from AI Agent
            if isinstance(overlay_text, dict):
                print(f"Processing structured data: {list(overlay_text.keys())}")
                print(f"Raw structured data: {overlay_text}")
                # Extract structured content for image overlay
                headline = overlay_text.get('headline', '')
                subhead = overlay_text.get('subhead', '')
                bullets = overlay_text.get('bullets', [])
                
                # Format bullets properly
                bullet_text = ""
                if bullets:
                    bullet_text = "\n".join([f"• {str(b)}" for b in bullets])
                
                # Combine all parts
                parts = []
                if headline:
                    parts.append(headline)
                if subhead:
                    parts.append(subhead)
                if bullet_text:
                    parts.append(bullet_text)
                
                overlay_text = "\n\n".join(parts)
                print(f"Formatted overlay text: {overlay_text[:100]}...")
            else:
                print(f"Overlay text is not a dict, it's: {type(overlay_text)}")
                print(f"Overlay text content: {str(overlay_text)[:200]}...")
            
            # Convert to string if needed
            overlay_text = str(overlay_text) if overlay_text is not None else ""

            if not overlay_text.strip():
                overlay_text = "Generated Post"

            # TODO: FUTURE IMPROVEMENT - Make dimensions configurable per platform
            # Currently hardcoded for Instagram (1080x1080) but should be dynamic based on:
            # - Platform requirements (Instagram, LinkedIn, Twitter, etc.)
            # - Node configuration parameters
            # - User preferences
            # For now, using Instagram-optimized dimensions as default
            width = int(state.get('image_width', 1080))  # Instagram recommended: 1080x1080
            height = int(state.get('image_height', 1080))
            background_url = state.get('image_url') or state.get('background_image_url')

            # Prepare base image
            base_image = None
            try:
                if background_url and isinstance(background_url, str) and background_url.startswith('http'):
                    resp = requests.get(background_url, timeout=10)
                    resp.raise_for_status()
                    base_image = Image.open(io.BytesIO(resp.content)).convert('RGB')
            except Exception as e:
                print(f"Warning: Failed to fetch background image: {e}")
                base_image = None

            if base_image is None:
                # Try to get a dynamic background image based on content
                base_image = self._get_dynamic_background_image(overlay_text, width, height)
                
                # Fallback to gradient if no dynamic image found
                if base_image is None:
                    print("Using fallback gradient background")
                    # Create a visually appealing gradient background for Instagram
                    # Use modern Instagram-style colors
                    base_image = Image.new('RGB', (width, height), (255, 255, 255))
                    
                    # Create a beautiful gradient background
                    for y in range(height):
                        for x in range(width):
                            # Create a modern gradient from top to bottom
                            progress = y / height
                            
                            # Instagram-style gradient: light blue to purple to pink
                            if progress < 0.33:
                                # Top: Light blue to purple
                                r = int(135 + (147 - 135) * (progress * 3))
                                g = int(206 + (112 - 206) * (progress * 3))
                                b = int(250 + (219 - 250) * (progress * 3))
                            elif progress < 0.66:
                                # Middle: Purple to pink
                                r = int(147 + (255 - 147) * ((progress - 0.33) * 3))
                                g = int(112 + (182 - 112) * ((progress - 0.33) * 3))
                                b = int(219 + (193 - 219) * ((progress - 0.33) * 3))
                            else:
                                # Bottom: Pink to light pink
                                r = int(255 + (255 - 255) * ((progress - 0.66) * 3))
                                g = int(182 + (192 - 182) * ((progress - 0.66) * 3))
                                b = int(193 + (203 - 193) * ((progress - 0.66) * 3))
                            
                            base_image.putpixel((x, y), (r, g, b))

            # Normalize to RGBA for overlays
            image_rgba = base_image.convert('RGBA')

            # Draw modern Instagram-style text panel
            overlay = Image.new('RGBA', image_rgba.size, (255, 255, 255, 0))
            draw_overlay = ImageDraw.Draw(overlay)
            panel_margin = int(min(width, height) * 0.08)
            panel_top = int(height * 0.2)
            panel_bottom = int(height * 0.8)
            
            # Create a modern rounded rectangle effect with gradient
            # Main panel with subtle transparency
            draw_overlay.rectangle(
                [(panel_margin, panel_top), (width - panel_margin, panel_bottom)],
                fill=(255, 255, 255, 200),  # White with transparency
                outline=(255, 255, 255, 100),
                width=3
            )
            image_rgba = Image.alpha_composite(image_rgba, overlay)

            # Draw text with Instagram-optimized fonts and sizing
            draw = ImageDraw.Draw(image_rgba)
            
            # TODO: FUTURE IMPROVEMENT - Make font sizing configurable per platform
            # Currently optimized for Instagram (1080x1080) but should be dynamic based on:
            # - Platform requirements and best practices
            # - Image dimensions and aspect ratios
            # - Content type and readability requirements
            # For now, using Instagram-optimized font sizes as default
            # Headline: 48-60px, Subhead: 32-40px, Body: 24-28px
            headline_size = int(width * 0.055)  # ~60px for 1080px width
            subhead_size = int(width * 0.037)   # ~40px for 1080px width
            body_size = int(width * 0.025)      # ~27px for 1080px width
            
            try:
                # Try to load better fonts if available
                font_large = ImageFont.truetype("arial.ttf", headline_size)
                font_medium = ImageFont.truetype("arial.ttf", subhead_size)
                font_small = ImageFont.truetype("arial.ttf", body_size)
            except Exception:
                # Fallback to default fonts with calculated sizes
                try:
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()
                    font_small = ImageFont.load_default()
                except Exception:
                    # Ultimate fallback
                    font_large = ImageFont.load_default()
                    font_medium = ImageFont.load_default()
                    font_small = ImageFont.load_default()

            # TODO: FUTURE IMPROVEMENT - Make text wrapping configurable per platform
            # Currently optimized for Instagram but should be dynamic based on:
            # - Platform-specific content guidelines
            # - Font sizes and readability requirements
            # - Content type (headlines, body text, etc.)
            # For now, using Instagram-optimized line lengths
            import textwrap
            max_text_width = width - (panel_margin * 2) - 60  # More padding for better readability
            
            # Calculate characters per line based on font size
            # Approximate: 1 character = font_size * 0.6 pixels
            char_px_large = headline_size * 0.6
            char_px_medium = subhead_size * 0.6
            char_px_small = body_size * 0.6
            
            max_chars_headline = max(15, int(max_text_width / char_px_large))
            max_chars_subhead = max(20, int(max_text_width / char_px_medium))
            max_chars_body = max(25, int(max_text_width / char_px_small))

            # TODO: FUTURE IMPROVEMENT - Make text formatting configurable per platform
            # Currently optimized for Instagram but should be dynamic based on:
            # - Platform-specific content structure requirements
            # - Content type (headlines, subheads, bullets, etc.)
            # - User preferences and branding guidelines
            # For now, using Instagram-optimized formatting
            lines = []
            line_types = []  # Track if each line is headline, subhead, or body
            
            paragraphs = str(overlay_text).split('\n')
            for i, paragraph in enumerate(paragraphs):
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                # Determine text type based on position and content
                if i == 0:  # First paragraph = headline
                    wrapped = textwrap.wrap(paragraph, width=max_chars_headline)
                    lines.extend(wrapped)
                    line_types.extend(['headline'] * len(wrapped))
                elif i == 1 and len(paragraphs) > 2:  # Second paragraph = subhead (if we have bullets)
                    wrapped = textwrap.wrap(paragraph, width=max_chars_subhead)
                    lines.extend(wrapped)
                    line_types.extend(['subhead'] * len(wrapped))
                else:  # Bullets and other content = body
                    wrapped = textwrap.wrap(paragraph, width=max_chars_body)
                    lines.extend(wrapped)
                    line_types.extend(['body'] * len(wrapped))

            # TODO: FUTURE IMPROVEMENT - Make line heights and positioning configurable per platform
            # Currently optimized for Instagram but should be dynamic based on:
            # - Platform-specific design guidelines
            # - Font sizes and readability requirements
            # - Content hierarchy and visual balance
            # For now, using Instagram-optimized line heights and positioning
            line_heights = {
                'headline': int(headline_size * 1.3),  # ~78px for 60px font
                'subhead': int(subhead_size * 1.2),    # ~48px for 40px font
                'body': int(body_size * 1.4)           # ~38px for 27px font
            }
            
            # Calculate total text block height
            total_height = sum(line_heights.get(line_type, line_heights['body']) for line_type in line_types)
            
            # Center text vertically in panel
            y = panel_top + ((panel_bottom - panel_top - total_height) // 2)
            x = panel_margin + 30  # More left padding for better Instagram aesthetics

            # TODO: FUTURE IMPROVEMENT - Make text styling configurable per platform
            # Currently optimized for Instagram but should be dynamic based on:
            # - Platform-specific color schemes and branding
            # - Content type and hierarchy requirements
            # - Accessibility and readability standards
            # For now, using Instagram-optimized styling
            for idx, (line, line_type) in enumerate(zip(lines, line_types)):
                if line_type == 'headline':
                    font = font_large
                    text_color = (30, 30, 30, 255)  # Darker for headlines
                    line_height = line_heights['headline']
                elif line_type == 'subhead':
                    font = font_medium
                    text_color = (50, 50, 50, 255)  # Medium for subheads
                    line_height = line_heights['subhead']
                else:  # body
                    font = font_small
                    text_color = (70, 70, 70, 255)  # Lighter for body text
                    line_height = line_heights['body']
                
                draw.text((x, y), line, fill=text_color, font=font)
                y += line_height

            # Export to data URL
            output_image = image_rgba.convert('RGB')
            buffer = io.BytesIO()
            output_image.save(buffer, format='JPEG', quality=90)
            encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
            data_url = f"data:image/jpeg;base64,{encoded}"

            state['image_url'] = data_url
            state['image_data_url'] = data_url
            state['overlay_text_used'] = overlay_text
            state['status'] = 'completed'
            state['timestamp'] = datetime.now().isoformat()

            return state
        except Exception as e:
            print(f"Error in text overlay node: {e}")
            state['status'] = 'failed'
            state['error'] = str(e)
            state['timestamp'] = datetime.now().isoformat()
            return state

    def image_upload_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Upload an image (data URL or URL) to Cloudinary and return a public URL.
        Requires env: CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET.
        Inputs: image_data_url or image_url; if both present and image_url is a data URL, prefer image_data_url.
        Outputs: image_url (secure URL)
        """
        try:
            cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
            api_key = os.getenv('CLOUDINARY_API_KEY')
            api_secret = os.getenv('CLOUDINARY_API_SECRET')
            if not (cloud_name and api_key and api_secret):
                raise ValueError('Cloudinary credentials not configured')

            # Determine payload source
            data_url = state.get('image_data_url')
            image_url = state.get('image_url')

            file_param = None
            if data_url and isinstance(data_url, str) and data_url.startswith('data:image/'):
                file_param = data_url
            elif image_url and isinstance(image_url, str):
                file_param = image_url
            else:
                raise ValueError('No image data provided for upload')

            # Cloudinary signed upload
            upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
            timestamp = str(int(time.time()))

            # Optional: deterministic public_id by hashing content (for dedupe)
            public_id = None
            try:
                if file_param.startswith('data:image/'):
                    content_base64 = file_param.split(',', 1)[1]
                    content_bytes = base64.b64decode(content_base64)
                    public_id = hashlib.sha1(content_bytes).hexdigest()[:16]
            except Exception:
                public_id = None

            # Signature
            to_sign = {'timestamp': timestamp}
            if public_id:
                to_sign['public_id'] = public_id
            # Cloudinary signature: sha1 of querystring of sorted params + api_secret
            sorted_items = sorted(to_sign.items())
            query = "&".join([f"{k}={v}" for k, v in sorted_items])
            signature = hashlib.sha1((query + api_secret).encode('utf-8')).hexdigest()

            data = {
                'file': file_param,
                'api_key': api_key,
                'timestamp': timestamp,
                'signature': signature
            }
            if public_id:
                data['public_id'] = public_id

            resp = requests.post(upload_url, data=data)
            resp.raise_for_status()
            result = resp.json()

            secure_url = result.get('secure_url') or result.get('url')
            if not secure_url:
                raise ValueError('Cloudinary upload succeeded but no secure_url returned')

            state['image_url'] = secure_url
            state['cloudinary_result'] = {'public_id': result.get('public_id'), 'version': result.get('version')}
            state['status'] = 'uploaded'
            state['timestamp'] = datetime.now().isoformat()
            return state
        except Exception as e:
            print(f"Error in image upload node: {e}")
            state['status'] = 'failed'
            state['error'] = str(e)
            state['timestamp'] = datetime.now().isoformat()
            return state

    # Helper methods
    def _transform_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Simple data transformation"""
        transformed = {}
        for key, value in data.items():
            if isinstance(value, str):
                transformed[key] = value.upper()
            elif isinstance(value, (int, float)):
                transformed[key] = value * 2
            else:
                transformed[key] = value
        return transformed
    
    def _filter_data(self, data: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Simple data filtering"""
        filtered = {}
        for key, value in data.items():
            if key in criteria:
                if isinstance(value, str) and criteria[key].lower() in value.lower():
                    filtered[key] = value
                elif isinstance(value, (int, float)) and value > criteria.get(f"{key}_min", 0):
                    filtered[key] = value
            else:
                filtered[key] = value
        return filtered
    
    def _aggregate_data(self, data: Dict[str, Any], agg_type: str) -> Dict[str, Any]:
        """Simple data aggregation"""
        numeric_values = [v for v in data.values() if isinstance(v, (int, float))]
        if not numeric_values:
            return data
        
        if agg_type == 'sum':
            result = sum(numeric_values)
        elif agg_type == 'avg':
            result = sum(numeric_values) / len(numeric_values)
        elif agg_type == 'max':
            result = max(numeric_values)
        elif agg_type == 'min':
            result = min(numeric_values)
        else:
            result = sum(numeric_values)
        
        return {**data, f'{agg_type}_result': result}
    
    def _evaluate_condition(self, condition: str, value: Any) -> bool:
        """Simple condition evaluation"""
        if 'contains' in condition.lower():
            return str(value).lower() in condition.lower()
        elif 'greater' in condition.lower() or '>' in condition:
            try:
                return float(value) > 0
            except:
                return False
        elif 'less' in condition.lower() or '<' in condition:
            try:
                return float(value) < 0
            except:
                return False
        else:
            return bool(value)
    
    def _get_dynamic_background_image(self, content: str, width: int, height: int) -> Optional[Image.Image]:
        """
        Get a dynamic background image based on content using free image APIs.
        Tries multiple sources: Unsplash, Pexels, then falls back to gradient.
        """
        try:
            # Extract keywords from content for image search
            keywords = self._extract_image_keywords(content)
            if not keywords:
                print("No keywords extracted for image search")
                return None
            
            print(f"Searching for background image with keywords: {keywords}")
            
            # Try Unsplash API first (free, high quality)
            image_url = self._search_unsplash_image(keywords)
            if image_url:
                print(f"Found Unsplash image: {image_url}")
                return self._download_and_process_image(image_url, width, height)
            
            # Try Pexels API as fallback (also free)
            image_url = self._search_pexels_image(keywords)
            if image_url:
                print(f"Found Pexels image: {image_url}")
                return self._download_and_process_image(image_url, width, height)
            
            # Try Pixabay API as another fallback
            image_url = self._search_pixabay_image(keywords)
            if image_url:
                print(f"Found Pixabay image: {image_url}")
                return self._download_and_process_image(image_url, width, height)
            
            # Try Lorem Picsum as final fallback (always works)
            image_url = self._search_lorem_picsum_image(keywords)
            if image_url:
                print(f"Found Lorem Picsum image: {image_url}")
                return self._download_and_process_image(image_url, width, height)
            
            print("No suitable background image found from APIs")
            return None
            
        except Exception as e:
            print(f"Error getting dynamic background image: {e}")
            return None
    
    def _extract_image_keywords(self, content: str) -> List[str]:
        """Extract relevant keywords from content for image search"""
        try:
            # Convert content to string if it's not already
            content_str = str(content).lower()
            
            # Define keyword categories and their associated search terms
            keyword_mapping = {
                'technology': ['ai', 'artificial intelligence', 'machine learning', 'tech', 'technology', 'digital', 'innovation', 'future', 'automation', 'data', 'analytics', 'cloud', 'software', 'app', 'mobile', 'web', 'internet', 'cyber', 'smart', 'automated', 'algorithm', 'neural', 'deep learning', 'robotics', 'automation'],
                'business': ['business', 'entrepreneur', 'startup', 'corporate', 'office', 'meeting', 'strategy', 'growth', 'success', 'leadership', 'management', 'team', 'collaboration', 'productivity', 'efficiency', 'profit', 'revenue', 'marketing', 'sales', 'customer', 'service'],
                'creative': ['creative', 'design', 'art', 'visual', 'colorful', 'abstract', 'modern', 'minimal', 'aesthetic', 'beautiful', 'stunning', 'inspiration', 'creative', 'artistic', 'designer', 'brand', 'logo', 'typography', 'illustration', 'graphic'],
                'nature': ['nature', 'outdoor', 'landscape', 'mountain', 'ocean', 'forest', 'tree', 'flower', 'green', 'blue', 'sky', 'sunset', 'sunrise', 'natural', 'organic', 'environment', 'sustainability', 'eco', 'earth', 'planet'],
                'lifestyle': ['lifestyle', 'health', 'fitness', 'wellness', 'mindfulness', 'meditation', 'yoga', 'exercise', 'nutrition', 'balance', 'happiness', 'joy', 'peace', 'relaxation', 'stress', 'work-life', 'personal', 'development'],
                'education': ['education', 'learning', 'study', 'knowledge', 'wisdom', 'book', 'library', 'school', 'university', 'course', 'training', 'skill', 'development', 'growth', 'improvement', 'expertise', 'mastery', 'certification'],
                'finance': ['finance', 'money', 'investment', 'wealth', 'financial', 'economy', 'market', 'trading', 'stock', 'crypto', 'bitcoin', 'banking', 'savings', 'budget', 'planning', 'retirement', 'insurance'],
                'travel': ['travel', 'adventure', 'exploration', 'journey', 'destination', 'vacation', 'holiday', 'trip', 'world', 'global', 'culture', 'experience', 'discovery', 'wanderlust', 'backpack', 'passport'],
                'food': ['food', 'cooking', 'recipe', 'cuisine', 'restaurant', 'chef', 'kitchen', 'delicious', 'tasty', 'nutrition', 'healthy', 'organic', 'fresh', 'ingredients', 'meal', 'dining'],
                'fashion': ['fashion', 'style', 'clothing', 'outfit', 'trend', 'beauty', 'accessories', 'shoes', 'jewelry', 'makeup', 'model', 'runway', 'designer', 'brand', 'luxury', 'elegant']
            }
            
            # Find matching categories
            matched_categories = []
            for category, keywords in keyword_mapping.items():
                for keyword in keywords:
                    if keyword in content_str:
                        matched_categories.append(category)
                        break  # Found one keyword from this category, move to next
            
            # If no specific categories found, use general terms
            if not matched_categories:
                # Extract common words and use them as search terms
                words = content_str.split()
                # Filter out common stop words
                stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'mine', 'yours', 'hers', 'ours', 'theirs'}
                filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
                if filtered_words:
                    return filtered_words[:3]  # Return top 3 words
            
            # Return search terms for matched categories
            search_terms = []
            for category in matched_categories[:2]:  # Limit to 2 categories
                if category == 'technology':
                    search_terms.extend(['technology', 'digital', 'innovation'])
                elif category == 'business':
                    search_terms.extend(['business', 'corporate', 'professional'])
                elif category == 'creative':
                    search_terms.extend(['creative', 'design', 'art'])
                elif category == 'nature':
                    search_terms.extend(['nature', 'landscape', 'outdoor'])
                elif category == 'lifestyle':
                    search_terms.extend(['lifestyle', 'wellness', 'health'])
                elif category == 'education':
                    search_terms.extend(['education', 'learning', 'knowledge'])
                elif category == 'finance':
                    search_terms.extend(['finance', 'business', 'professional'])
                elif category == 'travel':
                    search_terms.extend(['travel', 'adventure', 'landscape'])
                elif category == 'food':
                    search_terms.extend(['food', 'cooking', 'cuisine'])
                elif category == 'fashion':
                    search_terms.extend(['fashion', 'style', 'design'])
            
            return search_terms[:3] if search_terms else ['abstract', 'modern', 'design']
            
        except Exception as e:
            print(f"Error extracting keywords: {e}")
            return ['abstract', 'modern', 'design']
    
    def _search_unsplash_image(self, keywords: List[str]) -> Optional[str]:
        """Search for an image on Unsplash using keywords"""
        try:
            # Use Unsplash Source API (free, no API key required)
            search_query = '+'.join(keywords[:2])  # Use first 2 keywords
            url = f"https://source.unsplash.com/1080x1080/?{search_query}"
            
            # Test if the URL is accessible and returns an image
            response = requests.get(url, timeout=10, stream=True)
            if response.status_code == 200:
                # Check if it's actually an image
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    print(f"Found Unsplash image: {url}")
                    return url
                else:
                    print(f"Unsplash returned non-image content: {content_type}")
            return None
            
        except Exception as e:
            print(f"Error searching Unsplash: {e}")
            return None
    
    def _search_pexels_image(self, keywords: List[str]) -> Optional[str]:
        """Search for an image on Pexels using keywords"""
        try:
            # Use Pexels Source API (free, no API key required)
            search_query = '+'.join(keywords[:2])  # Use first 2 keywords
            url = f"https://images.pexels.com/photos/{search_query}/1080/1080"
            
            # Test if the URL is accessible and returns an image
            response = requests.get(url, timeout=10, stream=True)
            if response.status_code == 200:
                # Check if it's actually an image
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    print(f"Found Pexels image: {url}")
                    return url
                else:
                    print(f"Pexels returned non-image content: {content_type}")
            return None
            
        except Exception as e:
            print(f"Error searching Pexels: {e}")
            return None
    
    def _search_pixabay_image(self, keywords: List[str]) -> Optional[str]:
        """Search for an image on Pixabay using keywords"""
        try:
            # Use Pixabay Source API (free, no API key required)
            search_query = '+'.join(keywords[:2])  # Use first 2 keywords
            url = f"https://pixabay.com/get/{search_query}/1080/1080"
            
            # Test if the URL is accessible and returns an image
            response = requests.get(url, timeout=10, stream=True)
            if response.status_code == 200:
                # Check if it's actually an image
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    print(f"Found Pixabay image: {url}")
                    return url
                else:
                    print(f"Pixabay returned non-image content: {content_type}")
            return None
            
        except Exception as e:
            print(f"Error searching Pixabay: {e}")
            return None
    
    def _search_lorem_picsum_image(self, keywords: List[str]) -> Optional[str]:
        """Search for an image on Lorem Picsum using keywords"""
        try:
            # Lorem Picsum provides random images with specific IDs
            # We'll use the first keyword to generate a consistent image ID
            if keywords:
                # Create a hash from the first keyword to get a consistent image ID
                import hashlib
                keyword_hash = hashlib.md5(keywords[0].encode()).hexdigest()
                image_id = int(keyword_hash[:8], 16) % 1000  # Get a number between 0-999
                
                url = f"https://picsum.photos/id/{image_id}/1080/1080"
                print(f"Generated Lorem Picsum URL with ID {image_id} from keyword '{keywords[0]}'")
                return url
            else:
                # Fallback to random image
                url = f"https://picsum.photos/1080/1080"
                print("Using random Lorem Picsum image")
                return url
            
        except Exception as e:
            print(f"Error searching Lorem Picsum: {e}")
            return None
    
    def _download_and_process_image(self, image_url: str, width: int, height: int) -> Optional[Image.Image]:
        """Download and process image from URL"""
        try:
            print(f"Downloading image from: {image_url}")
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Open and process image
            image = Image.open(io.BytesIO(response.content)).convert('RGB')
            
            # Resize to target dimensions while maintaining aspect ratio
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
            
            # Create a new image with target dimensions
            new_image = Image.new('RGB', (width, height), (255, 255, 255))
            
            # Center the image
            x = (width - image.width) // 2
            y = (height - image.height) // 2
            new_image.paste(image, (x, y))
            
            print(f"Successfully processed background image: {image.size} -> {new_image.size}")
            return new_image
            
        except Exception as e:
            print(f"Error downloading/processing image: {e}")
            return None 