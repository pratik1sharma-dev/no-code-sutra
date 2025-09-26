from typing import Dict, Any, Tuple, Optional, List
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import textwrap
import os
import math
import random
from abc import ABC, abstractmethod
from ..contracts import TextOverlayInputV1, TextOverlayOutputV1

# Import the new Instagram Template Engine
try:
    from .instagram_templates import create_instagram_post_with_template, InstagramTemplateEngine
    TEMPLATES_AVAILABLE = True
    print("✅ Instagram Template Engine loaded successfully")
except ImportError as e:
    print(f"⚠️ Instagram Template Engine not available: {e}")
    TEMPLATES_AVAILABLE = False


class PlatformConfig:
    """Platform-specific configuration for different social media platforms"""
    
    def __init__(self, platform: str):
        self.platform = platform
        self.config = self._get_platform_config()
    
    def _get_platform_config(self) -> Dict[str, Any]:
        """Get platform-specific configuration"""
        configs = {
            'instagram': {
                'dimensions': (1080, 1080),
                'aspect_ratio': 'square',
                'font_sizes': {
                    'hero': 3.2,
                    'headline': 2.6,
                    'subhead': 1.8,
                    'body': 1.4,
                    'caption': 1.2,
                    'bullet': 1.5,
                    'quote': 2.2
                },
                'min_font_size': 28,
                'post_types': {
                    'single': {
                        'content_structure': ['headline', 'subhead', 'bullets'],
                        'max_bullets': 2,
                        'color_palettes': {
                            'modern': {
                                'primary': (59, 130, 246),    # Instagram Blue
                                'secondary': (139, 92, 246),  # Purple
                                'accent': (34, 197, 94),     # Green
                                'neutral': (107, 114, 128),  # Gray
                                'background': (249, 250, 251) # Light Gray
                            },
                            'professional': {
                                'primary': (17, 24, 39),     # Dark Blue
                                'secondary': (55, 65, 81),   # Dark Gray
                                'accent': (59, 130, 246),    # Blue
                                'neutral': (156, 163, 175),  # Light Gray
                                'background': (255, 255, 255) # White
                            },
                            'instagram_vibrant': {
                                'primary': (236, 72, 153),   # Instagram Pink
                                'secondary': (139, 92, 246), # Purple
                                'accent': (251, 146, 60),   # Orange
                                'neutral': (107, 114, 128), # Gray
                                'background': (255, 255, 255) # White
                            },
                            'instagram_minimal': {
                                'primary': (15, 15, 15),     # Black
                                'secondary': (45, 45, 45),   # Dark Gray
                                'accent': (59, 130, 246),    # Blue
                                'neutral': (156, 163, 175),  # Light Gray
                                'background': (249, 250, 251) # Off White
                            }
                        }
                    },
                    'carousel': {
                        'content_structure': ['headline', 'subhead', 'slides'],
                        'max_slides': 10,
                        'slide_structure': ['title', 'content', 'stats'],
                        'color_palettes': {
                            'modern': {
                                'primary': (59, 130, 246),    # Instagram Blue
                                'secondary': (139, 92, 246),  # Purple
                                'accent': (34, 197, 94),     # Green
                                'neutral': (107, 114, 128),  # Gray
                                'background': (249, 250, 251) # Light Gray
                            },
                            'instagram_vibrant': {
                                'primary': (236, 72, 153),   # Instagram Pink
                                'secondary': (139, 92, 246), # Purple
                                'accent': (251, 146, 60),   # Orange
                                'neutral': (107, 114, 128), # Gray
                                'background': (255, 255, 255) # White
                            },
                            'instagram_minimal': {
                                'primary': (15, 15, 15),     # Black
                                'secondary': (45, 45, 45),   # Dark Gray
                                'accent': (59, 130, 246),    # Blue
                                'neutral': (156, 163, 175),  # Light Gray
                                'background': (249, 250, 251) # Off White
                            }
                        }
                    },
                    'video_reel': {
                        'content_structure': ['headline', 'subhead', 'script', 'key_points'],
                        'max_key_points': 5,
                        'color_palettes': {
                            'modern': {
                                'primary': (59, 130, 246),
                                'secondary': (139, 92, 246),
                                'accent': (34, 197, 94),
                                'neutral': (107, 114, 128),
                                'background': (249, 250, 251)
                            }
                        }
                    },
                    'story': {
                        'content_structure': ['headline', 'content', 'call_to_action'],
                        'color_palettes': {
                            'modern': {
                                'primary': (59, 130, 246),
                                'secondary': (139, 92, 246),
                                'accent': (34, 197, 94),
                                'neutral': (107, 114, 128),
                                'background': (249, 250, 251)
                            }
                        }
                    }
                }
            },
            'linkedin': {
                'dimensions': (1200, 628),
                'aspect_ratio': 'landscape',
                'font_sizes': {
                    'hero': 2.8,
                    'headline': 2.4,
                    'subhead': 1.6,
                    'body': 1.3,
                    'caption': 1.1,
                    'bullet': 1.4,
                    'quote': 2.0
                },
                'min_font_size': 24,
                'content_structure': ['headline', 'subhead', 'bullets', 'quote'],
                'max_bullets': 4,
                'color_palettes': {
                    'professional': {
                        'primary': (0, 119, 181),
                        'secondary': (0, 0, 0),
                        'accent': (0, 119, 181),
                        'neutral': (102, 102, 102),
                        'background': (255, 255, 255)
                    }
                }
            },
            'twitter': {
                'dimensions': (1200, 675),
                'aspect_ratio': 'landscape',
                'font_sizes': {
                    'hero': 2.6,
                    'headline': 2.2,
                    'subhead': 1.5,
                    'body': 1.2,
                    'caption': 1.0,
                    'bullet': 1.3,
                    'quote': 1.8
                },
                'min_font_size': 22,
                'content_structure': ['headline', 'subhead', 'bullets'],
                'max_bullets': 3,
                'color_palettes': {
                    'twitter': {
                        'primary': (29, 161, 242),
                        'secondary': (20, 23, 26),
                        'accent': (29, 161, 242),
                        'neutral': (101, 119, 134),
                        'background': (255, 255, 255)
                    }
                }
            }
        }
        
        return configs.get(self.platform, configs['instagram'])


