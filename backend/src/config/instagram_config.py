"""
Instagram API Configuration and Setup Guide

This file contains configuration settings and setup instructions for Instagram API integration.
"""

import os
from typing import Dict, Any

class InstagramConfig:
    """Configuration class for Instagram API integration"""
    
    # Instagram Graph API version
    API_VERSION = "v23.0"
    
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

if __name__ == "__main__":
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
    
    print("\n📚 For complete setup instructions, see: INSTAGRAM_SETUP.md")
