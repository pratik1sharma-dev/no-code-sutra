# Canva API Integration Setup Guide

This guide will help you set up Canva API integration for accessing templates and creating professional designs.

## 🔑 Prerequisites

1. **Canva Developer Account**
   - Visit [Canva Developers](https://www.canva.com/developers/)
   - Sign up for a developer account
   - Create a new app

2. **OAuth 2.0 Setup**
   - Configure OAuth 2.0 settings in your Canva app
   - Set up redirect URIs

## 📋 Step-by-Step Setup

### Step 1: Create Canva App

1. Go to [Canva Developers Console](https://www.canva.com/developers/apps)
2. Click "Create App"
3. Fill in app details:
   - **App Name**: Your app name
   - **Description**: Brief description
   - **Website**: Your website URL

### Step 2: Configure OAuth Settings

1. In your app dashboard, go to "OAuth 2.0" section
2. Add redirect URIs:
   - **Development**: `http://127.0.0.1:8000/api/auth/canva/callback`
   - **Production**: `https://yourdomain.com/api/auth/canva/callback`

3. Note down your credentials:
   - **Client ID**
   - **Client Secret**

### Step 3: Set Environment Variables

Add these to your `.env` file:

```bash
# Canva API Integration
CANVA_CLIENT_ID=your_canva_client_id_here
CANVA_CLIENT_SECRET=your_canva_client_secret_here
CANVA_REDIRECT_URI=http://127.0.0.1:8000/api/auth/canva/callback
```

### Step 4: Configure Scopes

Your app needs these scopes:
- `profile:read` - Read user profile
- `asset:read` - Read assets
- `asset:write` - Write assets
- `brandtemplate:content:read` - Read brand template content
- `brandtemplate:meta:read` - Read brand template metadata
- `design:content:read` - Read design content
- `design:content:write` - Write design content
- `design:meta:read` - Read design metadata

## 🔄 OAuth Flow

### 1. Authorization URL

```python
from services.canva_integration import CanvaIntegration

canva = CanvaIntegration()
auth_url = canva.get_authorization_url()
print(f"Visit this URL to authorize: {auth_url}")
```

### 2. Handle Callback

When user authorizes, they'll be redirected to your callback URL with a `code` parameter:

```python
# In your callback handler
authorization_code = request.args.get('code')
token_data = canva.exchange_code_for_token(authorization_code)
```

### 3. Save Tokens

```python
# Tokens are automatically saved to canva_tokens.json
canva.save_tokens_to_file()
```

## 🎨 Using Canva Templates

### Search Templates

```python
# Search for templates
templates = canva.search_templates(query="business", category="social-media")

# Get popular templates
popular = canva.get_popular_templates(category="instagram")
```

### Apply Content to Template

```python
# Content to apply
content = {
    'headline': 'Transform Your Business',
    'subhead': 'Innovative solutions for modern companies',
    'bullets': ['AI-Powered Analytics', 'Cloud Integration', '24/7 Support']
}

# Apply to template
design = canva.apply_content_to_template('template_id_here', content)
```

### Export Design

```python
# Export as image
image_data = canva.export_design(
    design_id='design_id_here',
    format='png',
    width=1080,
    height=1080
)
```

## 🔧 Workflow Integration

### Canva Template Node

The Canva template node can be used in your workflows:

```json
{
  "type": "canvaTemplate",
  "config": {
    "template_id": "EAGFcgTrfLo",
    "content": {
      "headline": "{{aiAgent.headline}}",
      "subhead": "{{aiAgent.subhead}}",
      "bullets": "{{aiAgent.bullets}}"
    },
    "export_format": "png",
    "export_width": 1080,
    "export_height": 1080
  }
}
```

### Node Output

The node outputs:
- `canva_design_id`: Created design ID
- `canva_design_url`: Design URL in Canva
- `canva_image_data`: Base64 image data
- `canva_image_data_url`: Data URL for other nodes

## 🚀 API Endpoints

### Available Methods

- `get_user_profile()` - Get user profile
- `search_templates()` - Search templates
- `get_template_details()` - Get template details
- `create_design_from_template()` - Create design from template
- `export_design()` - Export design as image
- `update_design_content()` - Update design content
- `get_user_designs()` - Get user's designs

## 🔒 Security Considerations

1. **Token Storage**: Tokens are saved locally in `canva_tokens.json`
2. **Token Refresh**: Access tokens are automatically refreshed when expired
3. **Scope Limitation**: Only request necessary scopes
4. **HTTPS**: Use HTTPS in production for OAuth callbacks

## 🐛 Troubleshooting

### Common Issues

1. **Invalid Redirect URI**
   - Ensure redirect URI matches exactly in Canva app settings
   - Check for trailing slashes

2. **Invalid Client ID/Secret**
   - Verify credentials in `.env` file
   - Check app status in Canva developer console

3. **Token Expired**
   - Tokens are automatically refreshed
   - If refresh fails, re-authenticate user

4. **API Rate Limits**
   - Canva has rate limits on API calls
   - Implement retry logic for failed requests

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📚 API Documentation

For detailed API documentation, visit:
- [Canva API Documentation](https://www.canva.com/developers/api-docs/)
- [OAuth 2.0 Guide](https://www.canva.com/developers/api-docs/oauth/)

## 🎯 Next Steps

1. **Test Integration**: Use the test scripts to verify setup
2. **Template Library**: Build a library of favorite templates
3. **Workflow Integration**: Add Canva nodes to your workflows
4. **Production Deployment**: Update redirect URIs for production

## 📞 Support

If you encounter issues:
1. Check Canva API status
2. Verify your app configuration
3. Review error logs
4. Contact Canva developer support
