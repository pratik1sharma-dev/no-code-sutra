# LLM Setup Guide - Free Alternatives to OpenAI

## 🎯 Cost Comparison
- **OpenAI GPT-4**: ~$30 per 1M tokens
- **Together AI**: ~$0.20 per 1M tokens (150x cheaper!)
- **Hugging Face**: Free tier available
- **Ollama**: Completely free (local)

## 🚀 Quick Setup Options

### Option 1: Ollama (Recommended - Completely Free)

**Install Ollama:**
```bash
# Windows (using winget)
winget install Ollama.Ollama

# Or download from: https://ollama.ai/download
```

**Pull a model:**
```bash
ollama pull llama3.1
# or
ollama pull mistral
# or
ollama pull codellama
```

**Configure environment:**
```bash
# Copy env.example to .env
cp env.example .env

# Edit .env to use Ollama
USE_OLLAMA=true
OLLAMA_MODEL=llama3.1
```

### Option 2: Hugging Face (Free Tier)

**Get API token:**
1. Go to https://huggingface.co/
2. Create account
3. Go to Settings → Access Tokens
4. Create new token

**Configure environment:**
```bash
HUGGINGFACE_API_TOKEN=your_token_here
HF_MODEL_ID=meta-llama/Llama-3.1-8B-Instruct
```

### Option 3: Together AI (Very Cheap)

**Get API key:**
1. Go to https://together.ai/
2. Sign up
3. Get API key from dashboard

**Configure environment:**
```bash
TOGETHER_API_KEY=your_api_key_here
```

## 📊 Model Performance Comparison

| Model | Cost | Speed | Quality | Setup |
|-------|------|-------|---------|-------|
| Ollama (Llama 3.1) | Free | Fast | Good | Easy |
| Together AI | $0.20/1M | Very Fast | Excellent | Easy |
| Hugging Face | Free | Medium | Good | Medium |
| OpenAI GPT-4 | $30/1M | Fast | Best | Easy |

## 🔧 Installation Commands

```bash
# Install new dependencies
pip install -r requirements.txt

# For Ollama (if not using winget)
# Download from https://ollama.ai/download

# Test your setup
python -c "
from src.services.aiWorkflowGenerator import AIWorkflowGenerator
generator = AIWorkflowGenerator()
print('LLM Provider:', type(generator.llm).__name__ if generator.llm else 'None')
"
```

## 🎯 Recommended Setup for Development

1. **Start with Ollama** (free, local)
2. **Add Together AI** as backup (very cheap)
3. **Keep OpenAI** as last resort

## 💡 Tips

- **Ollama**: Best for development and testing
- **Together AI**: Best for production (cheap + good quality)
- **Hugging Face**: Good free option with rate limits
- **OpenAI**: Only use for critical features that need best quality

## 🚨 Troubleshooting

**Ollama not working:**
```bash
# Check if Ollama is running
ollama list

# Restart Ollama service
ollama serve
```

**Hugging Face rate limits:**
- Free tier has 30,000 requests/month
- Consider upgrading to Pro ($9/month) for more

**Together AI issues:**
- Check API key in dashboard
- Verify model availability 