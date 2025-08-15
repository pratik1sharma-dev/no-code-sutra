#!/usr/bin/env python3
"""
Test script to verify an Instagram token works with updated API version.
This is a manual test and should not run in CI.
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

from services.instagram_service import InstagramService


def test_new_token():
    """Manual test for Instagram token"""
    print("🔍 Testing Instagram Token (manual)")
    print("=" * 50)
    load_dotenv()

    new_token = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    page_id = os.getenv("INSTAGRAM_PAGE_ID", "")
    if not new_token:
        print("ℹ️  No INSTAGRAM_ACCESS_TOKEN set; skipping real post test.")
        return True

    try:
        print("🔐 Initializing InstagramService...")
        instagram_service = InstagramService(new_token, instagram_business_account_id=page_id or None)
        print("✅ Service initialized.")
        print(f"IG Business Account ID: {instagram_service.instagram_business_account_id}")

        # Sample post (commented by default; uncomment to run)
        # test_caption = "Test post from No Code Sutra - API v23.0 working! 🚀"
        # media_result = instagram_service.create_media_container(test_caption)
        # print(f"✅ Media container created: {media_result.get('id', 'Unknown')}")
        # publish_result = instagram_service.publish_media(media_result['id'])
        # print(f"✅ Post published successfully! Post ID: {publish_result.get('id', 'Unknown')}")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_new_token()
