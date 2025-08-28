# Instagram OAuth Setup Guide

This guide will help you set up permanent Instagram authentication using OAuth 2.0 instead of manually generating tokens from the Facebook Graph API Explorer.

## Overview

The new OAuth system provides:
- **Permanent tokens**: 60-day long-lived access tokens
- **Automatic refresh**: Tokens can be refreshed before expiration
- **Secure authentication**: Proper OAuth 2.0 flow
- **Multiple accounts**: Support for multiple Instagram Business Accounts
- **User-friendly**: Simple web interface for authentication

## Prerequisites

1. **Facebook Developer Account**: You need a Facebook Developer account
2. **Facebook App**: A Facebook app with Instagram Basic Display or Instagram Graph API permissions
3. **Instagram Business Account**: Your Instagram account must be converted to a Business account
4. **Facebook Page**: Connected to your Instagram Business account

## Step 1: Create a Facebook App

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "Create App" → "Business" → "Next"
3. Fill in your app details:
   - **App Name**: Your app name (e.g., "No-Code Sutra Instagram")
   - **App Contact Email**: Your email
   - **Business Account**: Select your business account
4. Click "Create App"

## Step 2: Configure Instagram Basic Display

1. In your app dashboard, go to "Add Product" → "Instagram Basic Display"
2. Click "Set Up"
3. Configure the following:

### Basic Display Settings
- **Client OAuth Settings**:
  - **Valid OAuth Redirect URIs**: `http://localhost:3000/auth/instagram/callback`
  - **Deauthorize Callback URL**: `http://localhost:3000/auth/instagram/deauthorize`
  - **Data Deletion Request URL**: `http://localhost:3000/auth/instagram/data-deletion`

### App Review (Optional for Development)
- For development, you can add yourself as a test user
- Go to "Roles" → "Test Users" → "Add Test Users"
- Add your Facebook account as a test user

## Step 3: Configure Instagram Graph API (Alternative)

If you prefer Instagram Graph API (recommended for business use):

1. Go to "Add Product" → "Instagram Graph API"
2. Click "Set Up"
3. Configure:
   - **Instagram Basic Display**: Enable
   - **Instagram Graph API**: Enable
   - **Webhooks**: Configure if needed

## Step 4: Get App Credentials

1. Go to "Settings" → "Basic"
2. Note down:
   - **App ID** (you'll need this)
   - **App Secret** (you'll need this)

## Step 5: Configure Environment Variables

Add these to your `.env` file:

```bash
# Instagram OAuth Configuration
FACEBOOK_APP_ID=your_app_id_here
FACEBOOK_APP_SECRET=your_app_secret_here
INSTAGRAM_REDIRECT_URI=http://localhost:3000/auth/instagram/callback

# Optional: Existing token (will be replaced by OAuth)
INSTAGRAM_ACCESS_TOKEN=your_existing_token_here
```

## Step 6: Test the OAuth Flow

### Using the API Endpoints

1. **Get Authorization URL**:
   ```bash
   curl http://localhost:8000/api/auth/instagram/url
   ```

2. **Complete OAuth Flow**:
   - Visit the authorization URL in your browser
   - Authorize the app
   - Copy the authorization code from the callback URL
   - Exchange it for a token:
   ```bash
   curl "http://localhost:8000/api/auth/instagram/callback?code=YOUR_AUTH_CODE"
   ```

3. **Validate Token**:
   ```bash
   curl -X POST http://localhost:8000/api/auth/instagram/validate \
     -H "Content-Type: application/json" \
     -d '{"access_token": "YOUR_TOKEN"}'
   ```

4. **Refresh Token** (when needed):
   ```bash
   curl -X POST http://localhost:8000/api/auth/instagram/refresh \
     -H "Content-Type: application/json" \
     -d '{"access_token": "YOUR_TOKEN"}'
   ```

### Using the Frontend Component

1. Import the `InstagramAuth` component in your React app
2. Add it to your settings or configuration page
3. Click "Connect Instagram Account"
4. Complete the OAuth flow in the popup window
5. The token will be automatically saved

## Step 7: Update Your Workflow

The Instagram nodes will now automatically use the OAuth-managed tokens. No changes needed to your existing workflows.

## Token Management

### Token Lifecycle
- **Short-lived tokens**: 1-2 hours (from initial OAuth)
- **Long-lived tokens**: 60 days (automatically generated)
- **Refresh**: Can be refreshed before expiration

### Automatic Refresh
The system can automatically refresh tokens before they expire. You can set up a cron job or use the refresh endpoint manually.

### Multiple Accounts
If you have multiple Instagram Business Accounts, the OAuth flow will show all available accounts and you can choose which one to use.

## Troubleshooting

### Common Issues

1. **"Invalid OAuth Redirect URI"**:
   - Ensure the redirect URI in your Facebook app matches exactly
   - Check for trailing slashes or protocol mismatches

2. **"App not in development mode"**:
   - Add yourself as a test user in the Facebook app
   - Or submit your app for review

3. **"Instagram Business Account not found"**:
   - Ensure your Instagram account is converted to a Business account
   - Connect it to a Facebook page
   - Verify the page has Instagram Basic Display permissions

4. **"Insufficient permissions"**:
   - Request the required permissions in your Facebook app
   - Ensure the user has granted the necessary permissions

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.getLogger('services.instagram_oauth').setLevel(logging.DEBUG)
```

## Security Considerations

1. **App Secret**: Never expose your app secret in client-side code
2. **Token Storage**: Store tokens securely (environment variables, encrypted database)
3. **HTTPS**: Use HTTPS in production for all OAuth endpoints
4. **State Parameter**: The OAuth flow includes CSRF protection via state parameter

## Production Deployment

For production deployment:

1. **Update Redirect URIs**: Change from `localhost` to your production domain
2. **HTTPS**: Ensure all endpoints use HTTPS
3. **App Review**: Submit your app for Facebook review if needed
4. **Token Storage**: Implement secure token storage (database with encryption)
5. **Auto-refresh**: Set up automatic token refresh before expiration

## API Reference

### Endpoints

- `GET /api/auth/instagram/url` - Get authorization URL
- `GET /api/auth/instagram/callback` - Handle OAuth callback
- `POST /api/auth/instagram/validate` - Validate existing token
- `POST /api/auth/instagram/refresh` - Refresh long-lived token

### Response Format

```json
{
  "success": true,
  "access_token": "EAAG...",
  "token_type": "long_lived",
  "expires_at": "2024-03-15T10:30:00Z",
  "instagram_accounts": [
    {
      "page_id": "123456789",
      "page_name": "My Business Page",
      "instagram_account": {
        "id": "987654321",
        "username": "mybusiness",
        "name": "My Business"
      }
    }
  ]
}
```

This OAuth system provides a much more robust and user-friendly way to manage Instagram authentication compared to manually generating tokens from the Graph API Explorer.

