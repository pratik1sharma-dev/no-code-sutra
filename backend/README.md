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

# Database (Postgres)
# Local
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/nocodesutra
# Supabase example (ensure sslmode=require)
# DATABASE_URL=postgresql://USER:PASSWORD@HOST:6543/postgres?sslmode=require

# Instagram Integration
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token

# Cloudinary (for image hosting)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# Dynamic Background Image APIs (Optional - for enhanced image selection)
UNSPLASH_ACCESS_KEY=your_unsplash_access_key_here
PEXELS_API_KEY=your_pexels_api_key_here
PIXABAY_API_KEY=your_pixabay_api_key_here
```

### 3. Run Development Server
```bash
python src/main.py
```

Server will be available at: http://localhost:8000

## API Endpoints

### Workflow Generation
- `POST /api/workflows/generate` - Generate agentic workflow from natural language

### Workflow Management
- `GET /api/workflows` - List all saved workflows
- `GET /api/workflows/{id}` - Get specific workflow by ID
- `POST /api/workflows/save` - Save or update a workflow
- `DELETE /api/workflows/{id}` - Delete a workflow
- `GET /api/workflows/{id}/executions` - Get execution history for a workflow

### Workflow Execution
- `POST /api/workflows/execute` - Execute a workflow
- `POST /api/executions/save` - Save execution result

### Node Registry
- `GET /api/nodes/registry` - List available workflow nodes

### Health Check
- `GET /health` - API health status

## Persistence (New)

- Env: `DATABASE_URL` (defaults to local Postgres)
- Endpoints:
  - `POST /api/workflows/save` — Save or update a workflow (ORM upsert via merge)
  - `POST /api/executions/save` — Save execution result summary (ORM upsert via merge)

## Architecture

### **Design Philosophy**
We follow a **state-based data flow** pattern that ensures consistency and predictability across all nodes. See [Design Guidelines](DESIGN_GUIDELINES.md) for detailed architecture standards.

### **Data Flow Pattern**
```
AI Workflow Generator → Workflow JSON → Node Config → Workflow Executor → State → Node
     ↓                           ↓              ↓              ↓         ↓      ↓
Generates prompt    → {"config": {"prompt": → config.get() → state['prompt'] → Node reads
                    "Create..."}}           copies to state              from state
```

### **Directory Structure**
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
- **Enhanced Dynamic Background Images**: Automatically selects relevant images from multiple sources (Unsplash, Pexels, Pixabay, curated stock images)
- **Professional Text Overlay**: Instagram-optimized text formatting with mobile-optimized fonts
- **Real Instagram Posting**: Posts directly to Instagram Business accounts
- **Robust Fallback Mechanisms**: Multiple reliable image sources ensure 95%+ success rate
- **Comprehensive Logging**: Detailed debugging and monitoring

### Workflow Chain
Recommended chain for Instagram posts:
```
aiAgent → imageGenerator → textOverlay → imageUpload → instagram_post
```

1. **aiAgent**: Generates structured content (headline, bullets, caption, hashtags)
2. **imageGenerator**: Fetches relevant background image from multiple sources
3. **textOverlay**: Creates image with professional text overlay
4. **imageUpload**: Uploads image to Cloudinary for public hosting
5. **instagram_post**: Posts to Instagram with image and caption

### Enhanced Dynamic Background Images
The system automatically:
- Extracts keywords from generated content
- Searches multiple image APIs (Unsplash, Pexels, Pixabay, Unsplash Source API)
- Uses smart fallback to curated stock images for business, tech, AI, modern themes
- Selects the most relevant background image
- Applies professional text overlay with mobile-optimized fonts
- Works without any API keys (95%+ success rate)

## Available Nodes

### Core Nodes
- `aiAgent` - AI content generation with structured output
- `data` - Data processing and transformation
- `condition` - Conditional logic and branching
- `delay` - Timing and scheduling

### Instagram Nodes
- `imageGenerator` - Fetches relevant background images from multiple sources
- `textOverlay` - Creates images with professional text overlay
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

### 📚 **Documentation Index**
- **[Complete Documentation Index](DOCUMENTATION_INDEX.md)** - All documentation files and their purposes

### Architecture & Design
- **[Design Guidelines](DESIGN_GUIDELINES.md)** - Architecture standards and data flow patterns
- **[Implementation Summary](IMPLEMENTATION_SUMMARY.md)** - Technical implementation overview

### Setup Guides
- **[Instagram Setup Guide](INSTAGRAM_SETUP_GUIDE.md)** - Complete Instagram integration setup
- **[Bedrock Setup Guide](BEDROCK_SETUP_GUIDE.md)** - Amazon Bedrock configuration
- **[LLM Setup Guide](LLM_SETUP_GUIDE.md)** - Language model configuration

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