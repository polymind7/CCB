"""
Streamlit-based Claude Chat UI
Stores conversations locally in JSON files
Run: streamlit run app.py
"""

import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Page config - MUST BE FIRST!
st.set_page_config(
    page_title="Claude Chat",
    page_icon="🤖",
    layout="wide"
)

# Initialize Anthropic client
@st.cache_resource
def get_client():
    return Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

client = get_client()

# Storage directory
STORAGE_DIR = Path("conversations")
STORAGE_DIR.mkdir(exist_ok=True)

# Available models
MODELS = {
    "Claude Sonnet 4.5": "claude-sonnet-4-5-20250929",
    "Claude Opus 4": "claude-opus-4-20250514",
    "Claude Sonnet 4": "claude-sonnet-4-20250514",
}

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "total_cost" not in st.session_state:
    st.session_state.total_cost = 0.0
if "selected_model" not in st.session_state:
    st.session_state.selected_model = "Claude Sonnet 4.5"


def save_conversation():
    """Save current conversation to JSON file"""
    if not st.session_state.conversation_id:
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = STORAGE_DIR / f"{st.session_state.conversation_id}.json"
    data = {
        "id": st.session_state.conversation_id,
        "created": datetime.now().isoformat(),
        "model": st.session_state.selected_model,
        "messages": st.session_state.messages,
        "total_cost": st.session_state.total_cost
    }
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def load_conversation(conversation_id):
    """Load conversation from JSON file"""
    filename = STORAGE_DIR / f"{conversation_id}.json"
    if filename.exists():
        with open(filename, 'r') as f:
            data = json.load(f)
            st.session_state.messages = data.get("messages", [])
            st.session_state.conversation_id = data.get("id")
            st.session_state.total_cost = data.get("total_cost", 0.0)
            st.session_state.selected_model = data.get("model", "Claude Sonnet 4.5")

def list_conversations():
    """List all saved conversations"""
    conversations = []
    for file in STORAGE_DIR.glob("*.json"):
        with open(file, 'r') as f:
            data = json.load(f)
            # Get first user message as preview
            preview = "New conversation"
            for msg in data.get("messages", []):
                if msg["role"] == "user":
                    preview = msg["content"][:50] + "..." if len(msg["content"]) > 50 else msg["content"]
                    break
            conversations.append({
                "id": data.get("id"),
                "created": data.get("created"),
                "preview": preview,
                "cost": data.get("total_cost", 0.0)
            })
    return sorted(conversations, key=lambda x: x["created"], reverse=True)

def calculate_cost(input_tokens, output_tokens, model):
    """Calculate cost based on model pricing"""
    # Pricing per million tokens
    pricing = {
        "claude-sonnet-4-5-20250929": (3, 15),
        "claude-opus-4-20250514": (15, 75),
        "claude-sonnet-4-20250514": (3, 15),
    }

    input_cost, output_cost = pricing.get(model, (3, 15))
    cost = (input_tokens * input_cost / 1_000_000) + (output_tokens * output_cost / 1_000_000)
    return cost

# Sidebar
with st.sidebar:
    st.title("💬 Claude Chat")

    # Model selection
    st.session_state.selected_model = st.selectbox(
        "Model",
        options=list(MODELS.keys()),
        index=list(MODELS.keys()).index(st.session_state.selected_model)
    )

    st.divider()

    # New conversation button
    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_id = None
        st.session_state.total_cost = 0.0
        st.rerun()

    st.divider()

    # Conversation history
    st.subheader("💾 Conversations")
    conversations = list_conversations()

    if conversations:
        for conv in conversations[:10]:  # Show last 10
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(
                    f"📄 {conv['preview']}",
                    key=conv['id'],
                    use_container_width=True
                ):
                    load_conversation(conv['id'])
                    st.rerun()
            with col2:
                st.caption(f"${conv['cost']:.3f}")
    else:
        st.info("No saved conversations")

    st.divider()

    # Stats
    st.subheader("📊 Session Stats")
    st.metric("Total Cost", f"${st.session_state.total_cost:.4f}")
    st.metric("Messages", len([m for m in st.session_state.messages if m["role"] == "user"]))

# Main chat interface
st.title("🤖 Claude Chat Interface")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Message Claude..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    # Get Claude response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            # Prepare messages for API
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]

            # Stream response
            with client.messages.stream(
                model=MODELS[st.session_state.selected_model],
                max_tokens=8000,
                messages=api_messages
            ) as stream:
                for text in stream.text_stream:
                    full_response += text
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)

                # Get usage stats
                final_message = stream.get_final_message()
                input_tokens = final_message.usage.input_tokens
                output_tokens = final_message.usage.output_tokens

                # Calculate cost
                cost = calculate_cost(
                    input_tokens,
                    output_tokens,
                    MODELS[st.session_state.selected_model]
                )
                st.session_state.total_cost += cost

                # Show stats
                st.caption(f"Tokens: {input_tokens} in / {output_tokens} out | Cost: ${cost:.4f}")

            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": full_response})

            # Save conversation
            save_conversation()

        except Exception as e:
            st.error(f"Error: {str(e)}")

# Footer
st.divider()
st.caption("💾 Conversations saved locally in 'conversations/' directory")
