# Chatbot Backend API

This is a Flask-based backend API for the personality chatbot feature on the portfolio website.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a `.env` file:**
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PUSHOVER_TOKEN=your_pushover_token_optional
   PUSHOVER_USER=your_pushover_user_optional
   PROFILE_SUMMARY=your_profile_summary_here
   LINKEDIN_PROFILE=your_linkedin_profile_text_here
   PORT=5000
   ```

3. **Optional: Create profile files**
   - Create a `me/` directory
   - Add `me/summary.txt` with your profile summary
   - Add `me/Profile.pdf` with your LinkedIn profile (if you want to extract from PDF)

## Running Locally

```bash
python api.py
```

The API will be available at `http://localhost:5000`

## Deployment Options

### Option 1: Railway (Recommended - Easy & Free tier available)

1. Create account at [railway.app](https://railway.app)
2. Create a new project
3. Connect your GitHub repository
4. Add environment variables in Railway dashboard
5. Deploy!

### Option 2: Render

1. Create account at [render.com](https://render.com)
2. Create a new Web Service
3. Connect your repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `gunicorn api:app`
6. Add environment variables
7. Deploy!

### Option 3: Fly.io

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Run `fly launch` in the backend directory
3. Add environment variables: `fly secrets set OPENAI_API_KEY=your_key`
4. Deploy: `fly deploy`

### Option 4: PythonAnywhere

1. Upload files to PythonAnywhere
2. Create a web app
3. Set WSGI file to point to `api.py`
4. Add environment variables in the web app settings

## Environment Variables

- `OPENAI_API_KEY` (required): Your OpenAI API key
- `PROFILE_SUMMARY` (optional): Your profile summary text
- `LINKEDIN_PROFILE` (optional): Your LinkedIn profile text
- `PUSHOVER_TOKEN` (optional): For notifications
- `PUSHOVER_USER` (optional): For notifications
- `PORT` (optional): Port to run on (default: 5000)

## API Endpoints

- `POST /chat` - Main chat endpoint
  - Body: `{ "message": "user message", "history": [...] }`
  - Returns: `{ "response": "assistant response" }`

- `GET /health` - Health check endpoint
  - Returns: `{ "status": "ok", "name": "..." }`

## CORS Configuration

Update the `origins` list in `api.py` to include your production domain.

