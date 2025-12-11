# Quick Start Guide - FastAPI Backend

## Step 1: Create Virtual Environment

```bash
cd backend
python -m venv venv
```

## Step 2: Activate Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

## Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Set Environment Variables

Create a `.env` file in the root directory (or copy from existing):

```env
OPENAI_API_KEY=your_openai_api_key_here
```

## Step 5: Start FastAPI Backend

**Option A: Using the startup script (Windows):**
```powershell
cd backend
.\start_server.ps1
```

**Option B: Manual start (after activating venv):**
```bash
python fastapi_app.py
```

**Option C: Using uvicorn directly:**
```bash
uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload
```

The API will start at `http://localhost:8000`

## Step 6: Update Frontend (Optional)

The frontend is already configured to use `http://localhost:8000/chat` by default.

If you want to use a different URL, create/update `.env` in the root:

```env
PUBLIC_CHAT_API_URL=http://localhost:8000/chat
```

## Step 7: Start Frontend

In a new terminal, from the root directory:

```bash
npm run dev
```

## Verify It's Working

1. Check backend health: Visit `http://localhost:8000/health`
2. Check API docs: Visit `http://localhost:8000/docs`
3. Test the chatbot in your browser at `http://localhost:4321`

## Troubleshooting

- **Port already in use**: Change `PORT=8000` in `.env` or update the port in `fastapi_app.py`
- **Module not found**: Make sure you're in the `backend` directory or install dependencies globally
- **DOCX not found**: Ensure `me/shreyresume.docx` exists in the project root
- **CORS errors**: The frontend URL should be in the `allow_origins` list in `fastapi_app.py`

