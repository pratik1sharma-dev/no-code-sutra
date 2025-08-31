"""
Instagram Template Engine - Professional Design Templates
Provides multiple design templates for Instagram posts with AI-powered template selection
"""

from typing import Dict, Any, Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64
import math
import random
from abc import ABC, abstractmethod
import colorsys


class BaseTemplate(ABC):
    """Base class for all Instagram templates"""
    
    def __init__(self, width: int = 1080, height: int = 1080):
        self.width = width
        self.height = height
        self.brand_colors = None
        self.custom_fonts = None
    
    @abstractmethod
    def get_template_name(self) -> str:
        """Get template name"""
        pass
    
    @abstractmethod
    def get_template_description(self) -> str:
        """Get template description"""
        pass
    
    @abstractmethod
    def render(self, background_img: Image.Image, content: Dict[str, Any], 
               brand_config: Optional[Dict[str, Any]] = None) -> Image.Image:
        """Render the template with content"""
        pass
    
    def set_brand_config(self, brand_config: Dict[str, Any]):
        """Set brand configuration"""
        self.brand_colors = brand_config.get('colors', {})
        self.custom_fonts = brand_config.get('fonts', {})
    
    def get_font(self, font_type: str, size: int) -> ImageFont.FreeTypeFont:
        """Get font with fallback"""
        try:
            if self.custom_fonts and font_type in self.custom_fonts:
                return ImageFont.truetype(self.custom_fonts[font_type], size)
            
            # Try common system fonts
            font_paths = {
                'bold': ['/System/Library/Fonts/Arial Bold.ttf', 'arial.ttf', 'DejaVuSans-Bold.ttf'],
                'regular': ['/System/Library/Fonts/Arial.ttf', 'arial.ttf', 'DejaVuSans.ttf'],
                'light': ['/System/Library/Fonts/Arial.ttf', 'arial.ttf', 'DejaVuSans.ttf']
            }
            
            for font_path in font_paths.get(font_type, font_paths['regular']):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    continue
                    
            return ImageFont.load_default()
        except:
            return ImageFont.load_default()
    
    def get_color(self, color_type: str) -> Tuple[int, int, int, int]:
        """Get color with brand override"""
        default_colors = {
            'primary': (59, 130, 246, 255),    # Instagram Blue
            'secondary': (139, 92, 246, 255),  # Purple
            'accent': (34, 197, 94, 255),      # Green
            'text_dark': (15, 15, 15, 255),    # Almost Black
            'text_light': (255, 255, 255, 255), # White
            'background': (255, 255, 255, 255), # White
            'overlay': (0, 0, 0, 128)          # Semi-transparent black
        }
        
        if self.brand_colors and color_type in self.brand_colors:
            color = self.brand_colors[color_type]
            if isinstance(color, (list, tuple)) and len(color) >= 3:
                return tuple(color[:4]) if len(color) >= 4 else tuple(color[:3]) + (255,)
        
        return default_colors.get(color_type, default_colors['primary'])
    
    def create_gradient_overlay(self, width: int, height: int, 
                               color1: Tuple[int, int, int], color2: Tuple[int, int, int],
                               direction: str = 'vertical', opacity: int = 180) -> Image.Image:
        """Create gradient overlay"""
        gradient = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(gradient)
        
        if direction == 'vertical':
            for y in range(height):
                ratio = y / height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(0, y), (width, y)], fill=(r, g, b, opacity))
        else:  # horizontal
            for x in range(width):
                ratio = x / width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                draw.line([(x, 0), (x, height)], fill=(r, g, b, opacity))
        
        return gradient


