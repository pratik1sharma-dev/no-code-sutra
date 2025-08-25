from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
import re
import os
import json
import random


class DynamicImageFetcher:
    """Fetches relevant background images from multiple public APIs"""
    
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_CUSTOM_SEARCH_API_KEY')
        self.google_search_engine_id = os.getenv('GOOGLE_CUSTOM_SEARCH_ENGINE_ID')
        self.unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.pexels_api_key = os.getenv('PEXELS_API_KEY')
        self.pixabay_api_key = os.getenv('PIXABAY_API_KEY')
        
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
    
    def fetch_relevant_image(self, content: Dict[str, Any]) -> str:
        """Fetch the most relevant background image using enhanced fallback chain"""
        keywords = self.extract_keywords(content)
        
        if not keywords:
            # Fallback to generic terms
            keywords = ['business', 'technology', 'modern']
        
        # Create search query from keywords
        search_query = ' '.join(keywords[:3])  # Use top 3 keywords
        
        print(f"Searching for images with query: {search_query}")
        
        # Try Google Custom Search first (access to entire web)
        image_url = self.search_google_custom(search_query)
        if image_url:
            print(f"Found Google Custom Search image: {image_url}")
            return image_url
        
        # Try Unsplash Source second (no API key required)
        image_url = self.search_unsplash_source(search_query)
        if image_url:
            print(f"Found Unsplash Source image: {image_url}")
            return image_url
        
        # Try Unsplash API third (high quality stock photos, requires API key)
        image_url = self.search_unsplash(search_query)
        if image_url:
            print(f"Found Unsplash API image: {image_url}")
            return image_url
        
        # Try Pexels API fourth (requires API key)
        image_url = self.search_pexels(search_query)
        if image_url:
            print(f"Found Pexels API image: {image_url}")
            return image_url
        
        # Try Pixabay API fifth (requires API key)
        image_url = self.search_pixabay(search_query)
        if image_url:
            print(f"Found Pixabay API image: {image_url}")
            return image_url
        
        # Try curated stock images (no API key required)
        image_url = self.get_stock_image(search_query)
        print(f"Using curated stock image: {image_url}")
        return image_url


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Get content from previous nodes
        content = state.get('structured_data') or state.get('overlay_text') or {}
        
        # Get user preferences
        prompt = state.get('prompt', '')
        style = state.get('style', 'modern')
        user_image_url = state.get('user_image_url')  # For future user uploads
        
        # Initialize image fetcher
        image_fetcher = DynamicImageFetcher()
        
        # Determine image source
        if user_image_url:
            # User provided image (future feature)
            image_url = user_image_url
            source = 'user_upload'
        elif prompt and 'generate' in prompt.lower():
            # AI image generation (future feature)
            # For now, fall back to dynamic fetching
            image_url = image_fetcher.fetch_relevant_image(content)
            source = 'ai_generation_fallback'
        else:
            # Dynamic background image fetching
            image_url = image_fetcher.fetch_relevant_image(content)
            source = 'dynamic_fetch'
        
        # Prepare response
        image_data = {
            'prompt': prompt,
            'style': style,
            'image_url': image_url,
            'source': source,
            'keywords': image_fetcher.extract_keywords(content) if content else [],
            'generated_at': datetime.now().isoformat()
        }
        
        # Update state
        state['image_data'] = image_data
        state['image_url'] = image_url
        state['background_image_url'] = image_url  # For text overlay compatibility
        state['image'] = image_data
        state['status'] = 'completed'
        state['timestamp'] = datetime.now().isoformat()
        
        print(f"Image generator completed - Source: {source}, URL: {image_url}")
        return state
        
    except Exception as e:
        print(f"Error in image generator node: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state