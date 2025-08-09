"""
Instagram API Configuration and Setup Guide

This file contains configuration settings and setup instructions for Instagram API integration.
"""

import os
from typing import Dict, Any

class InstagramConfig:
    """Configuration class for Instagram API integration"""
    
    # Instagram Graph API version
    API_VERSION = "v18.0"
    
    # Base URL for Instagram Graph API
    BASE_URL = f"https://graph.facebook.com/{API_VERSION}"
    
    # Required permissions for Instagram posting
    REQUIRED_PERMISSIONS = [
        "instagram_basic",
        "instagram_content_publish",
        "pages_read_engagement",
        "pages_manage_posts"
    ]
    
    # Instagram Business Account requirements
    BUSINESS_ACCOUNT_REQUIREMENTS = [
        "Facebook Page connected to Instagram Business Account",
        "Instagram Business Account (not Personal Account)",
        "Valid access token with required permissions"
    ]
    
    @staticmethod
    def get_environment_variables() -> Dict[str, str]:
        """Get required environment variables for Instagram integration"""
        return {
            "INSTAGRAM_ACCESS_TOKEN": "Facebook/Instagram access token",
            "INSTAGRAM_BUSINESS_ACCOUNT_ID": "Instagram Business Account ID (optional)",
            "FACEBOOK_PAGE_ID": "Facebook Page ID (optional)"
        }
    
    @staticmethod
    def validate_setup() -> Dict[str, Any]:
        """Validate Instagram API setup"""
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "setup_steps": []
        }
        
        # Check access token
        access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        if not access_token:
            validation_result["valid"] = False
            validation_result["errors"].append("INSTAGRAM_ACCESS_TOKEN not found in environment variables")
            validation_result["setup_steps"].append("Set INSTAGRAM_ACCESS_TOKEN environment variable")
        
        # Check if we're in development mode
        if access_token == "test_token_12345":
            validation_result["warnings"].append("Using test token - Instagram posting will be simulated")
            validation_result["setup_steps"].append("Replace test token with real Instagram access token for live posting")
        
        return validation_result

# Setup Instructions
SETUP_INSTRUCTIONS = """
🔧 Instagram API Setup Instructions:

1. **Facebook Developer Account Setup:**
   - Go to https://developers.facebook.com/
   - Create a new app or use existing app
   - Add Instagram Basic Display or Instagram Graph API product

2. **Instagram Business Account:**
   - Convert your Instagram account to Business Account
   - Connect it to a Facebook Page
   - Ensure the Facebook Page is also connected to your app

3. **Permissions & Tokens:**
   - Request required permissions: {permissions}
   - Generate a long-lived access token
   - Set INSTAGRAM_ACCESS_TOKEN environment variable

4. **Environment Variables:**
   - INSTAGRAM_ACCESS_TOKEN=your_actual_token_here
   - INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_business_id (optional)

5. **Testing:**
   - Start with test tokens to verify workflow
   - Replace with real tokens for live posting
   - Monitor API rate limits and usage

⚠️  Important Notes:
- Instagram API requires Business Account (not Personal)
- Access tokens expire and need periodic renewal
- Respect Instagram's content policies and rate limits
- Test thoroughly before going live

📚 Documentation:
- Instagram Graph API: https://developers.facebook.com/docs/instagram-api
- Facebook Graph API: https://developers.facebook.com/docs/graph-api
""".format(permissions=", ".join(InstagramConfig.REQUIRED_PERMISSIONS))

# Example workflow configuration
EXAMPLE_WORKFLOW_CONFIG = {
    "nodes": [
        {
            "id": "instagram_post",
            "type": "social_media",
            "config": {
                "platform": "instagram",
                "access_token": "your_real_access_token_here",
                "post": "instagram_content"
            }
        }
    ]
}

if __name__ == "__main__":
    # Print setup instructions
    print(SETUP_INSTRUCTIONS)
    
    # Validate current setup
    validation = InstagramConfig.validate_setup()
    print(f"\n🔍 Setup Validation: {'✅ Valid' if validation['valid'] else '❌ Invalid'}")
    
    if validation['errors']:
        print("❌ Errors:")
        for error in validation['errors']:
            print(f"  - {error}")
    
    if validation['warnings']:
        print("⚠️  Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    
    if validation['setup_steps']:
        print("🔧 Setup Steps:")
        for step in validation['setup_steps']:
            print(f"  - {step}")
