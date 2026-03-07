import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FunctionTool, ToolSet
# Import your tools from your existing tools.py
from tools import get_buyer_status, trigger_idsaya_esignature, submit_lhdn_estamp, check_construction_progress

load_dotenv()

def create_journey_agent():
    # We use InteractiveBrowserCredential to avoid the "MFA Blank Screen" issue
    credential = InteractiveBrowserCredential()
    
    # Connect to your Azure Project
    project_client = AIProjectClient.from_connection_string(
        credential=credential,
        conn_str=os.environ["PROJECT_CONNECTION_STRING"]
    )

    # Wrap your tools so the AI can use them
    user_functions = [
        get_buyer_status, 
        trigger_idsaya_esignature, 
        submit_lhdn_estamp, 
        check_construction_progress
    ]
    
    tools = FunctionTool(user_functions)
    toolset = ToolSet()
    toolset.add(tools)

    # Create the Agent instance in the cloud
    agent = project_client.agents.create_agent(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
        name="Chin-Hin-AI-Concierge",
        instructions=(
            "You are the Chin Hin Homebuyer Concierge. "
            "Use your tools to check buyer status and construction progress. "
            "Guide users through the 7-stage homebuying journey professionally."
        ),
        toolset=toolset
    )
    
    return project_client, agent