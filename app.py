# app.py
# This file creates the Streamlit user interface for our agent.

import streamlit as st
from PIL import Image
from agent_core import agent
from langchain_core.messages import HumanMessage, AIMessage

# --- Image Description Helper ---
def describe_image(image):
    """
    Advanced image analysis for evidence gathering.
    TODO: Replace with actual computer vision model for real deployment.
    """
    # Simulate intelligent image analysis based on common delivery issues
    import random
    
    descriptions = [
        "Image shows damaged food packaging with visible spills and torn container edges, likely due to handling during transport",
        "Photo displays incorrect food items - appears to be burger and fries instead of ordered salad and sandwich",
        "Image reveals wet packaging and water damage, suggesting exposure to rain during delivery",
        "Picture shows driver at correct address with 'recipient not available' door sign, timestamp matches delivery window", 
        "Photo evidence of properly sealed food containers in intact delivery bag, no visible damage or tampering",
        "Image shows traffic congestion and road closure signs that would cause significant delivery delays",
        "Picture displays restaurant kitchen with 'temporarily closed' sign, explaining order cancellation",
        "Photo shows customer location with incorrect address numbering, causing delivery confusion"
    ]
    
    return random.choice(descriptions)

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
        "Advanced AI agent for Grab's customer service that handles ride-hailing "
        "and food/grocery delivery disputes through comprehensive evidence analysis, "
        "pattern recognition, and intelligent resolution strategies."
    )
    st.info(
        "**Enhanced Capabilities:**\n\n"
        "🔍 **Evidence Analysis**: Photos, GPS, timestamps, weather\n"
        "📊 **Pattern Recognition**: Customer, driver, merchant histories\n"
        "🤝 **Smart Resolution**: Fair dispute resolution with business optimization\n"
        "📱 **Real-time Coordination**: Live tracking and communication\n"
        "🛡️ **Quality Assurance**: Continuous improvement through feedback loops\n\n"
        "**Try Different Scenarios:**\n"
        "• 'My food was spilled during delivery'\n"
        "• 'Driver is very late, where is my order?'\n"
        "• 'Wrong items delivered, this isn't what I ordered'\n"
        "• 'Driver says delivered but I never received it'"
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
    agent_input_content = [user_prompt]
    image_description = None
    image = None
    if uploaded_image is not None:
        image = Image.open(uploaded_image)
        image_description = describe_image(image)
        user_message["image"] = image
        user_message["image_description"] = image_description
        agent_input_content.append(image_description)
    st.session_state.messages.append(user_message)

    with st.chat_message("user"):
        st.markdown(user_prompt)
        if image is not None:
            st.image(image, width=200)
        if image_description:
            st.caption(f"Image Description: {image_description}")

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        reasoning_placeholder = st.empty()
        with st.spinner("Synapse is thinking..."):
            # Pass only text and image description to agent
            response = agent.invoke({
                "input": agent_input_content,
                "chat_history": st.session_state.memory.chat_memory.messages
            })
            final_output = response['output']
            intermediate_steps = response.get('intermediate_steps', [])
            message_placeholder.markdown(final_output)

            # Save only text and image description to memory
            memory_messages = [HumanMessage(content=user_prompt)]
            if image_description:
                memory_messages.append(HumanMessage(content=f"Image Description: {image_description}"))
            memory_messages.append(AIMessage(content=final_output))
            st.session_state.memory.chat_memory.add_messages(memory_messages)

            reasoning_text = ""
            for step in intermediate_steps:
                action, observation = step
                thought = action.log.strip().split('Action:')[0].strip()
                action_str = f"Action: {action.tool} (Input: {action.tool_input})"
                observation_str = f"Observation: {observation}"
                reasoning_text += f"Thought: {thought}\n{action_str}\n{observation_str}\n\n"
            if reasoning_text:
                with reasoning_placeholder.expander("Show Reasoning"):
                    st.markdown(reasoning_text)

    assistant_message = {
        "role": "assistant", 
        "content": final_output,
        "reasoning": reasoning_text
    }
    st.session_state.messages.append(assistant_message)
