# tools.py
# Advanced tools for Grab's AI customer service agent
# All functions simulate real-world business logic and data analysis

import random
from datetime import datetime, timedelta

def collect_evidence(query: str) -> str:
    """
    Comprehensive evidence collection including photos, timestamps, GPS data, and statements.
    """
    print(f"--- Collecting Evidence: {query} ---")
    
    if "spilled" in query.lower():
        return """Evidence Analysis:
        • Customer Photo: Shows spilled beverage and stained packaging
        • Driver Photo: Bag seal intact at pickup, visible liquid damage upon delivery
        • Timestamp: Issue occurred during transport (15:23 pickup → 15:45 delivery)
        • GPS Route: Standard route taken, no unusual delays or detours
        • Merchant Statement: 'Drink was properly sealed in leak-proof container'
        • Assessment: Likely packaging failure during normal transport"""
    
    elif "late" in query.lower() or "delay" in query.lower():
        return """Evidence Analysis:
        • Order Timeline: 45 minutes total (20 min prep + 25 min delivery)
        • Traffic Data: Heavy congestion on main route (+15 min expected)
        • Driver GPS: Followed optimal route, no unauthorized stops
        • Merchant Delay: Kitchen backed up due to lunch rush
        • Customer Communication: Driver sent 2 delay notifications
        • Assessment: Legitimate delay due to external factors"""
        
    elif "wrong" in query.lower() and "order" in query.lower():
        return """Evidence Analysis:
        • Order Verification: Photos show different items than ordered
        • Merchant Logs: Kitchen prepared order #1247 instead of #1274
        • Driver Confirmation: Picked up sealed bag matching order number
        • Customer Receipt: Shows correct original order details
        • Quality Check: Merchant failed to verify order contents
        • Assessment: Merchant preparation error, driver followed protocol"""
        
    return "Evidence collected: Standard investigation completed. No anomalies detected."

def check_customer_history(customer_id: str) -> str:
    """Check customer's order history and complaint patterns."""
    print(f"--- Checking Customer History: {customer_id} ---")
    
    # Simulate different customer profiles
    profiles = [
        "Premium customer (50+ orders, 4.8/5 rating, 1 complaint in 6 months) - High trust level",
        "Regular customer (15 orders, 4.2/5 rating, 2 complaints resolved) - Normal trust level", 
        "New customer (3 orders, no ratings, first complaint) - Standard verification needed",
        "Frequent complainer (20 orders, 3.1/5 rating, 8 complaints) - Enhanced verification required"
    ]
    
    return f"Customer Profile: {random.choice(profiles)}"

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
