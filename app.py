# app.py
# This file creates the Streamlit user interface for our agent.

import streamlit as st
from PIL import Image
from agent_core import agent 
from langchain_core.messages import HumanMessage, AIMessage

# --- Page Configuration ---
st.set_page_config(
    page_title="Project Synapse Demo",
    page_icon="🧠",
    layout="wide"
)

# --- Grab-themed CSS Styling ---
st.markdown("""
<style>
    .stApp { background-color: #F7F7F7; }
    .stButton>button { background-color: #00B14F; color: white; border-radius: 8px; border: none; padding: 10px 16px; }
    .stButton>button:hover { background-color: #008E3E; color: white; }
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: 2px solid #F0F0F0; }
    h1, h2, h3 { color: #333333; }
    .stExpander { border: 1px solid #E0E0E0; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- Sidebar Content ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Grab_logo.svg/2560px-Grab_logo.svg.png", width=150)
    st.title("Project Synapse")
    st.subheader("AI Last-Mile Coordinator")
    st.markdown("---")
    st.markdown(
        "This prototype demonstrates how the Synapse agent can resolve last-mile "
        "delivery disruptions by reasoning with text and image evidence."
    )
    st.info(
        "**Demo Scenario: Damaged Package**\n\n"
        "1. Describe the problem in the chat.\n"
        "2. Upload a photo of the evidence.\n"
        "3. Click the 'Send' button."
    )
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        if 'memory' in st.session_state:
            st.session_state.memory.clear()
        st.rerun()

# --- Main Chat Interface ---

if "messages" not in st.session_state:
    st.session_state.messages = []
if "memory" not in st.session_state:
    st.session_state.memory = agent.memory

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message:
            st.image(message["image"], width=200)
        if "reasoning" in message and message["reasoning"]:
            with st.expander("Show Reasoning"):
                st.json(message["reasoning"])

with st.form(key="chat_form", clear_on_submit=True):
    user_prompt = st.text_input("Describe the disruption...", key="prompt_input")
    uploaded_image = st.file_uploader("Upload an image for evidence", type=["png", "jpg", "jpeg"], key="image_uploader")
    submit_button = st.form_submit_button(label='Send')

if submit_button and user_prompt:
    user_message = {"role": "user", "content": user_prompt}
    
    # The content for the LLM is a list of parts (text and optional image)
    agent_input_content = [user_prompt]
    
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        user_message["image"] = image
        agent_input_content.append(image)
    
    st.session_state.messages.append(user_message)
    
    with st.chat_message("user"):
        st.markdown(user_prompt)
        if uploaded_image is not None:
            st.image(image, width=200)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        reasoning_placeholder = st.empty()
        
        with st.spinner("Synapse is thinking..."):
            # Manually pass the history to the agent for context
            # This prevents the agent from trying to save the image to its text-only memory
            response = agent.invoke({
                "input": agent_input_content,
                "chat_history": st.session_state.memory.chat_memory.messages
            })
            
            final_output = response['output']
            intermediate_steps = response.get('intermediate_steps', [])
            
            message_placeholder.markdown(final_output)

            # Manually save only the text parts of the conversation to memory
            st.session_state.memory.chat_memory.add_messages([
                HumanMessage(content=user_prompt),
                AIMessage(content=final_output)
            ])

            reasoning_data = []
            for step in intermediate_steps:
                action, observation = step
                reasoning_data.append({
                    "Step": f"Thought: {action.log.strip().split('Action:')[0]}",
                    "Action": {"Tool": action.tool, "Tool Input": action.tool_input},
                    "Observation": observation
                })
            
            if reasoning_data:
                with reasoning_placeholder.expander("Show Reasoning"):
                    st.json(reasoning_data)

    assistant_message = {
        "role": "assistant", 
        "content": final_output,
        "reasoning": reasoning_data
    }
    st.session_state.messages.append(assistant_message)
