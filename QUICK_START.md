# Quick Start Guide - Chatbot Integration

## What Was Implemented

✅ React ChatBot component (`src/components/ChatBot.tsx`)
✅ Astro API route for local development (`src/pages/api/chat.ts`)
✅ Python backend API for production (`backend/api.py`)
✅ Integration into portfolio homepage
✅ Comprehensive documentation

## Quick Setup (3 Steps)

### 1. For Local Testing (Using Astro API Routes)

Create `.env` in project root:
```env
OPENAI_API_KEY=sk-your-key-here
```

Run:
```bash
npm run dev
```

### 2. For Production (Recommended)

**Deploy Python Backend:**
1. Go to https://railway.app (or Render/Fly.io)
2. Create new project → Connect GitHub repo
3. Deploy `backend` folder
4. Add environment variable: `OPENAI_API_KEY=your-key`
5. Copy the deployed URL (e.g., `https://your-app.railway.app`)

**Update Frontend:**
Create `.env` in project root:
```env
PUBLIC_CHAT_API_URL=https://your-app.railway.app
```

Push to GitHub - done!

### 3. Test It

- Local: http://localhost:4321
- Production: https://shr-chauhan.github.io

Click the chat button (bottom-right) and start chatting!

## Files Created

- `src/components/ChatBot.tsx` - React chat UI component
- `src/pages/api/chat.ts` - Astro API endpoint (local dev)
- `backend/api.py` - Python Flask backend (production)
- `backend/requirements.txt` - Python dependencies
- `backend/README.md` - Backend deployment guide
- `CHATBOT_SETUP.md` - Comprehensive setup guide

## Important Notes

⚠️ **GitHub Pages is static-only** - You MUST deploy the Python backend separately for production

⚠️ **Never commit `.env` files** - They contain sensitive API keys

✅ **Railway is recommended** - Easiest deployment, free tier available

For detailed instructions, see `CHATBOT_SETUP.md`

