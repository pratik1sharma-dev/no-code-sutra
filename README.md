# No Code Sutra 🚀

**The First Agentic AI Workflow Platform** - Turn your ideas into intelligent automation workflows instantly.

## 🌟 What Makes Us Different

While other no-code platforms offer simple if/then automation, **No Code Sutra** provides **agentic workflows** powered by AI that can:

- 🧠 **Make intelligent decisions** based on context
- 🔍 **Research and analyze** data dynamically  
- ✍️ **Create personalized content** for each situation
- 🎯 **Learn and adapt** over time
- 🔄 **Handle complex branching** logic

## 🏗️ Architecture

```
Frontend (TypeScript/React) 
    ↓ API calls
Backend (Python + LangGraph) ← Agentic AI workflows
    ↓ AI calls
OpenAI GPT-4
```

### Frontend
- **React 18** + **TypeScript** for type safety
- **Tailwind CSS** for modern, responsive design
- **React Flow** for visual workflow builder
- **Zustand** for state management

### Backend  
- **FastAPI** for high-performance async API
- **LangGraph** for agentic workflow orchestration
- **OpenAI GPT-4** for intelligent decision making
- **PostgreSQL** for workflow storage

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
pip install fastapi uvicorn

# Start the server
cd src
python main-simple.py
```
Backend will be available at: http://localhost:8000

### 4. Test the Platform
1. Visit http://localhost:3000
2. Type: "Find construction companies in NYC and send them personalized emails"
3. Watch AI generate an agentic workflow!
4. Review and customize the workflow
5. Deploy and monitor execution

## 🧠 Agentic Workflow Examples

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

### Content Creation Workflow
```
User: "Create blog posts about AI trends and post them to LinkedIn"

AI Agents:
1. Research Agent
   - Analyzes current AI trends
   - Identifies trending topics
   - Researches relevant data

2. Content Creator Agent
   - Writes engaging blog posts
   - Optimizes for SEO
   - Creates social media variations

3. Publishing Agent
   - Schedules optimal posting times
   - Adapts content for different platforms
   - Monitors engagement
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
python start.py      # Start development server
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

### 1. Lead Research Agent
- **Capabilities**: Web search, LinkedIn analysis, lead scoring
- **Use Cases**: Finding prospects, qualifying leads, market research

### 2. Content Creator Agent  
- **Capabilities**: Blog writing, social media, SEO optimization
- **Use Cases**: Content marketing, social media management

### 3. Email Campaign Agent
- **Capabilities**: Email personalization, campaign management, A/B testing
- **Use Cases**: Email marketing, customer outreach

### 4. Data Analyzer Agent
- **Capabilities**: Data processing, insight generation, reporting
- **Use Cases**: Business intelligence, performance analysis

## 🎯 Key Features

### For Users
- ✅ **Natural Language Input** - Describe what you want in plain English
- ✅ **Instant Workflow Generation** - AI creates workflows in seconds
- ✅ **Visual Workflow Builder** - Drag-and-drop customization
- ✅ **Real-time Execution** - Monitor workflows as they run
- ✅ **Intelligent Agents** - AI makes decisions and adapts

### For Developers
- ✅ **TypeScript Frontend** - Type-safe, modern React
- ✅ **Python Backend** - FastAPI with LangGraph
- ✅ **Extensible Architecture** - Easy to add new agents
- ✅ **Comprehensive API** - RESTful endpoints with docs
- ✅ **Production Ready** - Scalable and maintainable

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
# - OPENAI_API_KEY
# - DATABASE_URL
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: [Coming Soon]
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

---

**No Code Sutra** - The future of intelligent automation is here! 🚀 