from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from openai import OpenAI
import json
import os
import requests

load_dotenv(override=True)

app = Flask(__name__)

# Configure CORS - Update with your actual portfolio domain
CORS(app, origins=[
    "https://shr-chauhan.github.io",
    "http://localhost:4321",  # For local development
    "http://localhost:3000"   # Alternative local port
])

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
        
        # Load profile data from environment variables or files
        self.linkedin = os.getenv("LINKEDIN_PROFILE", "")
        self.summary = os.getenv("PROFILE_SUMMARY", "")
        
        # Try to load from files if environment variables are not set
        if not self.summary:
            try:
                with open("me/summary.txt", "r", encoding="utf-8") as f:
                    self.summary = f.read()
            except FileNotFoundError:
                print("Warning: me/summary.txt not found. Using default summary.")
                self.summary = """Shrey Chauhan is a Senior Engineering Manager at Quantum, where he leads the Unified Surveillance Platform (USP) engineering team. USP is Quantum's optimized hyperconverged infrastructure solution for large-scale video surveillance.

Before this, he was one of the founding engineers at EnCloudEn, where he led engineering for virtual desktop, private cloud, and HCI platforms. He joined as the second engineer, became Director of Engineering, and helped grow a 15-member team that built the technology foundation that ultimately led to EnCloudEn's acquisition by Quantum.

He graduated from NIT Trichy in 2014 with a degree in Computer Science. During college, he led the dance team as its president, and many of his leadership qualities trace back to that experience. He loves building systems, solving problems, and playing 1-minute chess between tasks. He's also passionate about sports."""
        
        if not self.linkedin:
            try:
                from pypdf import PdfReader
                reader = PdfReader("me/Profile.pdf")
                self.linkedin = ""
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        self.linkedin += text
            except (FileNotFoundError, ImportError):
                print("Warning: LinkedIn profile PDF not found or pypdf not installed.")

    def handle_tool_call(self, tool_calls):
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name}", flush=True)
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
You are given a summary of {self.name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer to any question, use your record_unknown_question tool to record the question that you couldn't answer, even if it's about something trivial or unrelated to career. \
If the user is engaging in discussion, try to steer them towards getting in touch via email; ask for their email and record it using your record_user_details tool."""

        system_prompt += f"\n\n## Summary:\n{self.summary}\n\n## LinkedIn Profile:\n{self.linkedin}\n\n"
        system_prompt += f"With this context, please chat with the user, always staying in character as {self.name}."
        return system_prompt
    
    def chat(self, message, history):
        messages = [{"role": "system", "content": self.system_prompt()}] + history + [{"role": "user", "content": message}]
        done = False
        while not done:
            response = self.openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools
            )
            if response.choices[0].finish_reason == "tool_calls":
                message_obj = response.choices[0].message
                tool_calls = message_obj.tool_calls
                results = self.handle_tool_call(tool_calls)
                messages.append(message_obj)
                messages.extend(results)
            else:
                done = True
        return response.choices[0].message.content

# Initialize the chatbot
me = Me()

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.json
        message = data.get('message')
        history = data.get('history', [])
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        response = me.chat(message, history)
        return jsonify({"response": response})
    except Exception as e:
        print(f"Error in chat endpoint: {e}", flush=True)
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "name": "Shrey Chauhan Chatbot API"})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)

