# 🔑 Setting Up OpenRouter API for AI-Powered Questions

## Quick Setup (Recommended)

### Step 1: Get Your OpenRouter API Key

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

### Step 2: Configure Your Environment

1. **Open the `.env` file:**
   ```bash
   # Navigate to the project root directory
   cd garudaco
   
   # Edit the .env file (in the same directory as docker-compose.yml)
   nano .env  # or use your preferred editor
   ```

2. **Update the configuration:**
   ```bash
   # Replace with your actual OpenRouter API key
   OPENAI_API_KEY=sk-or-v1-your_actual_key_here
   
   # Choose your preferred model (see options below)
   API_MODEL=deepseek/deepseek-chat-v3.1:free
   ```

### Step 3: Choose Your AI Model

Popular free models available:
```bash
# Free Models (Recommended for testing)
API_MODEL=deepseek/deepseek-chat-v3.1:free
API_MODEL=microsoft/phi-3-mini-128k-instruct:free
API_MODEL=meta-llama/llama-3.1-8b-instruct:free

# Paid Models (Higher quality, costs credits)
API_MODEL=anthropic/claude-3.5-sonnet
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