from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests
from docx import Document  # python-docx library
from pathlib import Path

load_dotenv(override=True)

app = FastAPI(title="Shrey Chauhan Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://shr-chauhan.github.io",
        "http://localhost:4321",
        "http://localhost:3000",
        "http://localhost:5173",  # Vite default
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def push(text):
    """Send notification via Pushover (optional)"""
    if os.getenv("PUSHOVER_TOKEN") and os.getenv("PUSHOVER_USER"):
        try:
            requests.post(
                "https://api.pushover.net/1/messages.json",
                data={
                    "token": os.getenv("PUSHOVER_TOKEN"),
                    "user": os.getenv("PUSHOVER_USER"),
                    "message": text,
                },
                timeout=5
            )
        except Exception as e:
            print(f"Pushover notification failed: {e}")

def record_user_details(email, name="Name not provided", notes="not provided"):
    """Record user contact information"""
    push(f"Recording {name} with email {email} and notes {notes}")
    return {"recorded": "ok"}

def record_unknown_question(question):
    """Record questions that couldn't be answered"""
    push(f"Recording unknown question: {question}")
    return {"recorded": "ok"}

# OpenAI function definitions
record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {"type": "string", "description": "The email address of this user"},
            "name": {"type": "string", "description": "The user's name, if they provided it"},
            "notes": {"type": "string", "description": "Any additional information about the conversation"}
        },
        "required": ["email"],
        "additionalProperties": False
    }
}

record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {"type": "string", "description": "The question that couldn't be answered"}
        },
        "required": ["question"],
    }
}

tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]

class Me:
    def __init__(self):
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.name = "Shrey Chauhan"
        
        # Get project root directory (parent of backend/)
        project_root = Path(__file__).parent.parent
        me_dir = project_root / "me"
        
        # Load summary
        summary_path = me_dir / "summary.txt"
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                self.summary = f.read().strip()
            print(f"✅ Loaded profile summary ({len(self.summary)} characters)")
        except FileNotFoundError:
            print("Warning: me/summary.txt not found. Using default summary.")
            self.summary = "Shrey Chauhan is a Senior Engineering Manager at Quantum, where he leads the Unified Surveillance Platform (USP) engineering team."
        
        # Load resume from DOCX
        self.resume = ""
        resume_path = me_dir / "shreyresume.docx"
        try:
            doc = Document(resume_path)
            self.resume = "\n".join([paragraph.text for paragraph in doc.paragraphs if paragraph.text.strip()])
            print(f"✅ Loaded resume from DOCX ({len(self.resume)} characters)")
        except FileNotFoundError:
            print(f"Warning: {resume_path} not found.")
        except Exception as e:
            print(f"Warning: Could not load resume from DOCX: {e}")

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"🔧 Tool called: {tool_name}", flush=True)
            tool = globals().get(tool_name)
            result = tool(**arguments) if tool else {}
            results.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })
        return results
    
    def system_prompt(self):
        system_prompt = f"""You are acting as {self.name}. You are answering questions on {self.name}'s website, \
particularly questions related to {self.name}'s career, background, skills and experience. \
Your responsibility is to represent {self.name} for interactions on the website as faithfully as possible. \
You are given a summary of {self.name}'s background and resume which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool."""

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## Resume:\n{self.resume}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        max_iterations = 10
        iterations = 0
        
        while not done and iterations < max_iterations:
            iterations += 1
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                temperature=0.7
            )
            
            if response.choices[0].finish_reason == "tool_calls":
                message_obj = response.choices[0].message
                tool_calls = message_obj.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message_obj)
                messages.extend(results)
            else:
                done = True
        
        if not done:
            raise Exception("Maximum iterations reached")
            
        return response.choices[0].message.content

# Initialize the chatbot
me = Me()

# Request/Response models
class ChatRequest(BaseModel):
    message: str
    history: list = []

class ChatResponse(BaseModel):
    response: str

@app.get("/health")
def health():
    return {"status": "ok", "name": "Shrey Chauhan Chatbot API"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        response_text = me.chat(request.message, request.history)
        return ChatResponse(response=response_text)
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}", flush=True)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host='0.0.0.0', port=port)

