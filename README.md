# No Code Sutra 🚀

**The First Agentic AI Workflow Platform** - Turn your ideas into intelligent automation workflows instantly.

## 🌟 What Makes Us Different

While other no-code platforms offer simple if/then automation, **No Code Sutra** provides **agentic workflows** powered by AI that can:

- 🧠 **Make intelligent decisions** based on context
- 🔍 **Research and analyze** data dynamically  
- ✍️ **Create personalized content** for each situation
- 🎯 **Learn and adapt** over time
- 🔄 **Handle complex branching** logic
- 📸 **Generate dynamic visual content** with AI-powered image selection

## 🏗️ Architecture

```
Frontend (TypeScript/React) 
    ↓ API calls
Backend (Python + LangGraph) ← Agentic AI workflows
    ↓ AI calls
Amazon Bedrock (LLaMA) + Instagram Graph API
```

### Frontend
- **React 18** + **TypeScript** for type safety
- **Tailwind CSS** for modern, responsive design
- **React Flow** for visual workflow builder
- **Zustand** for state management

### Backend  
- **FastAPI** for high-performance async API
- **LangGraph** for agentic workflow orchestration (with a modular NodeDispatcher)
- **Amazon Bedrock/OpenAI via LLMClient** for intelligent decision making
- **Instagram Graph API** for social media automation
- **Dynamic Image APIs** (Unsplash, Pexels, Lorem Picsum) for content generation

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd no-code-sutra
```

### 2. Start Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend will be available at: http://localhost:3000

### 3. Start Backend
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1  # PowerShell
# OR .\venv\Scripts\activate.bat  # Command Prompt

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
copy env.example .env
# Edit .env with your credentials

# Start the server
python src/main.py
```
Backend will be available at: http://localhost:8000

### 4. Test Instagram Integration
1. Visit http://localhost:3000
2. Type: "Create an Instagram post about AI trends with dynamic background"
3. Watch AI generate content and select relevant background images
4. Review the generated workflow
5. Execute and post to Instagram!

## 📸 Instagram Integration Features

### ✅ **Working Features**
- **AI Content Generation** - Uses LLMClient (Bedrock/OpenAI) with structured outputs
- **Dynamic Background Images** - Automatically selects relevant images from free APIs
- **Text Overlay** - Professional text formatting with Instagram-optimized styling
- **Cloudinary Upload** - Image hosting with signed uploads
- **Real Instagram Posting** - Posts directly to Instagram Business accounts
- **Fallback Mechanisms** - Graceful handling of API failures
- **Security** - Proper credential management and git history cleaning

### 🎨 **Content Generation**
- **Structured Content** - Headlines, bullet points, captions, hashtags
- **Platform Optimization** - Instagram-specific formatting and sizing
- **Visual Enhancement** - Professional text overlay with modern styling
- **Dynamic Images** - Context-aware background image selection

### 🔧 **Technical Implementation**
- **Multi-API Image Search** - Unsplash, Pexels, Lorem Picsum fallback
- **Error Handling** - Comprehensive logging and recovery
- **Rate Limiting** - Respects API limits and quotas
- **Content Validation** - Ensures Instagram compliance

## 🧠 Agentic Workflow Examples

### Instagram Content Workflow
```
User: "Create an Instagram post about AI trends with dynamic background"

AI Agents:
1. Content Research Agent
   - Analyzes current AI trends
   - Identifies engaging topics
   - Researches relevant hashtags

2. Content Creator Agent
   - Generates structured content (headline, bullets, caption)
   - Optimizes for Instagram engagement
   - Creates platform-specific formatting

3. Visual Content Agent
   - Extracts keywords from content
   - Searches multiple image APIs
   - Selects most relevant background image
   - Applies professional text overlay

4. Instagram Publishing Agent
   - Validates content compliance
   - Posts to Instagram Business account
   - Tracks post performance
```

