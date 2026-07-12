import streamlit as st
import tempfile
import os
import json
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.google import Gemini
from pdf_tools import extract_text_from_pdf, get_pdf_info

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    st.error("GOOGLE_API_KEY not found in .env")
    st.stop()

st.set_page_config(
    page_title="Legal Shield",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background-color: #0d1b2a;
    color: #e8eaf0;
    font-family: 'Georgia', serif;
}
h1 {
    color: #ffffff !important;
    font-family: 'Georgia', serif !important;
    font-size: 2.4rem !important;
    text-align: center !important;
    letter-spacing: 3px !important;
    padding-bottom: 12px !important;
    border-bottom: 2px solid #b0bec5 !important;
    margin-bottom: 20px !important;
}
h2, h3 {
    color: #cfd8dc !important;
    font-family: 'Georgia', serif !important;
    letter-spacing: 1px !important;
}
p, div, span, label {
    color: #e8eaf0 !important;
    font-size: 15px !important;
}
.stCaption {
    color: #90a4ae !important;
    text-align: center !important;
    font-style: italic !important;
    font-size: 14px !important;
}
div[data-testid="stFileUploader"] {
    background-color: #1c2e40 !important;
    border: 2px dashed #b0bec5 !important;
    border-radius: 12px !important;
    padding: 16px !important;
}
div[data-testid="stFileUploader"] button {
    background-color: #263d52 !important;
    color: #ffffff !important;
    border: 1px solid #b0bec5 !important;
}
div[data-testid="stFileUploaderDropzoneInstructions"] * {
    color: #cfd8dc !important;
}
div[data-testid="stFileUploaderFile"] {
    background-color: #1c2e40 !important;
    border: 1px solid #546e7a !important;
    border-radius: 8px !important;
}
div[data-testid="stFileUploaderFile"] * {
    color: #ffffff !important;
}
div[data-testid="stFileUploaderFileName"] {
    color: #ffffff !important;
}
div[data-testid="stFileUploaderFileData"] * {
    color: #90a4ae !important;
}
button[data-testid="stFileUploaderDeleteBtn"] {
    color: #ffffff !important;
    background-color: #263d52 !important;
    border-radius: 50% !important;
}
div[data-testid="stFileUploader"] > div > div > div {
    background-color: #1c2e40 !important;
    border: 1px solid #546e7a !important;
    border-radius: 8px !important;
}
div[data-testid="stFileUploader"] > div > div > div * {
    color: #ffffff !important;
}
.stButton > button {
    background-color: #1c2e40 !important;
    color: #ffffff !important;
    border: 1px solid #546e7a !important;
    border-radius: 8px !important;
    font-family: 'Georgia', serif !important;
    font-size: 14px !important;
    letter-spacing: 1px !important;
    padding: 8px 16px !important;
    width: 100% !important;
    transition: all 0.3s ease !important;
}
.stButton > button:hover {
    background-color: #263d52 !important;
    border-color: #b0bec5 !important;
    color: #ffffff !important;
}
div[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left: 4px solid #78909c !important;
    background-color: #1c2e40 !important;
    color: #ffffff !important;
}
div[data-testid="stProgressBar"] > div {
    background-color: #263d52 !important;
    border-radius: 10px !important;
}
div[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #37474f, #b0bec5) !important;
    border-radius: 10px !important;
}
div[data-testid="stMetric"] {
    background-color: #1c2e40 !important;
    border: 1px solid #37474f !important;
    border-radius: 10px !important;
    padding: 14px !important;
    text-align: center !important;
}
div[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-size: 28px !important;
}
div[data-testid="stMetricLabel"] {
    color: #90a4ae !important;
    font-size: 13px !important;
}
div[data-testid="stChatMessage"] {
    background-color: #1c2e40 !important;
    border: 1px solid #37474f !important;
    border-radius: 12px !important;
    margin-bottom: 10px !important;
    padding: 10px !important;
}
div[data-testid="stChatInput"] {
    background-color: #1c2e40 !important;
    border: 1px solid #546e7a !important;
    border-radius: 12px !important;
}
div[data-testid="stChatInput"] textarea {
    background-color: #1c2e40 !important;
    color: #ffffff !important;
    caret-color: #ffffff !important;
}
div[data-testid="stChatInput"] textarea::placeholder {
    color: #90a4ae !important;
}
div[data-testid="stChatInput"] button svg {
    fill: #ffffff !important;
}
hr {
    border-color: #37474f !important;
    margin: 20px 0 !important;
}
div[data-testid="stInfo"] {
    background-color: #1c2e40 !important;
    border-left: 4px solid #78909c !important;
    border-radius: 8px !important;
    color: #ffffff !important;
}
.stSpinner > div {
    border-top-color: #b0bec5 !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Legal Shield</h1>", unsafe_allow_html=True)
st.caption("Upload any contract — I'll tell you if you're being scammed!")


for key, val in {
    "contract_text": "",
    "chat_history" : [],
    "pdf_loaded"   : False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = val


st.markdown("---")
uploaded_file = st.file_uploader("Upload your Contract PDF", type=["pdf"])

if uploaded_file and not st.session_state.pdf_loaded:

    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.read())
        tmp_path = tmp.name

    
    info = get_pdf_info(tmp_path)
    text = extract_text_from_pdf(tmp_path)
    os.unlink(tmp_path)  

    if text and "Error" not in text:
        
        st.session_state.contract_text = text
        st.session_state.pdf_loaded    = True
        st.info(f"Contract loaded — {info['total_pages']} pages")
    else:
        st.error("Could not read PDF.")


def get_agent(contract_text: str):
    return Agent(
        model=Gemini(
            id="gemini-3.5-flash",
            api_key=GOOGLE_API_KEY,
        ),
        instructions=f"""
        You are Legal Shield — an expert AI legal document assistant.

        Here is the contract the user uploaded:
        ---
        {contract_text[:4000]}
        ---

        You can help the user by:
        1. SUMMARIZING the contract in simple bullet points
        2. FINDING risky or unfair clauses — mark them clearly
        3. EXPLAINING difficult legal terms in plain English
        4. SUGGESTING fairer versions of risky clauses
        5. ANSWERING any question about the contract

        Always remind the user: you are an AI, not a real lawyer.

        End every response with:
        ---
        Ask me anything else about this contract!
        """,
        markdown=True,
    )


if st.session_state.pdf_loaded:
    st.markdown("---")
    st.markdown("### Ask Anything About Your Contract")

    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Summarize"):
            st.session_state.quick_prompt = "Please summarize this contract"
    with col2:
        if st.button("Find Risks"):
            st.session_state.quick_prompt = "Find all risky clauses"
    with col3:
        if st.button("Suggest Fixes"):
            st.session_state.quick_prompt = "Suggest improvements for risky clauses"


    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])


    if "quick_prompt" in st.session_state:
        prompt = st.session_state.quick_prompt
        del st.session_state.quick_prompt
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        agent = get_agent(st.session_state.contract_text)
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = agent.run(prompt)
                reply    = response.content
                st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

    
    user_input = st.chat_input("Type your question here...")
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
        agent = get_agent(st.session_state.contract_text)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = agent.run(user_input)
                reply    = response.content
                st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

else:
    st.markdown("""
    <div style='text-align:center; padding:50px 30px;
    border:1px dashed #546e7a; border-radius:14px;
    background-color:#1c2e40; margin-top:30px;'>
        <h2 style='color:#cfd8dc; letter-spacing:2px;'>
            Upload a Contract PDF
        </h2>
        <p style='color:#90a4ae; font-size:15px;'>
            Your document will be instantly analyzed for risks,<br>
            scam patterns, and power imbalance.
        </p>
    </div>
    """, unsafe_allow_html=True)