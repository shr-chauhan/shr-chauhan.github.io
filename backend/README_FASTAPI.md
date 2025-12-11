# FastAPI Chatbot Backend

This is a FastAPI-based backend for the Shrey Chauhan portfolio chatbot, converted from the original Gradio app.

## Setup

1. **Install dependencies:**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file in the `backend` directory (or root directory):
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   PUSHOVER_TOKEN=your_pushover_token (optional)
   PUSHOVER_USER=your_pushover_user (optional)
   PORT=8000
   ```

3. **Run the FastAPI server:**
   ```bash
   python fastapi_app.py
   ```
   
   Or with uvicorn directly:
   ```bash
   uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload
   ```

   The API will be available at `http://localhost:8000`

4. **API Documentation:**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Frontend Configuration

Update your `.env` file in the root directory to point to the FastAPI backend:

```env
PUBLIC_CHAT_API_URL=http://localhost:8000/chat
```

For production, update this to your deployed FastAPI backend URL.

## API Endpoints

- `GET /health` - Health check endpoint
- `POST /chat` - Chat endpoint
  - Request body:
    ```json
    {
      "message": "Hello",
      "history": []
    }
    ```
  - Response:
    ```json
    {
      "response": "Hello! How can I help you?"
    }
    ```

## Features

- ✅ Uses DOCX resume (`me/shreyresume.docx`) instead of PDF
- ✅ OpenAI function calling for recording user details and unknown questions
- ✅ CORS configured for local development and production
- ✅ Automatic API documentation
- ✅ Type validation with Pydantic
- ✅ Better error handling

## Deployment

For production deployment (Railway, Render, Fly.io, etc.):

1. Set environment variables in your hosting platform
2. Update `PUBLIC_CHAT_API_URL` in your frontend to point to the deployed backend
3. Make sure the `me/` directory with `summary.txt` and `shreyresume.docx` is accessible to the backend

## Troubleshooting

- **Import errors**: Make sure all dependencies are installed (`pip install -r requirements.txt`)
- **DOCX not loading**: Ensure `me/shreyresume.docx` exists in the project root (same level as `backend/`)
- **CORS errors**: Check that your frontend URL is in the `allow_origins` list in `fastapi_app.py`

