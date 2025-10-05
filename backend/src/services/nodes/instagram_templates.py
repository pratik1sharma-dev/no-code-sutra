"""
Instagram Template Engine - Professional Design Templates
Provides multiple design templates for Instagram posts with AI-powered template selection
"""

import cv2
import numpy as np
from typing import Dict, Any, Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
import base64
import math
import random
from abc import ABC, abstractmethod
import colorsys

# Try to import computer vision libraries for character detection
try:
    import cv2
    import numpy as np
    CV_AVAILABLE = True
    print("✅ OpenCV loaded successfully for character detection")
except ImportError:
    CV_AVAILABLE = False
    print("⚠️ OpenCV not available for character detection")

try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    print("✅ MediaPipe loaded successfully for character detection")
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ MediaPipe not available for character detection")


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
                                              'vertical', 100)
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


class StoryTemplate(BaseTemplate):
    """Story-focused design optimized for narrative content and character expressions"""
    
    def get_template_name(self) -> str:
        return "story"
    
    def get_template_description(self) -> str:
        return "Story-focused layout with emphasis on narrative content and character expressions"
    
    def render(self, background_img: Image.Image, content: Dict[str, Any], 
               brand_config: Optional[Dict[str, Any]] = None) -> Image.Image:
        if brand_config:
            self.set_brand_config(brand_config)
        
        # Create base image
        img = background_img.copy().resize((self.width, self.height), Image.Resampling.LANCZOS)
        
        # Add semi-transparent overlay for better text readability
        overlay = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 80))
        img = Image.alpha_composite(img.convert('RGBA'), overlay)
        
        draw = ImageDraw.Draw(img)
        
        # Get colors
        text_color = self.get_color('text_light')  # White text for contrast
        accent_color = self.get_color('accent')
        
        # Story content gets primary focus
        story_line = content.get('story_line', content.get('content', ''))
        headline = content.get('headline', '')
        subhead = content.get('subhead', '')
        expression = content.get('expression', '')
        
        # Detect safe zone for text placement, avoiding character
        safe_zones = self._detect_safe_text_zones(img)
        text_area = safe_zones.get('largest_zone', (int(self.width * 0.4), 80, self.width - 80, self.height - 80))

        # Unpack text area coordinates
        text_area_left, text_area_top, text_area_right, text_area_bottom = text_area
        text_area_width = text_area_right - text_area_left
        
        # Primary text placement - story content
        if story_line:
            story_font = self.get_font('regular', 40)
            max_text_width = text_area_width - 40  # Padding
            lines = self._wrap_text(draw, story_line, story_font, max_text_width)
            line_height = 50
            
            total_text_height = len(lines) * line_height
            start_y = text_area_top + (text_area_bottom - text_area_top - total_text_height) // 2
            start_y = max(start_y, text_area_top + 20) # Ensure it's within bounds
            
            current_y = start_y
            for line in lines:
                bbox = draw.textbbox((0, 0), line, font=story_font)
                text_width = bbox[2] - bbox[0]
                x_position = text_area_left + (text_area_width - text_width) // 2

                # Add subtle shadow for readability
                draw.text((x_position + 2, current_y + 2), line, fill=(0, 0, 0, 150), font=story_font)
                draw.text((x_position, current_y), line, fill=text_color[:3], font=story_font)
                current_y += line_height

        # Headline at top of safe zone
        if headline:
            headline_font = self.get_font('bold', 48)
            bbox = draw.textbbox((0, 0), headline, font=headline_font)
            text_width = bbox[2] - bbox[0]
            x_position = text_area_left + (text_area_width - text_width) // 2
            headline_y = text_area_top + 40
            draw.text((x_position, headline_y), headline, fill=text_color[:3], font=headline_font)

        # Subhead below headline
        if subhead and not story_line:
            subhead_font = self.get_font('regular', 36)
            bbox = draw.textbbox((0, 0), subhead, font=subhead_font)
            text_width = bbox[2] - bbox[0]
            x_position = text_area_left + (text_area_width - text_width) // 2
            subhead_y = text_area_top + 100
            draw.text((x_position, subhead_y), subhead, fill=text_color[:3], font=subhead_font)

        # Expression at bottom of safe zone
        if expression:
            expr_font = self.get_font('bold', 32)
            expr_text = f"~ {expression.strip().capitalize()} ~"
            bbox = draw.textbbox((0, 0), expr_text, font=expr_font)
            text_width = bbox[2] - bbox[0]
            x_position = text_area_left + (text_area_width - text_width) // 2
            expr_y = text_area_bottom - 80
            draw.text((x_position, expr_y), expr_text, fill=accent_color[:3], font=expr_font)
        
        return img.convert('RGB')
    
    def _detect_safe_text_zones(self, image: Image.Image) -> Dict[str, Tuple[int, int, int, int]]:
        """
        Detect character-free zones in image for safe text placement.
        Returns dictionary of safe zones for text.
        """
        try:
            width, height = image.size
            
            # Try to use MediaPipe for actual face detection if available
            if MEDIAPIPE_AVAILABLE:
                character_free_zones = self._detect_character_zones_with_mediapipe(image)
                if character_free_zones:
                    return character_free_zones
            
            # Fallback to heuristic-based zones (can be enhanced with actual detection)
            
            # Default heuristic zones that tend to be safer for text
            top_zone = (0, 0, width, int(height * 0.25))      # Top 25%
            bottom_zone = (0, int(height * 0.75), width, height)  # Bottom 25%  
            center_zone = (int(width * 0.1), int(height * 0.3), int(width * 0.9), int(height * 0.7))  # Central 60%
            left_zone = (0, int(height * 0.2), int(width * 0.3), int(height * 0.8))  # Left 30%
            right_zone = (int(width * 0.7), int(height * 0.2), width, int(height * 0.8))  # Right 30%
            
            # Largest zone (central area)
            largest_zone = center_zone
            
            return {
                'top_zone': top_zone,
                'bottom_zone': bottom_zone,
                'center_zone': center_zone,
                'left_zone': left_zone,
                'right_zone': right_zone,
                'largest_zone': largest_zone
            }
            
        except Exception as e:
            # Fallback to basic zones if detection fails
            width, height = image.size
            return {
                'top_zone': (0, 0, width, int(height * 0.25)),
                'bottom_zone': (0, int(height * 0.75), width, height),
                'center_zone': (50, int(height * 0.2), width - 50, int(height * 0.8)),
                'left_zone': (0, int(height * 0.2), int(width * 0.3), int(height * 0.8)),
                'right_zone': (int(width * 0.7), int(height * 0.2), width, int(height * 0.8)),
                'largest_zone': (50, int(height * 0.2), width - 50, int(height * 0.8))
            }
    
    def _detect_character_zones_with_mediapipe(self, image: Image.Image) -> Optional[Dict[str, Tuple[int, int, int, int]]]:
        """
        Use MediaPipe to detect faces and calculate character-free zones for text.
        """
        try:
            if not MEDIAPIPE_AVAILABLE:
                return None
            
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            height, width = opencv_image.shape[:2]
            
            # Initialize MediaPipe Face Detection
            mp_face_detection = mp.solutions.face_detection
            face_detection = mp_face_detection.FaceDetection(
                model_selection=1,  # Better for farther faces
                min_detection_confidence=0.5
            )
            
            # Detect faces
            results = face_detection.process(opencv_image)
            
            if not results.detections:
                # No faces detected, return default zones
                return None
            
            # Calculate bounding boxes for all detected faces
            face_boxes = []
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x_min = int(bbox.xmin * width)
                y_min = int(bbox.ymin * height)
                x_max = int((bbox.xmin + bbox.width) * width)
                y_max = int((bbox.ymin + bbox.height) * height)
                face_boxes.append((x_min, y_min, x_max, y_max))
            
            # Calculate character-free zones by excluding face areas
            safe_zones = self._calculate_safe_zones_from_faces(face_boxes, width, height)
            return safe_zones
            
        except Exception as e:
            print(f"⚠️ Character detection failed: {e}")
            return None
    
    def _calculate_safe_zones_from_faces(self, face_boxes: List[Tuple[int, int, int, int]], 
                                        image_width: int, image_height: int) -> Dict[str, Tuple[int, int, int, int]]:
        """
        Calculate safe text zones based on detected face positions.
        """
        # Merge overlapping face boxes
        merged_boxes = self._merge_overlapping_boxes(face_boxes)
        
        # Calculate total occupied area
        occupied_area = sum((box[2] - box[0]) * (box[3] - box[1]) for box in merged_boxes)
        total_area = image_width * image_height
        occupancy_ratio = occupied_area / total_area
        
        # If faces occupy too much space (>60%), use edge zones
        if occupancy_ratio > 0.6:
            top_zone = (0, 0, image_width, int(image_height * 0.2))
            bottom_zone = (0, int(image_height * 0.8), image_width, image_height)
            left_zone = (0, 0, int(image_width * 0.2), image_height)
            right_zone = (int(image_width * 0.8), 0, image_width, image_height)
        else:
            # Calculate safe zones avoiding face areas
            # Find vertical gaps between faces
            face_ys = []
            for box in merged_boxes:
                face_ys.extend([box[1], box[3]])
            
            face_ys = sorted(set(face_ys))
            
            # Top safe zone (above all faces)
            top_y_max = min(face_ys) if face_ys else int(image_height * 0.25)
            top_zone = (0, 0, image_width, min(top_y_max, int(image_height * 0.3)))
            
            # Bottom safe zone (below all faces)  
            bottom_y_min = max(face_ys) if face_ys else int(image_height * 0.75)
            bottom_zone = (0, max(bottom_y_min, int(image_height * 0.7)), image_width, image_height)
            
            # Calculate horizontal safe zones
            face_xs = []
            for box in merged_boxes:
                face_xs.extend([box[0], box[2]])
            
            face_xs = sorted(set(face_xs))
            
            # Left safe zone
            left_x_max = min(face_xs) if face_xs else int(image_width * 0.25)
            left_zone = (0, int(image_height * 0.2), min(left_x_max, int(image_width * 0.3)), int(image_height * 0.8))
            
            # Right safe zone
            right_x_min = max(face_xs) if face_xs else int(image_width * 0.75)
            right_zone = (max(right_x_min, int(image_width * 0.7)), int(image_height * 0.2), image_width, int(image_height * 0.8))
        
        # Central zone (with generous margins)
        center_zone = (
            int(image_width * 0.15), 
            int(image_height * 0.25), 
            int(image_width * 0.85), 
            int(image_height * 0.75)
        )
        
        # Largest safe zone (usually central with margins)
        largest_zone = center_zone
        
        return {
            'top_zone': top_zone,
            'bottom_zone': bottom_zone, 
            'center_zone': center_zone,
            'left_zone': left_zone,
            'right_zone': right_zone,
            'largest_zone': largest_zone
        }
    
    def _merge_overlapping_boxes(self, boxes: List[Tuple[int, int, int, int]]) -> List[Tuple[int, int, int, int]]:
        """
        Merge overlapping bounding boxes.
        """
        if not boxes:
            return []
        
        # Sort boxes by x coordinate
        boxes = sorted(boxes, key=lambda x: x[0])
        merged = [boxes[0]]
        
        for current in boxes[1:]:
            last = merged[-1]
            # Check if boxes overlap
            if current[0] <= last[2] and current[1] <= last[3] and current[2] >= last[0] and current[3] >= last[1]:
                # Merge boxes
                merged[-1] = (
                    min(last[0], current[0]),
                    min(last[1], current[1]),
                    max(last[2], current[2]),
                    max(last[3], current[3])
                )
            else:
                merged.append(current)
        
        return merged
    
    def _wrap_text(self, draw: ImageDraw.Draw, text: str, font: ImageFont.FreeTypeFont, 
                   max_width: int) -> List[str]:
        """Wrap text to fit within max_width"""
        lines = []
        words = text.split()
        
        if not words:
            return lines
        
        current_line = words[0]
        
        for word in words[1:]:
            test_line = current_line + " " + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            text_width = bbox[2] - bbox[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        return lines


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
            'quote': QuoteTemplate(),
            'story': StoryTemplate()
        }
        
        # Content type to template mapping for AI selection
        self.content_mapping = {
            'business': ['minimal', 'split_screen', 'bold'],
            'motivational': ['quote', 'gradient', 'bold'],
            'educational': ['split_screen', 'minimal', 'bold'],
            'promotional': ['bold', 'gradient', 'split_screen'],
            'personal': ['minimal', 'quote', 'gradient'],
            'tech': ['minimal', 'split_screen', 'gradient'],
            'lifestyle': ['gradient', 'minimal', 'quote'],
            'story': ['story', 'minimal', 'gradient']  # Add story-specific mapping
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
        
        # Special handling for storytelling content
        if 'story_line' in content or 'expression' in content or any(key in content for key in ['story_line', 'expression']):
            # Prioritize story template for storytelling content
            suitable_templates = ['story'] + [t for t in suitable_templates if t != 'story']
            # Also set content type to story if not already set
            if not content_type:
                content_type = 'story'
                suitable_templates = self.content_mapping.get(content_type, ['story', 'minimal'])
        
        # Return the most suitable template
        return suitable_templates[0] if suitable_templates else 'minimal'
    
    def _analyze_content_type(self, content: Dict[str, Any]) -> str:
        """Analyze content to determine type"""
        # Check for storytelling specific fields first
        if 'story_line' in content or 'expression' in content or 'character_name' in content:
            return 'story'
        
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
