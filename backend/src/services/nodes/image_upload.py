from typing import Dict, Any
from datetime import datetime
import os
import time
import base64
import hashlib
import requests
from ..contracts import ImageUploadInputV1, ImageUploadOutputV1


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        if not (cloud_name and api_key and api_secret):
            raise ValueError('Cloudinary credentials not configured')

        # Check if this is a carousel upload
        carousel_images = state.get('carousel_images', [])
        if carousel_images:
            return _upload_carousel_images(state, cloud_name, api_key, api_secret)
        
        # Single image upload (existing logic)
        data_url = state.get('image_data_url')
        image_url = state.get('image_url')

        file_param = None
        if data_url and isinstance(data_url, str) and data_url.startswith('data:image/'):
            file_param = data_url
        elif image_url and isinstance(image_url, str):
            file_param = image_url
        else:
            raise ValueError('No image data provided for upload')

        upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
        timestamp = str(int(time.time()))

        public_id = None
        try:
            if file_param.startswith('data:image/'):
                content_base64 = file_param.split(',', 1)[1]
                content_bytes = base64.b64decode(content_base64)
                public_id = hashlib.sha1(content_bytes).hexdigest()[:16]
        except Exception:
            public_id = None

        to_sign = {'timestamp': timestamp}
        if public_id:
            to_sign['public_id'] = public_id
        sorted_items = sorted(to_sign.items())
        query = "&".join([f"{k}={v}" for k, v in sorted_items])
        signature = hashlib.sha1((query + api_secret).encode('utf-8')).hexdigest()

        data = {
            'file': file_param,
            'api_key': api_key,
            'timestamp': timestamp,
            'signature': signature
        }
        if public_id:
            data['public_id'] = public_id

        resp = requests.post(upload_url, data=data)
        resp.raise_for_status()
        result = resp.json()

        secure_url = result.get('secure_url') or result.get('url')
        if not secure_url:
            raise ValueError('Cloudinary upload succeeded but no secure_url returned')

        state['image_url'] = secure_url
        state['cloudinary_result'] = {'public_id': result.get('public_id'), 'version': result.get('version')}
        out = ImageUploadOutputV1(public_url=secure_url, public_id=result.get('public_id'), version=str(result.get('version') or ''))
        state['image_upload_output'] = out.model_dump()
        state['status'] = 'uploaded'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        print(f"Error in image upload node: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state


def _upload_carousel_images(state: Dict[str, Any], cloud_name: str, api_key: str, api_secret: str) -> Dict[str, Any]:
    """Upload multiple carousel images to Cloudinary"""
    try:
        carousel_images = state.get('carousel_images', [])
        print(f"🚀 Starting carousel upload process...")
        print(f"🚀 Found {len(carousel_images)} carousel images to upload")
        
        if not carousel_images:
            raise ValueError('No carousel images provided for upload')
        
        uploaded_images = []
        upload_url = f"https://api.cloudinary.com/v1_1/{cloud_name}/image/upload"
        
        for i, slide in enumerate(carousel_images):
            print(f"📤 Processing carousel slide {i+1}/{len(carousel_images)}...")
            
            try:
                # Extract image data URL from slide
                if isinstance(slide, dict) and 'image_data_url' in slide:
                    data_url = slide['image_data_url']
                    print(f"📤 Slide {i+1}: Found image_data_url in slide dict")
                elif isinstance(slide, str) and slide.startswith('data:image/'):
                    data_url = slide
                    print(f"📤 Slide {i+1}: Found direct data URL string")
                else:
                    print(f"❌ Slide {i+1}: Skipping invalid slide format: {type(slide)}")
                    continue
                
                if not data_url.startswith('data:image/'):
                    print(f"❌ Slide {i+1}: Skipping non-data URL: {data_url[:50]}...")
                    continue
                
                print(f"📤 Slide {i+1}: Valid data URL found, length: {len(data_url)}")
                
                # Generate public ID for this slide
                content_base64 = data_url.split(',', 1)[1]
                content_bytes = base64.b64decode(content_base64)
                public_id = hashlib.sha1(content_bytes).hexdigest()[:16] + f"_slide_{i}"
                print(f"📤 Slide {i+1}: Generated public_id: {public_id}")
                
                # Generate signature
                timestamp = str(int(time.time()))
                to_sign = {'timestamp': timestamp, 'public_id': public_id}
                sorted_items = sorted(to_sign.items())
                query = "&".join([f"{k}={v}" for k, v in sorted_items])
                signature = hashlib.sha1((query + api_secret).encode('utf-8')).hexdigest()
                
                # Upload to Cloudinary
                data = {
                    'file': data_url,
                    'api_key': api_key,
                    'timestamp': timestamp,
                    'signature': signature,
                    'public_id': public_id
                }
                
                print(f"📤 Slide {i+1}: Uploading to Cloudinary...")
                resp = requests.post(upload_url, data=data)
                resp.raise_for_status()
                result = resp.json()
                
                secure_url = result.get('secure_url') or result.get('url')
                if secure_url:
                    uploaded_images.append({
                        'slide_index': i,
                        'image_url': secure_url,
                        'public_id': result.get('public_id'),
                        'version': result.get('version')
                    })
                    print(f"✅ Slide {i+1}: Successfully uploaded to Cloudinary")
                    print(f"✅ Slide {i+1}: Public URL: {secure_url}")
                else:
                    print(f"❌ Slide {i+1}: Failed to get URL from Cloudinary response")
                    
            except Exception as slide_error:
                print(f"❌ Slide {i+1}: Upload failed with error: {slide_error}")
                continue
        
        print(f"🎯 Carousel upload summary:")
        print(f"🎯 Total slides processed: {len(carousel_images)}")
        print(f"🎯 Successfully uploaded: {len(uploaded_images)}")
        print(f"🎯 Failed uploads: {len(carousel_images) - len(uploaded_images)}")
        
        if not uploaded_images:
            raise ValueError('No carousel images were successfully uploaded')
        
        # Update state with uploaded carousel images
        state['uploaded_carousel_images'] = uploaded_images
        state['carousel_image_urls'] = [img['image_url'] for img in uploaded_images]
        state['status'] = 'carousel_uploaded'
        state['timestamp'] = datetime.now().isoformat()
        
        print(f"🎯 Final carousel image URLs:")
        for i, url in enumerate(state['carousel_image_urls']):
            print(f"🎯 Slide {i+1}: {url}")
        
        return state
        
    except Exception as e:
        print(f"❌ Error in carousel image upload: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state