# Google Custom Search API Setup Guide

## Overview
Google Custom Search API allows us to search the entire web for images, giving access to real-world, current, and diverse image sources instead of just stock photos.

## Benefits
- ✅ **Access to entire web** - Not limited to stock photo sites
- ✅ **Real-time results** - Latest images from news, blogs, social media
- ✅ **High quality** - Professional images from various sources
- ✅ **Relevant results** - Google's excellent search algorithm
- ✅ **Cost-effective** - 100 free queries per day

## Setup Steps

### 1. Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Custom Search API

### 2. Get API Key
1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click "Create Credentials" → "API Key"
3. Copy the API key

### 3. Create Custom Search Engine
1. Go to [Custom Search Engine](https://cse.google.com/cse/)
2. Click "Add" to create a new search engine
3. Configure settings:
   - **Sites to search**: Leave blank (search entire web)
   - **Search the entire web**: Check this option
   - **Image search**: Enable
4. Copy the Search Engine ID (cx parameter)

### 4. Configure Environment Variables
Add to your `.env` file:
```bash
GOOGLE_CUSTOM_SEARCH_API_KEY=your_api_key_here
GOOGLE_CUSTOM_SEARCH_ENGINE_ID=your_search_engine_id_here
```

## Usage Limits
- **Free tier**: 100 queries per day
- **Paid tier**: $5 per 1000 queries
- **Rate limit**: 10 queries per second

## Image Search Parameters
Our implementation uses these parameters for optimal results:
- `searchType`: 'image' - Search for images only
- `num`: 1 - Return one result
- `imgSize`: 'large' - High resolution images
- `imgType`: 'photo' - Photographs only
- `safe`: 'active' - Safe search enabled

## Fallback Strategy
If Google Custom Search fails or hits limits, the system falls back to:
1. Unsplash API
2. Pexels API
3. Pixabay API
4. Unsplash Source
5. Curated stock images

## Example Queries
- "narendra modi prime minister" → Real photos of Modi
- "business meeting office" → Current business images
- "technology computer digital" → Latest tech images
- "clean city construction" → Real development photos

## Troubleshooting
- **API key invalid**: Check credentials in Google Cloud Console
- **Search engine not found**: Verify Search Engine ID
- **No results**: Try different search terms
- **Rate limit exceeded**: Wait or upgrade to paid tier
