from typing import Dict, Any
from datetime import datetime
import requests
from PIL import Image, ImageDraw, ImageFont
import io
import base64


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        overlay_text = state.get('overlay_text') or state.get('structured_data')
        if isinstance(overlay_text, dict):
            headline = overlay_text.get('headline', '')
            subhead = overlay_text.get('subhead', '')
            bullets = overlay_text.get('bullets', [])
            bullet_text = "\n".join([f"• {str(b)}" for b in bullets]) if bullets else ""
            parts = []
            if headline:
                parts.append(headline)
            if subhead:
                parts.append(subhead)
            if bullet_text:
                parts.append(bullet_text)
            overlay_text = "\n\n".join(parts)
        overlay_text = str(overlay_text) if overlay_text is not None else ""
        if not overlay_text.strip():
            overlay_text = "Generated Post"

        width = int(state.get('image_width', 1080))
        height = int(state.get('image_height', 1080))
        background_url = state.get('image_url') or state.get('background_image_url')

        base_image = None
        try:
            if background_url and isinstance(background_url, str) and background_url.startswith('http'):
                resp = requests.get(background_url, timeout=10)
                resp.raise_for_status()
                base_image = Image.open(io.BytesIO(resp.content)).convert('RGB')
        except Exception:
            base_image = None

        if base_image is None:
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

        image_rgba = base_image.convert('RGBA')
        overlay = Image.new('RGBA', image_rgba.size, (255, 255, 255, 0))
        draw_overlay = ImageDraw.Draw(overlay)
        panel_margin = int(min(width, height) * 0.08)
        panel_top = int(height * 0.2)
        panel_bottom = int(height * 0.8)
        draw_overlay.rectangle(
            [(panel_margin, panel_top), (width - panel_margin, panel_bottom)],
            fill=(255, 255, 255, 200),
            outline=(255, 255, 255, 100),
            width=3
        )
        image_rgba = Image.alpha_composite(image_rgba, overlay)

        draw = ImageDraw.Draw(image_rgba)
        headline_size = int(width * 0.055)
        subhead_size = int(width * 0.037)
        body_size = int(width * 0.025)
        try:
            font_large = ImageFont.truetype("arial.ttf", headline_size)
            font_medium = ImageFont.truetype("arial.ttf", subhead_size)
            font_small = ImageFont.truetype("arial.ttf", body_size)
        except Exception:
            font_large = ImageFont.load_default()
            font_medium = ImageFont.load_default()
            font_small = ImageFont.load_default()

        import textwrap
        max_text_width = width - (panel_margin * 2) - 60
        char_px_large = headline_size * 0.6
        char_px_medium = subhead_size * 0.6
        char_px_small = body_size * 0.6
        max_chars_headline = max(15, int(max_text_width / char_px_large))
        max_chars_subhead = max(20, int(max_text_width / char_px_medium))
        max_chars_body = max(25, int(max_text_width / char_px_small))

        lines = []
        line_types = []
        paragraphs = str(overlay_text).split('\n')
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            if i == 0:
                wrapped = textwrap.wrap(paragraph, width=max_chars_headline)
                lines.extend(wrapped)
                line_types.extend(['headline'] * len(wrapped))
            elif i == 1 and len(paragraphs) > 2:
                wrapped = textwrap.wrap(paragraph, width=max_chars_subhead)
                lines.extend(wrapped)
                line_types.extend(['subhead'] * len(wrapped))
            else:
                wrapped = textwrap.wrap(paragraph, width=max_chars_body)
                lines.extend(wrapped)
                line_types.extend(['body'] * len(wrapped))

        line_heights = {
            'headline': int(headline_size * 1.3),
            'subhead': int(subhead_size * 1.2),
            'body': int(body_size * 1.4)
        }
        total_height = sum(line_heights.get(lt, line_heights['body']) for lt in line_types)
        y = panel_top + ((panel_bottom - panel_top - total_height) // 2)
        x = panel_margin + 30
        for line, line_type in zip(lines, line_types):
            if line_type == 'headline':
                font = font_large
                text_color = (30, 30, 30, 255)
                line_height = line_heights['headline']
            elif line_type == 'subhead':
                font = font_medium
                text_color = (50, 50, 50, 255)
                line_height = line_heights['subhead']
            else:
                font = font_small
                text_color = (70, 70, 70, 255)
                line_height = line_heights['body']
            draw.text((x, y), line, fill=text_color, font=font)
            y += line_height

        output_image = image_rgba.convert('RGB')
        buffer = io.BytesIO()
        output_image.save(buffer, format='JPEG', quality=90)
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