from typing import Dict, Any, Tuple, Optional
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import textwrap
import os
import math


class FontSystem:
    """Flexible font system for text overlay with mobile-optimized sizing"""
    
    def __init__(self, image_width: int, image_height: int):
        self.image_width = image_width
        self.image_height = image_height
        self.font_cache = {}
        
        # Mobile-optimized font size calculations based on image dimensions
        self.base_size = max(16, min(image_width, image_height) // 40)  # Minimum 16px, scales with image
        
        # Font size hierarchy for different content types
        self.font_sizes = {
            'headline': int(self.base_size * 2.8),      # Large, impactful headlines
            'subhead': int(self.base_size * 2.0),       # Medium subheadings
            'body': int(self.base_size * 1.4),          # Regular body text
            'caption': int(self.base_size * 1.1),       # Smaller captions
            'bullet': int(self.base_size * 1.3)         # Bullet points
        }
        
        # Ensure minimum readable sizes for mobile
        self.font_sizes = {k: max(v, 24) for k, v in self.font_sizes.items()}
        
        # Color schemes for different text types
        self.colors = {
            'headline': (25, 25, 25, 255),      # Dark, high contrast
            'subhead': (45, 45, 45, 255),       # Medium dark
            'body': (65, 65, 65, 255),          # Medium gray
            'caption': (85, 85, 85, 255),       # Light gray
            'bullet': (60, 60, 60, 255)         # Medium gray for bullets
        }
        
        # Line spacing multipliers
        self.line_spacing = {
            'headline': 1.3,
            'subhead': 1.2,
            'body': 1.15,
            'caption': 1.1,
            'bullet': 1.2
        }
        
        # Initialize fonts
        self._initialize_fonts()
    
    def _initialize_fonts(self):
        """Initialize fonts with fallback system"""
        try:
            # Try to load system fonts first
            font_paths = self._get_system_fonts()
            
            for font_type, size in self.font_sizes.items():
                font = self._load_best_font(font_paths, size)
                self.font_cache[font_type] = font
                
        except Exception as e:
            print(f"Font initialization warning: {e}")
            # Fallback to default font with scaling
            self._initialize_fallback_fonts()
    
    def _get_system_fonts(self) -> list:
        """Get available system fonts with priority order"""
        font_paths = []
        
        # Common system font paths
        system_fonts = [
            # macOS
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            "/System/Library/Fonts/SF-Pro-Display-Regular.otf",
            # Linux
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            # Windows (if running on Windows)
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/calibri.ttf"
        ]
        
        for font_path in system_fonts:
            if os.path.exists(font_path):
                font_paths.append(font_path)
        
        return font_paths
    
    def _load_best_font(self, font_paths: list, size: int) -> ImageFont.FreeTypeFont:
        """Load the best available font for given size"""
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue
        
        # Fallback to default font
        return ImageFont.load_default()
    
    def _initialize_fallback_fonts(self):
        """Initialize fallback fonts using default font with scaling"""
        base_font = ImageFont.load_default()
        
        for font_type, size in self.font_sizes.items():
            # Create a scaled version of the default font
            self.font_cache[font_type] = base_font
    
    def get_font(self, font_type: str) -> ImageFont.FreeTypeFont:
        """Get font for specified type"""
        return self.font_cache.get(font_type, self.font_cache.get('body'))
    
    def get_color(self, font_type: str) -> Tuple[int, int, int, int]:
        """Get color for specified font type"""
        return self.colors.get(font_type, self.colors['body'])
    
    def get_line_spacing(self, font_type: str) -> float:
        """Get line spacing multiplier for font type"""
        return self.line_spacing.get(font_type, 1.2)
    
    def calculate_text_dimensions(self, text: str, font_type: str) -> Tuple[int, int]:
        """Calculate text dimensions for given font type"""
        font = self.get_font(font_type)
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    
    def get_optimal_wrap_width(self, font_type: str, max_width: int) -> int:
        """Calculate optimal wrap width for text wrapping"""
        font = self.get_font(font_type)
        # Estimate characters per line based on average character width
        avg_char_width = font.getbbox("M")[2]  # Use 'M' as reference
        return max(10, int(max_width / avg_char_width))


class TextRenderer:
    """Handles text rendering with proper positioning and effects"""
    
    def __init__(self, font_system: FontSystem):
        self.font_system = font_system
    
    def render_text_block(self, draw: ImageDraw.Draw, text: str, font_type: str, 
                         position: Tuple[int, int], max_width: int) -> int:
        """Render a block of text with proper wrapping and return height used"""
        if not text:
            return 0
        
        x, y = position
        font = self.font_system.get_font(font_type)
        color = self.font_system.get_color(font_type)
        line_spacing = self.font_system.get_line_spacing(font_type)
        
        # Calculate optimal wrap width
        wrap_width = self.font_system.get_optimal_wrap_width(font_type, max_width)
        
        # Wrap text
        lines = textwrap.wrap(text, width=wrap_width)
        
        total_height = 0
        for line in lines:
            # Draw text with slight shadow for better readability
            self._draw_text_with_shadow(draw, line, (x, y + total_height), font, color)
            
            # Calculate line height
            bbox = font.getbbox(line)
            line_height = bbox[3] - bbox[1]
            total_height += int(line_height * line_spacing)
        
        return total_height
    
    def _draw_text_with_shadow(self, draw: ImageDraw.Draw, text: str, position: Tuple[int, int], 
                              font: ImageFont.FreeTypeFont, color: Tuple[int, int, int, int]):
        """Draw text with subtle shadow for better readability"""
        x, y = position
        
        # Draw shadow (slightly offset and semi-transparent)
        shadow_color = (0, 0, 0, 100)
        draw.text((x + 1, y + 1), text, font=font, fill=shadow_color)
        
        # Draw main text
        draw.text((x, y), text, font=font, fill=color)


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        overlay_text = state.get('overlay_text') or state.get('structured_data')
        print(f"Text overlay node processing - state: {overlay_text} type: {type(overlay_text)}")

        # Process structured data directly
        if isinstance(overlay_text, dict):
            headline = overlay_text.get('headline', '')
            subhead = overlay_text.get('subhead', '')
            bullets = overlay_text.get('bullets', [])
            structured_content = {
                'headline': headline,
                'subhead': subhead, 
                'bullets': bullets
            }
        else:
            structured_content = None

        width = int(state.get('image_width', 1080))
        height = int(state.get('image_height', 1080))
        background_url = state.get('image_url') or state.get('background_image_url')

        # Initialize font system
        font_system = FontSystem(width, height)
        text_renderer = TextRenderer(font_system)

        # Load or create base image
        base_image = _load_base_image(background_url, width, height)
        image_rgba = base_image.convert('RGBA')
        
        # Create overlay panel
        image_rgba = _create_overlay_panel(image_rgba, width, height)
        draw = ImageDraw.Draw(image_rgba)

        # Calculate layout parameters
        panel_margin = int(min(width, height) * 0.08)
        panel_top = int(height * 0.15)  # Start higher for better mobile layout
        panel_bottom = int(height * 0.85)
        content_width = width - (panel_margin * 2) - 60
        x = panel_margin + 30
        y = panel_top + 40

        # Render content with proper hierarchy
        if structured_content:
            # Render headline
            if structured_content.get('headline'):
                headline_height = text_renderer.render_text_block(
                    draw, structured_content['headline'], 'headline', (x, y), content_width
                )
                y += headline_height + 30

            # Render subhead
            if structured_content.get('subhead'):
                subhead_height = text_renderer.render_text_block(
                    draw, structured_content['subhead'], 'subhead', (x, y), content_width
                )
                y += subhead_height + 25

            # Render bullets
            if structured_content.get('bullets'):
                for bullet in structured_content['bullets']:
                    bullet_text = f"• {str(bullet)}"
                    bullet_height = text_renderer.render_text_block(
                        draw, bullet_text, 'bullet', (x, y), content_width
                    )
                    y += bullet_height + 15

        # Convert and encode final image
        output_image = image_rgba.convert('RGB')
        buffer = io.BytesIO()
        output_image.save(buffer, format='JPEG', quality=95)  # Higher quality for production
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


def _load_base_image(background_url: Optional[str], width: int, height: int) -> Image.Image:
    """Load or create base image"""
    base_image = None
    
    if background_url and isinstance(background_url, str) and background_url.startswith('http'):
        try:
            resp = requests.get(background_url, timeout=10)
            resp.raise_for_status()
            base_image = Image.open(io.BytesIO(resp.content)).convert('RGB')
        except Exception as e:
            print(f"Failed to load background image: {e}")
            base_image = None

    if base_image is None:
        # Create modern gradient background
        base_image = _create_gradient_background(width, height)
    
    return base_image


def _create_gradient_background(width: int, height: int) -> Image.Image:
    """Create a modern gradient background"""
    base_image = Image.new('RGB', (width, height), (255, 255, 255))
    
    for y in range(height):
        for x in range(width):
            progress = y / height
            if progress < 0.33:
                r = int(135 + (147 - 135) * (progress * 3))
                g = int(206 + (112 - 206) * (progress * 3))
                b = int(250 + (219 - 250) * (progress * 3))
            elif progress < 0.66:
                r = int(147 + (255 - 147) * ((progress - 0.33) * 3))
                g = int(112 + (182 - 112) * ((progress - 0.33) * 3))
                b = int(219 + (193 - 219) * ((progress - 0.33) * 3))
            else:
                r = int(255 + (255 - 255) * ((progress - 0.66) * 3))
                g = int(182 + (192 - 182) * ((progress - 0.66) * 3))
                b = int(193 + (203 - 193) * ((progress - 0.66) * 3))
            base_image.putpixel((x, y), (r, g, b))
    
    return base_image


def _create_overlay_panel(image_rgba: Image.Image, width: int, height: int) -> Image.Image:
    """Create overlay panel with modern styling"""
    overlay = Image.new('RGBA', image_rgba.size, (255, 255, 255, 0))
    draw_overlay = ImageDraw.Draw(overlay)
    
    panel_margin = int(min(width, height) * 0.08)
    panel_top = int(height * 0.15)
    panel_bottom = int(height * 0.85)
    
    # Create semi-transparent panel with rounded corners effect
    draw_overlay.rectangle(
        [(panel_margin, panel_top), (width - panel_margin, panel_bottom)],
        fill=(255, 255, 255, 220),  # Slightly more opaque for better readability
        outline=(255, 255, 255, 150),
        width=2
    )
    
    return Image.alpha_composite(image_rgba, overlay)