class MinimalTemplate(BaseTemplate):
    """Clean, minimal design with lots of whitespace"""
    
    def get_template_name(self) -> str:
        return "minimal"
    
    def get_template_description(self) -> str:
        return "Clean minimal design with elegant typography and subtle accents"
    
    def render(self, background_img: Image.Image, content: Dict[str, Any], 
               brand_config: Optional[Dict[str, Any]] = None) -> Image.Image:
        if brand_config:
            self.set_brand_config(brand_config)
        
        # Create base image
        img = background_img.copy().resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # Apply subtle overlay for text readability
        overlay = Image.new('RGBA', (self.width, self.height), (255, 255, 255, 200))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        draw = ImageDraw.Draw(img)
        
        # Get colors
        text_color = self.get_color('text_dark')
        accent_color = self.get_color('accent')
        
        y_position = 120
        
        # Headline - large, bold, centered
        if 'headline' in content and content['headline']:
            font = self.get_font('bold', 56)
            headline = content['headline']
            
            # Calculate text position for centering
            bbox = draw.textbbox((0, 0), headline, font=font)
            text_width = bbox[2] - bbox[0]
            x_position = (self.width - text_width) // 2
            
            # Draw thin accent line above headline
            line_width = min(text_width, 200)
            line_x = (self.width - line_width) // 2
            draw.rectangle([line_x, y_position - 20, line_x + line_width, y_position - 16], 
                         fill=accent_color[:3])
            
            # Draw headline
            draw.text((x_position, y_position), headline, fill=text_color[:3], font=font)
            y_position += 100
        
        # Subhead - medium, lighter
        if 'subhead' in content and content['subhead']:
            font = self.get_font('regular', 32)
            subhead = content['subhead']
            
            # Calculate text position for centering
            bbox = draw.textbbox((0, 0), subhead, font=font)
            text_width = bbox[2] - bbox[0]
            x_position = (self.width - text_width) // 2
            
            # Use secondary color for subhead
            secondary_color = self.get_color('secondary')
            draw.text((x_position, y_position), subhead, fill=secondary_color[:3], font=font)
            y_position += 80
        
        # Bullets - clean, simple
        if 'bullets' in content and content['bullets']:
            font = self.get_font('regular', 28)
            bullets = content['bullets'][:3]  # Max 3 bullets for minimal design
            
            for bullet in bullets:
                # Simple bullet point
                bullet_text = f"• {bullet}"
                bbox = draw.textbbox((0, 0), bullet_text, font=font)
                text_width = bbox[2] - bbox[0]
                x_position = (self.width - text_width) // 2
                
                draw.text((x_position, y_position), bullet_text, fill=text_color[:3], font=font)
                y_position += 50
        
        return img.convert('RGB')


