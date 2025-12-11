# Chatbot Setup Guide

This guide explains how to set up and deploy the personality chatbot feature for your portfolio website.

## Architecture Overview

The chatbot consists of two parts:
1. **Frontend**: React component (`src/components/ChatBot.tsx`) integrated into your Astro site
2. **Backend**: API endpoint that handles chat requests

## Backend Hosting Options

Since GitHub Pages only serves static files, you need to host the backend separately. Here are your options:

### Option 1: Python Backend (Recommended for Production)

Deploy the Python Flask backend (`backend/api.py`) to a cloud service.

**Best Options:**
- **Railway** (Easiest, free tier available): https://railway.app
- **Render** (Free tier available): https://render.com
- **Fly.io** (Free tier available): https://fly.io
- **PythonAnywhere** (Free tier available): https://www.pythonanywhere.com

**Steps for Railway (Recommended):**
1. Sign up at https://railway.app
2. Create a new project
3. Connect your GitHub repository
4. Add a new service → Deploy from GitHub repo
5. Select the `backend` folder
6. Add environment variables:
   - `OPENAI_API_KEY` (required)
   - `PROFILE_SUMMARY` (optional)
   - `LINKEDIN_PROFILE` (optional)
   - `PUSHOVER_TOKEN` (optional)
   - `PUSHOVER_USER` (optional)
7. Railway will auto-detect Python and deploy
8. Copy the deployed URL (e.g., `https://your-app.railway.app`)
9. Set `PUBLIC_CHAT_API_URL` in your Astro project to this URL

### Option 2: Astro API Routes (Local Development Only)

For local testing, you can use Astro's built-in API routes. However, **this won't work on GitHub Pages** since it's static-only.

**Setup:**
1. Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_key_here
   PROFILE_SUMMARY=your_summary_here
   ```
2. Run `npm run dev`
3. The chatbot will use `/api/chat` endpoint automatically

**Note:** This only works locally. For production, you must use Option 1.

## Setup Instructions

### Step 1: Install Dependencies

Already done! The following packages are installed:
- `react`, `react-dom`, `@astrojs/react` - For React component
- `openai` - For OpenAI API integration

### Step 2: Configure Environment Variables

#### For Local Development (Astro API Routes):

Create a `.env` file in the project root:
```env
OPENAI_API_KEY=sk-your-openai-key-here
PROFILE_SUMMARY=Your profile summary text here...
LINKEDIN_PROFILE=Your LinkedIn profile text here...
```

#### For Production (Separate Backend):

1. Deploy the Python backend (see Option 1 above)
2. Create a `.env` file in the project root:
```env
PUBLIC_CHAT_API_URL=https://your-backend-url.railway.app
```

**Important:** Never commit `.env` files to Git! They're already in `.gitignore`.

### Step 3: Update CORS Settings (If Using Python Backend)

If you deploy the Python backend separately, update the CORS origins in `backend/api.py`:

```python
CORS(app, origins=[
    "https://shr-chauhan.github.io",  # Your production site
    "http://localhost:4321",          # Local development
])
```

### Step 4: Test Locally

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Open http://localhost:4321
3. Click the chat button in the bottom-right corner
4. Try asking a question like "Tell me about your work experience"

### Step 5: Deploy

#### Frontend (Astro Site):
- Push to GitHub - GitHub Actions will automatically deploy to GitHub Pages
- Make sure `PUBLIC_CHAT_API_URL` is set if using a separate backend

#### Backend (Python API):
- Follow the deployment steps for your chosen platform (Railway, Render, etc.)
- Update `PUBLIC_CHAT_API_URL` in your Astro project to point to the deployed backend

## Environment Variables Reference

### Frontend (Astro Project)

| Variable | Required | Description |
|----------|----------|-------------|
| `PUBLIC_CHAT_API_URL` | No | URL of the backend API. If not set, uses `/api/chat` (local only) |
| `OPENAI_API_KEY` | Yes* | OpenAI API key (only needed if using Astro API routes) |
| `PROFILE_SUMMARY` | No | Profile summary text |
| `LINKEDIN_PROFILE` | No | LinkedIn profile text |

*Only required if using Astro API routes for local development

### Backend (Python API)

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `PROFILE_SUMMARY` | No | Profile summary (or use `me/summary.txt`) |
| `LINKEDIN_PROFILE` | No | LinkedIn profile (or use `me/Profile.pdf`) |
| `PUSHOVER_TOKEN` | No | For notifications |
| `PUSHOVER_USER` | No | For notifications |
| `PORT` | No | Port to run on (default: 5000) |

## Troubleshooting

### Chatbot not appearing
- Make sure React is properly installed: `npm install`
- Check browser console for errors
- Verify the component is imported in `index.astro`

### "API key not configured" error
- Check that `OPENAI_API_KEY` is set in your `.env` file
- If using separate backend, verify it's set in the backend's environment variables

### CORS errors
- Update CORS origins in `backend/api.py` to include your domain
- Check that `PUBLIC_CHAT_API_URL` is correctly set

### Backend not responding
- Check backend health endpoint: `https://your-backend-url/health`
- Verify backend is deployed and running
- Check backend logs for errors

## Cost Considerations

- **OpenAI API**: Pay-per-use. GPT-4o-mini is very affordable (~$0.15 per 1M input tokens)
- **Backend Hosting**: 
  - Railway: Free tier includes $5/month credit
  - Render: Free tier available (spins down after inactivity)
  - Fly.io: Free tier available
  - PythonAnywhere: Free tier available

## Security Notes

- Never expose your OpenAI API key in client-side code
- Always keep API keys in environment variables
- Use CORS to restrict which domains can access your backend
- Consider rate limiting for production use

## Next Steps

1. Deploy the Python backend to Railway/Render
2. Set `PUBLIC_CHAT_API_URL` environment variable
3. Test the chatbot on your live site
4. Customize the profile summary and system prompt as needed

