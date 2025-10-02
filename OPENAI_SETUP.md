# � Complete Setup Guide - Google OAuth & OpenRouter API

## Quick Setup Overview

This guide covers setting up both Google OAuth authentication and OpenRouter API for AI-powered question generation.

## Part 1: Google OAuth Setup

### 1. Access Google Cloud Console
- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Sign in with your Google account

### 2. Create or Select Project
- **New Project**: Click "New Project" → Enter name → Create
- **Existing Project**: Select from dropdown

### 3. Enable Google Sign-In API
- Navigate to **APIs & Services** → **Library**
- Search for "Google Sign-In API" or "Google+ API"
- Click **Enable**

### 4. Create OAuth 2.0 Credentials
- Go to **APIs & Services** → **Credentials**
- Click **+ CREATE CREDENTIALS** → **OAuth client ID**
- Select **Web application**

### 5. Configure OAuth Settings

**Application Name**: `Garudaco Learning Platform`

**Authorized JavaScript Origins**:
```
http://localhost:3000
```

**Authorized Redirect URIs**:
```
http://localhost:3000
http://localhost:3000/login
```

### 6. Get Your Credentials
After creating, you'll receive:
- **Client ID**: `1234567890-abcdefghijklmnop.apps.googleusercontent.com`
- **Client Secret**: `GOCSPX-abcdefghijklmnopqrstuvwx`

## Part 2: OpenRouter API Setup

### 1. Get Your OpenRouter API Key

1. **Visit OpenRouter:**
   - Go to https://openrouter.ai/
   - Sign up for a free account or login

2. **Get Free Credits:**
   - New accounts get free credits to start
   - No credit card required for free tier

3. **Create API Key:**
   - Go to https://openrouter.ai/keys
   - Click "Create Key"
   - Copy the key (starts with `sk-or-v1-`)

### 2. Choose Your AI Model

Popular free models available:
```bash
# Free Models (Recommended for testing)
API_MODEL=deepseek/deepseek-chat-v3.1:free
API_MODEL=microsoft/phi-3-mini-128k-instruct:free
## Complete Verification Checklist

### Google OAuth Setup
- [ ] Google Cloud project created
- [ ] Google Sign-In API enabled
- [ ] OAuth client ID created
- [ ] Authorized origins configured (`http://localhost:3000`)
- [ ] Redirect URIs configured
- [ ] Client ID added to root `.env`
- [ ] Client Secret added to root `.env`
- [ ] Client ID added to `frontend/.env`

### OpenRouter API Setup
- [ ] OpenRouter account created
- [ ] API key generated
- [ ] API key added to root `.env`
- [ ] Model selected and configured
- [ ] Free credits available or billing set up

### Application Testing
- [ ] Containers restarted after configuration
- [ ] Can access http://localhost:3000
- [ ] Google Sign-In button appears
- [ ] Login flow completes successfully
- [ ] Dashboard loads after authentication
- [ ] Can add topics successfully
- [ ] Can generate assessments successfully
- [ ] Questions are generated with AI

---

🎉 **Congratulations!** Your Garudaco learning platform is fully configured and ready for production use.

## Quick Commands Reference

```bash
# Start application
docker-compose up --build

# Stop application
docker-compose down

# View logs
docker logs garudaco-backend
docker logs garudaco-frontend

# Check container status
docker ps
```

## Need Help?

If you encounter any issues:
1. Check the troubleshooting sections above
2. Verify all environment variables are set correctly
3. Ensure containers are running properly
4. Check browser console for frontend errors
5. Review backend logs for API issues
```

## Part 3: Environment Configuration

### 1. Update Root `.env` File

Create or update the `.env` file in the project root:

```env
# OpenRouter API Configuration
OPENAI_API_KEY=sk-or-v1-your_actual_key_here
API_MODEL=deepseek/deepseek-chat-v3.1:free

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-minimum-32-characters
```

### 2. Update Frontend `.env` File

Create `frontend/.env`:

```env
# Google OAuth for Frontend
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com

# Backend API URL
REACT_APP_API_URL=http://localhost:5000/api
```

## Part 4: Testing Your Setup

1. **Restart Containers**:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

2. **Test Authentication**:
   - Open http://localhost:3000
   - Click "Sign in with Google"
   - Complete OAuth flow
   - Should redirect to dashboard

3. **Test AI Generation**:
   - Add a topic in the dashboard
   - Generate an assessment
   - Verify questions are generated successfully

## Production Deployment

### For Production Domain
When deploying to production (e.g., `https://yourdomain.com`):

**Update Google OAuth Settings**:
```
Authorized Origins: https://yourdomain.com
Redirect URIs: https://yourdomain.com, https://yourdomain.com/login
```

**Update Environment**:
```env
REACT_APP_API_URL=https://yourdomain.com/api
```