class ModernFontSystem:
    """Modern font system optimized for different platforms"""
    
    def __init__(self, image_width: int, image_height: int, platform: str = 'instagram'):
        self.image_width = image_width
        self.image_height = image_height
        self.platform = platform
        self.platform_config = PlatformConfig(platform)
        self.font_cache = {}
        
        # Platform-optimized font sizes
        self.base_size = max(20, min(image_width, image_height) // 35)
        
        # Get platform-specific font sizes
        platform_font_sizes = self.platform_config.config['font_sizes']
        self.font_sizes = {
            font_type: int(self.base_size * multiplier)
            for font_type, multiplier in platform_font_sizes.items()
        }
        
        # Ensure minimum readable sizes for platform
        min_font_size = self.platform_config.config['min_font_size']
        self.font_sizes = {k: max(v, min_font_size) for k, v in self.font_sizes.items()}
        
        # Instagram-optimized color schemes with more vibrant colors
        self.colors = {
            'hero': (59, 130, 246, 255),    # Instagram blue for hero
            'headline': (59, 130, 246, 255), # Instagram blue for headlines
            'subhead': (139, 92, 246, 255), # Purple for subheads
            'body': (45, 45, 45, 255),      # Dark gray for body
            'caption': (107, 114, 128, 255), # Medium gray for captions
            'bullet': (34, 197, 94, 255),   # Green for bullets
            'quote': (236, 72, 153, 255),   # Instagram pink for quotes
            'accent': (59, 130, 246, 255),  # Instagram blue
            'success': (34, 197, 94, 255),  # Green
            'warning': (251, 146, 60, 255), # Orange
            'error': (239, 68, 68, 255),    # Red
            'instagram_blue': (59, 130, 246, 255),
            'instagram_purple': (139, 92, 246, 255),
            'instagram_pink': (236, 72, 153, 255),
            'instagram_green': (34, 197, 94, 255),
            'instagram_orange': (251, 146, 60, 255)
        }
        
        # Platform-agnostic line spacing
        self.line_spacing = {
            'hero': 1.4,
            'headline': 1.3,
            'subhead': 1.25,
            'body': 1.2,
            'caption': 1.15,
            'bullet': 1.25,
            'quote': 1.35
        }
        
        # Initialize fonts
        self._initialize_fonts()
    
    def _initialize_fonts(self):
        """Initialize modern fonts with fallback system"""
        try:
            font_paths = self._get_modern_fonts()
            
            for font_type, size in self.font_sizes.items():
                font = self._load_best_font(font_paths, size)
                self.font_cache[font_type] = font
                
        except Exception as e:
            print(f"Font initialization warning: {e}")
            self._initialize_fallback_fonts()
    
    def _get_modern_fonts(self) -> list:
        """Get Instagram-optimized modern fonts with priority order"""
        font_paths = []
        
        # Instagram-optimized modern fonts (priority order)
        modern_fonts = [
            # Custom Instagram-style fonts (if available)
            "src/assets/fonts/Inter-Bold.ttf",
            "src/assets/fonts/Poppins-Bold.ttf", 
            "src/assets/fonts/Montserrat-Bold.ttf",
            "src/assets/fonts/Roboto-Bold.ttf",
            "src/assets/fonts/OpenSans-Bold.ttf",
            # System modern fonts (fallbacks)
            "/System/Library/Fonts/SF-Pro-Display-Bold.otf",
            "/System/Library/Fonts/SF-Pro-Display-Regular.otf",
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/Arial.ttf",
            # Linux modern fonts
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            # Windows modern fonts
            "C:/Windows/Fonts/calibri.ttf",
            "C:/Windows/Fonts/arial.ttf"
        ]
        
        for font_path in modern_fonts:
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
        avg_char_width = font.getbbox("M")[2]
        return max(10, int(max_width / avg_char_width))


class ModernTextRenderer:
    """Modern text renderer with platform-optimized styling"""
    
    def __init__(self, font_system: ModernFontSystem):
        self.font_system = font_system
    
    def render_text_block(self, draw: ImageDraw.Draw, text: str, font_type: str, 
                         position: Tuple[int, int], max_width: int, color: Optional[Tuple[int, int, int, int]] = None) -> int:
        """Render a block of text with modern styling and return height used"""
        if not text:
            return 0
        
        x, y = position
        font = self.font_system.get_font(font_type)
        if color is None:
            color = self.font_system.get_color(font_type)
        line_spacing = self.font_system.get_line_spacing(font_type)
        
        # Calculate optimal wrap width
        wrap_width = self.font_system.get_optimal_wrap_width(font_type, max_width)
        
        # Wrap text
        lines = textwrap.wrap(text, width=wrap_width)
        
        total_height = 0
        for line in lines:
            # Draw text with modern shadow for better readability
            self._draw_text_with_modern_shadow(draw, line, (x, y + total_height), font, color)
            
            # Calculate line height
            bbox = font.getbbox(line)
            line_height = bbox[3] - bbox[1]
            total_height += int(line_height * line_spacing)
        
        return total_height
    
    def _draw_text_with_modern_shadow(self, draw: ImageDraw.Draw, text: str, position: Tuple[int, int], 
                                     font: ImageFont.FreeTypeFont, color: Tuple[int, int, int, int]):
        """Draw text with advanced professional styling"""
        x, y = position
        
        # Advanced shadow system with color tinting
        shadow_colors = [
            (0, 0, 0, 60),   # Light shadow
            (0, 0, 0, 40),   # Very light shadow
            (0, 0, 0, 20)    # Subtle shadow
        ]
        
        shadow_offsets = [(2, 2), (1, 1), (0, 0)]
        
        # Draw layered shadows for professional depth
        for i, (offset, shadow_color) in enumerate(zip(shadow_offsets, shadow_colors)):
            draw.text((x + offset[0], y + offset[1]), text, font=font, fill=shadow_color)
        
        # Draw main text with professional color
        draw.text((x, y), text, font=font, fill=color)
        
        # Add subtle text glow for premium feel
        glow_color = (*color[:3], 30)  # Same color with low opacity
        draw.text((x - 1, y - 1), text, font=font, fill=glow_color)
        draw.text((x + 1, y + 1), text, font=font, fill=glow_color)


class PlatformDesignSystem:
    """Advanced professional design system with dynamic layouts"""
    
    def __init__(self, width: int, height: int, platform: str = 'instagram'):
        self.width = width
        self.height = height
        self.platform = platform
        self.platform_config = PlatformConfig(platform)
        
        # Get platform-specific color palettes - handle different config structures
        config = self.platform_config.config
        if 'post_types' in config and 'single' in config['post_types']:
            # New structure with post types
            self.color_palettes = config['post_types']['single'].get('color_palettes', {})
        else:
            # Old structure with direct color_palettes
            self.color_palettes = config.get('color_palettes', {})
        
        # Select a random palette for variety, with fallback
        if self.color_palettes:
            self.current_palette = random.choice(list(self.color_palettes.values()))
        else:
            # Fallback palette
            self.current_palette = {
                'primary': (59, 130, 246),
                'secondary': (139, 92, 246),
                'accent': (34, 197, 94),
                'neutral': (107, 114, 128),
                'background': (249, 250, 251)
            }
        
        # Dynamic layout templates
        self.layout_templates = {
            'hero': {'position': 'center', 'size': 'large', 'emphasis': 'bold'},
            'feature': {'position': 'left', 'size': 'medium', 'emphasis': 'normal'},
            'minimal': {'position': 'center', 'size': 'small', 'emphasis': 'subtle'},
            'dynamic': {'position': 'asymmetric', 'size': 'variable', 'emphasis': 'mixed'}
        }
        
        # Professional design elements
        self.design_elements = {
            'geometric_shapes': True,
            'gradient_overlays': True,
            'texture_patterns': True,
            'dynamic_spacing': True
        }
    
    def create_modern_card(self, image: Image.Image, content_rect: Tuple[int, int, int, int]) -> Image.Image:
        """Create advanced professional card with dynamic elements"""
        # Create a new image with transparency
        card_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(card_image)
        
        x1, y1, x2, y2 = content_rect
        
        # Create dramatic gradient background instead of plain white
        self._create_dramatic_gradient_background(card_image, content_rect)
        
        # Add professional accent elements
        self._add_accent_elements(card_image, content_rect)
        
        # Add geometric design elements for visual interest
        self._add_geometric_elements(card_image, content_rect)
        
        # Add subtle texture pattern for depth
        self._add_texture_pattern(card_image, content_rect)
        
        # Add subtle professional shadow
        self._add_professional_shadow(card_image, content_rect)
        
        return card_image
    
    def _add_instagram_gradient_overlay(self, image: Image.Image, rect: Tuple[int, int, int, int]):
        """Add Instagram-style gradient overlay for modern look"""
        x1, y1, x2, y2 = rect
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Instagram-style gradient from top to bottom
        for y in range(y1, y2):
            progress = (y - y1) / (y2 - y1)
            # Instagram-style gradient with more depth
            alpha = int(30 * (1 - progress))  # Stronger fade for Instagram
            overlay_draw.line([(x1, y), (x2, y)], fill=(255, 255, 255, alpha))
        
        # Add Instagram-style color gradient
        for y in range(y1, y2):
            progress = (y - y1) / (y2 - y1)
            # Instagram blue gradient
            blue_alpha = int(15 * progress)  # Blue tint at bottom
            overlay_draw.line([(x1, y), (x2, y)], fill=(59, 130, 246, blue_alpha))
        
        # Composite the gradient
        image.paste(overlay, (0, 0), overlay)
    
    def _create_dramatic_gradient_background(self, image: Image.Image, rect: Tuple[int, int, int, int]):
        """Create dramatic gradient background instead of plain white"""
        x1, y1, x2, y2 = rect
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Create dramatic gradient from top-left to bottom-right
        for y in range(y1, y2):
            for x in range(x1, x2):
                # Calculate gradient progress
                progress_x = (x - x1) / (x2 - x1)
                progress_y = (y - y1) / (y2 - y1)
                
                # Create dramatic color transition
                # Start with light color, transition to darker
                r = int(255 - (progress_x + progress_y) * 30)
                g = int(255 - (progress_x + progress_y) * 25)
                b = int(255 - (progress_x + progress_y) * 20)
                
                # Add subtle color tint based on palette
                if self.current_palette.get('primary'):
                    primary_r, primary_g, primary_b = self.current_palette['primary']
                    r = int(r + primary_r * 0.05)
                    g = int(g + primary_g * 0.05)
                    b = int(b + primary_b * 0.05)
                
                # Ensure values are in valid range
                r = max(0, min(255, r))
                g = max(0, min(255, g))
                b = max(0, min(255, b))
                
                overlay_draw.point((x, y), fill=(r, g, b, 240))
        
        # Composite the gradient
        image.paste(overlay, (0, 0), overlay)
    
    def _add_accent_elements(self, image: Image.Image, rect: Tuple[int, int, int, int]):
        """Add professional accent elements"""
        x1, y1, x2, y2 = rect
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Add subtle accent line at the top
        accent_color = self.current_palette.get('primary', (59, 130, 246))
        line_height = 4
        overlay_draw.rectangle([x1, y1, x2, y1 + line_height], 
                              fill=(*accent_color, 180))
        
        # Add subtle corner accent
        corner_size = 20
        overlay_draw.rectangle([x1, y1, x1 + corner_size, y1 + corner_size], 
                              fill=(*accent_color, 60))
        
        # Composite the accents
        image.paste(overlay, (0, 0), overlay)
    
    def _add_professional_shadow(self, image: Image.Image, rect: Tuple[int, int, int, int]):
        """Add professional shadow for depth"""
        x1, y1, x2, y2 = rect
        shadow = Image.new('RGBA', image.size, (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow)
        
        # Professional shadow (subtle and elegant)
        shadow_rects = [
            ((x1 + 2, y1 + 2, x2 + 2, y2 + 2), (0, 0, 0, 40)),   # Light shadow
            ((x1 + 1, y1 + 1, x2 + 1, y2 + 1), (0, 0, 0, 20))    # Very light shadow
        ]
        
        for shadow_rect, shadow_color in shadow_rects:
            shadow_draw.rectangle(shadow_rect, fill=shadow_color)
        
        # Composite the shadow behind the card
        image.paste(shadow, (0, 0), shadow)
    
    def _add_geometric_elements(self, image: Image.Image, rect: Tuple[int, int, int, int]):
        """Add professional geometric design elements"""
        x1, y1, x2, y2 = rect
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Add geometric shapes for visual interest
        primary_color = self.current_palette.get('primary', (59, 130, 246))
        secondary_color = self.current_palette.get('secondary', (139, 92, 246))
        
        # Top-right corner triangle
        triangle_points = [(x2 - 40, y1), (x2, y1), (x2, y1 + 40)]
        overlay_draw.polygon(triangle_points, fill=(*primary_color, 30))
        
        # Bottom-left corner circle
        circle_center = (x1 + 30, y2 - 30)
        circle_radius = 15
        overlay_draw.ellipse([circle_center[0] - circle_radius, circle_center[1] - circle_radius,
                             circle_center[0] + circle_radius, circle_center[1] + circle_radius],
                            fill=(*secondary_color, 20))
        
        # Diagonal accent line
        overlay_draw.line([(x1 + 20, y1 + 20), (x1 + 80, y1 + 80)], 
                         fill=(*primary_color, 40), width=3)
        
        # Composite the geometric elements
        image.paste(overlay, (0, 0), overlay)
    
    def _add_texture_pattern(self, image: Image.Image, rect: Tuple[int, int, int, int]):
        """Add subtle texture pattern for depth"""
        x1, y1, x2, y2 = rect
        overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        # Create subtle dot pattern
        dot_spacing = 20
        dot_size = 1
        
        for y in range(y1, y2, dot_spacing):
            for x in range(x1, x2, dot_spacing):
                # Random opacity for natural look
                opacity = random.randint(5, 15)
                overlay_draw.ellipse([x, y, x + dot_size, y + dot_size], 
                                   fill=(255, 255, 255, opacity))
        
        # Composite the texture
        image.paste(overlay, (0, 0), overlay)
    
    def get_dynamic_layout(self, content_type: str, content_length: int) -> Dict[str, Any]:
        """Get dynamic layout based on content type and length"""
        if content_length < 50:
            return self.layout_templates['minimal']
        elif content_length < 150:
            return self.layout_templates['feature']
        elif content_length < 300:
            return self.layout_templates['hero']
        else:
            return self.layout_templates['dynamic']
    
    def create_accent_element(self, image: Image.Image, position: Tuple[int, int], size: int) -> Image.Image:
        """Create accent elements like dots, lines, or shapes"""
        accent_image = Image.new('RGBA', image.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(accent_image)
        
        x, y = position
        
        # Create a modern accent dot
        dot_color = (*self.current_palette['primary'], 200)
        draw.ellipse([x, y, x + size, y + size], fill=dot_color)
        
        return accent_image


class ContentStructureConverter:
    """Platform-agnostic content structure converter"""
    
    def __init__(self, platform: str = 'instagram', post_type: str = 'single'):
        self.platform = platform
        self.post_type = post_type
        self.platform_config = PlatformConfig(platform)
    
    def convert_to_platform_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert any JSON structure to platform-optimized format.
        Focus on the most impactful elements that fit well on the platform.
        """
        result = {}
        
        # Get post type specific configuration
        post_config = self.platform_config.config['post_types'].get(self.post_type, 
                                                                   self.platform_config.config['post_types']['single'])
        content_structure = post_config['content_structure']
        
        if self.post_type == 'carousel':
            # Handle carousel content structure
            result = self._convert_carousel_content(data, content_structure)
        elif self.post_type == 'video_reel':
            # Handle video reel content structure
            result = self._convert_video_reel_content(data, content_structure)
        elif self.post_type == 'story':
            # Handle story content structure
            result = self._convert_story_content(data, content_structure)
        else:
            # Handle single post content structure
            result = self._convert_single_content(data, content_structure, post_config)
        
        return result
    
    def _convert_single_content(self, data: Dict[str, Any], content_structure: List[str], post_config: Dict[str, Any]) -> Dict[str, Any]:
        """Convert data for single post structure"""
        result = {}
        max_bullets = post_config.get('max_bullets', 2)
        
        for content_type in content_structure:
            if content_type == 'headline':
                result['headline'] = self._extract_text(data, ['headline', 'title', 'main_title', 'hero'])
            elif content_type == 'subhead':
                result['subhead'] = self._extract_text(data, ['subhead', 'subtitle', 'description', 'summary'])
            elif content_type == 'bullets':
                bullets = self._extract_list(data, ['bullets', 'bullet_points', 'key_points', 'tips', 'insights'])
                result['bullets'] = bullets[:max_bullets] if bullets else []
            elif content_type == 'quote':
                result['quote'] = self._extract_text(data, ['quote', 'testimonial', 'highlight'])
        
        # Add caption and hashtags if available
        result['caption'] = self._extract_text(data, ['caption', 'description', 'summary'])
        result['hashtags'] = self._extract_list(data, ['hashtags', 'tags'])
        
        return result
    
    def _convert_carousel_content(self, data: Dict[str, Any], content_structure: List[str]) -> Dict[str, Any]:
        """Convert data for carousel structure"""
        result = {}
        
        # Extract main carousel content
        for content_type in content_structure:
            if content_type == 'headline':
                result['headline'] = self._extract_text(data, ['headline', 'title', 'main_title'])
            elif content_type == 'subhead':
                result['subhead'] = self._extract_text(data, ['subhead', 'subtitle', 'description'])
            elif content_type == 'slides':
                slides = self._extract_slides(data)
                result['slides'] = slides
        
        # Add caption and hashtags
        result['caption'] = self._extract_text(data, ['caption', 'description'])
        result['hashtags'] = self._extract_list(data, ['hashtags', 'tags'])
        
        return result
    
    def _convert_video_reel_content(self, data: Dict[str, Any], content_structure: List[str]) -> Dict[str, Any]:
        """Convert data for video reel structure"""
        result = {}
        
        for content_type in content_structure:
            if content_type == 'headline':
                result['headline'] = self._extract_text(data, ['headline', 'title', 'main_title'])
            elif content_type == 'subhead':
                result['subhead'] = self._extract_text(data, ['subhead', 'subtitle', 'description'])
            elif content_type == 'script':
                result['script'] = self._extract_text(data, ['script', 'content', 'description'])
            elif content_type == 'key_points':
                points = self._extract_list(data, ['key_points', 'talking_points', 'main_points', 'bullets'])
                result['key_points'] = points[:5] if points else []
        
        # Add caption and hashtags
        result['caption'] = self._extract_text(data, ['caption', 'description'])
        result['hashtags'] = self._extract_list(data, ['hashtags', 'tags'])
        
        return result
    
    def _convert_story_content(self, data: Dict[str, Any], content_structure: List[str]) -> Dict[str, Any]:
        """Convert data for story structure"""
        result = {}
        
        for content_type in content_structure:
            if content_type == 'headline':
                result['headline'] = self._extract_text(data, ['headline', 'title'])
            elif content_type == 'content':
                result['content'] = self._extract_text(data, ['content', 'description', 'text'])
            elif content_type == 'call_to_action':
                result['call_to_action'] = self._extract_text(data, ['call_to_action', 'cta', 'action'])
        
        # Add caption and hashtags
        result['caption'] = self._extract_text(data, ['caption', 'description'])
        result['hashtags'] = self._extract_list(data, ['hashtags', 'tags'])
        
        return result
    
    def _extract_slides(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract slides from data"""
        slides = []
        
        # Try to get slides directly
        if 'slides' in data and isinstance(data['slides'], list):
            slides = data['slides']
        elif 'bullet_points' in data and isinstance(data['bullet_points'], list):
            # Convert bullet points to slides
            for i, bullet in enumerate(data['bullet_points']):
                slides.append({
                    'title': f"Point {i+1}",
                    'content': str(bullet),
                    'stats': ''
                })
        elif 'key_points' in data and isinstance(data['key_points'], list):
            # Convert key points to slides
            for i, point in enumerate(data['key_points']):
                slides.append({
                    'title': f"Key Point {i+1}",
                    'content': str(point),
                    'stats': ''
                })
        
        # Limit slides to max 10
        return slides[:10]
    
    def _extract_text(self, data: Dict[str, Any], possible_keys: List[str]) -> str:
        """Extract text from data using possible keys"""
        for key in possible_keys:
            if key in data and data[key]:
                text = str(data[key]).strip()
                if text:
                    return text
        return ""
    
    def _extract_list(self, data: Dict[str, Any], possible_keys: List[str]) -> List[str]:
        """Extract list from data using possible keys"""
        for key in possible_keys:
            if key in data and isinstance(data[key], list):
                return [str(item).strip() for item in data[key] if item]
        return []


class SmartTextPlacement:
    """Smart text placement system that analyzes image content and places text optimally"""
    
    def __init__(self, image: Image.Image):
        self.image = image
        self.width = image.width
        self.height = image.height
        self.zone_scores = self._analyze_image_zones()
    
    def _analyze_image_zones(self) -> Dict[str, Dict[str, float]]:
        """Analyze different zones of the image for text placement suitability"""
        
        zones = {
            'top': (0, 0, self.width, int(self.height * 0.2)),      # Top 20%
            'bottom': (0, int(self.height * 0.75), self.width, self.height),  # Bottom 25%
            'left': (0, 0, int(self.width * 0.3), self.height),     # Left 30%
            'right': (int(self.width * 0.7), 0, self.width, self.height),  # Right 30%
            'center': (int(self.width * 0.3), int(self.height * 0.3), 
                      int(self.width * 0.7), int(self.height * 0.7))     # Center 40x40%
        }
        
        zone_scores = {}
        
        for zone_name, (x1, y1, x2, y2) in zones.items():
            # Crop the zone
            zone_image = self.image.crop((x1, y1, x2, y2))
            
            # Calculate scores for this zone
            brightness_score = self._calculate_brightness(zone_image)
            contrast_score = self._calculate_contrast(zone_image)
            busyness_score = self._calculate_busyness(zone_image)
            
            zone_scores[zone_name] = {
                'brightness': brightness_score,
                'contrast': contrast_score, 
                'busyness': busyness_score,
                'readability': self._calculate_readability(brightness_score, contrast_score, busyness_score),
                'coordinates': (x1, y1, x2, y2)
            }
        
        return zone_scores
    
    def _calculate_brightness(self, image: Image.Image) -> float:
        """Calculate average brightness (0-255)"""
        # Convert to grayscale
        gray = image.convert('L')
        # Get pixel data
        pixels = list(gray.getdata())
        # Calculate average brightness
        return sum(pixels) / len(pixels)
    
    def _calculate_contrast(self, image: Image.Image) -> float:
        """Calculate contrast (standard deviation of brightness)"""
        gray = image.convert('L')
        pixels = list(gray.getdata())
        mean = sum(pixels) / len(pixels)
        variance = sum((p - mean) ** 2 for p in pixels) / len(pixels)
        return variance ** 0.5
    
    def _calculate_busyness(self, image: Image.Image) -> float:
        """Calculate how 'busy' an area is (edge density)"""
        # Simple edge detection using brightness differences
        gray = image.convert('L')
        pixels = list(gray.getdata())
        width, height = gray.size
        
        edge_count = 0
        total_pixels = 0
        
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                idx = y * width + x
                current = pixels[idx]
                
                # Check horizontal and vertical neighbors
                neighbors = [
                    pixels[idx - 1],  # left
                    pixels[idx + 1],  # right
                    pixels[idx - width],  # top
                    pixels[idx + width]   # bottom
                ]
                
                        # Count significant brightness differences
                for neighbor in neighbors:
                    if abs(current - neighbor) > 30:  # Threshold for edge detection
                        edge_count += 1
                
                total_pixels += 1
        
        # Return edge density as busyness score
        return (edge_count / (total_pixels * 4)) * 100 if total_pixels > 0 else 0
    
    def _calculate_readability(self, brightness: float, contrast: float, busyness: float) -> float:
        """Calculate overall readability score (0-100)"""
        # Optimal brightness: 100-200 (not too dark, not too bright)
        brightness_score = max(0, 100 - abs(brightness - 150) / 1.5)
        
        # Higher contrast = better readability
        contrast_score = min(contrast / 2, 100)
        
        # Lower busyness = better readability  
        busyness_score = max(100 - busyness, 0)
        
        # Weighted average
        return (brightness_score * 0.4 + contrast_score * 0.4 + busyness_score * 0.2)
    
    def _get_zone_size(self, zone_name: str) -> int:
        """Calculate the area of a zone in pixels"""
        zone_coords = {
            'top': (0, 0, self.width, int(self.height * 0.2)),
            'bottom': (0, int(self.height * 0.75), self.width, self.height),
            'left': (0, 0, int(self.width * 0.3), self.height),
            'right': (int(self.width * 0.7), 0, self.width, self.height),
            'center': (int(self.width * 0.3), int(self.height * 0.3), 
                      int(self.width * 0.7), int(self.height * 0.7))
        }
        
        x1, y1, x2, y2 = zone_coords[zone_name]
        return (x2 - x1) * (y2 - y1)
    
    def select_best_zone(self, content_type: str, content_length: int) -> Tuple[str, Dict[str, Any]]:
        """Select the best zone based on content type and image analysis"""
        
        # Content type preferences
        content_preferences = {
            'headline': ['top', 'center', 'left', 'right', 'bottom'],
            'subhead': ['top', 'center', 'left', 'right', 'bottom'], 
            'bullets': ['bottom', 'left', 'right', 'center', 'top'],
            'quote': ['left', 'right', 'center', 'top', 'bottom'],
            'caption': ['bottom', 'left', 'right', 'center', 'top']
        }
        
        # Get preferred zones for this content type
        preferred_zones = content_preferences.get(content_type, ['center', 'top', 'bottom'])
        
        # Score each preferred zone
        zone_rankings = []
        
        for zone_name in preferred_zones:
            if zone_name in self.zone_scores:
                score = self.zone_scores[zone_name]['readability']
                
                # Adjust score based on content length
                if content_length > 100:  # Long content
                    # Prefer larger zones
                    zone_size = self._get_zone_size(zone_name)
                    size_bonus = min(zone_size / 1000, 20)  # Max 20 point bonus
                    score += size_bonus
                elif content_length < 30:  # Short content
                    # Prefer center zones for impact
                    if zone_name == 'center':
                        score += 15
                
                zone_rankings.append((zone_name, score))
        
        # Sort by score (highest first)
        zone_rankings.sort(key=lambda x: x[1], reverse=True)
        
        # Return best zone and its data
        best_zone = zone_rankings[0][0] if zone_rankings else 'center'
        return best_zone, self.zone_scores[best_zone]
    
    def adapt_text_style(self, zone_name: str) -> Dict[str, Any]:
        """Adapt text styling based on zone characteristics"""
        
        zone_data = self.zone_scores[zone_name]
        brightness = zone_data['brightness']
        contrast = zone_data['contrast']
        
        # Choose text color based on background brightness
        if brightness > 150:  # Light background
            text_color = (0, 0, 0, 255)  # Black text
            bg_opacity = 0.8  # More opaque background
        else:  # Dark background  
            text_color = (255, 255, 255, 255)  # White text
            bg_opacity = 0.6  # Less opaque background
        
        # Adjust shadow intensity based on contrast
        shadow_intensity = min(contrast / 50, 1.0)  # Normalize to 0-1
        
        return {
            'text_color': text_color,
            'background_opacity': bg_opacity,
            'shadow_intensity': shadow_intensity,
            'zone_coordinates': zone_data['coordinates']
        }

    def get_optimal_text_area(self, zone_name: str, content_length: int) -> Tuple[int, int, int, int]:
        """Get optimal text area within the selected zone"""
        
        zone_data = self.zone_scores[zone_name]
        x1, y1, x2, y2 = zone_data['coordinates']
        
        # Calculate optimal text area based on content length
        if content_length < 50:  # Short content
            # Use smaller area for better visual balance
            margin_x = int((x2 - x1) * 0.1)
            margin_y = int((y2 - y1) * 0.1)
        elif content_length < 150:  # Medium content
            margin_x = int((x2 - x1) * 0.15)
            margin_y = int((y2 - y1) * 0.15)
        else:  # Long content
            margin_x = int((x2 - x1) * 0.2)
            margin_y = int((y2 - y1) * 0.2)
        
        return (x1 + margin_x, y1 + margin_y, x2 - margin_x, y2 - margin_y)


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Validate input using the contract
        validated_input = TextOverlayInputV1(**state)
        overlay_text = validated_input.structured_data
        
        # DEBUG: Show exactly what text we're going to overlay
        print(f"🔍 TEXT OVERLAY DEBUG - Raw overlay_text: {overlay_text}")
        print(f"🔍 TEXT OVERLAY DEBUG - Type: {type(overlay_text)}")
        
        if isinstance(overlay_text, dict):
            print(f"🔍 TEXT OVERLAY DEBUG - Dict keys: {list(overlay_text.keys())}")
            for key, value in overlay_text.items():
                if isinstance(value, str):
                    print(f"🔍 TEXT OVERLAY DEBUG - {key}: '{value}' (length: {len(value)})")
                elif isinstance(value, list):
                    print(f"🔍 TEXT OVERLAY DEBUG - {key}: {len(value)} items")
                    for i, item in enumerate(value[:3]):  # Show first 3 items
                        print(f"🔍 TEXT OVERLAY DEBUG -   [{i}]: '{item}' (length: {len(str(item))})")
                else:
                    print(f"🔍 TEXT OVERLAY DEBUG - {key}: {type(value)} = {value}")
        else:
            print(f"🔍 TEXT OVERLAY DEBUG - String content: '{overlay_text}' (length: {len(str(overlay_text))})")
        
        # NEW: Priority order - Instagram Templates > Canva > Smart Placement
        if TEMPLATES_AVAILABLE and validated_input.use_instagram_template:
            print(f"🎨 Using Instagram Template Engine (template: {validated_input.instagram_template_name or 'auto-select'})")
            return generate_instagram_template_overlay(state, overlay_text, validated_input.platform, validated_input.post_type)
        elif validated_input.canva_template_id and validated_input.use_canva_template:
            print(f"🎨 Using Canva template: {validated_input.canva_template_id}")
            return generate_canva_template_overlay(state, overlay_text, validated_input.platform, validated_input.post_type)
        
        # Auto-detect post type from content structure
        if isinstance(overlay_text, dict):
            if 'slides' in overlay_text and isinstance(overlay_text['slides'], list) and len(overlay_text['slides']) > 1:
                validated_input.post_type = 'carousel'
                print(f"🎯 Auto-detected carousel post type from slides array ({len(overlay_text['slides'])} slides)")
            elif 'script' in overlay_text or 'key_points' in overlay_text:
                validated_input.post_type = 'video_reel'
                print(f"🎯 Auto-detected video_reel post type from content structure")
            elif 'call_to_action' in overlay_text:
                validated_input.post_type = 'story'
                print(f"🎯 Auto-detected story post type from content structure")
        
        print(f"Text overlay - Platform: {validated_input.platform}, Post Type: {validated_input.post_type}")

        # Process structured data intelligently for any JSON structure
        if isinstance(overlay_text, dict):
            content_converter = ContentStructureConverter(validated_input.platform, validated_input.post_type)
            structured_content = content_converter.convert_to_platform_structure(overlay_text)
        else:
            structured_content = None

        # Route to appropriate rendering function based on post type
        if validated_input.post_type == 'carousel':
            return generate_carousel_overlay(state, structured_content, validated_input.platform)
        elif validated_input.post_type == 'video_reel':
            return generate_video_reel_overlay(state, structured_content, validated_input.platform)
        elif validated_input.post_type == 'story':
            return generate_story_overlay(state, structured_content, validated_input.platform)
        else:
            return generate_single_overlay(state, structured_content, validated_input.platform, validated_input.post_type)
            
    except Exception as e:
        print(f"Error in text overlay node: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state


def generate_single_overlay(state: Dict[str, Any], structured_content: Dict[str, Any], platform: str, post_type: str = 'single') -> Dict[str, Any]:
    """Generate single image overlay (existing logic)"""
    try:
        width = int(state.get('image_width', 1080))
        height = int(state.get('image_height', 1080))
        background_url = state.get('image_url') or state.get('background_image_url')
        
        print(f"Text overlay - Background URL: {background_url}")

        # Initialize modern systems with platform support
        font_system = ModernFontSystem(width, height, platform)
        text_renderer = ModernTextRenderer(font_system)
        design_system = PlatformDesignSystem(width, height, platform)

        # Load or create base image
        base_image = _load_modern_background(background_url, width, height)
        image_rgba = base_image.convert('RGBA')
        
        # Apply smart text placement instead of fixed layout
        # This analyzes the image and places text in optimal zones
        final_image = _apply_smart_text_placement(image_rgba, structured_content, design_system)
        
        # Convert to base64 for return
        buffer = io.BytesIO()
        final_image.save(buffer, format='PNG')
        image_data = buffer.getvalue()
        image_data_url = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
        
        # Structure the output using the contract
        output = TextOverlayOutputV1(
            image_url=image_data_url,
            image_data_url=image_data_url,
            platform_used=platform,
            post_type=post_type,
            timestamp=datetime.now().isoformat()
        )
        return output.dict()
        
    except Exception as e:
        print(f"Error in single overlay generation: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state


def generate_carousel_overlay(state: Dict[str, Any], structured_content: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Generate carousel overlay with multiple slides"""
    try:
        slides_data = structured_content.get('slides', [])
        print(f"🎨 Starting carousel overlay generation...")
        print(f"🎨 Found {len(slides_data)} slides to process")
        
        if not slides_data:
            print(f"🎨 No slides found, falling back to single overlay")
            # Fallback to single overlay if no slides
            return generate_single_overlay(state, structured_content, platform)
        
        generated_slides = []
        
        for i, slide in enumerate(slides_data):
            print(f"🎨 Generating slide {i+1}/{len(slides_data)}...")
            print(f"🎨 Slide {i+1} data: {slide}")
            
            # Create slide-specific state
            slide_state = state.copy()
            slide_state['slide_index'] = i
            slide_state['slide_data'] = slide
            
            # Generate single slide image
            slide_image = generate_single_slide(slide_state, slide, platform)
            generated_slides.append(slide_image)
            
            print(f"✅ Slide {i+1} generated successfully")
        
        print(f"🎯 Carousel generation summary:")
        print(f"🎯 Total slides generated: {len(generated_slides)}")
        
        # Structure the output using the contract
        output = TextOverlayOutputV1(
            carousel_images=generated_slides,
            platform_used=platform,
            post_type='carousel',
            timestamp=datetime.now().isoformat()
        )
        return output.dict()
        
    except Exception as e:
        print(f"❌ Error in carousel overlay generation: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state


def generate_single_slide(state: Dict[str, Any], slide_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Generate a single slide for carousel with slide-specific background"""
    try:
        width = int(state.get('image_width', 1080))
        height = int(state.get('image_height', 1080))
        
        # Get slide-specific background image
        background_url = _get_slide_specific_background(slide_data, state)
        
        print(f"🎨 Slide {state.get('slide_index', 0) + 1}: Using background from search terms: {slide_data.get('image_search_terms', [])}")
        
        # Initialize systems
        font_system = ModernFontSystem(width, height, platform)
        text_renderer = ModernTextRenderer(font_system)
        design_system = PlatformDesignSystem(width, height, platform)

        # Load base image
        base_image = _load_modern_background(background_url, width, height)
        image_rgba = base_image.convert('RGBA')
        
        # Apply smart text placement for carousel slides too
        final_image = _apply_smart_text_placement(image_rgba, slide_data, design_system)
        
        # Convert and encode
        output_image = final_image.convert('RGB')
        buffer = io.BytesIO()
        output_image.save(buffer, format='JPEG', quality=95)
        encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
        data_url = f"data:image/jpeg;base64,{encoded}"

        return {
            'slide_index': state.get('slide_index', 0),
            'image_data_url': data_url,
            'slide_data': slide_data,
            'smart_placement_used': True
        }
        
    except Exception as e:
        print(f"Error in single slide generation: {e}")
        return {
            'slide_index': state.get('slide_index', 0),
            'error': str(e)
        }


def generate_video_reel_overlay(state: Dict[str, Any], structured_content: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Generate video reel overlay (placeholder for now)"""
    # For now, generate a single image with video reel content
    return generate_single_overlay(state, structured_content, platform)


def generate_story_overlay(state: Dict[str, Any], structured_content: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Generate story overlay (placeholder for now)"""
    # For now, generate a single image with story content
    return generate_single_overlay(state, structured_content, platform)


def _load_modern_background(background_url: Optional[str], width: int, height: int) -> Image.Image:
    """Load or create modern background"""
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
        # Create modern Instagram-style background
        base_image = _create_modern_instagram_background(width, height)
    
    return base_image


def _get_slide_specific_background(slide_data: Dict[str, Any], state: Dict[str, Any]) -> str:
    """Get slide-specific background image using image_search_terms"""
    try:
        # Get image search terms from slide data
        search_terms = slide_data.get('image_search_terms', [])
        
        if not search_terms:
            # Fallback to generic background
            print(f"⚠️ No image_search_terms found, using fallback background")
            return state.get('image_url') or state.get('background_image_url') or None
        
        # Create search query from terms
        search_query = ' '.join(search_terms[:3])  # Use top 3 terms
        print(f"🔍 Searching for slide background: {search_query}")
        
        # Use existing image fetcher to get background
        from .image_generator import DynamicImageFetcher
        image_fetcher = DynamicImageFetcher()
        
        # Create content dict for image fetcher
        content = {
            'headline': slide_data.get('title', ''),
            'subhead': slide_data.get('content', ''),
            'caption': f"{slide_data.get('title', '')} {slide_data.get('content', '')}"
        }
        
        # Override keywords with slide-specific search terms
        content['_custom_keywords'] = search_terms
        
        # Get background image
        background_url = image_fetcher.fetch_relevant_image(content)
        
        if background_url:
            print(f"✅ Found slide-specific background: {background_url}")
            return background_url
        else:
            print(f"⚠️ Failed to find slide-specific background, using fallback")
            return state.get('image_url') or state.get('background_image_url') or None
            
    except Exception as e:
        print(f"❌ Error getting slide-specific background: {e}")
        return state.get('image_url') or state.get('background_image_url') or None


def _create_modern_instagram_background(width: int, height: int) -> Image.Image:
    """Create a modern Instagram-style background"""
    # Create base with modern gradient
    base_image = Image.new('RGB', (width, height), (255, 255, 255))
    
    # Create modern gradient overlay
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Modern gradient from top-left to bottom-right
    for y in range(height):
        for x in range(width):
            # Calculate gradient based on position
            progress_x = x / width
            progress_y = y / height
            
            # Modern color palette
            r = int(240 + (245 - 240) * progress_x)
            g = int(245 + (250 - 245) * progress_y)
            b = int(250 + (255 - 250) * (progress_x + progress_y) / 2)
            
            # Add subtle variation
            variation = int(10 * math.sin(progress_x * 3.14) * math.cos(progress_y * 3.14))
            r = max(0, min(255, r + variation))
            g = max(0, min(255, g + variation))
            b = max(0, min(255, b + variation))
            
            overlay_draw.point((x, y), fill=(r, g, b, 255))
    
    # Composite the gradient
    base_image.paste(overlay, (0, 0), overlay)
    
    return base_image


def _create_modern_platform_layout(image_rgba: Image.Image, width: int, height: int, design_system: PlatformDesignSystem, platform: str) -> Image.Image:
    """Create dramatic, professional layout with enhanced styling"""
    # Create dramatic card overlay with better proportions
    margin = int(min(width, height) * 0.08)  # Larger margins for drama
    card_top = int(height * 0.15)    # Start higher for impact
    card_bottom = int(height * 0.85) # End higher for balance
    
    # Create dramatic card
    card_image = design_system.create_modern_card(image_rgba, (margin, card_top, width - margin, card_bottom))
    
    # Composite the card
    result = Image.alpha_composite(image_rgba, card_image)
    
    return result


def _apply_smart_text_placement(image: Image.Image, structured_content: Dict[str, Any], 
                               design_system: PlatformDesignSystem) -> Image.Image:
    """Apply smart text placement with intelligent styling and minimal overlays"""
    
    # Initialize smart placement system
    smart_placement = SmartTextPlacement(image)
    
    # Create a copy for text overlay
    result_image = image.copy()
    draw = ImageDraw.Draw(result_image)
    
    # Get platform configuration
    platform_config = PlatformConfig('instagram')
    font_system = ModernFontSystem(image.width, image.height, 'instagram')
    text_renderer = ModernTextRenderer(font_system)
    
    # Process each content type with smart placement
    content_structure = platform_config.config['post_types']['single']['content_structure']
    
    for content_type in content_structure:
        if content_type in structured_content and structured_content[content_type]:
            content = structured_content[content_type]
            content_length = len(str(content))
            
            # Select best zone for this content
            zone_name, zone_data = smart_placement.select_best_zone(content_type, content_length)
            
            # Get optimal text area within the zone
            text_area = smart_placement.get_optimal_text_area(zone_name, content_length)
            
            # Get intelligent styling based on image colors
            style_data = _get_intelligent_text_styling(image, zone_data, content_type)
            
            # Decide if we need any overlay for readability
            overlay_needed = _should_add_overlay(zone_data)
            
            if overlay_needed:
                # Add minimal overlay only when needed
                _add_minimal_overlay(result_image, text_area, style_data)
            
            # Render text with intelligent styling
            _render_text_with_smart_styling(
                draw, content, content_type, text_area, 
                style_data, text_renderer
            )
    
    return result_image


def _get_intelligent_text_styling(image: Image.Image, zone_data: Dict[str, Any], content_type: str) -> Dict[str, Any]:
    """Get intelligent text styling based on image colors and content type"""
    
    # Extract dominant colors from the zone
    zone_coords = zone_data['coordinates']
    zone_image = image.crop(zone_coords)
    dominant_colors = _extract_dominant_colors(zone_image)
    
    # Analyze color temperature
    color_temp = _analyze_color_temperature(dominant_colors)
    
    # Select harmonious text color
    if color_temp == 'warm':
        # Warm image (reds, oranges, yellows) → use cool colors
        text_color = (59, 130, 246, 255)  # Instagram blue
    elif color_temp == 'cool':
        # Cool image (blues, greens, purples) → use warm colors  
        text_color = (251, 146, 60, 255)  # Orange
    else:
        # Neutral image → use high contrast
        brightness = zone_data['brightness']
        if brightness > 150:
            text_color = (0, 0, 0, 255)  # Black
        else:
            text_color = (255, 255, 255, 255)  # White
    
    # Add shadow for better readability
    shadow_color = (0, 0, 0, 100) if text_color[0] > 128 else (255, 255, 255, 100)
    
    return {
        'text_color': text_color,
        'shadow_color': shadow_color,
        'font_size': _get_adaptive_font_size(content_type, zone_data),
        'overlay_opacity': _calculate_overlay_opacity(zone_data)
    }


def _extract_dominant_colors(image: Image.Image, num_colors: int = 3) -> List[Tuple[int, int, int]]:
    """Extract dominant colors from image using simple color analysis"""
    
    # Convert to RGB and get pixel data
    rgb_image = image.convert('RGB')
    pixels = list(rgb_image.getdata())
    
    # Simple color clustering (k-means approximation)
    colors = []
    for i in range(0, len(pixels), 100):  # Sample every 100th pixel
        colors.append(pixels[i])
    
    # Group similar colors
    color_groups = {}
    for color in colors:
        # Round to nearest 32 for grouping
        rounded = tuple((c // 32) * 32 for c in color)
        if rounded in color_groups:
            color_groups[rounded] += 1
        else:
            color_groups[rounded] = 1
    
    # Get most frequent colors
    sorted_colors = sorted(color_groups.items(), key=lambda x: x[1], reverse=True)
    return [color for color, count in sorted_colors[:num_colors]]


def _analyze_color_temperature(colors: List[Tuple[int, int, int]]) -> str:
    """Analyze if colors are warm, cool, or neutral"""
    
    if not colors:
        return 'neutral'
    
    # Calculate average RGB values
    avg_r = sum(c[0] for c in colors) / len(colors)
    avg_g = sum(c[1] for c in colors) / len(colors)
    avg_b = sum(c[2] for c in colors) / len(colors)
    
    # Simple temperature analysis
    if avg_r > avg_b + 30:  # More red than blue
        return 'warm'
    elif avg_b > avg_r + 30:  # More blue than red
        return 'cool'
    else:
        return 'neutral'


def _should_add_overlay(zone_data: Dict[str, Any]) -> bool:
    """Decide if overlay is needed for readability"""
    
    readability = zone_data['readability']
    busyness = zone_data['busyness']
    
    # No overlay if high readability and low busyness
    if readability > 75 and busyness < 3:
        return False
    
    # Add overlay if low readability or high busyness
    return readability < 60 or busyness > 8


def _add_minimal_overlay(image: Image.Image, text_area: Tuple[int, int, int, int], style_data: Dict[str, Any]):
    """Add minimal overlay only when needed"""
    
    x1, y1, x2, y2 = text_area
    
    # Create very subtle overlay
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    
    # Add minimal background with very low opacity
    opacity = style_data.get('overlay_opacity', 30)
    overlay_draw.rectangle([x1-10, y1-10, x2+10, y2+10], 
                          fill=(255, 255, 255, opacity))
    
    # Composite the overlay
    image.paste(overlay, (0, 0), overlay)


def _render_text_with_smart_styling(draw: ImageDraw.Draw, content: Any, content_type: str, 
                                   text_area: Tuple[int, int, int, int], style_data: Dict[str, Any], 
                                   text_renderer: ModernTextRenderer):
    """Render text with intelligent styling"""
    
    x1, y1, x2, y2 = text_area
    text_color = style_data['text_color']
    shadow_color = style_data['shadow_color']
    
    # Calculate text position
    if content_type == 'headline':
        text_x = x1 + 20
        text_y = y1 + 20
    elif content_type == 'subhead':
        text_x = x1 + 20
        text_y = y1 + 80
    elif content_type == 'bullets':
        text_x = x1 + 20
        text_y = y1 + 140
    
    # Render text with shadow for better readability
    text_width = x2 - x1 - 40
    
    if content_type == 'bullets' and isinstance(content, list):
        for i, bullet in enumerate(content[:3]):
            bullet_text = f"• {bullet}"
            bullet_y = text_y + (i * 40)
            
            # Draw shadow first
            text_renderer.render_text_block(
                draw, bullet_text, 'bullet',
                (text_x + 2, bullet_y + 2), text_width,
                color=shadow_color
            )
            
            # Draw main text
            text_renderer.render_text_block(
                draw, bullet_text, 'bullet',
                (text_x, bullet_y), text_width,
                color=text_color
            )
    else:
        # Draw shadow first
        text_renderer.render_text_block(
            draw, str(content), content_type,
            (text_x + 2, text_y + 2), text_width,
            color=shadow_color
        )
        
        # Draw main text
        text_renderer.render_text_block(
            draw, str(content), content_type,
            (text_x, text_y), text_width,
            color=text_color
        )


def _get_adaptive_font_size(content_type: str, zone_data: Dict[str, Any]) -> int:
    """Get adaptive font size based on content type and zone characteristics"""
    
    base_sizes = {
        'headline': 48,
        'subhead': 32,
        'bullets': 28,
        'quote': 36
    }
    
    base_size = base_sizes.get(content_type, 32)
    
    # Adjust based on zone size
    zone_size = zone_data.get('coordinates', (0, 0, 100, 100))
    zone_width = zone_size[2] - zone_size[0]
    
    if zone_width < 300:
        return int(base_size * 0.8)  # Smaller for narrow zones
    elif zone_width > 600:
        return int(base_size * 1.2)  # Larger for wide zones
    else:
        return base_size


def _calculate_overlay_opacity(zone_data: Dict[str, Any]) -> int:
    """Calculate optimal overlay opacity based on zone characteristics"""
    
    readability = zone_data['readability']
    busyness = zone_data['busyness']
    
    # High readability = low opacity
    if readability > 80:
        return 10
    elif readability > 60:
        return 30
    elif readability > 40:
        return 50
    else:
        return 70


def generate_instagram_template_overlay(state: Dict[str, Any], overlay_text: Dict[str, Any], platform: str, post_type: str = 'single') -> Dict[str, Any]:
    """Generate overlay using Instagram Template Engine"""
    try:
        if not TEMPLATES_AVAILABLE:
            print("⚠️ Instagram Template Engine not available, falling back to smart placement")
            return generate_single_overlay(state, overlay_text, platform, post_type)
        
        print("🎨 Generating Instagram template overlay...")
        
        # Get background image
        background_url = state.get('image_url') or state.get('background_image_url')
        if not background_url:
            raise ValueError("No background image URL provided")
        
        # Load background image
        background_img = _load_modern_background(background_url, 1080, 1080)
        
        # Get template preferences with flexible priority system
        template_name = state.get('instagram_template_name')  # Manual override (highest priority)
        
        if not template_name and isinstance(overlay_text, dict):
            # Check if AI agent optionally recommended a template
            ai_template = overlay_text.get('recommended_template')
            if ai_template and ai_template in ['minimal', 'bold', 'gradient', 'split_screen', 'quote']:
                template_name = ai_template
                print(f"🤖 Using AI-recommended template: {template_name}")
                reason = overlay_text.get('template_reason', 'AI suggestion based on content analysis')
                print(f"   Reason: {reason}")
            else:
                print(f"🎯 No AI template recommendation - will use auto-selection fallback")
        
        brand_config = state.get('brand_config')  # Brand customization
        
        # Prepare content structure for templates
        content = {}
        if isinstance(overlay_text, dict):
            content = {
                'headline': overlay_text.get('headline', overlay_text.get('title', '')),
                'subhead': overlay_text.get('subhead', overlay_text.get('subtitle', overlay_text.get('description', ''))),
                'bullets': overlay_text.get('bullets', overlay_text.get('key_points', overlay_text.get('points', [])))
            }
        else:
            # Handle string content
            content = {'headline': str(overlay_text)}
        
        # Clean up content
        if isinstance(content.get('bullets'), str):
            content['bullets'] = [content['bullets']]
        elif not isinstance(content.get('bullets'), list):
            content['bullets'] = []
        
        print(f"📝 Template content: {content}")
        print(f"🎨 Template name: {template_name}")
        print(f"🎨 Brand config: {brand_config}")
        
        # Create the Instagram post with template
        result = create_instagram_post_with_template(
            background_img, 
            content, 
            template_name, 
            brand_config
        )
        
        if result['success']:
            # Structure the output using the contract
            output = TextOverlayOutputV1(
                image_url=result.get('image_url', ''),
                image_data_url=result.get('image_data_url', ''),
                template_used=result.get('template_name', 'unknown'),
                platform_used=platform,
                post_type=post_type,
                timestamp=datetime.now().isoformat()
            )
            return output.dict()
        else:
            raise Exception(f"Template generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in Instagram template overlay: {e}")
        # Fallback to existing smart placement
        print("🔄 Falling back to smart placement overlay...")
        return generate_single_overlay(state, overlay_text, platform, post_type)


def generate_canva_template_overlay(state: Dict[str, Any], overlay_text: Dict[str, Any], platform: str, post_type: str = 'single') -> Dict[str, Any]:
    """Generate overlay using Canva template"""
    try:
        print("🎨 Generating Canva template overlay...")
        
        # Import Canva integration
        from services.canva_integration import CanvaIntegration
        
        # Get Canva template ID
        canva_template_id = state.get('canva_template_id')
        if not canva_template_id:
            raise ValueError("canva_template_id is required for Canva template overlay")
        
        # Initialize Canva integration
        canva = CanvaIntegration()
        
        # Get credentials from database
        from services.canva_credentials import canva_credentials_service
        
        user_id = state.get('user_id', 'default_user')
        access_token = canva_credentials_service.get_access_token(user_id)
        
        if not access_token:
            raise ValueError("No valid Canva access token found. Please authenticate with Canva first.")
        
        canva.access_token = access_token
        
        # Prepare content for Canva template
        if isinstance(overlay_text, dict):
            # Extract content from structured data
            content = {
                'headline': overlay_text.get('headline', ''),
                'subhead': overlay_text.get('subhead', ''),
                'bullets': overlay_text.get('bullets', [])
            }
            
            # Handle carousel content
            if 'slides' in overlay_text and isinstance(overlay_text['slides'], list):
                content['slides'] = overlay_text['slides']
        else:
            # Fallback content
            content = {
                'headline': str(overlay_text),
                'subhead': '',
                'bullets': []
            }
        
        print(f"🎨 Content prepared for Canva: {content}")
        
        # Apply content to Canva template
        print("🎨 Applying content to Canva template...")
        design = canva.apply_content_to_template(canva_template_id, content)
        
        design_id = design.get('id')
        design_url = design.get('url')
        
        print(f"🎨 Canva design created: {design_id}")
        
        # Export the design as image
        print("🎨 Exporting Canva design...")
        export_format = state.get('export_format', 'png')
        export_width = state.get('export_width', 1080)
        export_height = state.get('export_height', 1080)
        
        image_data = canva.export_design(
            design_id, 
            format=export_format,
            width=export_width,
            height=export_height
        )
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        data_url = f"data:image/{export_format};base64,{image_base64}"
        
        print(f"🎨 Canva design exported successfully")
        
        # Structure the output using the contract
        output = TextOverlayOutputV1(
            image_url=data_url,
            image_data_url=data_url,
            template_used=f"canva_{design_id}",
            platform_used=platform,
            post_type=post_type,
            timestamp=datetime.now().isoformat()
        )

        # Combine contract-validated data with Canva-specific outputs
        final_output = output.dict()
        final_output['canva_design_id'] = design_id
        final_output['canva_design_url'] = design_url

        return final_output
        
    except Exception as e:
        print(f"❌ Error in Canva template overlay: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state