class BoldTemplate(BaseTemplate):
    """Bold, high-contrast design with strong typography"""
    
    def get_template_name(self) -> str:
        return "bold"
    
    def get_template_description(self) -> str:
        return "Bold design with high contrast and strong visual hierarchy"
    
    def render(self, background_img: Image.Image, content: Dict[str, Any], 
               brand_config: Optional[Dict[str, Any]] = None) -> Image.Image:
        if brand_config:
            self.set_brand_config(brand_config)
        
        # Create base image
        img = background_img.copy().resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # Apply dark overlay for high contrast
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 160))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        draw = ImageDraw.Draw(img)
        
        # Get colors
        text_color = self.get_color('text_light')
        primary_color = self.get_color('primary')
        accent_color = self.get_color('accent')
        
        # Draw bold accent bar at top
        draw.rectangle([0, 0, self.width, 12], fill=primary_color[:3])
        
        y_position = 150
        
        # Headline - very large, bold
        if 'headline' in content and content['headline']:
            font = self.get_font('bold', 72)
            headline = content['headline'].upper()  # Bold templates use uppercase
            
            # Multi-line if needed
            words = headline.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > self.width - 120:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                else:
                    current_line.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x_position = (self.width - text_width) // 2
                
                # Draw text with slight shadow
                draw.text((x_position + 3, y_position + 3), line, fill=(0, 0, 0, 100), font=font)
                draw.text((x_position, y_position), line, fill=text_color[:3], font=font)
                y_position += 85
        
        y_position += 30
        
        # Subhead with background box
        if 'subhead' in content and content['subhead']:
            font = self.get_font('bold', 36)
            subhead = content['subhead']
            
            bbox = draw.textbbox((0, 0), subhead, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Background box
            box_padding = 20
            box_x = (self.width - text_width - box_padding * 2) // 2
            box_y = y_position - 10
            
            draw.rectangle([box_x, box_y, box_x + text_width + box_padding * 2, 
                          box_y + text_height + box_padding], fill=accent_color[:3])
            
            # Text
            x_position = box_x + box_padding
            draw.text((x_position, y_position), subhead, fill=(255, 255, 255), font=font)
            y_position += text_height + box_padding + 40
        
        # Bullets with accent markers
        if 'bullets' in content and content['bullets']:
            font = self.get_font('bold', 32)
            bullets = content['bullets'][:4]  # Max 4 bullets
            
            for i, bullet in enumerate(bullets):
                # Accent number
                number_font = self.get_font('bold', 40)
                number = str(i + 1)
                
                # Draw number background circle
                circle_size = 60
                circle_x = 80
                circle_y = y_position + 5
                
                draw.ellipse([circle_x - circle_size//2, circle_y - circle_size//2,
                            circle_x + circle_size//2, circle_y + circle_size//2], 
                           fill=primary_color[:3])
                
                # Draw number
                bbox = draw.textbbox((0, 0), number, font=number_font)
                num_width = bbox[2] - bbox[0]
                num_height = bbox[3] - bbox[1]
                draw.text((circle_x - num_width//2, circle_y - num_height//2 - 5), 
                         number, fill=(255, 255, 255), font=number_font)
                
                # Draw bullet text
                bullet_x = circle_x + circle_size//2 + 30
                draw.text((bullet_x, y_position), bullet, fill=text_color[:3], font=font)
                y_position += 70
        
        return img.convert('RGB')


class GradientTemplate(BaseTemplate):
    """Modern gradient design with smooth color transitions"""
    
    def get_template_name(self) -> str:
        return "gradient"
    
    def get_template_description(self) -> str:
        return "Modern gradient design with smooth color transitions and contemporary feel"
    
    def render(self, background_img: Image.Image, content: Dict[str, Any], 
               brand_config: Optional[Dict[str, Any]] = None) -> Image.Image:
        if brand_config:
            self.set_brand_config(brand_config)
        
        # Create base image
        img = background_img.copy().resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # Apply gradient overlay
        primary_color = self.get_color('primary')
        secondary_color = self.get_color('secondary')
        
        gradient = self.create_gradient_overlay(self.width, self.height, 
                                              primary_color[:3], secondary_color[:3], 
                                              'vertical', 200)
        img = Image.alpha_composite(img.convert('RGBA'), gradient)
        
        draw = ImageDraw.Draw(img)
        
        # Get colors
        text_color = self.get_color('text_light')
        accent_color = self.get_color('accent')
        
        y_position = 180
        
        # Headline with glow effect
        if 'headline' in content and content['headline']:
            font = self.get_font('bold', 64)
            headline = content['headline']
            
            bbox = draw.textbbox((0, 0), headline, font=font)
            text_width = bbox[2] - bbox[0]
            x_position = (self.width - text_width) // 2
            
            # Glow effect (multiple shadows)
            for offset in range(5, 0, -1):
                alpha = 50 - (offset * 8)
                glow_color = (*accent_color[:3], alpha)
                for dx in range(-offset, offset + 1):
                    for dy in range(-offset, offset + 1):
                        if dx != 0 or dy != 0:
                            draw.text((x_position + dx, y_position + dy), headline, 
                                    fill=glow_color[:3], font=font)
            
            # Main text
            draw.text((x_position, y_position), headline, fill=text_color[:3], font=font)
            y_position += 100
        
        # Subhead with subtle background
        if 'subhead' in content and content['subhead']:
            font = self.get_font('regular', 36)
            subhead = content['subhead']
            
            bbox = draw.textbbox((0, 0), subhead, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x_position = (self.width - text_width) // 2
            
            # Subtle background
            padding = 15
            draw.rounded_rectangle([x_position - padding, y_position - padding//2,
                                  x_position + text_width + padding, 
                                  y_position + text_height + padding//2],
                                 radius=20, fill=(255, 255, 255, 50))
            
            draw.text((x_position, y_position), subhead, fill=text_color[:3], font=font)
            y_position += 90
        
        # Bullets with gradient bullets
        if 'bullets' in content and content['bullets']:
            font = self.get_font('regular', 30)
            bullets = content['bullets'][:3]
            
            bullet_width = self.width - 160
            x_start = 80
            
            for i, bullet in enumerate(bullets):
                # Gradient bullet background
                bullet_height = 50
                bullet_bg = self.create_gradient_overlay(bullet_width, bullet_height,
                                                       accent_color[:3], primary_color[:3],
                                                       'horizontal', 180)
                
                # Paste bullet background
                img.paste(bullet_bg, (x_start, y_position), bullet_bg)
                
                # Bullet text
                draw.text((x_start + 20, y_position + 10), bullet, 
                         fill=text_color[:3], font=font)
                y_position += 65
        
        return img.convert('RGB')


class SplitScreenTemplate(BaseTemplate):
    """Split screen design with content on one side"""
    
    def get_template_name(self) -> str:
        return "split_screen"
    
    def get_template_description(self) -> str:
        return "Split screen layout with image on one side and content on the other"
    
    def render(self, background_img: Image.Image, content: Dict[str, Any], 
               brand_config: Optional[Dict[str, Any]] = None) -> Image.Image:
        if brand_config:
            self.set_brand_config(brand_config)
        
        # Create base canvas
        img = Image.new('RGB', (self.width, self.height), self.get_color('background')[:3])
        
        # Split dimensions
        split_x = self.width // 2
        
        # Left side - background image
        left_bg = background_img.copy().resize((split_x, self.height), Image.Resampling.LANCZOS)
        img.paste(left_bg, (0, 0))
        
        # Right side - content area with subtle background
        primary_color = self.get_color('primary')
        right_bg = Image.new('RGBA', (split_x, self.height), (*primary_color[:3], 240))
        img.paste(right_bg, (split_x, 0), right_bg)
        
        draw = ImageDraw.Draw(img)
        
        # Content area
        content_x = split_x + 40
        content_width = split_x - 80
        y_position = 150
        
        # Colors
        text_color = self.get_color('text_light')
        accent_color = self.get_color('accent')
        
        # Headline
        if 'headline' in content and content['headline']:
            font = self.get_font('bold', 48)
            headline = content['headline']
            
            # Word wrap for headline
            words = headline.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > content_width:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                else:
                    current_line.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for line in lines:
                draw.text((content_x, y_position), line, fill=text_color[:3], font=font)
                y_position += 60
            
            y_position += 20
        
        # Accent line
        draw.rectangle([content_x, y_position, content_x + content_width // 2, y_position + 4], 
                      fill=accent_color[:3])
        y_position += 30
        
        # Subhead
        if 'subhead' in content and content['subhead']:
            font = self.get_font('regular', 28)
            subhead = content['subhead']
            
            # Word wrap
            words = subhead.split()
            lines = []
            current_line = []
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > content_width:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                else:
                    current_line.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            for line in lines:
                draw.text((content_x, y_position), line, fill=text_color[:3], font=font)
                y_position += 35
            
            y_position += 40
        
        # Bullets
        if 'bullets' in content and content['bullets']:
            font = self.get_font('regular', 26)
            bullets = content['bullets'][:4]
            
            for bullet in bullets:
                # Bullet point
                draw.ellipse([content_x, y_position + 8, content_x + 12, y_position + 20], 
                           fill=accent_color[:3])
                
                # Bullet text with word wrap
                bullet_words = bullet.split()
                bullet_lines = []
                current_line = []
                
                for word in bullet_words:
                    test_line = ' '.join(current_line + [word])
                    bbox = draw.textbbox((0, 0), test_line, font=font)
                    if bbox[2] - bbox[0] > content_width - 30:
                        if current_line:
                            bullet_lines.append(' '.join(current_line))
                            current_line = [word]
                        else:
                            bullet_lines.append(word)
                    else:
                        current_line.append(word)
                
                if current_line:
                    bullet_lines.append(' '.join(current_line))
                
                line_y = y_position
                for bullet_line in bullet_lines:
                    draw.text((content_x + 25, line_y), bullet_line, fill=text_color[:3], font=font)
                    line_y += 30
                
                y_position = line_y + 15
        
        return img


class QuoteTemplate(BaseTemplate):
    """Quote-focused design with elegant typography"""
    
    def get_template_name(self) -> str:
        return "quote"
    
    def get_template_description(self) -> str:
        return "Elegant quote-focused design with sophisticated typography"
    
    def render(self, background_img: Image.Image, content: Dict[str, Any], 
               brand_config: Optional[Dict[str, Any]] = None) -> Image.Image:
        if brand_config:
            self.set_brand_config(brand_config)
        
        # Create base image with overlay
        img = background_img.copy().resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # Apply elegant overlay
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 120))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        draw = ImageDraw.Draw(img)
        
        # Colors
        text_color = self.get_color('text_light')
        accent_color = self.get_color('accent')
        primary_color = self.get_color('primary')
        
        # Large quote marks
        quote_font = self.get_font('bold', 120)
        draw.text((80, 100), '"', fill=accent_color[:3], font=quote_font)
        
        # Main quote (use headline as quote)
        quote_text = content.get('headline', content.get('subhead', ''))
        if quote_text:
            font = self.get_font('regular', 42)
            
            # Word wrap for quote
            words = quote_text.split()
            lines = []
            current_line = []
            max_width = self.width - 200
            
            for word in words:
                test_line = ' '.join(current_line + [word])
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] > max_width:
                    if current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        lines.append(word)
                else:
                    current_line.append(word)
            
            if current_line:
                lines.append(' '.join(current_line))
            
            # Center the quote
            y_position = (self.height - len(lines) * 55) // 2
            
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x_position = (self.width - text_width) // 2
                
                draw.text((x_position, y_position), line, fill=text_color[:3], font=font)
                y_position += 55
        
        # Closing quote mark
        draw.text((self.width - 150, self.height - 200), '"', fill=accent_color[:3], font=quote_font)
        
        # Attribution line
        draw.rectangle([200, self.height - 120, self.width - 200, self.height - 116], 
                      fill=primary_color[:3])
        
        # Author/source (use subhead if different from headline)
        if 'subhead' in content and content['subhead'] != quote_text:
            author_font = self.get_font('regular', 24)
            author = f"- {content['subhead']}"
            
            bbox = draw.textbbox((0, 0), author, font=author_font)
            text_width = bbox[2] - bbox[0]
            x_position = self.width - text_width - 100
            
            draw.text((x_position, self.height - 100), author, fill=text_color[:3], font=author_font)
        
        return img


class InstagramTemplateEngine:
    """Main template engine for Instagram posts"""
    
    def __init__(self):
        self.templates = {
            'minimal': MinimalTemplate(),
            'bold': BoldTemplate(),
            'gradient': GradientTemplate(),
            'split_screen': SplitScreenTemplate(),
            'quote': QuoteTemplate()
        }
        
        # Content type to template mapping for AI selection
        self.content_mapping = {
            'business': ['minimal', 'split_screen', 'bold'],
            'motivational': ['quote', 'gradient', 'bold'],
            'educational': ['split_screen', 'minimal', 'bold'],
            'promotional': ['bold', 'gradient', 'split_screen'],
            'personal': ['minimal', 'quote', 'gradient'],
            'tech': ['minimal', 'split_screen', 'gradient'],
            'lifestyle': ['gradient', 'minimal', 'quote']
        }
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates"""
        return [
            {
                'name': template.get_template_name(),
                'description': template.get_template_description()
            }
            for template in self.templates.values()
        ]
    
    def select_template(self, content: Dict[str, Any], content_type: str = None) -> str:
        """AI-powered template selection based on content analysis"""
        
        # Analyze content if type not provided
        if not content_type:
            content_type = self._analyze_content_type(content)
        
        # Get suitable templates for content type
        suitable_templates = self.content_mapping.get(content_type, ['minimal', 'bold'])
        
        # Additional logic based on content characteristics
        if 'quote' in str(content).lower() or len(content.get('headline', '')) > 50:
            suitable_templates = ['quote'] + [t for t in suitable_templates if t != 'quote']
        
        if len(content.get('bullets', [])) > 3:
            suitable_templates = ['split_screen', 'bold'] + [t for t in suitable_templates if t not in ['split_screen', 'bold']]
        
        # Return the most suitable template
        return suitable_templates[0] if suitable_templates else 'minimal'
    
    def _analyze_content_type(self, content: Dict[str, Any]) -> str:
        """Analyze content to determine type"""
        text = ' '.join([
            str(content.get('headline', '')),
            str(content.get('subhead', '')),
            ' '.join(content.get('bullets', []))
        ]).lower()
        
        # Keywords for different content types
        keywords = {
            'business': ['business', 'company', 'professional', 'corporate', 'strategy', 'growth'],
            'motivational': ['inspire', 'motivate', 'success', 'achieve', 'dream', 'goal'],
            'educational': ['learn', 'tip', 'guide', 'how to', 'tutorial', 'step'],
            'promotional': ['sale', 'discount', 'offer', 'buy', 'shop', 'deal'],
            'tech': ['technology', 'software', 'app', 'digital', 'ai', 'tech'],
            'lifestyle': ['life', 'lifestyle', 'wellness', 'health', 'travel', 'food'],
            'personal': ['my', 'me', 'i', 'personal', 'journey', 'story', 'meet', 'profile', 'biography', 'interview', 'feature', 'about', 'myself', 'experience', 'background']
        }
        
        # Count keyword matches
        scores = {}
        for category, category_keywords in keywords.items():
            score = sum(1 for keyword in category_keywords if keyword in text)
            scores[category] = score
        
        # Return category with highest score
        return max(scores.items(), key=lambda x: x[1])[0] if any(scores.values()) else 'business'
    
    def render_template(self, template_name: str, background_img: Image.Image, 
                       content: Dict[str, Any], brand_config: Optional[Dict[str, Any]] = None) -> Image.Image:
        """Render specific template"""
        if template_name not in self.templates:
            template_name = 'minimal'  # Fallback
        
        template = self.templates[template_name]
        return template.render(background_img, content, brand_config)
    
    def create_branded_post(self, background_img: Image.Image, content: Dict[str, Any],
                           template_name: str = None, brand_config: Optional[Dict[str, Any]] = None) -> Tuple[Image.Image, str]:
        """Create a branded Instagram post with automatic template selection"""
        
        # Auto-select template if not specified
        if not template_name:
            template_name = self.select_template(content)
        
        # Render the template
        result_img = self.render_template(template_name, background_img, content, brand_config)
        
        return result_img, template_name


def create_instagram_post_with_template(background_img: Image.Image, content: Dict[str, Any],
                                      template_name: str = None, brand_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Main function to create Instagram post with template system"""
    
    engine = InstagramTemplateEngine()
    
    try:
        # Create the post
        result_img, used_template = engine.create_branded_post(
            background_img, content, template_name, brand_config
        )
        
        # Convert to base64
        img_buffer = io.BytesIO()
        result_img.save(img_buffer, format='PNG', quality=95, optimize=True)
        img_buffer.seek(0)
        
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        data_url = f"data:image/png;base64,{img_base64}"
        
        return {
            'success': True,
            'image_data_url': data_url,
            'template_used': used_template,
            'image_format': 'PNG',
            'image_size': (result_img.width, result_img.height),
            'available_templates': engine.get_available_templates()
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'template_used': template_name or 'none',
            'available_templates': engine.get_available_templates()
        }
