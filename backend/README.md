# No Code Sutra - Python Backend

Agentic AI Workflow Platform powered by LangGraph and OpenAI.

## Features

- 🧠 **Agentic Workflows**: AI-driven decision making with LangGraph
- 🚀 **FastAPI**: High-performance async API
- 🤖 **OpenAI Integration**: GPT-4 powered workflow generation
- 📊 **Real-time Execution**: Live workflow monitoring
- 🔄 **Async Processing**: Non-blocking workflow execution

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Variables
Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=postgresql://user:password@localhost/nocodesutra
# Cloudinary (for real Instagram posting image hosting)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
# Instagram Access Token (for real posting)
INSTAGRAM_ACCESS_TOKEN=your_instagram_access_token
```

### 3. Run Development Server
```bash
cd src
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

### Workflow Generation
- `POST /api/workflows/generate` - Generate agentic workflow from natural language

### Workflow Execution
- `POST /api/workflows/execute` - Execute a workflow
- `GET /api/workflows/{id}/status` - Get workflow status

### Available Agents
- `GET /api/agents/available` - List available AI agents

## Architecture

```
src/
├── main.py              # FastAPI application
├── services/            # Business logic
│   ├── aiWorkflowGenerator.py     # AI workflow generation
│   └── langgraph_workflows/
│       └── workflow_executor.py   # Workflow execution engine
└── services/langgraph_nodes/
    └── workflow_nodes.py          # Node implementations
```

## New Nodes (Instagram real posting flow)
- `textOverlay` (Data): Renders AI text onto an image and outputs image_data_url/image_url
- `imageUpload` (Integration): Uploads the generated image to Cloudinary and returns a public `image_url`
- `instagram_post` (Social Media): Posts using the public `image_url` (real if token present, else simulation)

Recommended chain when no user-provided image:
- `aiAgent` → `textOverlay` → `imageUpload` → `instagram_post`

See `INSTAGRAM_SETUP.md` for details on tokens and requirements.

## Agentic Workflow Types

1. **Lead Research Agent** - Find and qualify leads
2. **Content Creator Agent** - Generate content and social posts
3. **Email Campaigner Agent** - Send personalized emails
4. **Data Analyzer Agent** - Analyze data and generate insights

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