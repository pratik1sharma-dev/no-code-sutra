"""
Canva Template Node
Applies content to Canva templates and returns the generated design
"""

import os
import sys
import base64
from typing import Dict, Any, Optional
from PIL import Image
from io import BytesIO

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.canva_integration import CanvaIntegration
from services.contracts import CanvaTemplateInputV1, CanvaTemplateOutputV1

def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute Canva template node
    
    Args:
        state: Current workflow state containing:
            - template_id: Canva template ID
            - content: Content to apply (headline, subhead, bullets, etc.)
            - export_format: Export format (png, jpg, pdf) - optional
            - export_width: Export width - optional
            - export_height: Export height - optional
            
    Returns:
        Updated state with:
            - canva_design_id: Created design ID
            - canva_design_url: Design URL
            - canva_image_data: Exported image data (base64)
            - canva_image_url: Cloudinary URL if uploaded
    """
    
    try:
        print("🎨 Executing Canva Template Node...")
        
        # Get parameters from state and validate
        inp = CanvaTemplateInputV1(
            template_id=state.get('template_id'),
            content=state.get('content', {}),
            export_format=state.get('export_format', 'png'),
            export_width=state.get('export_width', 1080),
            export_height=state.get('export_height', 1080)
        )
        
        if not inp.template_id:
            raise ValueError("template_id is required in state")
        
        if not inp.content:
            raise ValueError("content is required in state")
        
        print(f"📋 Template ID: {template_id}")
        print(f"📝 Content: {content}")
        
        # Initialize Canva integration
        canva = CanvaIntegration()
        
        # Load saved tokens if available
        canva.load_tokens_from_file()
        
        # Apply content to template
        print("🎨 Applying content to Canva template...")
        design = canva.apply_content_to_template(inp.template_id, inp.content)
        
        design_id = design.get('id')
        design_url = design.get('url')
        
        print(f"✅ Design created: {design_id}")
        
        # Export the design as image
        print("📤 Exporting design...")
        image_data = canva.export_design(
            design_id, 
            format=inp.export_format,
            width=inp.export_width,
            height=inp.export_height
        )
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        data_url = f"data:image/{export_format};base64,{image_base64}"
        
        print(f"✅ Design exported as {export_format}")
        
        # Save tokens for future use
        canva.save_tokens_to_file()
        
        # Update state
        state.update({
            'canva_design_id': design_id,
            'canva_design_url': design_url,
            'canva_image_data': data_url,
            'canva_image_data_url': data_url,  # For compatibility with other nodes
            'status': 'completed'
        })
        state['canva_template_input'] = inp.model_dump()
        state['canva_template_output'] = CanvaTemplateOutputV1(
            canva_design_id=design_id,
            canva_design_url=design_url,
            image_data_url=data_url
        ).model_dump()
        
        print("✅ Canva Template Node completed successfully!")
        return state
        
    except Exception as e:
        print(f"❌ Error in Canva Template Node: {e}")
        state.update({
            'status': 'error',
            'error': str(e)
        })
        return state

def get_node_info() -> Dict[str, Any]:
    """Get node information"""
    return {
        'name': 'canva_template',
        'description': 'Apply content to Canva templates and export designs',
        'input_schema': {
            'template_id': {
                'type': 'string',
                'description': 'Canva template ID',
                'required': True
            },
            'content': {
                'type': 'object',
                'description': 'Content to apply (headline, subhead, bullets, etc.)',
                'required': True,
                'properties': {
                    'headline': {'type': 'string'},
                    'subhead': {'type': 'string'},
                    'bullets': {'type': 'array', 'items': {'type': 'string'}}
                }
            },
            'export_format': {
                'type': 'string',
                'description': 'Export format (png, jpg, pdf)',
                'default': 'png'
            },
            'export_width': {
                'type': 'integer',
                'description': 'Export width in pixels',
                'default': 1080
            },
            'export_height': {
                'type': 'integer',
                'description': 'Export height in pixels',
                'default': 1080
            }
        },
        'output_schema': {
            'canva_design_id': {'type': 'string'},
            'canva_design_url': {'type': 'string'},
            'canva_image_data': {'type': 'string'},
            'canva_image_data_url': {'type': 'string'},
            'status': {'type': 'string'}
        }
    }

