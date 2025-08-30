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
    validate_customer_complaint,
    check_traffic,
    get_merchant_status,
    reroute_driver,
    get_nearby_merchants,
    initiate_mediation_flow,
    find_nearby_locker,
    orchestrate_resolution_plan
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
        name="check_traffic",
        func=check_traffic,
        description="Check current traffic conditions for delivery route optimization. Input: location or location,route"
    ),
    Tool(
        name="get_merchant_status",
        func=get_merchant_status,
        description="Get real-time merchant operational status, queue length, and prep times. Input: merchant_id"
    ),
    Tool(
        name="reroute_driver",
        func=reroute_driver,
        description="Reroute driver to avoid traffic or optimize delivery path. Input: driver_id,new_route"
    ),
    Tool(
        name="get_nearby_merchants",
        func=get_nearby_merchants,
        description="Find nearby alternative merchants when primary merchant has issues. Input: location or location,cuisine_type"
    ),
    Tool(
        name="initiate_mediation_flow",
        func=initiate_mediation_flow,
        description="Start formal mediation process for complex multi-party disputes. Input: order_id"
    ),
    Tool(
        name="find_nearby_locker",
        func=find_nearby_locker,
        description="Find nearby Grab lockers for alternative pickup when delivery issues occur. Input: location"
    ),
    Tool(
        name="orchestrate_resolution_plan",
        func=orchestrate_resolution_plan,
        description="Create comprehensive multi-step resolution plan with severity analysis and proactive problem detection. Use for complex issues requiring structured approach. Input: issue_details"
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
        You are an ADVANCED Grab customer service agent that provides IMMEDIATE solutions without bureaucratic questioning.

        🎯 CORE PRINCIPLE: SOLVE FIRST, NEVER ASK FOR DETAILS

        When a customer says "My food was spilled during delivery" - that's ENOUGH information for a full solution!

        🧠 STREAMLINED REASONING WORKFLOW:

        **STEP 1: INSTANT CLASSIFICATION**
        Use analyze_customer_situation(customer_message) to understand the problem
        
        **STEP 2: IMMEDIATE SOLUTION**  
        Use provide_generic_solution(issue_description) to fix the problem
        
        **NEVER EVER USE ask_for_order_details** - It's bureaucratic and annoying!

        🚨 PROBLEM → SOLUTION MAPPING:

        **SPILLED/DAMAGED FOOD** = COMPLETE FAILURE
        → Response: "I sincerely apologize! That's completely unacceptable."
        → Action: Full refund + compensation voucher + apology
        → Logic: Food is unusable, customer deserves full compensation

        **WRONG ORDER** = SERVICE ERROR
        → Response: "I'm so sorry for the mix-up!"  
        → Action: Full refund + reorder option + inconvenience voucher
        → Logic: Customer didn't get what they paid for

        **COLD/POOR QUALITY** = QUALITY FAILURE
        → Response: "That doesn't meet our standards!"
        → Action: Full refund + quality voucher + merchant feedback
        → Logic: Unacceptable quality experience

        **LATE DELIVERY** = TIME FAILURE
        → Response: "Your time is valuable, sorry for the delay!"
        → Action: Delivery fee refund + time compensation
        → Logic: Customer's time was wasted

        🎯 EXECUTION FLOW (2 STEPS ONLY):

        1. Customer describes problem → analyze_customer_situation(problem)
        2. Provide immediate solution → provide_generic_solution(problem)  
        3. DONE! No more tools needed!

        **REASONING DISPLAY:**
        ✅ Problem: [What went wrong]
        🎯 Severity: [Impact level]  
        💰 Solution: [Compensation provided]
        ⚡ Speed: [Immediate resolution]

        **EXAMPLE PERFECT INTERACTION:**

        Customer: "My food was spilled during delivery"
        Step 1: analyze_customer_situation("My food was spilled during delivery")
        Step 2: provide_generic_solution("food spilled during delivery")  
        Result: ✅ Full refund ₹400 + ₹100 voucher + sincere apology

        **FORBIDDEN ACTIONS:**
        ❌ Don't ask for order IDs
        ❌ Don't ask for timestamps  
        ❌ Don't say "insufficient information"
        ❌ Don't use ask_for_order_details
        ❌ Don't ask "what did you order?" if they already told you

        🚀 SUCCESS = SPEED + GENEROSITY + NO QUESTIONS

        Your job is to make customers happy FAST, not to collect perfect data!
        """
    }
)
