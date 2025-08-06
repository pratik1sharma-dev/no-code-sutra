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
├── models/              # Pydantic models
│   └── workflow.py      # Workflow data models
├── services/            # Business logic
│   ├── workflow_generator.py  # AI workflow generation
│   └── workflow_executor.py   # Workflow execution engine
└── agents/              # AI agent implementations
    ├── lead_researcher.py
    ├── content_creator.py
    └── email_campaigner.py
```

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