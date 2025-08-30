# Railway Deployment Security Guide

## Overview
This guide covers comprehensive security measures implemented for your No Code Sutra backend deployment on Railway.

## 🔒 Security Features Implemented

### 1. Authentication & Authorization
- **JWT Token Authentication**: Secure token-based auth with configurable expiration
- **API Key Authentication**: Master API key for system access
- **Role-based Permissions**: Granular permission system
- **Optional Authentication**: Flexible auth for public/private endpoints

### 2. Rate Limiting
- **Per-user Rate Limits**: Different limits for authenticated vs anonymous users
- **Endpoint-specific Limits**: 
  - Workflow execution: 50/hour
  - Authentication: 10/5min
  - Default: 100/hour
  - API Key users: 1000/hour
- **Automatic Blocking**: Temporary blocks for repeated violations
- **Memory Efficient**: Automatic cleanup of old request records

### 3. Input Validation & Sanitization
- **XSS Protection**: Detects and blocks script injection attempts
- **SQL Injection Prevention**: Filters suspicious SQL patterns
- **Path Traversal Protection**: Blocks directory traversal attempts
- **Request Size Limits**: 10MB maximum request size
- **Content Type Validation**: Only allows safe content types

### 4. Security Headers
- **X-Content-Type-Options**: Prevents MIME sniffing
- **X-Frame-Options**: Prevents clickjacking
- **X-XSS-Protection**: Browser XSS protection
- **Content Security Policy**: Restricts resource loading
- **HSTS**: Forces HTTPS in production
- **Referrer Policy**: Controls referrer information

### 5. CORS Security
- **Restricted Origins**: Only allows specified domains
- **Secure Headers**: Limited allowed headers
- **Credential Control**: Configurable credential sharing

### 6. Logging & Monitoring
- **Security Event Logging**: Tracks failed auth attempts, rate limit violations
- **Request Logging**: Monitors suspicious activity patterns
- **Performance Monitoring**: Detects potential DoS attacks

## 🚀 Railway Deployment Setup

### 1. Environment Variables (Set in Railway Dashboard)

**Required Security Variables:**
```bash
# Generate secure keys using: python -c "import secrets; print(secrets.token_urlsafe(64))"
JWT_SECRET=your-super-secret-jwt-key-64-chars-minimum
MASTER_API_KEY=your-master-api-key-32-chars-minimum

# Environment
ENVIRONMENT=production
DEBUG=false

# CORS (replace with your actual domains)
ALLOWED_ORIGINS=https://your-frontend.vercel.app,https://your-domain.com

# Database (Railway will provide this)
DATABASE_URL=${{Postgres.DATABASE_URL}}

# Rate Limiting
RATE_LIMIT_ENABLED=true
DEFAULT_RATE_LIMIT=100
AUTH_RATE_LIMIT=10
WORKFLOW_RATE_LIMIT=50

# Logging
LOG_LEVEL=INFO
SECURITY_LOG_ENABLED=true
```

### 2. Railway Configuration Files

**railway.toml** (already configured):
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "python backend/src/main.py"
healthcheckPath = "/health"
healthcheckTimeout = 300
restartPolicyType = "on_failure"

[env]
PORT = "8000"
PYTHONPATH = "/app/backend"
```

### 3. Generate Secure Keys

Run this command to generate secure keys:
```bash
python -c "
import secrets
print('JWT_SECRET=' + secrets.token_urlsafe(64))
print('MASTER_API_KEY=' + secrets.token_urlsafe(32))
"
```

## 🛡️ Security Best Practices

### 1. Environment Variables
- ✅ Never commit `.env` files to git
- ✅ Use Railway's environment variable dashboard
- ✅ Rotate keys regularly (monthly recommended)
- ✅ Use different keys for staging/production

### 2. API Key Management
- ✅ Store API keys in Railway environment variables
- ✅ Use different keys for different services
- ✅ Monitor API key usage in logs
- ✅ Implement key rotation strategy

### 3. Database Security
- ✅ Use Railway's managed PostgreSQL
- ✅ Enable SSL connections (automatic with Railway)
- ✅ Regular backups (Railway handles this)
- ✅ Monitor for unusual query patterns

### 4. Network Security
- ✅ Railway provides HTTPS by default
- ✅ Use Railway's private networking for internal services
- ✅ Configure firewall rules if needed
- ✅ Monitor traffic patterns

### 5. Monitoring & Alerting
- ✅ Enable Railway's built-in monitoring
- ✅ Set up log aggregation
- ✅ Monitor error rates and response times
- ✅ Set up alerts for security events

## 🔧 Usage Examples

### 1. API Key Authentication
```bash
curl -H "X-API-Key: your-api-key" \
     https://your-app.railway.app/api/workflows/generate
```

### 2. JWT Authentication
```bash
# Get token (implement login endpoint)
curl -X POST https://your-app.railway.app/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "user", "password": "pass"}'

# Use token
curl -H "Authorization: Bearer your-jwt-token" \
     https://your-app.railway.app/api/workflows/generate
```

### 3. Check Rate Limits
Rate limit information is returned in response headers:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Requests remaining in window
- `X-RateLimit-Reset`: When the limit resets

## 🚨 Security Monitoring

### Key Metrics to Monitor
1. **Failed Authentication Attempts**: High numbers may indicate brute force attacks
2. **Rate Limit Violations**: Unusual spikes may indicate abuse
3. **Slow Requests**: May indicate DoS attempts
4. **Error Rates**: Sudden increases may indicate attacks
5. **Geographic Patterns**: Unusual request origins

### Log Analysis
Security events are logged with structured data:
```
2024-01-01 12:00:00 - Security event: 429 - IP: 1.2.3.4 - Path: /api/workflows/execute
2024-01-01 12:00:01 - Slow request: 15.2s - IP: 1.2.3.4 - Path: /api/workflows/generate
```

## 🔄 Maintenance

### Regular Security Tasks
1. **Weekly**: Review security logs for anomalies
2. **Monthly**: Rotate API keys and JWT secrets
3. **Quarterly**: Update dependencies and security patches
4. **Annually**: Security audit and penetration testing

### Incident Response
1. **Immediate**: Block malicious IPs via Railway dashboard
2. **Short-term**: Rotate compromised keys
3. **Long-term**: Analyze attack patterns and improve defenses

## 📞 Support

For security issues:
1. Check Railway logs first
2. Review this security guide
3. Check application logs for specific errors
4. Contact Railway support for infrastructure issues

## 🔐 Security Checklist

Before deploying to production:

- [ ] Set all required environment variables
- [ ] Generate and set secure JWT_SECRET (64+ characters)
- [ ] Generate and set secure MASTER_API_KEY (32+ characters)
- [ ] Configure ALLOWED_ORIGINS for your frontend domains
- [ ] Set ENVIRONMENT=production
- [ ] Set DEBUG=false
- [ ] Enable rate limiting (RATE_LIMIT_ENABLED=true)
- [ ] Enable security logging (SECURITY_LOG_ENABLED=true)
- [ ] Test authentication endpoints
- [ ] Test rate limiting
- [ ] Verify CORS configuration
- [ ] Check security headers in browser dev tools
- [ ] Monitor logs for the first 24 hours after deployment

Your Railway backend is now secured with enterprise-grade security measures!
