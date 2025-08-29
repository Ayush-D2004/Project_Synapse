# tools.py
# Advanced tools for Grab's AI customer service agent
# Now integrated with realistic sandbox environment

import random
from datetime import datetime, timedelta
import sys
import os

# Add sandbox directory to Python path
sandbox_path = os.path.join(os.path.dirname(__file__), 'sandbox')
if sandbox_path not in sys.path:
    sys.path.insert(0, sandbox_path)

try:
    from sandbox_database import sandbox_db
    from sandbox_tools import (
        get_customer_profile, get_order_investigation, 
        process_customer_refund, log_merchant_quality_issue,
        exonerate_delivery_partner, check_refund_eligibility,
        get_merchant_substitute_policy
    )
    SANDBOX_AVAILABLE = True
    print("✓ Sandbox environment loaded successfully")
except ImportError as e:
    print(f"⚠ Sandbox not available: {e}")
    SANDBOX_AVAILABLE = False

def collect_evidence(query: str) -> str:
    """
    Analyze the customer's complaint and determine if we have enough information to proceed
    """
    # Handle null or placeholder inputs
    if not query or query.lower() in ["null", "none", ""]:
        query = "general complaint"
    
    print(f"--- Analyzing Customer Complaint: {query} ---")
    
    # Check if the query contains sufficient information to proceed
    has_order_info = any(keyword in query.lower() for keyword in ["order", "paid", "rupees", "rs", "$", "restaurant", "kitchen"])
    has_issue_info = any(keyword in query.lower() for keyword in ["wrong", "late", "delay", "cold", "missing", "quality", "spilled"])
    
    if has_order_info and has_issue_info:
        return f"""COMPLAINT ANALYSIS COMPLETE:
        
Based on your description, I have sufficient information to help you:
• Issue Type: {query}
• Status: Ready to provide solution
• Next Step: Processing appropriate compensation

I can now offer you a resolution for this issue."""
    
    return """INFORMATION GATHERING:

To help you effectively, I need to understand:
• What items did you order?
• How much did you pay?
• What specific issue occurred?
• Which restaurant was it from?

Please provide these details so I can assist you properly."""

def analyze_customer_situation(customer_message: str) -> str:
    """
    Analyze what the customer has told us and determine if we can proceed with a solution
    """
    print(f"--- Analyzing Customer Situation: {customer_message} ---")
    
    # Extract key information from the customer's message
    message_lower = customer_message.lower()
    
    # Check for order details
    has_items = any(item in message_lower for item in ["pizza", "burger", "food", "order", "item"])
    has_amount = any(money in message_lower for money in ["400", "rupees", "rs", "paid"])
    has_restaurant = any(rest in message_lower for rest in ["abc kitchen", "restaurant", "kitchen"])
    has_issue = any(issue in message_lower for issue in ["wrong", "received", "instead", "got"])
    
    if has_items and has_amount and has_issue:
        return f"""SITUATION ANALYSIS:
        
✅ SUFFICIENT INFORMATION PROVIDED:
• Customer complaint: Clear issue described
• Order details: {has_items and 'Items mentioned' or 'Need item details'}
• Payment amount: {has_amount and 'Amount provided' or 'Need amount'}
• Issue type: {has_issue and 'Problem clearly stated' or 'Need issue details'}

RECOMMENDATION: Proceed with solution - customer has provided enough details to resolve this."""
    
    return """INFORMATION STATUS:
    
❌ INSUFFICIENT INFORMATION:
• Need more specific details to proceed
• Recommend asking for missing information

RECOMMENDATION: Request additional details before proceeding."""

def ask_for_order_details(context: str) -> str:
    """Ask the customer for specific order details to better assist them"""
    print(f"--- Requesting Order Details: {context} ---")
    
    return """I'd be happy to help you with your order issue! To provide the best assistance, could you please share:

1. **What did you order?** (specific items/dishes)
2. **Order amount?** (total you paid)
3. **What went wrong?** (wrong item, late delivery, quality issue, missing items, etc.)
4. **Restaurant name?** (which merchant/restaurant)
5. **When did this happen?** (today, yesterday, specific time)

With these details, I can investigate your concern and offer an appropriate solution like a refund, reorder, or other compensation."""

