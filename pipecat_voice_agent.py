"""
Simple Voice Agent - Rich Dad Poor Dad Tutor
Using Groq (Cloud LLM) + Groq STT
No transport needed - just direct Streamlit interaction
"""

import streamlit as st
import os
from dotenv import load_dotenv
from groq import Groq

# Import multi-agent system
from agents.orchestrator import OrchestratorAgent

load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# System prompt
SYSTEM_PROMPT = """You are an AI tutor specializing in the book "Rich Dad Poor Dad" by Robert Kiyosaki.

Your role is to:
1. Help students understand key concepts about financial literacy, assets vs liabilities, and wealth building
2. Answer questions about the book's teachings in a conversational, encouraging way
3. Break down complex topics into simple, understandable explanations
4. Be enthusiastic and supportive in teaching financial concepts

Keep responses concise (2-3 sentences).
"""

# Initialize orchestrator
orchestrator = OrchestratorAgent()

# Streamlit UI
st.title("🎙️ Rich Dad Poor Dad Voice Tutor")
st.markdown("**Powered by Groq (llama-3.3-70b-versatile)**")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask me anything about Rich Dad Poor Dad..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get orchestrator response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = orchestrator.process(prompt)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# Sidebar
with st.sidebar:
    st.markdown("### 💡 Try asking:")
    st.markdown("- Teach me about assets and liabilities")
    st.markdown("- What is the difference between rich dad and poor dad?")
    st.markdown("- Quiz me on chapter 3")
    st.markdown("- Search for information about financial freedom")
