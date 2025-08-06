# No Code Sutra Backend - Virtual Environment Setup

## 🐍 Virtual Environment Setup

This project uses a Python virtual environment to isolate dependencies.

### ✅ **Current Status: Virtual Environment Active**

The virtual environment is now set up and active. You can see the `(venv)` prefix in your terminal.

### 🔧 **Setup Commands**

```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# PowerShell:
.\venv\Scripts\Activate.ps1

# Command Prompt:
.\venv\Scripts\activate.bat

# 3. Install dependencies
pip install fastapi uvicorn

# 4. Start the backend
cd src
python main-simple.py
```

### 🚀 **Quick Start (After Setup)**

```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Start the server
cd src
python main-simple.py
```

### 📦 **Dependencies**

The virtual environment contains:
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation (included with FastAPI)

### 🔍 **Verification**

To verify the virtual environment is working:

```bash
# Check if venv is active (should show venv path)
python -c "import sys; print(sys.prefix)"

# Check installed packages
pip list
```

### 🛠️ **Troubleshooting**

**If you see `(venv)` in your terminal**: ✅ Virtual environment is active
**If you don't see `(venv)`**: Run `.\venv\Scripts\Activate.ps1`

**If packages aren't found**: Make sure you're in the virtual environment and run `pip install fastapi uvicorn`

### 🌐 **API Endpoints**

Once the backend is running:
- **Health Check**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/docs
- **Workflow Generation**: http://localhost:8000/api/workflows/generate

### 🔗 **Frontend Integration**

The frontend (http://localhost:5175) will automatically connect to the backend when both are running. 