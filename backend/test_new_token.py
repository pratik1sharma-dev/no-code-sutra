#!/usr/bin/env python3
"""
Test script to verify the new Instagram token works with updated API version
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from services.instagram_service import InstagramService

def test_new_token():
    """Test the new Instagram token"""
    print("🔍 Testing New Instagram Token")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get the new token and page ID
    new_token = "EAAKlG3ZCl26MBPFL18w6GFZAQm5HF6ZCognZC3mhphPRQ5TKhN9zIdTidnF2SaKKA3BAvZCGgpiYEL89ZAwUKk7ukAZB58gKwWJef1EZAHs3eyNCRqo5GHRNLZCghwRF7mZC2bZAlB5Co3wePZCVbK2QboJRdMojnyjj79ZB3uEkJtZBEqDWY6nZCiZAwTFKzS0awSuK4sYAPeJ2xokcoV01AZC386gvK8S5k0ter2kcgjyS2TW7uTZCFmshJseAZDZD"
    page_id = "715009535037615"
    
    print(f"Testing token: {new_token[:20]}...")
    print(f"Using page ID: {page_id}")
    
    try:
        # First, let's test the token validation
        print("\n🔐 Testing token validation...")
        
        # Initialize Instagram service with new token and page ID
        instagram_service = InstagramService(new_token, page_id=page_id)
        print("✅ Instagram service initialized successfully!")
        print(f"✅ Instagram Business Account ID: {instagram_service.instagram_business_account_id}")
            
            # Test posting a simple text post
            test_caption = "Test post from No Code Sutra - API v23.0 working! 🚀"
            
            print(f"\n📝 Testing post with caption: {test_caption}")
            
            # Create media container
            media_result = instagram_service.create_media_container(test_caption)
            print(f"✅ Media container created: {media_result.get('id', 'Unknown')}")
            
            # Publish the post
            publish_result = instagram_service.publish_media(media_result['id'])
            print(f"✅ Post published successfully!")
            print(f"Post ID: {publish_result.get('id', 'Unknown')}")
            
        else:
            print("❌ No Instagram Business Account found for this page")
            print("Please ensure the Facebook page is connected to Instagram")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_new_token()