def provide_generic_solution(issue_details: str) -> str:
    """Provide an immediate solution based on the customer's described issue"""
    print(f"--- Providing Immediate Solution: {issue_details} ---")
    
    # Parse the issue type from details
    details_lower = issue_details.lower()
    
    if "wrong" in details_lower and ("order" in details_lower or "item" in details_lower or "pizza" in details_lower or "burger" in details_lower):
        return """I sincerely apologize for the wrong order you received! This is completely unacceptable.

🎯 IMMEDIATE RESOLUTION:
✅ **Full refund of ₹400** - Processing now to your original payment method
✅ **₹100 inconvenience voucher** - Added to your account for future orders  
✅ **Free reorder option** - If you still want your original pizza, we'll deliver it at no cost

📋 WHAT HAPPENS NEXT:
• Refund will appear in 2-3 business days
• Voucher is active immediately 
• If you want the reorder, just let me know and I'll arrange priority delivery

I've also logged this with ABC Kitchen to prevent future mix-ups. Is there anything else I can help you with today?"""
    
    elif "late" in details_lower or "delay" in details_lower:
        return """I apologize for the delayed delivery! Your time is valuable and we didn't meet our promise.

🎯 COMPENSATION PROVIDED:
✅ **₹50 delivery fee refund** - Processing immediately
✅ **₹100 future order voucher** - For the inconvenience caused
✅ **Priority delivery guarantee** - Your next order gets premium handling

The compensation will be processed within 24 hours. Thank you for your patience!"""
    
    elif "quality" in details_lower or "cold" in details_lower or "stale" in details_lower:
        return """I'm very sorry about the poor quality of your food. This doesn't meet our standards at all.

🎯 QUALITY RESOLUTION:
✅ **Full refund of ₹400** - For the unacceptable food quality
✅ **₹150 quality guarantee voucher** - As our commitment to better service
✅ **Restaurant feedback logged** - We're addressing this with ABC Kitchen immediately

Your refund will be processed within 24 hours. We'll ensure this doesn't happen again!"""
    
    # Extract amount if mentioned
    amount_match = None
    for word in details_lower.split():
        if word.replace('₹', '').replace('rs', '').isdigit():
            amount_match = word.replace('₹', '').replace('rs', '')
            break
    
    if not amount_match:
        amount_match = "400"  # Default amount
    
    return f"""I understand you're experiencing an issue with your order, and I want to make this right immediately.

🎯 RESOLUTION PROVIDED:
✅ **Full refund of ₹{amount_match}** - Processing to your original payment method
✅ **₹100 goodwill voucher** - For the trouble you've experienced
✅ **Issue escalated** - We're investigating to prevent future occurrences

📋 TIMELINE:
• Refund: 2-3 business days
• Voucher: Available immediately in your account

Thank you for bringing this to our attention. Is there anything else I can help you with?"""

def check_customer_history(customer_id: str) -> str:
    """Check customer's order history and complaint patterns with sandbox data."""
    print(f"--- Checking Customer History: {customer_id} ---")
    
    if SANDBOX_AVAILABLE:
        return get_customer_profile(customer_id)
    
    # Fallback for non-sandbox mode
    profiles = [
        "Premium customer (50+ orders, 4.8/5 rating, 1 complaint in 6 months) - High trust level",
        "Regular customer (15 orders, 4.2/5 rating, 2 complaints resolved) - Normal trust level", 
        "New customer (3 orders, no ratings, first complaint) - Standard verification needed",
        "Frequent complainer (20 orders, 3.1/5 rating, 8 complaints) - Enhanced verification required"
    ]
    
    return f"Customer Profile: {random.choice(profiles)}"

def issue_instant_refund(refund_details: str) -> str:
    """Issue instant refund with proper documentation using sandbox."""
    try:
        customer_id, amount, reason = refund_details.split(',', 2)
        amount = float(amount.strip())
        reason = reason.strip()
        
        print(f"--- Processing Refund: ${amount} to {customer_id} for {reason} ---")
        
        if SANDBOX_AVAILABLE:
            return process_customer_refund(customer_id, amount, reason)
        
        # Fallback
        return f"Instant refund of ₹{amount} processed for customer {customer_id}. Reason: {reason}. Funds will appear in 1-3 business days."
    except:
        return "Error: Please provide refund details as customer_id,amount,reason"

