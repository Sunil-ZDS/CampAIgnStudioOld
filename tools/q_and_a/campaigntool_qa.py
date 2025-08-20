# tools/ask_campaign.py

import streamlit as st
import asyncio

# services/chat_service.py
from services.openai_config import get_azure_openai_model
from services.openai_config import create_azure_openai_client

class ChatService:
    def __init__(self, azure_client = None):
        if azure_client is None:
            raise ValueError("An Azure OpenAI client must be provided to ChatService")
        
        self.azure_client = azure_client
        
    async def generate_response(self, user_input: str) -> str:
        try:
            response = await self.azure_client.chat.completions.create(
                model="o4-mini-global",  # Make sure this is the correct deployment name
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for marketing campaign planning."},
                    {"role": "user", "content": user_input}
                ],
                max_completion_tokens=8192,
                temperature=1
            )
            # print("🤖 Raw LLM Response:", response)

            if not response.choices or not response.choices[0].message.content:
                return "⚠️ Empty response from AI model."

            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ Error in generate_response: {e}")
            return f"Error generating response: {str(e)}"
         

async def show_ask_campaign_chat():
    st.markdown("<h2>💬 Ask CampAIgn – Your Marketing Assistant</h2>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Type your question...", key="ask_campaign_input")
    
    # Get Azure client from session state or create one
    if "azure_client" not in st.session_state:
        st.session_state.azure_client = asyncio.run(create_azure_openai_client())

    chat_service = ChatService(azure_client=st.session_state.azure_client)

    if st.button("Send", key="ask_campaign_send") and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            response = await chat_service.generate_response(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

        st.rerun()

#Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f'<div class="user-msg">👤 <b>You: </b> {msg["content"]}</div>', unsafe_allow_html=True)
        else:
            # st.markdown("")
            st.markdown(f'<div class="ai-msg">🧠 <b>CampAIgn: </b> {msg["content"]}</div>', unsafe_allow_html=True)

    if st.button("Clear Chat", key = "ask_campaign_clear"):
        st.session_state.chat_history.clear()
        st.rerun()


def show_ask_campaign():
    st.markdown("<h2>🔍 Ask Campaign</h2>", unsafe_allow_html=True)
    st.info("🚧 Work in progress. This feature will allow users to ask questions about their campaigns soon.")
    
    # Add placeholder or future chat/Q&A interface here

        # Back button
    if st.button("⬅ Back to Tools"):
        st.session_state.current_tool = None
        st.rerun()