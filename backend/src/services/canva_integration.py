"""
Canva API Integration Service
Handles OAuth authentication, template access, and content creation
"""

import os
import requests
import json
import hashlib
import secrets
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode
import base64
from datetime import datetime, timedelta

class CanvaIntegration:
    """Canva API integration service"""
    
    def __init__(self):
        self.client_id = os.getenv('CANVA_CLIENT_ID')
        self.client_secret = os.getenv('CANVA_CLIENT_SECRET')
        self.redirect_uri = os.getenv('CANVA_REDIRECT_URI', 'http://127.0.0.1:8000/api/auth/canva/callback')
        # Use production environment (development apps work here too)
        self.base_url = 'https://api.canva.com'
        self.auth_url = 'https://www.canva.com/api/oauth/authorize'  # Updated to correct endpoint
        self.token_url = 'https://api.canva.com/oauth/token'
        
        # Token storage
        self.access_token = None
        self.refresh_token = None
        self.token_expires_at = None
        
        # PKCE support
        self.code_verifier = None
        self.code_challenge = None
    
    def _generate_pkce_pair(self):
        """Generate PKCE code verifier and challenge"""
        # Generate code verifier (random string)
        self.code_verifier = secrets.token_urlsafe(32)
        
        # Generate code challenge (SHA256 hash of verifier, base64url encoded)
        challenge = hashlib.sha256(self.code_verifier.encode()).digest()
        self.code_challenge = base64.urlsafe_b64encode(challenge).decode().rstrip('=')
        
        return self.code_verifier, self.code_challenge
    
    def get_authorization_url(self, state: str = None) -> str:
        """
        Generate authorization URL for OAuth flow with PKCE
        
        Args:
            state: Optional state parameter for security
            
        Returns:
            Authorization URL for user to visit
        """
        # Generate PKCE pair
        code_verifier, code_challenge = self._generate_pkce_pair()
        
        # Use correct Canva API scopes
        scopes = [
            'profile:read',
            'asset:read',
            'asset:write',
            'brandtemplate:content:read',
            'brandtemplate:meta:read',
            'design:content:read',
            'design:content:write',
            'design:meta:read'
        ]
        
        # Log the scopes being used
        print("🎨 Canva OAuth Scopes:")
        print(f"   Scopes: {scopes}")
        print(f"   Scopes string: {' '.join(scopes)}")
        print("🎨 End of Canva OAuth Scopes")
        
        # Store code_verifier in state for later retrieval
        if state:
            # For now, we'll use a simple file-based storage
            # In production, this should be stored in a database or session
            import json
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            pkce_file = os.path.join(temp_dir, f"canva_pkce_{state}.json")
            
            pkce_data = {
                'code_verifier': code_verifier,
                'timestamp': datetime.now().isoformat()
            }
            
            with open(pkce_file, 'w') as f:
                json.dump(pkce_data, f)
        
        params = {
            'code_challenge_method': 'S256',
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'state': state or 'default_state',
            'code_challenge': code_challenge
        }
        
        # Only add scope parameter if there are scopes
        if scopes:
            params['scope'] = ' '.join(scopes)
        
        auth_url = f"{self.auth_url}?{urlencode(params)}"
        
        # Log the final parameters
        print("🎨 Canva OAuth Parameters:")
        print(f"   Parameters: {params}")
        print("🎨 End of Canva OAuth Parameters")
        
        # Log the generated URL for debugging
        print("🎨 Generated Canva Authorization URL:")
        print(f"   Auth URL: {self.auth_url}")
        print(f"   Client ID: {self.client_id}")
        print(f"   Redirect URI: {self.redirect_uri}")
        print(f"   State: {state or 'default_state'}")
        print(f"   Full URL: {auth_url}")
        print("🎨 End of Canva Authorization URL")
        
        return auth_url
    
    def exchange_code_for_token(self, authorization_code: str, state: str = None) -> Dict[str, Any]:
        """
        Exchange authorization code for access token with PKCE
        
        Args:
            authorization_code: Code received from OAuth callback
            state: State parameter to retrieve stored code_verifier
            
        Returns:
            Token response with access_token, refresh_token, etc.
        """
        # Retrieve code_verifier from storage
        code_verifier = None
        if state:
            import json
            import tempfile
            import os
            
            temp_dir = tempfile.gettempdir()
            pkce_file = os.path.join(temp_dir, f"canva_pkce_{state}.json")
            
            try:
                with open(pkce_file, 'r') as f:
                    pkce_data = json.load(f)
                    code_verifier = pkce_data.get('code_verifier')
                
                # Clean up the file
                os.remove(pkce_file)
            except (FileNotFoundError, json.JSONDecodeError):
                pass
        
        if not code_verifier:
            raise ValueError("Code verifier not found. Please generate authorization URL first.")
        
        # Check if the authorization code is a JWT (Canva might use a different flow)
        if authorization_code.startswith('eyJ'):
            print("🎨 Detected JWT authorization code - this might be a different OAuth flow")
            # For JWT-based flows, we might need to decode and use differently
            import jwt
            try:
                # Try to decode the JWT (without verification for now)
                decoded = jwt.decode(authorization_code, options={"verify_signature": False})
                print(f"🎨 JWT Decoded: {decoded}")
                
                # If it's a JWT, we might not need to exchange it
                # The JWT might contain the access token directly
                if 'access_token' in decoded:
                    print("🎨 JWT contains access token directly")
                    token_data = {
                        'access_token': decoded['access_token'],
                        'token_type': 'Bearer',
                        'expires_in': decoded.get('exp', 3600)
                    }
                    self._store_tokens(token_data)
                    return token_data
                
                # If JWT doesn't contain access_token, the JWT itself might be the access token
                print("🎨 JWT doesn't contain access_token - using JWT as access token")
                token_data = {
                    'access_token': authorization_code,  # Use the JWT as the access token
                    'token_type': 'Bearer',
                    'expires_in': decoded.get('exp', 3600) - decoded.get('iat', 0)
                }
                self._store_tokens(token_data)
                return token_data
                    
            except Exception as jwt_error:
                print(f"🎨 JWT decode error: {jwt_error}")
        
        # Standard OAuth flow (fallback)
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json'
        }
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
            'code': authorization_code,
            'code_verifier': code_verifier
        }
        
        # Log the token exchange request for debugging
        print("🎨 Canva Token Exchange Request:")
        print(f"   Token URL: {self.token_url}")
        print(f"   Headers: {headers}")
        print(f"   Client ID: {self.client_id}")
        print(f"   Redirect URI: {self.redirect_uri}")
        print(f"   Code: {authorization_code[:20]}...")
        print(f"   Code Verifier: {code_verifier[:20] if code_verifier else 'None'}...")
        print(f"   Request Data: {data}")
        print("🎨 End of Token Exchange Request")
        
        # Try with explicit headers
        response = requests.post(self.token_url, data=data, headers=headers)
        
        # Log the response for debugging
        print("🎨 Canva Token Exchange Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers: {dict(response.headers)}")
        try:
            response_text = response.text
            print(f"   Response Body: {response_text}")
        except:
            print("   Response Body: [Could not read]")
        print("🎨 End of Token Exchange Response")
        
        response.raise_for_status()
        
        token_data = response.json()
        self._store_tokens(token_data)
        return token_data
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Returns:
            New token data
        """
        if not self.refresh_token:
            raise ValueError("No refresh token available")
        
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }
        
        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self._store_tokens(token_data)
        return token_data
    
    def _store_tokens(self, token_data: Dict[str, Any]):
        """Store tokens internally"""
        self.access_token = token_data.get('access_token')
        self.refresh_token = token_data.get('refresh_token', self.refresh_token)
        
        if 'expires_in' in token_data:
            self.token_expires_at = datetime.now() + timedelta(seconds=token_data['expires_in'])
    
    def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if not self.access_token:
            raise ValueError("No access token available. Please authenticate first.")
        
        if self.token_expires_at and datetime.now() >= self.token_expires_at:
            self.refresh_access_token()
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get current user profile
        
        Returns:
            User profile information
        """
        self._ensure_valid_token()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/user/profile", headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def search_templates(self, query: str = None, category: str = None, 
                        limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search for templates
        
        Args:
            query: Search query
            category: Template category
            limit: Number of results to return
            
        Returns:
            List of matching templates
        """
        self._ensure_valid_token()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {'limit': limit}
        
        if query:
            params['q'] = query
        if category:
            params['category'] = category
        
        response = requests.get(f"{self.base_url}/templates", headers=headers, params=params)
        response.raise_for_status()
        
        return response.json().get('templates', [])
    
    def get_template_details(self, template_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific template
        
        Args:
            template_id: Canva template ID
            
        Returns:
            Template details
        """
        self._ensure_valid_token()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/templates/{template_id}", headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def download_template(self, template_id: str, format: str = 'png') -> bytes:
        """
        Download a template as an image file
        
        Args:
            template_id: Canva template ID
            format: Export format (png, jpg, pdf)
            
        Returns:
            Template image data as bytes
        """
        self._ensure_valid_token()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {
            'format': format,
            'width': 1080,
            'height': 1080
        }
        
        # Try to download template directly
        response = requests.get(f"{self.base_url}/templates/{template_id}/download", 
                              headers=headers, params=params)
        
        if response.status_code == 404:
            # If direct download not available, try getting template preview
            response = requests.get(f"{self.base_url}/templates/{template_id}/preview", 
                                  headers=headers, params=params)
        
        response.raise_for_status()
        return response.content
    
    def get_template_structure(self, template_id: str) -> Dict[str, Any]:
        """
        Get template structure and editable elements
        
        Args:
            template_id: Canva template ID
            
        Returns:
            Template structure with editable elements
        """
        self._ensure_valid_token()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        # Get template details first
        template_details = self.get_template_details(template_id)
        
        # Try to get template structure/JSON
        try:
            response = requests.get(f"{self.base_url}/templates/{template_id}/structure", 
                                  headers=headers)
            if response.status_code == 200:
                structure = response.json()
                return {
                    'template_details': template_details,
                    'structure': structure,
                    'editable_elements': structure.get('elements', []),
                    'dimensions': structure.get('dimensions', {}),
                    'background': structure.get('background', {})
                }
        except:
            pass
        
        # Fallback: return template details with basic structure
        return {
            'template_details': template_details,
            'structure': None,
            'editable_elements': template_details.get('elements', []),
            'dimensions': template_details.get('dimensions', {}),
            'background': template_details.get('background', {})
        }
    
    def create_design_from_template(self, template_id: str, 
                                  content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new design from a template with custom content
        
        Args:
            template_id: Canva template ID
            content: Content to apply to template
            
        Returns:
            Created design information
        """
        self._ensure_valid_token()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'template_id': template_id,
            'content': content
        }
        
        response = requests.post(f"{self.base_url}/designs", headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_user_designs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get user's designs
        
        Args:
            limit: Number of designs to return
            
        Returns:
            List of user designs
        """
        self._ensure_valid_token()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {'limit': limit}
        
        response = requests.get(f"{self.base_url}/designs", headers=headers, params=params)
        response.raise_for_status()
        
        return response.json().get('designs', [])
    
    def export_design(self, design_id: str, format: str = 'png', 
                     width: int = 1080, height: int = 1080) -> bytes:
        """
        Export a design as an image
        
        Args:
            design_id: Canva design ID
            format: Export format (png, jpg, pdf)
            width: Export width
            height: Export height
            
        Returns:
            Image data as bytes
        """
        self._ensure_valid_token()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        params = {
            'format': format,
            'width': width,
            'height': height
        }
        
        response = requests.get(f"{self.base_url}/designs/{design_id}/export", 
                              headers=headers, params=params)
        response.raise_for_status()
        
        return response.content
    
    def update_design_content(self, design_id: str, 
                            content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update content in an existing design
        
        Args:
            design_id: Canva design ID
            content: New content to apply
            
        Returns:
            Updated design information
        """
        self._ensure_valid_token()
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        data = {'content': content}
        
        response = requests.patch(f"{self.base_url}/designs/{design_id}", 
                                headers=headers, json=data)
        response.raise_for_status()
        
        return response.json()
    
    def get_template_categories(self) -> List[Dict[str, Any]]:
        """
        Get available template categories
        
        Returns:
            List of template categories
        """
        self._ensure_valid_token()
        
        headers = {'Authorization': f'Bearer {self.access_token}'}
        response = requests.get(f"{self.base_url}/templates/categories", headers=headers)
        response.raise_for_status()
        
        return response.json().get('categories', [])
    
    def apply_content_to_template(self, template_id: str, 
                                content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply content to a template and return the design
        
        Args:
            template_id: Canva template ID
            content_data: Content to apply (headline, subhead, bullets, etc.)
            
        Returns:
            Design with applied content
        """
        try:
            # Try to create design using Canva API (production mode)
            canva_content = self._map_content_to_canva_format(content_data)
            design = self.create_design_from_template(template_id, canva_content)
            return design
        except Exception as e:
            print(f"🎨 Canva design creation failed (likely dev mode): {e}")
            # Fallback: Create custom design using template structure
            return self._create_custom_design_from_template(template_id, content_data)
    
    def _create_custom_design_from_template(self, template_id: str, 
                                          content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a custom design by downloading template and editing it programmatically
        
        Args:
            template_id: Canva template ID
            content_data: Content to apply
            
        Returns:
            Custom design information
        """
        try:
            # Get template structure
            template_structure = self.get_template_structure(template_id)
            
            # Download template image
            template_image = self.download_template(template_id, 'png')
            
            # Create custom design using PIL/Pillow
            from PIL import Image, ImageDraw, ImageFont
            import io
            import base64
            
            # Load template image
            img = Image.open(io.BytesIO(template_image))
            draw = ImageDraw.Draw(img)
            
            # Try to load a font (fallback to default if not available)
            try:
                font_large = ImageFont.truetype("Arial.ttf", 48)
                font_medium = ImageFont.truetype("Arial.ttf", 32)
                font_small = ImageFont.truetype("Arial.ttf", 24)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Apply content to image
            y_position = 100
            
            # Add headline
            if 'headline' in content_data:
                draw.text((50, y_position), content_data['headline'], 
                         fill='black', font=font_large)
                y_position += 80
            
            # Add subhead
            if 'subhead' in content_data:
                draw.text((50, y_position), content_data['subhead'], 
                         fill='#666666', font=font_medium)
                y_position += 60
            
            # Add bullets
            if 'bullets' in content_data:
                for bullet in content_data['bullets']:
                    draw.text((50, y_position), f"• {bullet}", 
                             fill='#333333', font=font_small)
                    y_position += 40
            
            # Save to bytes
            output = io.BytesIO()
            img.save(output, format='PNG')
            output.seek(0)
            
            # Convert to base64 for easy handling
            image_base64 = base64.b64encode(output.getvalue()).decode('utf-8')
            
            # Generate unique design ID
            import uuid
            design_id = f"custom_design_{uuid.uuid4().hex[:8]}"
            
            return {
                'design_id': design_id,
                'template_id': template_id,
                'content_applied': content_data,
                'image_data': image_base64,
                'image_data_url': f"data:image/png;base64,{image_base64}",
                'format': 'png',
                'width': img.width,
                'height': img.height,
                'created_at': datetime.now().isoformat(),
                'method': 'custom_editing'
            }
            
        except Exception as e:
            print(f"🎨 Custom design creation failed: {e}")
            # Return a mock design with template info
            return {
                'design_id': f"mock_design_{template_id}",
                'template_id': template_id,
                'content_applied': content_data,
                'error': str(e),
                'method': 'mock_fallback',
                'created_at': datetime.now().isoformat()
            }
    
    def _map_content_to_canva_format(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map our content structure to Canva's expected format
        
        Args:
            content_data: Our content structure
            
        Returns:
            Canva-formatted content
        """
        # This mapping will depend on Canva's API structure
        # You'll need to adjust based on actual Canva API documentation
        
        canva_content = {
            'elements': []
        }
        
        # Map headline
        if 'headline' in content_data:
            canva_content['elements'].append({
                'type': 'text',
                'id': 'headline',
                'content': content_data['headline'],
                'style': {
                    'fontSize': 48,
                    'fontWeight': 'bold',
                    'color': '#000000'
                }
            })
        
        # Map subhead
        if 'subhead' in content_data:
            canva_content['elements'].append({
                'type': 'text',
                'id': 'subhead',
                'content': content_data['subhead'],
                'style': {
                    'fontSize': 32,
                    'fontWeight': 'normal',
                    'color': '#666666'
                }
            })
        
        # Map bullets
        if 'bullets' in content_data:
            for i, bullet in enumerate(content_data['bullets']):
                canva_content['elements'].append({
                    'type': 'text',
                    'id': f'bullet_{i}',
                    'content': f"• {bullet}",
                    'style': {
                        'fontSize': 24,
                        'fontWeight': 'normal',
                        'color': '#333333'
                    }
                })
        
        return canva_content
    
    def get_popular_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """
        Get popular templates
        
        Args:
            category: Optional category filter
            
        Returns:
            List of popular templates
        """
        return self.search_templates(category=category, limit=50)
    
    def save_tokens_to_file(self, filepath: str = 'canva_tokens.json'):
        """Save tokens to file for persistence"""
        token_data = {
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None
        }
        
        with open(filepath, 'w') as f:
            json.dump(token_data, f)
    
    def load_tokens_from_file(self, filepath: str = 'canva_tokens.json'):
        """Load tokens from file"""
        try:
            with open(filepath, 'r') as f:
                token_data = json.load(f)
            
            self.access_token = token_data.get('access_token')
            self.refresh_token = token_data.get('refresh_token')
            
            if token_data.get('expires_at'):
                self.token_expires_at = datetime.fromisoformat(token_data['expires_at'])
                
        except FileNotFoundError:
            pass  # No saved tokens
