# Amazon Bedrock Setup Guide

## 🚀 Fastest & Most Reliable LLM for No Code Sutra

### Why Amazon Bedrock?
- ⚡ **Lightning Fast**: 1-3 seconds per workflow generation
- 💰 **Cost Effective**: $0.40 per 1M tokens (~$0.0003 per workflow)
- 🌍 **Global**: Available in Singapore (low latency for India)
- 🛡️ **Enterprise Grade**: 99.9% uptime, production-ready
- 🔒 **Secure**: AWS security standards

## Setup Steps

### 1. AWS Account Setup
```bash
# Create AWS account if you don't have one
# Go to: https://aws.amazon.com/
```

### 2. Enable Bedrock Service
```bash
# Go to AWS Console > Bedrock
# Click "Get started"
# Accept terms and conditions
```

### 3. Enable Model Access
```bash
# In Bedrock Console > Model access
# Enable: "meta.llama3-1-8b-instruct-v1:0"
# This is the cheapest and fastest model
```

### 4. Get Bearer Token
```bash
# In Bedrock Console > API keys
# Create a new API key
# Copy the Bearer Token
```

### 5. Update Environment Variables
```bash
# Copy env.example to .env
cp env.example .env

# Edit .env file with your Bearer Token:
AWS_BEARER_TOKEN_BEDROCK=your_bearer_token_here
AWS_DEFAULT_REGION=ap-southeast-1
BEDROCK_MODEL_ID=meta.llama3-1-8b-instruct-v1:0
```

### 6. Install Dependencies
```bash
pip install boto3==1.34.0
```

### 7. Test Setup
```bash
# Start your server
python -m uvicorn src.main:app --reload

# Test workflow generation
curl -X POST http://localhost:8000/api/workflows/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Create a simple email workflow"}'
```

## Cost Analysis

### Per Workflow (typical):
- **Input tokens**: ~500 (system prompt + user request)
- **Output tokens**: ~1000 (JSON workflow)
- **Total cost**: ~$0.0003 per workflow

### Monthly Costs:
- **100 workflows/day**: $0.90/month
- **1000 workflows/day**: $9/month
- **10,000 workflows/day**: $90/month

## Performance Comparison

| Provider | Speed | Cost per 1M tokens | Reliability |
|----------|-------|-------------------|-------------|
| **Amazon Bedrock** | 1-3 seconds | $0.40 | ⭐⭐⭐⭐⭐ |
| **Ollama (Local)** | 2-3 minutes | $0 | ⭐⭐⭐ |
| **Hugging Face** | 5-30 seconds | Free | ⭐⭐ |
| **OpenAI GPT-4** | 2-5 seconds | $30 | ⭐⭐⭐⭐⭐ |

## Troubleshooting

### Common Issues:

1. **"Invalid Bearer Token" Error**
   ```bash
   # Check your Bearer Token in .env file
   # Ensure it's correctly copied from AWS Console
   ```

2. **"Model not available" Error**
   ```bash
   # Go to Bedrock Console > Model access
   # Enable the Llama 3.1 8B model
   ```

3. **"Region not available" Error**
   ```bash
   # Use ap-southeast-1 (Singapore)
   # Or ap-northeast-1 (Tokyo)
   ```

4. **"Timeout" Error**
   ```bash
   # Check internet connection
   # Increase timeout in code if needed
   ```

## Next Steps

1. **Test with simple workflows**
2. **Monitor costs in AWS Console**
3. **Scale as needed**
4. **Consider production deployment**

## Support

- **AWS Bedrock Documentation**: https://docs.aws.amazon.com/bedrock/
- **AWS Support**: Available with paid plans
- **Community**: AWS Developer Forums
