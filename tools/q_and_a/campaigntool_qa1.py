# tools/ask_campaign.py

import streamlit as st

# services/chat_service.py
from services.openai_config import create_azure_openai_model

class ChatService:
    def __init__(self):
        self.client = create_azure_openai_model()

    async def generate_response(self, user_input: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="o4-mini-global",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant for marketing campaign planning."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=500,
                temperature=1
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error generating response: {str(e)}"
        

async def show_ask_campaign_chat():
    st.markdown("<h2>💬 Ask CampAIgn – Your Marketing Assistant</h2>", unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.text_input("Type your question...", key="chat_input")

    chat_service = ChatService()

    if st.button("Send") and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.spinner("Thinking..."):
            response = await chat_service.generate_response(user_input)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

#Display chat history
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"<div style='text-align:right; color:#1f77b4;'>🧑‍💼 You: {msg['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left; color:green;'>🤖 CampAIgn: {msg['content']}</div>", unsafe_allow_html=True)

# if st.button("Clear Chat"):
#     st.session_state.chat_history.clear()
#     st.rerun()


def show_ask_campaign():
    st.markdown("<h2>🔍 Ask Campaign</h2>", unsafe_allow_html=True)
    st.info("🚧 Work in progress. This feature will allow users to ask questions about their campaigns soon.")
    
    # Add placeholder or future chat/Q&A interface here

        # Back button
    if st.button("⬅ Back to Tools"):
        st.session_state.current_tool = None
        st.rerun()