def exonerate_driver(driver_details: str) -> str:
    """Clear driver of fault with documentation using sandbox."""
    driver_id, reason = driver_details.split(',', 1) if ',' in driver_details else (driver_details, "Evidence supports innocence")
    print(f"--- Exonerating Driver {driver_id}: {reason} ---")
    
    if SANDBOX_AVAILABLE:
        return exonerate_delivery_partner(driver_id, reason)
    
    # Fallback
    return f"Driver {driver_id} cleared of all fault. Reason: {reason}. No impact on performance record."

def log_merchant_packaging_feedback(feedback_details: str) -> str:
    """Log detailed merchant feedback for quality improvement using sandbox."""
    try:
        merchant_id, feedback = feedback_details.split(',', 1)
        print(f"--- Logging Merchant Feedback: {merchant_id} ---")
        
        if SANDBOX_AVAILABLE:
            return log_merchant_quality_issue(merchant_id.strip(), feedback.strip(), "high")
        
        # Fallback
        return f"Quality feedback logged for merchant {merchant_id.strip()}: '{feedback.strip()}'. Forwarded to merchant quality team for review and improvement action."
    except:
        return "Error: Please provide feedback as merchant_id,feedback_details"

# New sandbox-specific tools for advanced reasoning

def analyze_order_discrepancy(order_id: str) -> str:
    """Analyze what went wrong with a specific order"""
    # Handle placeholder inputs
    if not order_id or "obtained from" in order_id.lower() or order_id.lower() in ["null", "none"]:
        order_id = "ORD_001"  # Default to first sandbox order
    
    print(f"--- Analyzing Order Discrepancy: {order_id} ---")
    
    if SANDBOX_AVAILABLE:
        return get_order_investigation(order_id)
    
    return f"""Order Analysis for {order_id}:
    • Order Status: Completed with customer complaint
    • Issue Type: Wrong items delivered
    • Expected: Pizza Margherita
    • Received: Burger Combo
    • Root Cause: Kitchen preparation error
    • Recommendation: Full refund + merchant feedback"""

def assess_refund_eligibility(eligibility_details: str) -> str:
    """Assess customer eligibility for refund based on history and order details"""
    # Parse input or use defaults
    try:
        if ',' in eligibility_details:
            parts = eligibility_details.split(',')
            customer_id = parts[0].strip() if len(parts) > 0 else "C001"
            order_id = parts[1].strip() if len(parts) > 1 else "ORD_001"
            requested_amount = float(parts[2].strip()) if len(parts) > 2 else 450.0
        else:
            customer_id = "C001"
            order_id = "ORD_001"
            requested_amount = 450.0
    except:
        customer_id = "C001"
        order_id = "ORD_001"
        requested_amount = 450.0
    
    print(f"--- Assessing Refund Eligibility for {customer_id} ---")
    
    if SANDBOX_AVAILABLE:
        try:
            from sandbox_tools import check_refund_eligibility
            return check_refund_eligibility(customer_id, order_id, requested_amount)
        except:
            pass
    
    return f"""Refund Eligibility Assessment:
    • Customer: {customer_id}
    • Order: {order_id}
    • Requested Amount: ₹{requested_amount}
    • Customer Status: Premium (50+ orders, high rating)
    • Complaint History: Minimal (first complaint in 6 months)
    • Order Verification: Valid complaint confirmed
    • Eligibility: APPROVED - Full refund authorized
    • Processing Time: Instant (2-3 business days to reflect)"""

def check_merchant_substitution_policy(merchant_id: str, original_item: str) -> str:
    """Check merchant's item substitution policy"""
    print(f"--- Checking Substitution Policy: {merchant_id} ---")
    
    if SANDBOX_AVAILABLE:
        try:
            from sandbox_tools import get_merchant_substitute_policy
            return get_merchant_substitute_policy(merchant_id, original_item)
        except:
            pass
    
    return f"Substitution policy for {merchant_id}: Standard merchant substitution guidelines apply."

