from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64
import os
from ..contracts import TextOverlayInputV1, TextOverlayOutputV1

# Import the new Instagram Template Engine
try:
    from .instagram_templates import create_instagram_post_with_template, InstagramTemplateEngine
    TEMPLATES_AVAILABLE = True
    print("✅ Instagram Template Engine loaded successfully")
except ImportError as e:
    print(f"⚠️ Instagram Template Engine not available: {e}")
    TEMPLATES_AVAILABLE = False


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """Template-based text overlay execution - all content now uses templates"""
    try:
        # Validate input using the contract
        validated_input = TextOverlayInputV1(**state)
        overlay_text = validated_input.structured_data
        
        # DEBUG: Show exactly what text we're going to overlay
        print(f"🔍 TEXT OVERLAY DEBUG - Raw overlay_text: {overlay_text}")
        print(f"🔍 TEXT OVERLAY DEBUG - Type: {type(overlay_text)}")
        
        # Auto-detect post type from content structure FIRST
        post_type = validated_input.post_type
        if isinstance(overlay_text, dict):
            if 'slides' in overlay_text and isinstance(overlay_text['slides'], list) and len(overlay_text['slides']) > 1:
                post_type = 'carousel'
                print(f"🎯 Auto-detected carousel post type from slides array ({len(overlay_text['slides'])} slides)")
            elif 'script' in overlay_text or 'key_points' in overlay_text:
                post_type = 'video_reel'
                print(f"🎯 Auto-detected video_reel post type from content structure")
            elif 'call_to_action' in overlay_text:
                post_type = 'story'
                print(f"🎯 Auto-detected story post type from content structure")
        
        print(f"Text overlay - Platform: {validated_input.platform}, Post Type: {post_type}")
        
        # Check if overlay should be skipped
        if state.get('skip_overlay', False):
            print("⏭️ Skipping text overlay - image already complete")
            return {
                **state,
                'image_data_url': '',
                'carousel_images': [],
                'template_used': 'skipped',
                'platform_used': validated_input.platform,
                'post_type': post_type,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            }
        
        # If no templates available, fallback (though this shouldn't happen with our implementation)
        if not TEMPLATES_AVAILABLE:
            print("⚠️ Template engine not available, cannot proceed")
            return {
                'status': 'failed',
                'error': 'Template engine not available',
                'timestamp': datetime.now().isoformat()
            }
        
        # Route to appropriate template-based processing
        if post_type == 'carousel':
            return _process_carousel_with_templates(state, overlay_text, validated_input.platform)
        elif post_type == 'story':
            return _process_story_with_templates(state, overlay_text, validated_input.platform)
        elif post_type == 'video_reel':
            return _process_video_reel_with_templates(state, overlay_text, validated_input.platform)
        else:
            # Process single post with templates
            return _process_single_with_templates(state, overlay_text, validated_input.platform, post_type)
            
    except Exception as e:
        print(f"Error in text overlay node: {e}")
        import traceback
        traceback.print_exc()
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state


