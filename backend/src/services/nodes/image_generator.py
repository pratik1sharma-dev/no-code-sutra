from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
import re
import os
import json
import random


class SmartImageGenerator:
    """Smart image generator supporting multiple modes: search, curated, AI-generated"""
    
    def __init__(self):
        # API keys for image search
        self.google_api_key = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
        self.google_search_engine_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
        self.unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.pexels_api_key = os.getenv('PEXELS_API_KEY')
        self.pixabay_api_key = os.getenv('PIXABAY_API_KEY')
        
        # AWS Bedrock image generation
        self.aws_region = os.getenv('AWS_DEFAULT_REGION', 'us-west-2')  # Titan Image Generator is available in us-west-2
        self.aws_token = os.getenv('AWS_BEARER_TOKEN_BEDROCK')
        
        # Initialize LLM client for mode detection and query enhancement
        from ..llm.bedrock_client import BedrockClient
        try:
            self.llm_client = BedrockClient() if os.getenv("AWS_BEARER_TOKEN_BEDROCK") else None
        except:
            self.llm_client = None
        
    
    def detect_image_mode(self, prompt: str, content: Dict[str, Any]) -> str:
        """Detect the best image generation mode based on prompt and content"""
        if not self.llm_client:
            return "search"  # Default fallback
        
        try:
            analysis_prompt = f"""Analyze this Instagram post request and determine the best image strategy:

Prompt: "{prompt}"
Content: {json.dumps(content, indent=2)}

Choose the best mode:
- "search": For general content needing stock photos/backgrounds
- "curated": For brand-consistent, corporate content  
- "ai_generate": For unique, creative, custom concepts that need original imagery
- "hybrid": For high-quality posts needing multiple options

Respond with ONLY the mode name: search, curated, ai_generate, or hybrid"""

            response = self.llm_client.generate(analysis_prompt)
            mode = response.strip().lower()
            
            if mode in ["search", "curated", "ai_generate", "hybrid"]:
                print(f"🤖 AI selected mode: {mode}")
                return mode
            else:
                print(f"⚠️ Invalid mode '{mode}', defaulting to search")
                return "search"
                
        except Exception as e:
            print(f"❌ Mode detection failed: {e}")
            return "search"
    
    def generate_ai_image(self, prompt: str, content: Dict[str, Any]) -> Optional[str]:
        """Generate AI image using AWS Bedrock Titan Image Generator"""
        if not self.aws_token:
            print("⚠️ AWS Bedrock token not configured for AI image generation")
            return None
        
        try:
            # Create optimized prompt for Titan Image Generator
            if self.llm_client:
                titan_prompt = self.create_titan_prompt(prompt, content)
            else:
                titan_prompt = f"Professional Instagram post image: {prompt}"
            
            print(f"🎨 Generating AI image with AWS Titan: {titan_prompt}")
            
            # Call AWS Bedrock Titan Image Generator (using v2 model)
            url = f"https://bedrock-runtime.{self.aws_region}.amazonaws.com/model/amazon.titan-image-generator-v2:0/invoke"
            
            # Validate prompt length (Titan has limits)
            if len(titan_prompt) > 512:
                titan_prompt = titan_prompt[:509] + "..."
                print(f"⚠️ Prompt truncated to 512 characters for Titan compatibility")
            
            payload = {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": titan_prompt,
                    "negativeText": "blurry, low quality, distorted, watermark, text overlay"
                },
                "imageGenerationConfig": {
                    "numberOfImages": 1,
                    "height": 1024,
                    "width": 1024,
                    "cfgScale": 8.0,
                    "seed": random.randint(0, 2147483647)
                }
            }
            
            # Validate payload structure
            required_fields = ["taskType", "textToImageParams", "imageGenerationConfig"]
            for field in required_fields:
                if field not in payload:
                    raise ValueError(f"Missing required field: {field}")
            
            if "text" not in payload["textToImageParams"]:
                raise ValueError("Missing required field: textToImageParams.text")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.aws_token}"
            }
            
            # Enhanced logging for debugging
            print(f"🔍 BEDROCK DEBUG - URL: {url}")
            print(f"🔍 BEDROCK DEBUG - Region: {self.aws_region}")
            print(f"🔍 BEDROCK DEBUG - Token length: {len(self.aws_token) if self.aws_token else 0}")
            print(f"🔍 BEDROCK DEBUG - Token prefix: {self.aws_token[:10] if self.aws_token else 'None'}...")
            print(f"🔍 BEDROCK DEBUG - Payload: {json.dumps(payload, indent=2)}")
            print(f"🔍 BEDROCK DEBUG - Headers: {json.dumps({k: v[:20] + '...' if k == 'Authorization' and len(v) > 20 else v for k, v in headers.items()}, indent=2)}")
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            # Log response details
            print(f"🔍 BEDROCK DEBUG - Response status: {response.status_code}")
            print(f"🔍 BEDROCK DEBUG - Response headers: {dict(response.headers)}")
            
            if response.status_code != 200:
                print(f"🔍 BEDROCK DEBUG - Error response body: {response.text}")
                response.raise_for_status()
            
            result = response.json()
            print(f"🔍 BEDROCK DEBUG - Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            
            # Extract base64 image and convert to URL
            if 'images' in result and len(result['images']) > 0:
                base64_image = result['images'][0]
                # For now, return a placeholder URL - in production, upload to S3/Cloudinary
                image_url = f"data:image/png;base64,{base64_image}"
                print(f"✅ AWS Titan image generated successfully")
                return image_url
            else:
                print(f"❌ No images returned from AWS Titan")
                print(f"🔍 BEDROCK DEBUG - Full response: {json.dumps(result, indent=2)}")
                return None
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ AWS Titan HTTP error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"🔍 BEDROCK DEBUG - HTTP Error response: {e.response.text}")
                print(f"🔍 BEDROCK DEBUG - HTTP Error status: {e.response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ AWS Titan request error: {e}")
        except json.JSONDecodeError as e:
            print(f"❌ AWS Titan JSON decode error: {e}")
        except Exception as e:
            print(f"❌ AWS Titan image generation failed: {e}")
            import traceback
            print(f"🔍 BEDROCK DEBUG - Full traceback: {traceback.format_exc()}")
        return None
    
    def create_titan_prompt(self, user_prompt: str, content: Dict[str, Any]) -> str:
        """Create optimized AWS Titan Image Generator prompt"""
        try:
            content_text = json.dumps(content, indent=2)
            prompt_optimization = f"""Create an AWS Titan Image Generator prompt for a professional Instagram post image.

User Request: "{user_prompt}"
Content: {content_text}

Requirements:
- Professional, high-quality, Instagram-ready
- Square aspect ratio (1:1)
- Modern, clean aesthetic
- Suitable for text overlay
- Brand-safe and appropriate
- No text or watermarks in the image

Generate a detailed Titan prompt (max 512 characters):"""

            response = self.llm_client.generate(prompt_optimization)
            optimized_prompt = response.strip()
            
            # Ensure it's not too long for Titan
            if len(optimized_prompt) > 512:
                optimized_prompt = optimized_prompt[:509] + "..."
            
            return optimized_prompt
            
        except Exception as e:
            print(f"❌ Titan prompt optimization failed: {e}")
            return f"Professional Instagram post background image: {user_prompt}"
    
    def get_curated_images(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get curated brand images from library"""
        # Enhanced curated library with more categories and better quality scores
        curated_library = {
            'business': [
                {
                    'url': 'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=1080&h=1080&fit=crop',
                    'quality_score': 85,
                    'tags': ['business', 'professional', 'office', 'corporate']
                },
                {
                    'url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1080&h=1080&fit=crop',
                    'quality_score': 90,
                    'tags': ['business', 'meeting', 'professional', 'teamwork']
                }
            ],
            'technology': [
                {
                    'url': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1080&h=1080&fit=crop',
                    'quality_score': 88,
                    'tags': ['technology', 'digital', 'innovation', 'modern']
                },
                {
                    'url': 'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1080&h=1080&fit=crop',
                    'quality_score': 92,
                    'tags': ['ai', 'artificial intelligence', 'technology', 'future']
                }
            ],
            'lifestyle': [
                {
                    'url': 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1080&h=1080&fit=crop',
                    'quality_score': 87,
                    'tags': ['lifestyle', 'modern', 'minimal', 'clean']
                }
            ]
        }
        
        # Find best matching category based on content
        keywords = self.extract_keywords(content)
        best_category = 'business'  # default
        
        for category, images in curated_library.items():
            for image in images:
                if any(keyword in image['tags'] for keyword in keywords):
                    best_category = category
                    break
        
        return curated_library.get(best_category, curated_library['business'])
    
    def extract_keywords(self, content: Dict[str, Any]) -> List[str]:
        """Extract relevant keywords from content for image search"""
        # Check if custom keywords are provided (for slide-specific images)
        if content.get('_custom_keywords'):
            print(f"🔍 Using custom keywords: {content['_custom_keywords']}")
            return content['_custom_keywords']
        
        keywords = []
        
        # Extract from headline
        if content.get('headline'):
            headline_words = re.findall(r'\b\w+\b', content['headline'].lower())
            keywords.extend([w for w in headline_words if len(w) > 3])
        
        # Extract from subhead
        if content.get('subhead'):
            subhead_words = re.findall(r'\b\w+\b', content['subhead'].lower())
            keywords.extend([w for w in subhead_words if len(w) > 3])
        
        # Extract from bullets
        if content.get('bullets'):
            for bullet in content['bullets']:
                bullet_words = re.findall(r'\b\w+\b', str(bullet).lower())
                keywords.extend([w for w in bullet_words if len(w) > 3])
        
        # Extract from caption
        if content.get('caption'):
            caption_words = re.findall(r'\b\w+\b', content['caption'].lower())
            keywords.extend([w for w in caption_words if len(w) > 3])
        
        # Remove duplicates and common words
        common_words = {'the', 'and', 'for', 'with', 'this', 'that', 'will', 'can', 'are', 'you', 'your', 'from', 'have', 'they', 'been', 'their', 'what', 'when', 'where', 'which', 'there', 'here', 'some', 'very', 'just', 'only', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'within', 'without', 'against', 'toward', 'towards', 'upon', 'under', 'over', 'behind', 'beneath', 'beside', 'beyond', 'inside', 'outside', 'around', 'across', 'along', 'throughout', 'through', 'during', 'before', 'after', 'since', 'until', 'while', 'whereas', 'although', 'though', 'unless', 'except', 'besides', 'including', 'excluding', 'like', 'unlike', 'as', 'than', 'rather', 'quite', 'very', 'too', 'enough', 'so', 'such', 'more', 'most', 'less', 'least', 'fewer', 'fewest', 'many', 'much', 'several', 'some', 'any', 'all', 'every', 'each', 'either', 'neither', 'both', 'none', 'no', 'yes', 'maybe', 'perhaps', 'probably', 'definitely', 'certainly', 'surely', 'obviously', 'clearly', 'evidently', 'apparently', 'seemingly', 'supposedly', 'allegedly', 'reportedly', 'purportedly', 'ostensibly', 'nominally', 'formally', 'officially', 'legally', 'technically', 'theoretically', 'practically', 'virtually', 'essentially', 'basically', 'fundamentally', 'primarily', 'mainly', 'chiefly', 'principally', 'largely', 'mostly', 'generally', 'usually', 'typically', 'normally', 'ordinarily', 'commonly', 'frequently', 'often', 'sometimes', 'occasionally', 'rarely', 'seldom', 'hardly', 'scarcely', 'barely', 'almost', 'nearly', 'approximately', 'roughly', 'about', 'around', 'somewhere', 'anywhere', 'everywhere', 'nowhere', 'somehow', 'anyhow', 'anyway', 'regardless', 'nevertheless', 'nonetheless', 'however', 'nevertheless', 'still', 'yet', 'though', 'although', 'even', 'despite', 'in spite', 'except', 'but', 'however', 'nevertheless', 'nonetheless', 'still', 'yet', 'though', 'although', 'even', 'despite', 'in spite', 'except', 'but', 'however', 'nevertheless', 'nonetheless', 'still', 'yet', 'though', 'although', 'even', 'despite', 'in spite', 'except', 'but'}
        
        unique_keywords = list(set(keywords) - common_words)
        
        # Return top 5 most relevant keywords
        return unique_keywords[:5]
    
    def enhance_search_query_with_ai(self, content: Dict[str, Any]) -> str:
        """Use AI to generate optimized image search queries"""
        if not self.llm_client:
            return self.fallback_query_generation(content)
        
        try:
            content_text = json.dumps(content, indent=2)
            prompt = f"""Analyze this content and generate the BEST single image search query for finding a professional, high-quality background image:

Content: {content_text}

Requirements:
- Generate ONE concise search query (2-4 words max)
- Focus on visual concepts, not text content
- Prioritize professional, clean, modern aesthetics
- Consider Instagram/social media suitability
- Avoid overly specific terms that might return no results

Examples:
- For business content: "modern office space"
- For tech content: "abstract technology"
- For lifestyle content: "minimalist lifestyle"

Return ONLY the search query, nothing else."""

            response = self.llm_client.generate(prompt)
            query = response.strip().strip('"').strip("'")
            
            # Validate query length and content
            if len(query.split()) <= 6 and len(query) > 3:
                print(f"🤖 AI-enhanced query: '{query}'")
                return query
            else:
                print(f"⚠️ AI query too long/short, using fallback: '{query}'")
                return self.fallback_query_generation(content)
                
        except Exception as e:
            print(f"❌ AI query enhancement failed: {e}")
            return self.fallback_query_generation(content)
    
    def fallback_query_generation(self, content: Dict[str, Any]) -> str:
        """Fallback query generation using keyword extraction"""
        keywords = self.extract_keywords(content)
        if not keywords:
            return "modern business professional"
        return ' '.join(keywords[:3])
    
    def search_unsplash(self, query: str) -> Optional[str]:
        """Search Unsplash for relevant images"""
        if not self.unsplash_access_key:
            print(f"⚠️ Unsplash API not configured - Access Key: {bool(self.unsplash_access_key)}")
            return None
            
        try:
            url = "https://api.unsplash.com/search/photos"
            params = {
                'query': query,
                'per_page': 1,
                'orientation': 'squarish'
            }
            headers = {
                'Authorization': f'Client-ID {self.unsplash_access_key}'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                return data['results'][0]['urls']['regular']
                
        except Exception as e:
            print(f"Unsplash search failed: {e}")
        
        return None
    
    def search_pexels(self, query: str) -> Optional[str]:
        """Search Pexels for relevant images"""
        if not self.pexels_api_key:
            return None
            
        try:
            url = "https://api.pexels.com/v1/search"
            params = {
                'query': query,
                'per_page': 1,
                'orientation': 'square'
            }
            headers = {
                'Authorization': self.pexels_api_key
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('photos') and len(data['photos']) > 0:
                return data['photos'][0]['src']['large']
                
        except Exception as e:
            print(f"Pexels search failed: {e}")
        
        return None
    
    def search_google_custom(self, query: str) -> Optional[str]:
        """Search Google Custom Search for relevant images"""
        if not self.google_api_key or not self.google_search_engine_id:
            print(f"⚠️ Google Custom Search not configured - API Key: {bool(self.google_api_key)}, Engine ID: {bool(self.google_search_engine_id)}")
            return None
            
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': self.google_search_engine_id,
                'q': query,
                'searchType': 'image',
                'num': 1,
                'imgSize': 'large',
                'imgType': 'photo',
                'safe': 'active'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('items') and len(data['items']) > 0:
                return data['items'][0]['link']
                
        except Exception as e:
            print(f"Google Custom Search failed: {e}")
        
        return None
    
    def search_pixabay(self, query: str) -> Optional[str]:
        """Search Pixabay for relevant images (free tier available)"""
        if not self.pixabay_api_key:
            return None
            
        try:
            url = "https://pixabay.com/api/"
            params = {
                'key': self.pixabay_api_key,
                'q': query,
                'per_page': 1,
                'image_type': 'photo',
                'orientation': 'horizontal'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('hits') and len(data['hits']) > 0:
                return data['hits'][0]['webformatURL']
                
        except Exception as e:
            print(f"Pixabay search failed: {e}")
        
        return None
    
    def search_unsplash_source(self, query: str) -> Optional[str]:
        """Search Unsplash Source API (no API key required, limited)"""
        try:
            # Use Unsplash Source API which doesn't require authentication
            # Format: https://source.unsplash.com/1080x1080/?query
            url = f"https://source.unsplash.com/1080x1080/?{query}"
            
            print(f"🔍 Trying Unsplash Source: {url}")
            
            # Test if the URL is accessible
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ Unsplash Source URL accessible")
                return url
            else:
                print(f"❌ Unsplash Source returned status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Unsplash Source search failed: {e}")
        
        return None
    
    def get_stock_image(self, query: str) -> str:
        """Get a stock image from various free sources"""
        # Curated list of high-quality stock images for common themes
        stock_images = {
            'business': [
                'https://images.unsplash.com/photo-1556761175-b413da4baf72?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1559136555-9303baea8ebd?w=1080&h=1080&fit=crop'
            ],
            'technology': [
                'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1518186285589-2f7649de83e0?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1517077304055-6e89abbf09b0?w=1080&h=1080&fit=crop'
            ],
            'modern': [
                'https://images.unsplash.com/photo-1497366216548-37526070297c?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1080&h=1080&fit=crop'
            ],
            'ai': [
                'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1676299251956-415118d97504?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1673187733777-4e8e6c0b1b1b?w=1080&h=1080&fit=crop'
            ],
            'innovation': [
                'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=1080&h=1080&fit=crop',
                'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1080&h=1080&fit=crop'
            ]
        }
        
        # Find the best matching category
        query_lower = query.lower()
        best_category = 'business'  # default
        
        for category in stock_images.keys():
            if category in query_lower:
                best_category = category
                break
        
        # Return a random image from the best category
        images = stock_images.get(best_category, stock_images['business'])
        return random.choice(images)
    
    def get_lorem_picsum(self, query: str) -> str:
        """Get a Lorem Picsum image with query-based seed"""
        # Create a seed from the query for consistent results
        seed = hash(query) % 1000
        return f"https://picsum.photos/seed/{seed}/1080/1080"
    
    def generate_image_by_mode(self, mode: str, prompt: str, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate image based on selected mode"""
        print(f"🎯 Generating image using mode: {mode}")
        
        if mode == "ai_generate":
            # AI-generated image
            image_url = self.generate_ai_image(prompt, content)
            if image_url:
                return {
                    'image_url': image_url,
                    'source': 'ai_generated',
                    'mode': mode,
                    'has_text': False,  # DALL-E generates background only by default
                    'skip_overlay': False,
                    'quality_score': 95
                }
        
        elif mode == "curated":
            # Curated brand images
            curated_images = self.get_curated_images(content)
            if curated_images:
                best_image = max(curated_images, key=lambda x: x['quality_score'])
                return {
                    'image_url': best_image['url'],
                    'source': 'curated',
                    'mode': mode,
                    'has_text': False,
                    'skip_overlay': False,
                    'quality_score': best_image['quality_score']
                }
        
        elif mode == "hybrid":
            # Try multiple sources and pick best
            all_candidates = []
            
            # Try AI generation
            ai_url = self.generate_ai_image(prompt, content)
            if ai_url:
                all_candidates.append({
                    'image_url': ai_url,
                    'source': 'ai_generated',
                    'quality_score': 95
                })
            
            # Try curated
            curated_images = self.get_curated_images(content)
            if curated_images:
                best_curated = max(curated_images, key=lambda x: x['quality_score'])
                all_candidates.append({
                    'image_url': best_curated['url'],
                    'source': 'curated',
                    'quality_score': best_curated['quality_score']
                })
            
            # Try search
            search_result = self.fetch_search_image(content)
            if search_result:
                all_candidates.append(search_result)
            
            # Return best candidate
            if all_candidates:
                best = max(all_candidates, key=lambda x: x['quality_score'])
                return {
                    **best,
                    'mode': mode,
                    'has_text': False,
                    'skip_overlay': False
                }
        
        # Default to search mode
        return self.fetch_search_image(content) or self.get_fallback_image()
    
    def fetch_search_image(self, content: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch image using search APIs"""
        keywords = self.extract_keywords(content)
        
        if not keywords:
            keywords = ['business', 'technology', 'modern']
        
        search_query = ' '.join(keywords[:3])
        print(f"🔍 Searching for images with query: {search_query}")
        
        # Try Google Custom Search first
        image_url = self.search_google_custom(search_query)
        if image_url:
            return {
                'image_url': image_url,
                'source': 'google_search',
                'quality_score': 80
            }
        
        # Try Unsplash Source
        image_url = self.search_unsplash_source(search_query)
        if image_url:
            return {
                'image_url': image_url,
                'source': 'unsplash_source',
                'quality_score': 75
            }
        
        # Try Unsplash API
        image_url = self.search_unsplash(search_query)
        if image_url:
            return {
                'image_url': image_url,
                'source': 'unsplash_api',
                'quality_score': 85
            }
        
        # Try other APIs...
        image_url = self.search_pexels(search_query)
        if image_url:
            return {
                'image_url': image_url,
                'source': 'pexels',
                'quality_score': 70
            }
        
        return None
    
    def get_fallback_image(self) -> Dict[str, Any]:
        """Get fallback image when all else fails"""
        fallback_url = self.get_stock_image("business professional")
        return {
            'image_url': fallback_url,
            'source': 'fallback_stock',
            'mode': 'search',
            'has_text': False,
            'skip_overlay': False,
            'quality_score': 60
        }


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Get content from previous nodes
        content = state.get('structured_data') or state.get('overlay_text') or {}
        
        # Get user preferences
        prompt = state.get('prompt', '')
        style = state.get('style', 'modern')
        user_image_url = state.get('user_image_url')  # For future user uploads
        
        # Initialize smart image generator
        smart_generator = SmartImageGenerator()
        
        # Determine image source
        if user_image_url:
            # User provided image
            result = {
                'image_url': user_image_url,
                'source': 'user_upload',
                'mode': 'user_upload',
                'has_text': False,
                'skip_overlay': False,
                'quality_score': 100
            }
        else:
            # Detect best mode for this content
            mode = smart_generator.detect_image_mode(prompt, content)
            
            # Generate image using detected mode
            result = smart_generator.generate_image_by_mode(mode, prompt, content)
        
        print(f"✅ Smart image generation completed - Mode: {result.get('mode', 'unknown')}, Source: {result.get('source', 'unknown')}")

        # Return enhanced state with mode information
        return {
            'image_url': result['image_url'],
            'source': result['source'],
            'mode': result.get('mode', 'search'),
            'has_text': result.get('has_text', False),
            'skip_overlay': result.get('skip_overlay', False),
            'quality_score': result.get('quality_score', 60),
            'keywords': smart_generator.extract_keywords(content) if content else []
        }
        
    except Exception as e:
        print(f"❌ Error in smart image generator: {e}")
        # Return fallback structure
        return {
            'image_url': None,
            'source': 'error',
            'mode': 'error',
            'has_text': False,
            'skip_overlay': False,
            'quality_score': 0,
            'keywords': []
        }