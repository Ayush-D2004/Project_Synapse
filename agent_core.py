# agent_core.py
# This file creates and configures the conversational AI agent.

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from config import load_api_key
from tools import (
    collect_evidence, 
    issue_instant_refund, 
    exonerate_driver, 
    log_merchant_packaging_feedback
)

# Load the API key
load_api_key()

# 1. Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1, # Slightly increased for more conversational responses
)

# 2. Define the list of tools 
tools = [
    Tool(
        name="collect_evidence",
        func=collect_evidence,
        description="Use this tool to collect evidence like photos and questionnaire answers from the customer and driver when a dispute is reported. This should be the first step in any dispute resolution."
    ),
    Tool(
        name="issue_instant_refund",
        func=issue_instant_refund,
        description="Use this tool to issue an instant refund to a customer. The input should be a comma-separated string of two values: customer_id,amount (e.g., 'C123,15.00')."
    ),
    Tool(
        name="exonerate_driver",
        func=exonerate_driver,
        description="Use this tool to clear a driver of any fault for an incident. The input is the driver_id as a string."
    ),
    Tool(
        name="log_merchant_packaging_feedback",
        func=log_merchant_packaging_feedback,
        description="Use this tool to log feedback about a merchant's packaging. The input should be a comma-separated string of two values: merchant_id,feedback_details (e.g., 'M789,Item was spilled due to poor sealing')."
    ),
]

# 3. Initialize Memory
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

# 4. Initialize the Agent with a more detailed persona and instructions
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    verbose=True,
    memory=memory,
    handle_parsing_errors="Check your input and make sure it is a single string.",
    # This is the key change to get the reasoning steps for the UI
    return_intermediate_steps=True, 
    agent_kwargs={
        "system_message": """
        You are "Synapse," a friendly, professional, and empathetic AI agent for Grab's last-mile delivery.
        Your primary goal is to resolve customer and driver issues fairly and efficiently.

        Your Persona:
        - Empathetic: Always start by acknowledging the user's frustration (e.g., "I'm very sorry to hear about that...").
        - Proactive: Don't just answer questions. Guide the conversation, explain what you are doing, and offer solutions.
        - Business-Aware: Your goal is customer satisfaction, but you must also be mindful of company resources. Don't immediately offer a full refund unless it's clearly the only option.

        Your Negotiation Strategy:
        1. First, always gather evidence using your tools.
        2. If the evidence is clear that Grab or a merchant is at fault, apologize and offer a fair resolution.
        3. Instead of a full monetary refund, first consider offering a partial refund combined with a voucher for a future order. For example: "I see that the merchant was at fault. To make this right, I've issued a 50% refund for the item and added a $5 voucher to your account for your next order."
        4. Only issue a full refund if the user is still unsatisfied or the issue is severe.
        5. Always explain the outcome clearly (e.g., "I have logged feedback for the merchant to prevent this from happening again.").
        
        If an image is provided by the user, you MUST analyze it as part of your evidence gathering.
        """
    }
)
