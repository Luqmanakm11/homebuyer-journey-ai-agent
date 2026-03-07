import streamlit as st
import requests

# 1. Page Configuration
st.set_page_config(
    page_title="Chin Hin Homebuyer Portal", 
    page_icon="🏡", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PRODUCTION-GRADE LOGIN FLOW ---
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if not st.session_state.logged_in_user:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🏡 Chin Hin Group</h1>", unsafe_allow_html=True)
        st.subheader("Homebuyer Digital Concierge")
        st.info("Welcome back! Please enter your credentials to access your property dashboard.")
        
        buyer_id_input = st.text_input("Buyer ID", placeholder="e.g. USER-2189")
        password_input = st.text_input("Password", type="password")
        
        if st.button("Secure Login", use_container_width=True, type="primary"):
            if buyer_id_input and password_input == "password123": 
                st.session_state.logged_in_user = buyer_id_input
                st.rerun()
            else:
                st.error("Invalid credentials. Please try again.")
    st.stop()

# --- 3. DYNAMIC DATA SETUP (For Demo) ---
buyer_id = st.session_state.logged_in_user

# Visual Progress Mapping
stage_mapping = {
    "1_LOAN_APPROVED": 0.15,
    "2_SPA_READY": 0.30,
    "3_PENDING_ESTAMP": 0.45,
    "4_CONSTRUCTION_ACTIVE": 0.60,
    "5_BILLING_STARTED": 0.75,
    "6_READY_FOR_VP": 0.90,
    "7_KEY_HANDOVER": 1.0
}
# Defaulting to Stage 6 for your demo user
current_stage_key = "6_READY_FOR_VP" 
progress_val = stage_mapping.get(current_stage_key, 0.5)

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://www.chinhin.com/wp-content/uploads/2021/03/logo-chinhin.png", width=150) # Placeholder for real logo
    st.title("👤 My Profile")
    st.success(f"Buyer: **{buyer_id}**")
    st.write("**Property:** AVA-85-367")
    
    st.divider()
    st.title("🔗 Quick Actions")
    st.link_button("✍️ Sign SPA (iDsaya)", "https://idsaya.my/", use_container_width=True)
    st.link_button("📑 View LHDN Stamp", """https://stamps.hasil.gov.my/stamps/?isStampsSite=true&lang=ms&refererUrl=https%3A%2F%2Fstamps.hasil.gov.my%2Fstamps%2F""", use_container_width=True)
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in_user = None
        st.session_state.messages = []
        st.rerun()

# --- 5. MAIN DASHBOARD ---
st.title(f"Welcome back, {buyer_id}")

# Status Metrics (The "Production" Look)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Unit ID", "AVA-85-367")
col2.metric("Document Status", "SPA Signed ✅")
col3.metric("LHDN Stamping", "Completed ✅")
col4.metric("Balance Due", "RM 0.00", delta="-RM 5,200")

st.divider()

# Progress Section
st.subheader("🏗️ Your Homeownership Journey")
st.progress(progress_val, text=f"Current Milestone: {current_stage_key.replace('_', ' ')}")

st.divider()

# --- 6. CONTEXT-AWARE AI CHAT ---
st.subheader("💬 AI Property Concierge")
st.caption("Ask me about your billing, construction photos, or key handover process.")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Display history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input
if prompt := st.chat_input("How can I help you today?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Accessing Chin Hin ERP..."):
            try:
                # Security Injection: Ensure AI only talks about THIS buyer
                secure_prompt = (
                    f"SYSTEM: You are the dedicated concierge for {buyer_id}. "
                    f"ONLY provide information regarding {buyer_id}. "
                    f"USER MESSAGE: {prompt}"
                )
                
                response = requests.post("http://127.0.0.1:8000/chat", json={"message": secure_prompt})
                reply = response.json().get("reply", "Technical error: No response from AI Brain.")
                
                st.markdown(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"⚠️ Connection Error: Please ensure your FastAPI server is running. ({e})")