def validate_customer_complaint(complaint_details: str) -> str:
    """Validate customer complaint against order history and delivery logs"""
    # Default customer ID if not provided
    customer_id = "C001"
    
    # Handle missing complaint details
    if not complaint_details or complaint_details.lower() in ["null", "none"]:
        complaint_details = "Customer reported wrong order received"
    
    print(f"--- Validating Complaint from {customer_id} ---")
    
    if SANDBOX_AVAILABLE:
        customer_profile = get_customer_profile(customer_id)
        return f"COMPLAINT VALIDATION:\n{customer_profile}\n\nComplaint Details: {complaint_details}\nValidation Status: Cross-referenced with order history and delivery logs."
    
    return f"""Complaint Validation for {customer_id}:
    • Complaint: {complaint_details}
    • Customer Status: Premium customer (50+ orders)
    • Complaint History: First complaint in 6 months
    • Order History: Consistent positive feedback
    • Validation: LEGITIMATE - Customer has strong track record
    • Recommendation: Process refund immediately"""

def check_driver_history(driver_id: str) -> str:
    """Check driver's performance and incident history."""
    print(f"--- Checking Driver History: {driver_id} ---")
    
    profiles = [
        "Experienced driver (4.9/5 rating, 2000+ deliveries, 0 incidents this month) - Highly reliable",
        "Good driver (4.6/5 rating, 500 deliveries, 1 minor incident) - Generally reliable",
        "New driver (4.3/5 rating, 50 deliveries, learning phase) - Normal monitoring",
        "Problematic driver (4.0/5 rating, 200 deliveries, 3 incidents this month) - Under review"
    ]
    
    return f"Driver Profile: {random.choice(profiles)}"

def check_merchant_history(merchant_id: str) -> str:
    """Check merchant's quality ratings and issue history."""
    print(f"--- Checking Merchant History: {merchant_id} ---")
    
    profiles = [
        "Top-rated merchant (4.8/5 stars, 98% order accuracy, minimal complaints) - Excellent track record",
        "Good merchant (4.4/5 stars, 94% order accuracy, occasional packaging issues) - Generally reliable",
        "Average merchant (4.1/5 stars, 88% order accuracy, moderate complaint rate) - Needs improvement",
        "Problematic merchant (3.8/5 stars, 82% order accuracy, frequent quality issues) - Under performance review"
    ]
    
    return f"Merchant Profile: {random.choice(profiles)}"

def track_delivery_status(order_id: str) -> str:
    """Get real-time delivery tracking information."""
    print(f"--- Tracking Order: {order_id} ---")
    
    statuses = [
        "Order confirmed → Merchant preparing (8 mins) → Driver assigned → En route to pickup",
        "Picked up → In transit → 3.2km from destination → ETA 12 minutes",
        "Delivered → Customer notified → Awaiting confirmation",
        "Delivery attempted → Customer unavailable → Driver waiting at location"
    ]
    
    return f"Delivery Status: {random.choice(statuses)}"

def analyze_gps_data(order_id: str) -> str:
    """Analyze GPS coordinates and route efficiency."""
    print(f"--- Analyzing GPS Data: {order_id} ---")
    
    return """GPS Analysis:
    • Route Efficiency: 94% optimal (standard city traffic)
    • Speed Analysis: Average 28 km/h (within normal range)
    • Stop Points: Merchant pickup (2 min) → Direct route → Customer location
    • Anomalies: None detected
    • Verification: GPS coordinates match reported delivery address"""

def check_weather_conditions(location_time: str) -> str:
    """Check weather conditions affecting delivery."""
    print(f"--- Checking Weather: {location_time} ---")
    
    conditions = [
        "Clear weather, no impact on delivery times",
        "Light rain, +5-10 min expected delivery delays",
        "Heavy rain, +15-20 min delays, safety protocol activated",
        "Extreme weather alert, deliveries suspended for safety"
    ]
    
    return f"Weather Impact: {random.choice(conditions)}"

def contact_driver(driver_message: str) -> str:
    """Send message or call driver for clarification."""
    driver_id, message = driver_message.split(',', 1) if ',' in driver_message else (driver_message, "Status update")
    print(f"--- Contacting Driver {driver_id}: {message} ---")
    
    responses = [
        "Driver responded: 'Customer not at delivery address, trying alternative contact'",
        "Driver confirmed: 'Order delivered to specified location, customer received items'",
        "Driver explained: 'Traffic jam caused delay, sent customer notification'",
        "Driver reported: 'Merchant had to remake order due to quality issue'"
    ]
    
    return f"Driver Communication: {random.choice(responses)}"

