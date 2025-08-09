# 🚀 Instagram API Integration Setup Guide

This guide will help you set up real Instagram posting functionality for your workflow automation system.

## 📋 Prerequisites

### 1. Instagram Business Account
- ✅ Convert your Instagram account to a **Business Account** (not Personal)
- ✅ Connect it to a **Facebook Page**
- ✅ Ensure the Facebook Page is also connected to your app

### 2. Facebook Developer Account
- ✅ Create a Facebook Developer account at [developers.facebook.com](https://developers.facebook.com/)
- ✅ Create a new app or use an existing one
- ✅ Add the **Instagram Graph API** product to your app

## 🔑 Required Permissions

Your Facebook app needs these permissions:

```
instagram_basic           - Read Instagram account info
instagram_content_publish - Post content to Instagram
pages_read_engagement    - Read Facebook page engagement
pages_manage_posts       - Manage Facebook page posts
```

## 🛠️ Setup Steps

### Step 1: Facebook App Configuration

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app or select existing app
3. Add **Instagram Graph API** product
4. Configure OAuth settings
5. Request required permissions

### Step 2: Generate Access Token

1. Use Facebook's Graph API Explorer
2. Select your app and required permissions
3. Generate a **long-lived access token**
4. Copy the token (you'll need this)

### Step 3: Environment Configuration

Create or update your `.env` file:

```bash
# Instagram API Configuration
INSTAGRAM_ACCESS_TOKEN=your_long_lived_access_token_here
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_business_id_here  # Optional
FACEBOOK_PAGE_ID=your_facebook_page_id_here            # Optional
```

### Step 4: Update Workflow Configuration

Replace the placeholder in your workflow JSON:

```json
{
  "id": "node_3",
  "type": "social_media",
  "config": {
    "platform": "instagram",
    "access_token": "your_actual_access_token_here",
    "post": "instagram_content"
  }
}
```

## 🧪 Testing

### Test Mode (Simulation)
- Use `"test_token_12345"` as access token
- Posts will be simulated (no real Instagram posting)
- Good for testing workflow logic

### Live Mode (Real Posting)
- Use your real Instagram access token
- Posts will appear on your actual Instagram account
- Monitor API responses and rate limits

## 📱 What Gets Posted

### Text-Only Posts
- AI-generated content from your workflow
- Formatted as Instagram captions
- Automatically handles content length limits

### Image Posts (Future Enhancement)
- Support for image + caption posts
- Image generation integration
- Media upload handling

## ⚠️ Important Notes

### Rate Limits
- Instagram API has rate limits
- Respect posting frequency guidelines
- Monitor API usage in Facebook Developer Console

### Content Policies
- Follow Instagram's Community Guidelines
- Avoid spam or automated content
- Ensure content quality and relevance

### Token Expiration
- Long-lived tokens expire (typically 60 days)
- Set up token refresh process
- Monitor token validity

## 🔍 Troubleshooting

### Common Issues

1. **"Invalid access token"**
   - Check token validity
   - Ensure token has required permissions
   - Verify token hasn't expired

2. **"No Instagram Business Account found"**
   - Confirm Instagram account is Business type
   - Check Facebook Page connection
   - Verify app permissions

3. **"Permission denied"**
   - Request additional permissions
   - Check app review status
   - Verify account connections

### Debug Mode

Enable detailed logging by setting:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 API Documentation

- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [Facebook Graph API](https://developers.facebook.com/docs/graph-api)
- [Instagram Content Publishing](https://developers.facebook.com/docs/instagram-api/guides/content-publishing)

## 🎯 Next Steps

1. **Complete Setup**: Follow all setup steps above
2. **Test Workflow**: Run with test token first
3. **Go Live**: Replace with real token
4. **Monitor**: Track posting success and API usage
5. **Enhance**: Add image generation, scheduling, etc.

## 🆘 Support

If you encounter issues:

1. Check this guide first
2. Review Facebook Developer Console logs
3. Verify Instagram Business Account setup
4. Test with Facebook Graph API Explorer
5. Check API rate limits and permissions

---

**Happy Instagram Posting! 📸✨**