## Security Best Practices

### ✅ Do's
- ✅ Use HTTPS in production
- ✅ Keep Client Secret secure (server-side only)
- ✅ Regularly rotate JWT secrets
- ✅ Monitor API usage and costs
- ✅ Set up rate limiting

### ❌ Don'ts
- ❌ Never expose secrets in frontend
- ❌ Don't use HTTP in production
- ❌ Don't commit secrets to version control
- ❌ Don't skip domain validation

## Troubleshooting

### Google OAuth Issues

**Error: "Invalid OAuth Client"**
- Verify Client ID in both `.env` files
- Check that IDs match exactly

**Error: "Redirect URI Mismatch"**
- Add exact URL to Google Console
- No trailing slashes in URLs

**Sign-In Button Not Appearing**
- Check browser console for errors
- Verify network connectivity
- Clear browser cache

### OpenRouter API Issues

**"Invalid API key"**
- Double-check your API key is correct
- Ensure no extra spaces or characters

**"Model not found"**
- Verify the model name is exactly as shown
- Check if model is available

**"Rate limit exceeded"**
- Wait a few minutes before trying again
- Consider using a different model

## Cost Management

### OpenRouter Usage
- Monitor usage on OpenRouter dashboard
- Start with free models for development
- Set up billing alerts for paid models
- Optimize prompts to reduce token usage

### Rate Limits
- **Free models**: Usually 10-20 requests per minute
- **Paid models**: Higher limits based on usage tier
API_MODEL=openai/gpt-4
API_MODEL=google/gemini-pro-1.5
```

### Step 4: Restart the Application

```bash
# If using Docker (recommended)
docker-compose down
docker-compose up --build

# Or if running directly
cd backend
python app.py
```

## Model Comparison

| Model | Cost | Performance | Best For |
|-------|------|-------------|----------|
| `deepseek/deepseek-chat-v3.1:free` | Free | Good | General use, testing |
| `microsoft/phi-3-mini-128k-instruct:free` | Free | Fast | Quick responses |
| `meta-llama/llama-3.1-8b-instruct:free` | Free | Balanced | Code & explanations |
| `anthropic/claude-3.5-sonnet` | Paid | Excellent | Complex reasoning |
| `openai/gpt-4` | Paid | Excellent | High-quality content |

## What Changes After Setup

### Before (Mock Responses):
- ❌ Same pre-written questions every time
- ❌ Limited question variety
- ❌ No difficulty adaptation

### After (Real AI):
- ✅ Fresh, unique questions for each topic
- ✅ Questions adapted to your topic's category
- ✅ Difficulty scaling based on your performance
- ✅ Varied question types (MCQ, coding, fill-in-blanks)
- ✅ Contextual explanations and feedback

## Security Best Practices

✅ **DO:**
- Use the `.env` file method (already configured)
- Keep your API key private
- Monitor your usage regularly

❌ **DON'T:**
- Share your API key publicly
- Commit your API key to version control
- Use paid models without monitoring costs

## Verify It's Working

1. **Check the setup:**
   ```bash
   # Look for this in terminal output when starting
   # Should NOT see "Mock response generated"
   ```

2. **Test question generation:**
   - Go to http://localhost:3000/assessment
   - Generate a new assessment
   - Questions should be unique and contextual

3. **Check for errors:**
   ```bash
   # In backend terminal, you should see:
   # - No "API Error" messages
   # - No "Mock response" logs
   ```

## Cost Management

### Free Tier Limits:
- Free models: No additional cost beyond rate limits
- Paid models: Use credits from your account

### Monitor Usage:
- Check usage at: https://openrouter.ai/activity
- Set up billing alerts if using paid models
- Typical cost: ~$0.001-0.01 per question (paid models)

## Troubleshooting

### Common Issues:

1. **"Mock response generated" still appearing:**
   ```bash
   # Check your API key in .env
   # Ensure it starts with sk-or-v1-
   # Restart the application
   ```

2. **API Error messages:**
   ```bash
   # Verify your API key is valid
   # Check you have credits (for paid models)
   # Try a different model
   ```

3. **Application won't start:**
   ```bash
   # Check .env file exists in project root directory
   # Verify no syntax errors in .env
   # Try: docker-compose down && docker-compose up --build
   ```

### Getting Help:

- OpenRouter Documentation: https://openrouter.ai/docs
- Model Status: https://openrouter.ai/models
- Community Support: https://discord.gg/fVyRaUDgxW

## Advanced Configuration

### Custom Model Settings:
```bash
# In .env, you can also configure:
API_MODEL=your-preferred-model
# Add other OpenRouter parameters as needed
```

### Multiple Model Setup:
- You can change the `API_MODEL` in `.env` anytime
- Restart the application to apply changes
- Different models have different strengths

Your garudaco app is now powered by real AI! 🚀