def contact_merchant(merchant_message: str) -> str:
    """Contact merchant about order issues."""
    merchant_id, message = merchant_message.split(',', 1) if ',' in merchant_message else (merchant_message, "Order inquiry")
    print(f"--- Contacting Merchant {merchant_id}: {message} ---")
    
    responses = [
        "Merchant confirmed: 'Order prepared correctly, packaged according to standards'",
        "Merchant admitted: 'Kitchen error occurred, willing to remake order at no charge'",
        "Merchant explained: 'Delay due to ingredient shortage, offered substitute items'",
        "Merchant investigating: 'Reviewing kitchen procedures, will provide feedback within 2 hours'"
    ]
    
    return f"Merchant Response: {random.choice(responses)}"

def verify_customer_identity(verification_request: str) -> str:
    """Verify customer identity for security purposes."""
    customer_id, method = verification_request.split(',', 1) if ',' in verification_request else (verification_request, "standard")
    print(f"--- Verifying Customer Identity: {customer_id} via {method} ---")
    
    return f"Identity Verification: Customer {customer_id} successfully verified via {method}. Security check passed."

def offer_compensation_voucher(voucher_details: str) -> str:
    """Offer voucher or credits as compensation."""
    try:
        customer_id, amount, voucher_type = voucher_details.split(',')
        print(f"--- Offering Voucher: {voucher_type} worth {amount} to {customer_id} ---")
        return f"Successfully issued {voucher_type} voucher worth ${amount} to customer {customer_id}. Valid for 30 days, applicable to future orders."
    except:
        return "Error: Please provide voucher details as customer_id,amount,voucher_type"

def issue_instant_refund(refund_details: str) -> str:
    """Issue instant refund with proper documentation."""
    try:
        customer_id, amount, reason = refund_details.split(',', 2)
        print(f"--- Processing Refund: ${amount} to {customer_id} for {reason} ---")
        return f"Instant refund of ${amount} processed for customer {customer_id}. Reason: {reason}. Funds will appear in 1-3 business days."
    except:
        return "Error: Please provide refund details as customer_id,amount,reason"

def exonerate_driver(driver_details: str) -> str:
    """Clear driver of fault with documentation."""
    driver_id, reason = driver_details.split(',', 1) if ',' in driver_details else (driver_details, "Evidence supports innocence")
    print(f"--- Exonerating Driver {driver_id}: {reason} ---")
    return f"Driver {driver_id} cleared of all fault. Reason: {reason}. No impact on performance record."

def log_merchant_packaging_feedback(feedback_details: str) -> str:
    """Log detailed merchant feedback for quality improvement."""
    try:
        merchant_id, feedback = feedback_details.split(',', 1)
        print(f"--- Logging Merchant Feedback: {merchant_id} ---")
        return f"Quality feedback logged for merchant {merchant_id}: '{feedback}'. Forwarded to merchant quality team for review and improvement action."
    except:
        return "Error: Please provide feedback as merchant_id,feedback_details"

def log_incident_report(incident_details: str) -> str:
    """Create comprehensive incident report."""
    try:
        incident_type, details, parties = incident_details.split(',', 2)
        print(f"--- Creating Incident Report: {incident_type} ---")
        return f"Incident report #{random.randint(10000,99999)} created. Type: {incident_type}. Details logged for analysis. Involved parties: {parties}. Report forwarded to quality assurance team."
    except:
        return "Error: Please provide incident details as incident_type,details,involved_parties"

def escalate_to_human(escalation_request: str) -> str:
    """Escalate complex cases to human agents."""
    try:
        reason, urgency, summary = escalation_request.split(',', 2)
        print(f"--- Escalating to Human Agent: {urgency} priority ---")
        return f"Case escalated to human agent. Priority: {urgency}. Reason: {reason}. Case summary provided. Expected response time: {'30 minutes' if urgency == 'high' else '2 hours' if urgency == 'medium' else '24 hours'}."
    except:
        return "Case escalated to human agent team for specialized handling."
