from typing import Dict, Any
from datetime import datetime
import os
import time
import base64
import hashlib
import requests


def execute(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME')
        api_key = os.getenv('CLOUDINARY_API_KEY')
        api_secret = os.getenv('CLOUDINARY_API_SECRET')
        if not (cloud_name and api_key and api_secret):
            raise ValueError('Cloudinary credentials not configured')

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
        state['status'] = 'uploaded'
        state['timestamp'] = datetime.now().isoformat()
        return state
    except Exception as e:
        print(f"Error in image upload node: {e}")
        state['status'] = 'failed'
        state['error'] = str(e)
        state['timestamp'] = datetime.now().isoformat()
        return state