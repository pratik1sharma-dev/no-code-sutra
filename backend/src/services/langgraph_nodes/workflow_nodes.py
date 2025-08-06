from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
import os
from datetime import datetime
import requests
from bs4 import BeautifulSoup

class LangGraphWorkflowNodes:
    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    
    def ai_agent_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """AI Agent node for intelligent processing"""
        try:
            prompt = state.get('prompt', '')
            context = state.get('context', '')
            
            template = ChatPromptTemplate.from_messages([
                ("system", "You are an intelligent AI agent. Process the given input and provide a helpful response."),
                ("human", "Context: {context}\n\nTask: {prompt}")
            ])
            
            chain = template | self.llm
            response = chain.invoke({"context": context, "prompt": prompt})
            
            state['result'] = response.content
            state['status'] = 'completed'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
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
            input_data = state.get('input_data', {})
            operation = state.get('operation', 'transform')
            
            if operation == 'transform':
                # Simple data transformation
                transformed_data = self._transform_data(input_data)
            elif operation == 'filter':
                # Data filtering
                transformed_data = self._filter_data(input_data, state.get('filter_criteria', {}))
            elif operation == 'aggregate':
                # Data aggregation
                transformed_data = self._aggregate_data(input_data, state.get('aggregation_type', 'sum'))
            else:
                transformed_data = input_data
            
            state['output_data'] = transformed_data
            state['status'] = 'completed'
            state['timestamp'] = datetime.now().isoformat()
            
            return state
        except Exception as e:
            state['status'] = 'failed'
            state['error'] = str(e)
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
            platform = state.get('platform', 'twitter')
            content = state.get('content', '')
            
            # For demo purposes, we'll simulate social media posting
            # In production, integrate with actual social media APIs
            
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
            state['status'] = 'failed'
            state['error'] = str(e)
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