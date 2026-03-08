import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
# Fixed the import here to the correct langchain package
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.agent_toolkits import FileManagementToolkit

from tools import (
    get_buyer_status, 
    trigger_idsaya_esignature, 
    submit_lhdn_estamp, 
    check_construction_progress,
    search_market_trends,
    get_idsaya_espa_guide,     
    get_lhdn_stamping_guide    
)

load_dotenv()

# --- FIX 1: Move memory outside so it persists across API calls ---
demo_memory = {}

def get_session_history(session_id: str):
    if session_id not in demo_memory:
        demo_memory[session_id] = ChatMessageHistory()
    return demo_memory[session_id]

def setup_agent():
    llm = ChatOpenAI(
        base_url=os.environ.get("OPENAI_BASE_URL"),
        api_key=os.environ.get("OPENAI_API_KEY"),
        model=os.environ.get("OPENAI_MODEL_NAME"),
        # temperature=0
    )

    # MCP-STYLE FILESYSTEM
    working_directory = os.path.join(os.getcwd(), "project_docs")
    if not os.path.exists(working_directory): os.makedirs(working_directory)
    
    file_toolkit = FileManagementToolkit(
        root_dir=working_directory,
        selected_tools=["read_file", "list_directory"]
    )

    tools = [
        get_buyer_status, 
        trigger_idsaya_esignature, 
        submit_lhdn_estamp, 
        check_construction_progress,
        search_market_trends,
        get_idsaya_espa_guide,     
        get_lhdn_stamping_guide    
    ] + file_toolkit.get_tools()

    prompt = ChatPromptTemplate.from_messages([
        ("system", (
            "You are the Lead Concierge for Chin Hin Group. You have access to three data layers:\n"
            "1. INTERNAL ERP: Use for buyer-specific status and legal signatures.\n"
            "2. PROJECT DOCS: Use to read house rules, policies, and GovTech guides from local files.\n"
            "3. LIVE WEB: Use to check market news or bank interest rates.\n\n"
            "Rules: Always check buyer status before legal steps. If a user asks about 'rules' or 'steps', "
            "list files first to find the right document. Be professional.\n\n"
            "CRITICAL HTML PARSING RULE: You have access to a local file system via tools. Some files may be "
            "raw `.html`. When you read an HTML file, completely ignore the formatting, CSS, and JavaScript tags. "
            "Extract ONLY the human-readable text to answer the user's questions about guides like iDsaya or LHDN."
        )),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # Using AgentExecutor to run the tools and handle parsing errors gracefully
    executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

    return RunnableWithMessageHistory(
        executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )