# Instagram Integration Setup Guide

## Overview
This guide explains how to set up Instagram integration for posting AI-generated content to Instagram Business accounts.

## Architecture
- **AIAgentNode**: Generates Instagram-optimized content (captions, hashtags, descriptions)
- **InstagramPostNode**: Posts the generated content to Instagram Business accounts
- **User Authentication**: Users provide their own Instagram API credentials

## Prerequisites

### 1. Instagram Business Account
- Convert your Instagram account to a Business account
- Link it to a Facebook Page
- Ensure you have admin access to the Facebook Page

### 2. Facebook Developer Account
- Create a Facebook Developer account at [developers.facebook.com](https://developers.facebook.com)
- Create a new app or use an existing one
- Add Instagram Basic Display or Instagram Graph API product

### 3. Required Permissions
- **Instagram Basic Display API**: For basic posting capabilities
- **Instagram Graph API**: For advanced business features (recommended)
- **Pages Read and Write**: To post to linked Facebook pages

## Setup Steps

### Step 1: Create Facebook App
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click "Create App"
3. Choose "Business" as the app type
4. Fill in app details and create

### Step 2: Add Instagram Product
1. In your app dashboard, click "Add Product"
2. Find "Instagram Basic Display" or "Instagram Graph API"
3. Click "Set Up"

### Step 3: Configure Instagram Basic Display
1. Add Instagram Basic Display product
2. Configure OAuth Redirect URIs
3. Add Instagram test users
4. Generate access tokens

### Step 4: Get Required Credentials
You'll need these values for the workflow:

```json
{
  "instagram_credentials": {
    "access_token": "your_long_lived_access_token",
    "instagram_business_account_id": "your_instagram_account_id",
    "page_id": "linked_facebook_page_id"
  }
}
```

### Step 5: Generate Access Token
1. Use Facebook's Graph API Explorer
2. Select your app and page
3. Request permissions: `instagram_basic`, `pages_read_engagement`
4. Generate access token
5. Convert to long-lived token (valid for 60 days)

## Workflow Configuration

### Node 1: AI Content Generation
```json
{
  "node_type": "aiAgent",
  "config": {
    "prompt": "Generate an Instagram post about sustainability with engaging caption and relevant hashtags",
    "platform": "instagram",
    "content_type": "post"
  }
}
```

### Node 2: Instagram Posting
```json
{
  "node_type": "instagram_post",
  "config": {
    "instagram_credentials": {
      "access_token": "{{user_access_token}}",
      "instagram_business_account_id": "{{user_account_id}}"
    }
  },
  "inputs": {
    "content": "{{ai_node_output}}"
  }
}
```

## Content Structure

The AI node should generate content in this format:

```json
{
  "caption": "Your engaging caption text here",
  "hashtags": ["sustainability", "environment", "green"],
  "image_url": "https://example.com/image.jpg",
  "media_type": "IMAGE"
}
```

## Security Best Practices

### 1. Credential Storage
- Never log access tokens
- Store credentials securely in node metadata
- Use environment variables for sensitive data

### 2. Token Management
- Implement token refresh logic
- Monitor token expiration
- Handle expired tokens gracefully

### 3. Rate Limiting
- Respect Instagram's API rate limits
- Implement exponential backoff for failures
- Monitor API usage

## Testing

### 1. Test with Mock Data
```bash
cd backend
python test_instagram_node.py
```

### 2. Test with Real Credentials
- Use test Instagram accounts initially
- Verify posting works before production use
- Test with various content types

## Troubleshooting

### Common Issues

#### 1. "Invalid access token"
- Check token expiration
- Verify token has correct permissions
- Ensure token is for the right account

#### 2. "Permission denied"
- Verify app has required permissions
- Check Facebook Page admin access
- Ensure Instagram account is business type

#### 3. "Rate limit exceeded"
- Implement rate limiting
- Add delays between requests
- Monitor API usage

### Debug Mode
Enable debug logging in your environment:
```bash
export LOG_LEVEL=DEBUG
```

## Production Considerations

### 1. Error Handling
- Implement retry logic
- Log errors for monitoring
- Provide user-friendly error messages

### 2. Monitoring
- Track posting success rates
- Monitor API response times
- Alert on failures

### 3. Scaling
- Implement queue system for high-volume posting
- Use connection pooling for API calls
- Consider async processing

## API Endpoints

### Instagram Graph API
- **Base URL**: `https://graph.facebook.com/v18.0/`
- **Post Creation**: `POST /{ig-user-id}/media`
- **Publishing**: `POST /{ig-user-id}/media_publish`

### Rate Limits
- **Basic Display**: 200 requests per hour
- **Graph API**: 200 requests per hour per user
- **Business**: Higher limits available

## Support

For issues with:
- **Instagram API**: Check [Instagram Developer Documentation](https://developers.facebook.com/docs/instagram-api/)
- **Facebook App**: Use [Facebook Developer Support](https://developers.facebook.com/support/)
- **Platform Integration**: Check our documentation or contact support

## Next Steps

1. Complete the setup steps above
2. Test with the provided test script
3. Integrate into your workflows
4. Monitor and optimize performance
5. Scale based on usage patterns