def _process_single_with_templates(state: Dict[str, Any], content: Dict[str, Any], platform: str, post_type: str) -> Dict[str, Any]:
    """Process single post using template system"""
    try:
        if not TEMPLATES_AVAILABLE:
            return {'status': 'failed', 'error': 'Template engine not available'}
        
        # Get background image
        background_url = state.get('image_url') or state.get('background_image_url')
        if not background_url:
            raise ValueError("No background image URL provided")
        
        # Load background image
        background_img = _load_background_image(background_url)
        
        # Get or select template
        template_name = _get_or_select_template(content, state)
        
        # Prepare content for template
        template_content = _prepare_content_for_template(content)
        
        # Apply template
        result = create_instagram_post_with_template(
            background_img, 
            template_content, 
            template_name, 
            state.get('brand_config')
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
        print(f"❌ Error in single template processing: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def _process_carousel_with_templates(state: Dict[str, Any], content: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Process carousel using template system for each slide"""
    try:
        if not TEMPLATES_AVAILABLE:
            return {'status': 'failed', 'error': 'Template engine not available'}
        
        slides_data = content.get('slides', [])
        print(f"🎨 Starting carousel template generation...")
        print(f"🎨 Found {len(slides_data)} slides to process")
        
        if not slides_data:
            print(f"🎨 No slides found, falling back to single processing")
            return _process_single_with_templates(state, content, platform, 'carousel')
        
        generated_slides = []
        image_urls_list = state.get('image_urls', [])
        
        for i, slide in enumerate(slides_data):
            print(f"🎨 Processing slide {i+1}/{len(slides_data)}...")
            print(f"🎨 Slide {i+1} data: {slide}")
            
            # Create slide-specific state with appropriate background
            slide_state = state.copy()
            slide_state['slide_index'] = i
            slide_state['slide_data'] = slide
            
            # Use appropriate background image for this slide if available
            if i < len(image_urls_list) and image_urls_list[i]:
                slide_state['image_url'] = image_urls_list[i]
                print(f"📱 Using image from image_urls list for slide {i}")
            else:
                # Fallback to main background if no specific image for slide
                slide_state['image_url'] = state.get('image_url')
            
            # Process this slide using templates
            slide_result = _process_slide_with_template(slide_state, slide, platform)
            generated_slides.append(slide_result)
            
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
        print(f"❌ Error in carousel template processing: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state


def _process_slide_with_template(state: Dict[str, Any], slide_data: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Process individual slide using template system"""
    try:
        if not TEMPLATES_AVAILABLE:
            return {'slide_index': state.get('slide_index', 0), 'error': 'Template engine not available'}
        
        # Get background image for this slide
        background_url = state.get('image_url') or state.get('background_image_url')
        if not background_url:
            raise ValueError("No background image URL provided for slide")
        
        # Load background image
        background_img = _load_background_image(background_url)
        
        # Get or select template for this slide
        template_name = _get_or_select_template(slide_data, state)
        
        # Prepare slide content for template
        template_content = _prepare_content_for_template(slide_data)
        
        # Apply template
        result = create_instagram_post_with_template(
            background_img, 
            template_content, 
            template_name, 
            state.get('brand_config')
        )
        
        if result['success']:
            return {
                'slide_index': state.get('slide_index', 0),
                'image_data_url': result.get('image_data_url', ''),
                'slide_data': slide_data,
                'template_used': result.get('template_name', 'unknown')
            }
        else:
            raise Exception(f"Slide template generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error processing slide with template: {e}")
        return {
            'slide_index': state.get('slide_index', 0),
            'error': str(e)
        }


def _process_story_with_templates(state: Dict[str, Any], content: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Process story using template system"""
    try:
        if not TEMPLATES_AVAILABLE:
            return {'status': 'failed', 'error': 'Template engine not available'}
        
        # For now, stories use the same logic as single posts but with story-specific template
        # Eventually we'll have story-specific templates
        
        # Get background image
        background_url = state.get('image_url') or state.get('background_image_url')
        if not background_url:
            raise ValueError("No background image URL provided")
        
        # Load background image
        background_img = _load_background_image(background_url)
        
        # Select story-appropriate template
        template_name = 'story'  # Use the new story template
        if not _template_exists(template_name):
            template_name = 'minimal'  # Fallback
        
        # Prepare content for template
        template_content = _prepare_content_for_template(content)
        
        # Apply template
        result = create_instagram_post_with_template(
            background_img, 
            template_content, 
            template_name, 
            state.get('brand_config')
        )
        
        if result['success']:
            # Structure the output using the contract
            output = TextOverlayOutputV1(
                image_url=result.get('image_url', ''),
                image_data_url=result.get('image_data_url', ''),
                template_used=result.get('template_name', 'unknown'),
                platform_used=platform,
                post_type='story',
                timestamp=datetime.now().isoformat()
            )
            return output.dict()
        else:
            raise Exception(f"Story template generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error in story template processing: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }


def _process_video_reel_with_templates(state: Dict[str, Any], content: Dict[str, Any], platform: str) -> Dict[str, Any]:
    """Process video reel using template system (placeholder for now)"""
    # For now, treat video reel like single post with reel-specific template
    return _process_single_with_templates(state, content, platform, 'video_reel')


def _get_or_select_template(content: Dict[str, Any], state: Dict[str, Any]) -> str:
    """Get template from state or auto-select based on content"""
    # First, check if template is specified in state
    template_name = state.get('instagram_template_name')
    if template_name:
        return template_name
    
    # Check if AI agent recommended a template
    if isinstance(content, dict) and content.get('recommended_template'):
        return content['recommended_template']
    
    # Auto-select based on content type
    if isinstance(content, dict):
        # Content with story_line suggests story template
        if 'story_line' in content or 'expression' in content:
            return 'story'
        # Content with quotes suggests quote template
        if 'quote' in str(content).lower() or len(content.get('headline', '')) > 50:
            return 'quote'
        # Content with many bullets suggests split_screen
        if len(content.get('bullets', [])) > 3:
            return 'split_screen'
    
    # Default template
    return 'minimal'


def _template_exists(template_name: str) -> bool:
    """Check if a template exists in the engine"""
    if not TEMPLATES_AVAILABLE:
        return False
    try:
        from .instagram_templates import InstagramTemplateEngine
        engine = InstagramTemplateEngine()
        available_names = [t['name'] for t in engine.get_available_templates()]
        return template_name in available_names
    except:
        return False


def _prepare_content_for_template(content: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare content in format expected by template system"""
    if not isinstance(content, dict):
        return {'headline': str(content), 'subhead': '', 'bullets': []}
    
    # Return content as-is since template system handles all fields
    return content


def _load_background_image(background_url: str) -> Image.Image:
    """Load background image from URL or data URL"""
    if background_url.startswith('http'):
        # Load from HTTP/HTTPS URL
        response = requests.get(background_url, timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content)).convert('RGB')
    elif background_url.startswith('data:image'):
        # Load from data URL
        header, b64data = background_url.split(',', 1)
        image_bytes = base64.b64decode(b64data)
        return Image.open(io.BytesIO(image_bytes)).convert('RGB')
    else:
        # Create fallback solid color image
        return Image.new('RGB', (1080, 1080), (240, 240, 240))


def _create_error_result(e: Exception, state: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a standard error result structure"""
    print(f"❌ Error in text overlay node: {e}")
    import traceback
    print(f"Traceback: {traceback.format_exc()}")
    error_result = {
        'status': 'failed',
        'error': str(e),
        'timestamp': datetime.now().isoformat()
    }
    if state:
        error_result.update(state)
    return error_result