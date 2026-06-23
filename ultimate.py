import os
import re
import tempfile
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from llama_parse import LlamaParse

# Dynamic LLM Provider Imports
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama

# ==========================================
# 1. PAGE CONFIG & AESTHETIC CUSTOMIZATION
# ==========================================
st.set_page_config(
    page_title="NexusPDF AI",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a sleek, modern UI (Glassmorphism & dark gradients)
st.markdown(
    """
    <style>
    /* Global Background Adjustments */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Card / Block Styling for PDFs */
    .pdf-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s, border-color 0.2s;
    }
    .pdf-card:hover {
        border-color: #6366f1;
        transform: translateY(-2px);
    }
    
    /* Status indicators */
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .status-success { background-color: rgba(16, 185, 129, 0.2); color: #10b981; }
    .status-pending { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; }
    
    /* Chat bubbles */
    .user-bubble {
        background-color: #312e81;
        padding: 1rem;
        border-radius: 12px 12px 0px 12px;
        margin: 0.5rem 0;
        border: 1px solid #4338ca;
    }
    .ai-bubble {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 12px 12px 12px 0px;
        margin: 0.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* FIX: Hide the glitchy floating file-uploader error overlay text block */
    div[data-testid="stFileUploaderErrorMessage"] {
        display: none !important;
    }
    /* FIX: Push down file indicator tags out of interaction button range */
    ul[data-testid="stFileUploaderFilesContainer"] {
        padding-top: 10px !important;
        margin-top: 5px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 2. INITIALIZATION & SESSION STATE
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "parsed_docs" not in st.session_state:
    st.session_state.parsed_docs = {}  # filename -> text content
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # list of {"role": x, "content": y, "engine": z}

# ==========================================
# 3. LOGIN GATEWAY
# ==========================================
def login_screen():
    st.markdown("<h1 style='text-align: center; color: #6366f1;'>NexusPDF AI Workspace</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #94a3b8;'>Secure multi-document intelligence engine</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🔑 Authentication")
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submit = st.form_submit_button("Access Workspace", use_container_width=True)
            
            if submit:
                if username == "admin" and password == "password":
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid credentials.")

if not st.session_state.logged_in:
    login_screen()
    st.stop()

# ==========================================
# 4. SIDEBAR CONFIGURATION (Keys & Engine Config)
# ==========================================
with st.sidebar:
    st.title("🛡️ Control Panel")
    
    st.markdown("### 🤖 Select AI Engine")
    provider = st.selectbox(
        "AI Architecture Provider",
        ["Ollama (Local Llama 3)", "Groq Cloud API", "Google Gemini API"]
    )
    
    # Initialize variables to safely reference later
    groq_key = ""
    gemini_key = ""
    selected_model = ""
    
    # Dynamic Key UI based on selection
    if provider == "Groq Cloud API":
        groq_key = st.text_input("GROQ API Key", type="password", value=os.getenv("GROQ_API_KEY", ""))
        selected_model = st.selectbox("Groq Model Layout", ["llama-3.1-8b-instant", "llama-3.3-70b-versatile"])
    elif provider == "Google Gemini API":
        gemini_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
        selected_model = st.selectbox("Gemini Model Layout", ["gemini-1.5-pro", "gemini-1.5-flash"])
    else:
        st.caption("🟢 Running locally via background loop (`localhost:11434`)")
        selected_model = "llama3 (Local)"
        
    st.markdown("---")
    
    # Optional Advanced PDF Parsing Setup (LlamaParse)
    st.markdown("### ⚙️ Parsing Overlays")
    llama_key = st.text_input("LlamaParse Key (Optional)", type="password", value=os.getenv("LLAMA_PARSE_KEY", ""))
    
    st.markdown("---")
    
    # Chat Management Section
    st.markdown("### 💬 Session Controls")
    if st.button("➕ Clear & New Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()
        
    # Visual History Feed
    if st.session_state.chat_history:
        st.markdown("**Recent Interactions:**")
        for msg in reversed(st.session_state.chat_history[-6:]):
            icon = "👤" if msg["role"] == "user" else "🤖"
            truncated = msg["content"][:35] + "..." if len(msg["content"]) > 35 else msg["content"]
            st.caption(f"{icon} {truncated}")
            
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ==========================================
# 5. CORE HELPER FUNCTIONS (Parsing & AI)
# ==========================================
def parse_pdf(file_obj, use_llama=False):
    """Parses PDF bytes using standard PyPDF or advanced LlamaParse."""
    file_obj.seek(0)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_obj.read())
        tmp_path = tmp.name

    try:
        if use_llama and llama_key:
            parser = LlamaParse(api_key=llama_key, result_type="text")
            documents = parser.load_data(tmp_path)
            raw_text = "\n".join([doc.text for doc in documents])
        else:
            loader = PyPDFLoader(tmp_path)
            pages = loader.load_and_split()
            raw_text = "\n".join([page.page_content for page in pages])
        return raw_text
    except Exception as e:
        return f"Error parsing file: {str(e)}"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def query_llm(user_prompt, context_dict, provider_choice):
    """Queries backend configuration with localized safety triggers & conversational awareness."""
    
    # --- HARD GUARDRAIL SYSTEM LAYER ---
    sensitive_pattern = r"\b(suicide|self-harm|depression|depressed|kill myself|end my life|murder|death|die)\b"
    if re.search(sensitive_pattern, user_prompt.lower()):
        return (
            "❤️ **It looks like you might be going through a difficult time. Please know that you are not alone, and there is support available.**\n\n"
            "If you or someone you know in Nepal is experiencing feelings of depression, distress, or self-harm thoughts, please reach out to these confidential, round-the-clock helplines:\n\n"
            "* **Mental Health Helpline (TUTH, Kathmandu):** Call `9813473506`\n"
            "* **National Suicide Prevention Helpline (Government of Nepal):** Call `1166`\n"
            "* **Transcultural Psychosocial Organization (TPO) Nepal:** Call `16600102005` (Toll-Free)\n"
            "* **Emergency Services (Police):** Call `100`\n\n"
            "Please reach out to one of these services or connect with a trusted friend, family member, or healthcare provider right away."
        )

    # Construct dynamic dual-purpose knowledge system prompt
    if context_dict:
        combined_context = ""
        for filename, text in context_dict.items():
            combined_context += f"\n--- DOCUMENT SOURCE: {filename} ---\n{text}\n"
        
        system_prompt = (
            "You are a helpful, empathetic, and sophisticated AI assistant. You have access to user-uploaded document catalogs. "
            "If the user asks questions related to the documents, use the provided context to extract an absolute, synthesized answer, "
            "and clearly mention which file name the information originates from.\n"
            "If the user's prompt is a normal casual query, greeting, or unrelated conversation, ignore the context completely "
            "and converse like a friendly, normal, and engaging chatbot.\n\n"
            f"Context:\n{combined_context}"
        )
    else:
        system_prompt = (
            "You are a friendly, conversational, and highly intelligent AI chatbot. Since the user has not uploaded any documents yet, "
            "chat with them naturally on any topic they wish. If they want to analyze files, kindly guide them to use the drop-zone below."
        )
    
    try:
        if provider_choice == "Groq Cloud API":
            if not groq_key:
                return "⚠️ Key Missing: Please provide your GROQ API Key in the sidebar control panel."
            llm = ChatGroq(temperature=0.4, groq_api_key=groq_key, model_name=selected_model)
            messages = [("system", system_prompt), ("human", user_prompt)]
            response = llm.invoke(messages)
            return response.content
            
        elif provider_choice == "Google Gemini API":
            if not gemini_key:
                return "⚠️ Key Missing: Please provide your Gemini API Key in the sidebar control panel."
            llm = ChatGoogleGenerativeAI(temperature=0.4, google_api_key=gemini_key, model=selected_model)
            full_prompt = f"{system_prompt}\n\nUser Question: {user_prompt}"
            response = llm.invoke(full_prompt)
            return response.content
            
        else:  # Local Ollama
            llm = Ollama(model="llama3", base_url="http://localhost:11434", temperature=0.4)
            full_prompt = f"{system_prompt}\n\nUser Question: {user_prompt}"
            response = llm.invoke(full_prompt)
            return response

    except Exception as e:
        return f"Execution Integration Error via [{provider_choice}]: {str(e)}"

# ==========================================
# 6. MAIN APPLICATION GRAPHICS & INTERFACE
# ==========================================
st.markdown("<h2 style='margin-bottom:0;'>📚 Cross-Document AI Workspace</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: #94a3b8;'>Sandbox Workspace running on: <b>{provider} ({selected_model})</b></p>", unsafe_allow_html=True)

# File Upload Section
uploaded_files = st.file_uploader(
    "Drop documents here to initialize synthesis pipeline", 
    type=["pdf"], 
    accept_multiple_files=True
)

if uploaded_files:
    st.markdown("### 📂 Document Processing Grid")
    
    unparsed_files = [f for f in uploaded_files if f.name not in st.session_state.parsed_docs]
    
    # GLOBAL PARSE ALL BUTTON
    if unparsed_files:
        st.markdown("<div style='margin-bottom: 15px;'>", unsafe_allow_html=True)
        batch_llama = st.checkbox("Use LlamaParse for entire batch processing", key="batch_llama_toggle") if llama_key else False
        
        if st.button(f"⚡ Parse All Documents ({len(unparsed_files)} remaining)", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            for idx, file in enumerate(unparsed_files):
                with st.spinner(f"Batch processing: parsing {file.name}..."):
                    extracted_text = parse_pdf(file, use_llama=batch_llama)
                    st.session_state.parsed_docs[file.name] = extracted_text
                progress_bar.progress((idx + 1) / len(unparsed_files))
            st.success("All documents processed successfully!")
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Grid Blocks View
    cols = st.columns(3)
    for index, file in enumerate(uploaded_files):
        col_target = cols[index % 3]
        
        with col_target:
            is_parsed = file.name in st.session_state.parsed_docs
            badge_class = "status-success" if is_parsed else "status-pending"
            badge_label = "Parsed" if is_parsed else "Ready to Parse"
            
            st.markdown(
                f"""
                <div class="pdf-card">
                    <h4 style="margin:0; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">📄 {file.name}</h4>
                    <p style="font-size:0.8rem; color:#94a3b8; margin: 4px 0 12px 0;">Size: {round(file.size/1024, 1)} KB</p>
                    <span class="status-badge {badge_class}">{badge_label}</span>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            if not is_parsed:
                use_llama = st.checkbox("Use LlamaParse", key=f"llama_check_{file.name}") if llama_key else False
                if st.button(f"⚡ Process {file.name[:10]}...", key=f"btn_{file.name}", use_container_width=True):
                    with st.spinner(f"Extracting structural insights..."):
                        extracted_text = parse_pdf(file, use_llama=use_llama)
                        st.session_state.parsed_docs[file.name] = extracted_text
                    st.rerun()

# ==========================================
# 7. UNIFIED CHAT EXPERIENCE INTERFACE
# ==========================================
st.markdown("---")
st.markdown("### 💬 Semantic Conversation Hub")

# Layout Chat History
for chat in st.session_state.chat_history:
    if chat["role"] == "user":
        st.markdown(f'<div class="user-bubble"><b>You:</b><br>{chat["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-bubble"><b>AI Engine ({chat.get("engine", "Active Core")}):</b><br>{chat["content"]}</div>', unsafe_allow_html=True)

# User input query capture
user_query = st.chat_input("Ask a question, analyze the docs, or say hello...")

if user_query:
    st.markdown(f'<div class="user-bubble"><b>You:</b><br>{user_query}</div>', unsafe_allow_html=True)
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    with st.spinner(f"Processing chat logic via {provider}..."):
        ai_response = query_llm(
            user_prompt=user_query,
            context_dict=st.session_state.parsed_docs,
            provider_choice=provider
        )
        
    st.markdown(f'<div class="ai-bubble"><b>AI Engine ({selected_model}):</b><br>{ai_response}</div>', unsafe_allow_html=True)
    st.session_state.chat_history.append({"role": "assistant", "content": ai_response, "engine": selected_model})
    st.rerun()