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
    log_merchant_packaging_feedback,
    check_customer_history,
    check_driver_history,
    check_merchant_history,
    escalate_to_human,
    offer_compensation_voucher,
    track_delivery_status,
    contact_driver,
    contact_merchant,
    analyze_gps_data,
    check_weather_conditions,
    verify_customer_identity,
    log_incident_report
)

# Load the API key
load_api_key()

# 1. Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2, # Balanced for reasoning and consistency
)

# 2. Define the list of tools 
tools = [
    Tool(
        name="collect_evidence",
        func=collect_evidence,
        description="Collect comprehensive evidence including photos, timestamps, GPS data, and statements from customer and driver. Use this first for any dispute."
    ),
    Tool(
        name="check_customer_history",
        func=check_customer_history,
        description="Check the customer's order history, complaint patterns, and account status. Input: customer_id"
    ),
    Tool(
        name="check_driver_history",
        func=check_driver_history,
        description="Check driver's performance ratings, incident history, and current status. Input: driver_id"
    ),
    Tool(
        name="check_merchant_history",
        func=check_merchant_history,
        description="Check merchant's quality ratings, packaging issues, and complaint history. Input: merchant_id"
    ),
    Tool(
        name="track_delivery_status",
        func=track_delivery_status,
        description="Get real-time delivery status, GPS location, and estimated time. Input: order_id"
    ),
    Tool(
        name="analyze_gps_data",
        func=analyze_gps_data,
        description="Analyze GPS coordinates and route data for delivery verification. Input: order_id"
    ),
    Tool(
        name="check_weather_conditions",
        func=check_weather_conditions,
        description="Check weather conditions that might affect delivery. Input: location,timestamp"
    ),
    Tool(
        name="contact_driver",
        func=contact_driver,
        description="Send message or call driver for clarification. Input: driver_id,message"
    ),
    Tool(
        name="contact_merchant",
        func=contact_merchant,
        description="Contact merchant about order issues or preparation delays. Input: merchant_id,message"
    ),
    Tool(
        name="verify_customer_identity",
        func=verify_customer_identity,
        description="Verify customer identity for security purposes. Input: customer_id,verification_method"
    ),
    Tool(
        name="offer_compensation_voucher",
        func=offer_compensation_voucher,
        description="Offer voucher or credits as compensation. Input: customer_id,amount,voucher_type"
    ),
    Tool(
        name="issue_instant_refund",
        func=issue_instant_refund,
        description="Issue instant refund when fault is clearly established. Input: customer_id,amount,reason"
    ),
    Tool(
        name="exonerate_driver",
        func=exonerate_driver,
        description="Clear driver of fault when evidence supports their innocence. Input: driver_id,reason"
    ),
    Tool(
        name="log_merchant_packaging_feedback",
        func=log_merchant_packaging_feedback,
        description="Log merchant feedback for quality improvement. Input: merchant_id,feedback_details"
    ),
    Tool(
        name="log_incident_report",
        func=log_incident_report,
        description="Create detailed incident report for future analysis. Input: incident_type,details,involved_parties"
    ),
    Tool(
        name="escalate_to_human",
        func=escalate_to_human,
        description="Escalate complex cases to human agents. Input: reason,urgency_level,case_summary"
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
        You are "Synapse," Grab's advanced AI customer service agent specializing in ride-hailing and food/grocery delivery disputes.
        You are empathetic, analytical, and solution-oriented, capable of handling complex multi-party scenarios.

        Your Core Capabilities:
        - Comprehensive evidence gathering and analysis
        - Historical pattern recognition for customers, drivers, and merchants
        - Real-time tracking and communication coordination
        - Fair dispute resolution with business impact consideration
        - Proactive problem prevention and quality improvement

        Your Decision-Making Framework:
        1. GATHER INTELLIGENCE: Always start by collecting evidence and checking histories of all parties involved
        2. ANALYZE CONTEXT: Consider weather, traffic, merchant preparation times, and other external factors
        3. VERIFY CLAIMS: Cross-reference customer statements with driver reports, GPS data, and merchant logs
        4. ASSESS FAULT: Determine responsibility fairly based on comprehensive evidence
        5. RESOLVE APPROPRIATELY: Choose the most suitable resolution that satisfies the customer while protecting business interests
        6. PREVENT RECURRENCE: Log feedback and patterns to improve system-wide quality

        Resolution Hierarchy (in order of preference):
        1. Service recovery with vouchers/credits (maintain customer loyalty, lower cost)
        2. Partial refunds with future incentives
        3. Full refunds (only when clearly justified)
        4. Escalation to human agents (complex or sensitive cases)

        Communication Style:
        - Begin with empathy and understanding
        - Explain your investigation process clearly
        - Be transparent about findings and reasoning
        - Offer solutions that feel generous while being cost-effective
        - Always explain next steps and prevention measures

        Special Scenarios to Handle:
        - Food safety issues (immediate escalation protocol)
        - Driver safety concerns (priority handling)
        - Repeat offenders (pattern-based responses)
        - High-value customers (enhanced service recovery)
        - Weather-related delays (proactive communication)
        - Technical app issues (system-level solutions)

        If image evidence is provided, analyze it thoroughly as part of your investigation.
        Always document your findings for continuous improvement of Grab's service quality.
        """
    }
)
