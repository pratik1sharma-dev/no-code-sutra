#!/usr/bin/env python3
"""
Test Instagram access token functionality
"""
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_instagram_token():
    """Test Instagram access token"""
    print("🔍 Testing Instagram Access Token...")
    print("=" * 50)
    
    # Get the access token
    access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
    
    if not access_token:
        print("❌ No Instagram access token found in environment variables")
        return False
    
    print(f"✅ Access token found: {access_token[:10]}...")
    
    # Test if it's not the test token
    if access_token == 'test_token_12345':
        print("❌ Using test token - this will trigger simulation mode")
        return False
    
    print("✅ Using real access token - should attempt real Instagram posting")
    
    # Test the Instagram service
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
        from services.instagram_service import InstagramService
        
        print("\n🧪 Testing Instagram Service...")
        instagram_service = InstagramService(access_token)
        
        # Test with a simple post
        test_content = "🧪 Test post from No-Code Sutra workflow automation system! #testing #automation"
        
        print(f"📝 Test content: {test_content}")
        print("🚀 Attempting to post to Instagram...")
        
        result = instagram_service.post_text_only(test_content)
        
        if result['status'] == 'success':
            print("🎉 SUCCESS! Real Instagram post completed!")
            print(f"📱 Post ID: {result['instagram_post_id']}")
            print(f"🆔 Creation ID: {result['creation_id']}")
            print(f"⏰ Posted at: {result['posted_at']}")
            return True
        else:
            print(f"❌ Instagram posting failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Instagram service: {e}")
        return False

if __name__ == "__main__":
    success = test_instagram_token()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Instagram token is working correctly!")
        print("✅ Real posting should work in your workflow")
    else:
        print("⚠️  Instagram token needs attention")
        print("📝 Check your token and permissions")
