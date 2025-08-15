# No Code Sutra - Python Backend

Agentic AI Workflow Platform powered by LangGraph and Amazon Bedrock.

## Features

- 🧠 **Agentic Workflows**: AI-driven decision making with LangGraph
- 🚀 **FastAPI**: High-performance async API
- 🤖 **Amazon Bedrock Integration**: LLaMA-powered workflow generation
- 📸 **Instagram Integration**: Real social media posting with dynamic content
- 🎨 **Dynamic Background Images**: AI-powered image selection from free APIs
- 📊 **Real-time Execution**: Live workflow monitoring
- 🔄 **Async Processing**: Non-blocking workflow execution
- 🔐 **Security First**: Proper credential management and git history protection

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create `.env` file from `env.example`:
```bash
copy env.example .env
```

Required environment variables:
```env
# Amazon Bedrock (Primary LLM)
AWS_BEARER_TOKEN_BEDROCK=your_bedrock_bearer_token_here
AWS_DEFAULT_REGION=ap-southeast-1
BEDROCK_MODEL_ID=meta.llama3-1-8b-instruct-v1:0

# Instagram Integration
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token

# Cloudinary (for image hosting)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 3. Run Development Server
```bash
python src/main.py
```

Server will be available at: http://localhost:8000

## API Endpoints

### Workflow Generation
- `POST /api/workflows/generate` - Generate agentic workflow from natural language

### Workflow Execution
- `POST /api/workflows/execute` - Execute a workflow
- `GET /api/workflows/{id}/status` - Get workflow status

### Node Registry
- `GET /api/nodes/registry` - List available workflow nodes

### Health Check
- `GET /health` - API health status

## Persistence (New)

- Env: `DATABASE_URL` (defaults to `sqlite:///./nocodesutra.db`)
- Endpoints:
  - `POST /api/workflows/save` — Save or update a workflow
  - `POST /api/executions/save` — Save execution result summary

## Architecture

```
src/
├── main.py                          # FastAPI application
├── services/                        # Business logic
│   ├── aiWorkflowGenerator.py       # AI workflow generation (uses LLMClient)
│   ├── node_dispatcher.py           # Node type → executor mapping (OCP)
│   ├── nodes/                       # Per-node executors (SRP)
│   │   ├── ai_agent.py
│   │   ├── data_node.py
│   │   ├── text_overlay.py
│   │   ├── image_upload.py
│   │   ├── social_media.py
│   │   ├── email.py
│   │   ├── slack.py
│   │   ├── condition.py
│   │   ├── delay.py
│   │   ├── schedule.py
│   │   ├── image_generator.py
│   │   └── seo_optimizer.py
│   ├── instagram_service.py         # Instagram API integration
│   └── langgraph_workflows/
│       └── workflow_executor.py     # Workflow execution engine
```

## Instagram Integration

### Working Features ✅
- **AI Content Generation**: Creates structured content (headlines, bullets, captions, hashtags)
- **Dynamic Background Images**: Automatically selects relevant images from Unsplash, Pexels, Lorem Picsum
- **Text Overlay**: Professional Instagram-optimized text formatting
- **Real Instagram Posting**: Posts directly to Instagram Business accounts
- **Fallback Mechanisms**: Graceful handling of API failures
- **Comprehensive Logging**: Detailed debugging and monitoring

### Workflow Chain
Recommended chain for Instagram posts:
```
aiAgent → textOverlay → imageUpload → instagram_post
```

1. **aiAgent**: Generates structured content (headline, bullets, caption, hashtags)
2. **textOverlay**: Creates image with text overlay and dynamic background
3. **imageUpload**: Uploads image to Cloudinary for public hosting
4. **instagram_post**: Posts to Instagram with image and caption

### Dynamic Background Images
The system automatically:
- Extracts keywords from generated content
- Searches multiple free image APIs (Unsplash, Pexels, Lorem Picsum)
- Selects the most relevant background image
- Applies professional text overlay with Instagram-optimized styling

## Available Nodes

### Core Nodes
- `aiAgent` - AI content generation with structured output
- `data` - Data processing and transformation
- `condition` - Conditional logic and branching
- `delay` - Timing and scheduling

### Instagram Nodes
- `textOverlay` - Creates images with text overlay and dynamic backgrounds
- `imageUpload` - Uploads images to Cloudinary
- `instagram_post` - Posts to Instagram Business accounts

### Social Media Nodes
- `social_media` - Generic social media posting
- `email` - Email sending capabilities
- `slack` - Slack message posting

### Content Nodes
- `blog_writer` - Blog content generation
- `seo_optimizer` - SEO optimization
- `image_generator` - AI image generation

## Security Features

### ✅ Implemented Security Measures
- **Environment Variables**: Secure credential management
- **Git History Protection**: Automatic .env exclusion
- **Input Validation**: Comprehensive data sanitization
- **Error Handling**: Secure error messages without sensitive data
- **API Rate Limiting**: Respects external API limits

### 🔒 Privacy Protection
- **Local Processing**: Sensitive data stays on your servers
- **No Data Mining**: We don't collect or analyze your content
- **Secure APIs**: All external API calls use proper authentication

## Development

### Code Style
```bash
black src/
isort src/
flake8 src/
```

### Testing
```bash
pytest tests/
```

### Running Tests
```bash
# Test Instagram integration
python test_instagram_service.py

# Test workflow execution
python test_workflow_execution.py

# Test environment setup
python test_env_setup.py
```

## Documentation

### Setup Guides
- **[Instagram Setup Guide](INSTAGRAM_SETUP_GUIDE.md)** - Complete Instagram integration setup
- **[Bedrock Setup Guide](BEDROCK_SETUP_GUIDE.md)** - Amazon Bedrock configuration
- **[LLM Setup Guide](LLM_SETUP_GUIDE.md)** - Language model configuration

### Implementation Details
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Technical implementation overview

## Troubleshooting

### Common Issues
1. **Instagram API Errors**: Check access token and permissions
2. **Bedrock Connection Issues**: Verify AWS credentials and region
3. **Image Upload Failures**: Validate Cloudinary credentials
4. **Workflow Execution Errors**: Check node configuration and data flow

### Debug Tools
- **Comprehensive Logging**: All operations are logged with detailed information
- **API Health Checks**: Monitor external API status
- **Error Recovery**: Automatic fallback mechanisms for failures

## Performance

### Optimizations
- **Async Processing**: Non-blocking workflow execution
- **Image Caching**: Reduces API calls for repeated images
- **Rate Limiting**: Respects external API quotas
- **Resource Management**: Efficient memory and CPU usage

### Monitoring
- **Real-time Status**: Live workflow execution monitoring
- **Performance Metrics**: Response times and success rates
- **Error Tracking**: Comprehensive error logging and reporting 