### Lead Generation Workflow
```
User: "Find construction companies in NYC and send them personalized emails"

AI Agents:
1. Lead Research Agent
   - Searches LinkedIn, websites, directories
   - Analyzes company size, projects, contact info
   - Decides which companies to target

2. Lead Qualification Agent  
   - Scores potential value
   - Analyzes company fit
   - Decides which leads to pursue

3. Email Campaign Agent
   - Creates unique email for each company
   - Adapts tone and content based on company profile
   - Optimizes subject lines and messaging

4. Execution Agent
   - Sends emails at optimal times
   - Tracks responses
   - Adapts strategy based on results
```

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run lint         # Run linter
```

### Backend Development
```bash
cd backend
python src/main.py   # Start development server
black src/           # Format code
isort src/           # Sort imports
flake8 src/          # Run linter
pytest tests/        # Run tests
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 Available AI Agents

### 1. Instagram Content Agent
- **Capabilities**: Content generation, image selection, text overlay, Instagram posting
- **Use Cases**: Social media marketing, brand promotion, content creation

### 2. Lead Research Agent
- **Capabilities**: Web search, LinkedIn analysis, lead scoring
- **Use Cases**: Finding prospects, qualifying leads, market research

### 3. Content Creator Agent  
- **Capabilities**: Blog writing, social media, SEO optimization
- **Use Cases**: Content marketing, social media management

### 4. Email Campaign Agent
- **Capabilities**: Email personalization, campaign management, A/B testing
- **Use Cases**: Email marketing, customer outreach

### 5. Data Analyzer Agent
- **Capabilities**: Data processing, insight generation, reporting
- **Use Cases**: Business intelligence, performance analysis

## 🎯 Key Features

### For Users
- ✅ **Natural Language Input** - Describe what you want in plain English
- ✅ **Instant Workflow Generation** - AI creates workflows in seconds
- ✅ **Visual Workflow Builder** - Drag-and-drop customization
- ✅ **Real-time Execution** - Monitor workflows as they run
- ✅ **Intelligent Agents** - AI makes decisions and adapts
- ✅ **Dynamic Visual Content** - AI-powered image selection and text overlay
- ✅ **Social Media Integration** - Direct posting to Instagram and other platforms

### For Developers
- ✅ **TypeScript Frontend** - Type-safe, modern React
- ✅ **Python Backend** - FastAPI with LangGraph
- ✅ **Extensible Architecture** - Easy to add new agents
- ✅ **Comprehensive API** - RESTful endpoints with docs
- ✅ **Production Ready** - Scalable and maintainable
- ✅ **Security First** - Proper credential management and git history protection

## 🔐 Security & Privacy

### ✅ **Security Features**
- **Environment Variables** - Secure credential management
- **Git History Protection** - Automatic .env exclusion
- **API Key Rotation** - Support for credential regeneration
- **Private Repository** - Enhanced access control
- **Input Validation** - Comprehensive data sanitization

### 🔒 **Privacy Protection**
- **Local Processing** - Sensitive data stays on your servers
- **No Data Mining** - We don't collect or analyze your content
- **Secure APIs** - All external API calls use proper authentication
- **Audit Logging** - Track all system activities

## 🚀 Deployment

### Frontend (Vercel)
```bash
cd frontend
npm run build
# Deploy to Vercel
```

### Backend (Railway/Heroku)
```bash
cd backend
# Deploy to Railway or Heroku
# Set environment variables:
# - AWS_BEARER_TOKEN_BEDROCK
# - INSTAGRAM_ACCESS_TOKEN
# - CLOUDINARY_CLOUD_NAME
# - CLOUDINARY_API_KEY
# - CLOUDINARY_API_SECRET
```

## 📚 Documentation

### Setup Guides
- **[Instagram Setup Guide](backend/INSTAGRAM_SETUP_GUIDE.md)** - Complete Instagram integration setup
- **[Bedrock Setup Guide](backend/BEDROCK_SETUP_GUIDE.md)** - Amazon Bedrock configuration
- **[LLM Setup Guide](backend/LLM_SETUP_GUIDE.md)** - Language model configuration

### Implementation Details
- **[Implementation Summary](backend/IMPLEMENTATION_SUMMARY.md)** - Technical implementation overview
- **[Backend README](backend/README.md)** - Backend-specific documentation

## 📚 Additional Docs
- Project Concerns & Actions: `docs/PROJECT_CONCERNS_AND_ACTIONS.md`
- Workflow Builder UI Improvements: `docs/WORKFLOW_BUILDER_UI_IMPROVEMENTS.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: [Available in /backend/docs]
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**No Code Sutra** - The future of intelligent automation is here! 🚀 