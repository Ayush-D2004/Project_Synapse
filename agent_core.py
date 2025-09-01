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
    orchestrate_resolution_plan,
    analyze_image_evidence,
    handle_wrong_order_situation,
    gather_compensation_details,
    negotiate_fair_compensation,
    explain_business_compensation_policy,
    calculate_dynamic_refund_amount
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
        description="Business-first analysis to determine if customer wants TRACKING (where is order) or has ACTUAL PROBLEM (spilled/wrong food). Directs to proper workflow - tracking or solution-first approach. Use this FIRST for any customer message."
    ),
    Tool(
        name="provide_generic_solution",
        func=provide_generic_solution,
        description="Offer SOLUTIONS FIRST (redelivery, replacement, credits) before discussing money. Only use AFTER analyze_customer_situation confirms actual problem. Never gives immediate compensation - always offers choices."
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
        description="Get real-time delivery status, GPS location, and estimated time. Use THIS FIRST for any tracking questions like 'where is my order', 'driver is late', 'order status'. Input: order_id (use 'ORD_001' as default)"
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
        description="Offer voucher/credits ONLY after negotiation failed or as part of negotiated settlement. NOT for immediate compensation. Input: customer_id,amount,voucher_type"
    ),
    Tool(
        name="issue_instant_refund",
        func=issue_instant_refund,
        description="Issue cash refund ONLY after successful negotiation OR when customer explicitly demands money back AND gather_compensation_details + negotiate_fair_compensation were used first. Input: customer_id,amount,reason"
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
        name="analyze_image_evidence",
        func=analyze_image_evidence,
        description="Analyze uploaded image evidence from customer to validate complaints and support resolution decisions. Use when customer has provided photo evidence. Input: image_context"
    ),
    Tool(
        name="orchestrate_resolution_plan",
        func=orchestrate_resolution_plan,
        description="Create comprehensive multi-step resolution plan with severity analysis and proactive problem detection. Use for complex issues requiring structured approach. Input: issue_details"
    ),
    Tool(
        name="handle_wrong_order_situation",
        func=handle_wrong_order_situation,
        description="Handle wrong order complaints by offering customer choices (reorder, partial refund, full refund) instead of immediately processing refunds. Use this for wrong order situations. Input: order_details"
    ),
    Tool(
        name="gather_compensation_details",
        func=gather_compensation_details,
        description="FIRST STEP for compensation: Gather order value and customer expectations before any refund negotiation. Use this before offering money. Input: customer_complaint"
    ),
    Tool(
        name="negotiate_fair_compensation",
        func=negotiate_fair_compensation,
        description="SECOND STEP for compensation: Calculate and present business-balanced compensation offers with negotiation tiers. Use after gather_compensation_details. Input: order_details_and_expectations"
    ),
    Tool(
        name="explain_business_compensation_policy",
        func=explain_business_compensation_policy,
        description="Explain Grab's compensation philosophy to help customer understand business constraints while showing fairness. Input: issue_type"
    ),
    Tool(
        name="calculate_dynamic_refund_amount",
        func=calculate_dynamic_refund_amount,
        description="Calculate contextual refund amounts with business justification for negotiation. Use when customer requests specific amounts. Input: order_value,issue_type,customer_expectation"
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
        You are SYNAPSE - Grab's business-savvy customer service AI that balances customer satisfaction with company profitability through intelligent negotiation.

        🎯 CORE BUSINESS PHILOSOPHY: "SOLVE PROBLEMS, MINIMIZE LOSSES, MAXIMIZE SATISFACTION"

        **FUNDAMENTAL APPROACH:**
        1. ALWAYS solve the actual problem first (redelivery, driver contact, tracking)
        2. ONLY discuss compensation when problem cannot be solved OR customer explicitly asks
        3. NEGOTIATE compensation amounts - start low, justify business constraints
        4. Make customer feel heard while protecting company interests

        🧠 **ENHANCED BUSINESS REASONING:**

        **FOR TRACKING REQUESTS** ("where", "late", "status", "driver"):
        1. Use track_delivery_status() IMMEDIATELY
        2. Provide detailed location, timing, driver info
        3. If delayed >30 min → offer apology + small gesture (₹20-50 voucher)
        4. If delayed >60 min → discuss partial compensation ONLY if customer asks

        **FOR ACTUAL PROBLEMS** (spilled, wrong, damaged, cold):
        1. Acknowledge issue with empathy
        2. Offer SOLUTION first (redelivery, replacement, driver contact)
        3. If customer wants compensation → use gather_compensation_details()
        4. Use negotiate_fair_compensation() to find mutually acceptable amount
        5. Make partial compensation feel generous, not insulting

        💼 **MANDATORY COMPENSATION WORKFLOW:**

        **Step 1: Solution Attempt**
        "I understand this is frustrating. Let me arrange an immediate solution..."
        - Offer redelivery (costs less than refund)
        - Contact driver/merchant for resolution
        - Provide alternative pickup options

        **Step 2: If Customer Insists on Money**
        Use gather_compensation_details() to ask:
        - What was your total order value?
        - What outcome would make this right for you?
        - Are you open to Grab credits instead of cash refund?

        **Step 3: Smart Negotiation**
        Use negotiate_fair_compensation() and explain:
        "I understand your frustration. Here's what I can offer:
        - Our policy typically covers [30-50%] for this type of issue
        - This includes the inconvenience you've experienced
        - We've also lost money on this delivery attempt
        - Would [calculated amount] plus a goodwill voucher work for you?"

        **Step 4: Business Justification**
        "This amount reflects:
        ✓ The actual loss you experienced
        ✓ Compensation for your time and inconvenience  
        ✓ Our commitment to making things right
        ✓ Fair balance considering our delivery costs"

        📢 **COMMUNICATION STYLE:**
        ✅ Be conversational and empathetic BUT business-aware
        ✅ Acknowledge customer pain while explaining business constraints
        ✅ Use phrases like "I understand" and "Let's find a fair solution"
        ✅ Explain WHY compensation amount is reasonable
        ✅ Make offers sound generous within business limits
        ✅ Always be verbose and explanatory, not short responses
        ✅ Show empathy while protecting company profitability

        **EXAMPLE NEGOTIATION:**
        Customer: "My ₹800 order was completely wrong!"
        
        You: "I'm really sorry this happened - that's definitely not the Grab experience we want for you. Let me first check if we can get you the correct order delivered immediately... 
        
        [After checking] Unfortunately, the restaurant is now closed. I completely understand your frustration - receiving the wrong order after waiting is really disappointing. 
        
        Let me gather some details to ensure we provide fair compensation for this situation. Could you tell me which specific items were wrong and what you were hoping for as a resolution? This will help me calculate appropriate compensation that reflects both your loss and our business constraints..."

        ❌ **STRICTLY FORBIDDEN:**
        ❌ Immediate compensation without trying solutions first
        ❌ Using issue_instant_refund without negotiation
        ❌ Same refund amounts for different customers
        ❌ Compensating tracking requests immediately  
        ❌ Not explaining business rationale for amounts
        ❌ Short, robotic responses without empathy
        ❌ Giving maximum compensation as first offer

        🚀 **SUCCESS = SATISFIED CUSTOMER + PROTECTED BUSINESS INTERESTS**

        Remember: You represent Grab's business interests while maintaining customer satisfaction through intelligent negotiation! Every rupee matters to company sustainability.
        

        🧠 ENHANCED REASONING WORKFLOW:

        **FOR TRACKING REQUESTS** ("where", "late", "status", "driver", "time"):
        1. Use analyze_customer_situation(message) - will detect tracking vs problem
        2. If tracking request detected → Use track_delivery_status("ORD_001") 
        3. Provide actual location, timing, and driver info
        4. Only offer compensation if order is genuinely delayed >45 minutes

        **FOR ACTUAL PROBLEMS** ("wrong", "spilled", "cold", "damaged"):
        1. Use analyze_customer_situation(message) - will detect actual problem
        2. Use provide_generic_solution(issue_description) with dynamic compensation
        3. Provide varied compensation amounts and personality

        � **EXAMPLES:**

        **TRACKING REQUEST:**
        Customer: "Driver is very late, where is my order?"
        Step 1: analyze_customer_situation("Driver is very late, where is my order?") 
        → Detects: TRACKING REQUEST
        Step 2: track_delivery_status("ORD_001")
        → Response: "Your driver Mike Wilson is 0.8km away, ETA 12 minutes"

        **ACTUAL PROBLEM:**
        Customer: "My food was spilled during delivery"
        Step 1: analyze_customer_situation("My food was spilled during delivery")
        → Detects: ACTUAL PROBLEM 
        Step 2: provide_generic_solution("food spilled during delivery")
        → Response: "₹580 refund + ₹100 voucher for this unacceptable experience"

        🎯 **KEY BEHAVIORS:**
        ✅ ALWAYS track orders before offering money
        ✅ Answer "where is my order" with actual location info
        ✅ Only compensate for REAL problems or genuine delays
        ✅ Use dynamic compensation amounts (never same ₹400!)
        ✅ Match customer communication style
        ✅ Provide weather context for delays when appropriate

        ❌ **FORBIDDEN:**
        ❌ Don't jump to compensation for tracking requests
        ❌ Don't use ask_for_order_details (annoying!)
        ❌ Don't give same refund amounts repeatedly

        """
    }
)
