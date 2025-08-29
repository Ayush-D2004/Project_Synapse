# agent_core.py
# This file creates and configures the conversational AI agent.

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import Tool
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from config import load_api_key
from tools import (
    collect_evidence, 
    ask_for_order_details,
    provide_generic_solution,
    analyze_customer_situation,
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
    log_incident_report,
    analyze_order_discrepancy,
    assess_refund_eligibility,
    check_merchant_substitution_policy,
    validate_customer_complaint
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
        name="analyze_customer_situation",
        func=analyze_customer_situation,
        description="Analyze if the customer has provided enough information to proceed with a solution. Use this to check if you can help them now or need more details."
    ),
    Tool(
        name="provide_generic_solution",
        func=provide_generic_solution,
        description="Provide an immediate solution for the customer's issue. Use this when you have enough information about their problem (wrong order, late delivery, quality issue, etc.)"
    ),
    Tool(
        name="ask_for_order_details",
        func=ask_for_order_details,
        description="Ask for missing order information only when absolutely necessary. Use sparingly - customers don't like repeating themselves."
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
        name="analyze_order_discrepancy",
        func=analyze_order_discrepancy,
        description="Analyze specific order to identify what went wrong. Input: order_id (use 'ORD_001' if not known)"
    ),
    Tool(
        name="assess_refund_eligibility", 
        func=assess_refund_eligibility,
        description="Assess customer's eligibility for refund. Input: 'customer_id,order_id,amount' or just 'refund_assessment' for defaults"
    ),
    Tool(
        name="check_merchant_substitution_policy",
        func=check_merchant_substitution_policy,
        description="Check merchant's policy on item substitutions and alternatives. Input: merchant_id,original_item"
    ),
    Tool(
        name="validate_customer_complaint",
        func=validate_customer_complaint,
        description="Validate customer complaint against order history and delivery records. Input: complaint_details (e.g., 'received wrong order')"
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
        You are a helpful customer service agent for Grab. Your goal is to resolve customer issues QUICKLY and DECISIVELY.

        🎯 GOLDEN RULES:
        1. **Don't over-ask for details** - If customer says "I ordered pizza, got burger, paid ₹400" that's ENOUGH to help them!
        2. **Provide solutions immediately** - Use provide_generic_solution as soon as you understand their issue
        3. **Stop asking for order IDs** - Not every customer remembers their order ID, and that's okay
        4. **Be solution-focused** - Customers want help, not interrogation

        🚀 WORKFLOW:
        1. Customer describes issue → Analyze if you have enough info
        2. If basic details present (what they ordered, what went wrong, rough amount) → Provide solution immediately
        3. Only ask for more details if the issue is completely unclear

        ⚠️ AVOID:
        - Asking for the same information multiple times
        - Saying "order not found in system" (just help them anyway!)
        - Requesting unnecessary details like exact timestamps
        - Being bureaucratic or robotic

        💡 EXAMPLES OF SUFFICIENT INFO:
        ✅ "I ordered pizza but got burger, paid ₹400" → Provide solution now!
        ✅ "Food was cold, order from ABC restaurant" → Provide solution now!
        ✅ "Wrong order delivered, cost ₹500" → Provide solution now!

        Remember: Happy customers matter more than perfect documentation. Be generous with refunds and solutions!
        """
    }
)
