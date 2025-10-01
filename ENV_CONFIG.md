# Environment Configuration

This project uses a **single `.env` file** located in the **root directory** for all configuration.

## Why Single .env File?

- ✅ **Simplicity**: One place for all environment variables
- ✅ **Consistency**: Same configuration for Docker and manual setup
- ✅ **Less Confusion**: No duplicate files in different directories
- ✅ **Docker Compatibility**: Works seamlessly with docker-compose

## Configuration Files:

```
garudaco/
├── .env                    # ← Main configuration file (edit this)
├── .env.example           # ← Template for new setups
├── docker-compose.yml     # ← References ./.env
└── backend/
    └── app.py             # ← Reads environment variables via load_dotenv()
```

## Setup Process:

1. Copy `.env.example` to `.env` (if starting fresh)
2. Edit `.env` with your OpenRouter API key and preferred model
3. Run `docker-compose up --build`

## Environment Variables:

- `OPENAI_API_KEY`: Your OpenRouter API key
- `API_MODEL`: The AI model to use for question generation

For detailed setup instructions, see [OPENAI_SETUP.md](OPENAI_SETUP.md).