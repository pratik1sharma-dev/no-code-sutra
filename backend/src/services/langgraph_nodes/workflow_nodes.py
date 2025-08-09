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

class LangGraphWorkflowNodes:
    def __init__(self):
        # Use Bedrock instead of OpenAI
        model_id = os.getenv("BEDROCK_MODEL_ID", "meta.llama3-1-8b-instruct-v1:0")
        region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        
        try:
            self.llm = ChatBedrock(
                model_id=model_id,
                region_name=region,
                model_kwargs={"temperature": 0.1}
            )
        except Exception as e:
            # Fallback to a mock LLM if Bedrock is not available
            print(f"Warning: Could not initialize Bedrock: {e}")
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
            
            # Extract task and topic from state
            task = state.get('task', 'research')
            topic = state.get('topic', 'general research')
            prompt = state.get('prompt', '')
            context = state.get('context', '')
            
            # Build appropriate prompt based on task
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
            
            template = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", user_prompt)
            ])
            
            chain = template | self.llm
            response = chain.invoke({"context": context, "prompt": prompt, "topic": topic})
            
            # Store the AI response in multiple formats for flexibility
            state['result'] = response.content
            state['output'] = response.content
            state['content'] = response.content
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
            
            print(f"Social media node - platform: {platform}, content: {content}, post: {post}")
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
                        result = instagram_service.post_text_only(str(content))
                        
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
                    'simulation_mode': True
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
            
            image_data = {
                'prompt': prompt,
                'style': style,
                'image_url': f"https://example.com/generated-image-{datetime.now().timestamp()}.jpg",
                'generated_at': datetime.now().isoformat()
            }
            
            state['image_data'] = image_data
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