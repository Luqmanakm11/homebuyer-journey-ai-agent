from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from langchain_agent import setup_agent

# 1. Create the API app
app = FastAPI(title="Chin Hin AI Concierge API")

# --- ADDED: CORS Middleware ---
# This allows your frontend (Streamlit/PowerApps) to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Initialize your agent once
print("Loading Chin Hin AI Brain...")
journey_agent = setup_agent()
print("AI Brain Loaded & Ready!")

# 3. Enhanced Data Format
class ChatRequest(BaseModel):
    message: str
    user_id: str = "DEMO-USER-001" # Default ID if none provided

# 4. The Chat Endpoint
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Pass the message AND the session_id config
        # This is the 'secret sauce' that connects to your demo_memory
        config = {"configurable": {"session_id": request.user_id}}
        
        response = journey_agent.invoke(
            {"input": request.message}, 
            config=config
        )
        
        return {"reply": response["output"]}
    
    except Exception as e:
        print(f"Error: {e}") # Log the error to your terminal
        return {"reply": f"Sorry, I encountered an error: {str(e)}"}