# sandbox_tools.py
# Advanced tools that interact with the sandbox database

import sys
import os
sys.path.append(os.path.dirname(__file__))

from sandbox_database import sandbox_db
from typing import Dict, List, Optional
import json

def get_customer_profile(customer_id: str) -> str:
    """Get comprehensive customer profile and history"""
    customer = sandbox_db.get_customer_details(customer_id)
    if not customer:
        return f"Customer {customer_id} not found in system"
    
    order_history = sandbox_db.get_customer_order_history(customer_id)
    
    profile_summary = f"""
Customer Profile Analysis:
• Name: {customer['name']} (ID: {customer_id})
• Account Status: {customer['account_status'].upper()}
• Customer Rating: {customer['rating']}/5.0
• Total Orders: {customer['total_orders']}
• Complaint History: {len(customer['complaint_history'])} complaints
• Wallet Balance: ₹{customer['wallet_balance']}
• Member Since: {customer['joined_date']}
• Risk Assessment: {'HIGH' if len(customer['complaint_history']) > 2 else 'MEDIUM' if len(customer['complaint_history']) > 0 else 'LOW'}
• Trustworthiness: {'EXCELLENT' if customer['rating'] > 4.5 else 'GOOD' if customer['rating'] > 4.0 else 'AVERAGE'}
"""
    return profile_summary

def get_order_investigation(order_id: str) -> str:
    """Comprehensive order investigation with all stakeholder data"""
    order = sandbox_db.get_order_details(order_id)
    if not order:
        return f"Order {order_id} not found in system"
    
    # Get related data
    customer = sandbox_db.get_customer_details(order['customer_id'])
    merchant = sandbox_db.get_merchant_details(order['merchant_id'])
    driver = sandbox_db.get_driver_details(order['driver_id'])
    delivery_log = sandbox_db.get_delivery_log(order_id)
    
    investigation_report = f"""
COMPREHENSIVE ORDER INVESTIGATION - {order_id}
{'='*50}

ORDER DETAILS:
• Order Amount: ₹{order['total_amount']} + ₹{order['delivery_charges']} delivery = ₹{order['final_amount']}
• Order Time: {order['order_time']}
• Delivery Time: {order['delivery_time']}
• Status: {order['status']}
• Payment Method: {order['payment_method']}

ITEMS ORDERED:
"""
    for item in order['items']:
        investigation_report += f"• {item['name']} x{item['quantity']} @ ₹{item['price']} each\n"
    
    investigation_report += f"""
MERCHANT ANALYSIS ({merchant['name']}):
• Merchant Rating: {merchant['rating']}/5.0
• Complaint Rate: {merchant['complaint_rate']*100:.1f}%
• Avg Preparation Time: {merchant['avg_preparation_time']} minutes
• Known Issues: {', '.join(merchant['quality_issues'])}
• Menu Status: {json.dumps(merchant['menu'], indent=2)}

DRIVER ANALYSIS ({driver['name']}):
• Driver Rating: {driver['rating']}/5.0
• Total Deliveries: {driver['total_deliveries']}
• Avg Delivery Time: {driver['delivery_time_avg']} minutes
• Incident History: {driver['incidents'] if driver['incidents'] else 'Clean record'}

DELIVERY LOG ANALYSIS:
"""
    if delivery_log:
        investigation_report += f"• Pickup Time: {delivery_log['pickup_time']}\n"
        investigation_report += f"• Items Actually Received by Driver:\n"
        for item in delivery_log['items_received']:
            note = f" ({item['note']})" if 'note' in item else ""
            investigation_report += f"  - {item['name']} x{item['quantity']}{note}\n"
        investigation_report += f"• Delivery Attempts: {delivery_log['delivery_attempts']}\n"
        investigation_report += f"• Route: {delivery_log['route_taken']}\n"
        investigation_report += f"• Delays: {delivery_log['delays'] if delivery_log['delays'] else 'None'}\n"
        investigation_report += f"• Driver Notes: {delivery_log['driver_notes']}\n"
    
    investigation_report += f"""
DISCREPANCY ANALYSIS:
• Ordered vs Delivered: {'MISMATCH DETECTED' if delivery_log and delivery_log['items_received'][0]['name'] != order['items'][0]['name'] else 'ITEMS MATCH'}
• Responsible Party: {'MERCHANT' if delivery_log and 'merchant_substitution' in str(delivery_log) else 'UNDER_INVESTIGATION'}
"""
    
    return investigation_report

def get_merchant_quality_assessment(merchant_id: str) -> str:
    """Get merchant quality assessment and recent issues"""
    merchant = sandbox_db.get_merchant_details(merchant_id)
    if not merchant:
        return f"Merchant {merchant_id} not found"
    
    recent_issues = sandbox_db.get_merchant_recent_issues(merchant_id)
    
    assessment = f"""
MERCHANT QUALITY ASSESSMENT - {merchant['name']}
{'='*50}
• Overall Rating: {merchant['rating']}/5.0
• Total Orders Processed: {merchant['total_orders']}
• Complaint Rate: {merchant['complaint_rate']*100:.1f}%
• Average Preparation Time: {merchant['avg_preparation_time']} minutes
• Status: {merchant['status'].upper()}
• Recent Quality Issues: {', '.join(recent_issues)}
• Last Quality Inspection: {merchant['last_inspection']}

MENU AVAILABILITY:
"""
    for item, details in merchant['menu'].items():
        status = "✓ Available" if details['available'] else "✗ Out of Stock"
        assessment += f"• {item.title()}: ₹{details['price']} - {status}\n"
    
    return assessment

def process_customer_refund(customer_id: str, amount: float, reason: str) -> str:
    """Process refund and update customer wallet"""
    try:
        amount = float(amount)
        refund_txn = sandbox_db.process_refund(customer_id, amount, reason)
        
        return f"""
REFUND PROCESSED SUCCESSFULLY
• Transaction ID: {refund_txn['id']}
• Customer ID: {customer_id}
• Refund Amount: ₹{amount}
• Reason: {reason}
• Reference: {refund_txn['reference']}
• Status: {refund_txn['status'].upper()}
• Processed At: {refund_txn['timestamp']}
• New Wallet Balance: ₹{sandbox_db.get_customer_details(customer_id)['wallet_balance']}
"""
    except Exception as e:
        return f"Error processing refund: {str(e)}"

def log_merchant_quality_issue(merchant_id: str, issue_description: str, severity: str = "medium") -> str:
    """Log quality issue against merchant"""
    success = sandbox_db.log_merchant_feedback(merchant_id, issue_description, severity)
    
    if success:
        return f"""
MERCHANT FEEDBACK LOGGED
• Merchant ID: {merchant_id}
• Issue: {issue_description}
• Severity: {severity.upper()}
• Status: Quality team will review within 24 hours
• Action: Merchant will be contacted for improvement measures
"""
    else:
        return f"Failed to log feedback for merchant {merchant_id}"

def exonerate_delivery_partner(driver_id: str, reason: str) -> str:
    """Clear delivery partner of fault"""
    success = sandbox_db.exonerate_driver(driver_id, reason)
    
    if success:
        driver = sandbox_db.get_driver_details(driver_id)
        return f"""
DRIVER EXONERATION COMPLETED
• Driver: {driver['name']} (ID: {driver_id})
• Reason: {reason}
• Status: Driver cleared of all fault for this incident
• Impact: No negative impact on driver's performance record
• Driver Rating Maintained: {driver['rating']}/5.0
"""
    else:
        return f"Failed to exonerate driver {driver_id}"

def create_incident_report(customer_id: str, order_id: str, issue_type: str, description: str) -> str:
    """Create comprehensive incident report"""
    complaint_id = sandbox_db.log_complaint(customer_id, order_id, issue_type, description)
    
    return f"""
INCIDENT REPORT CREATED
• Report ID: {complaint_id}
• Customer ID: {customer_id}
• Order ID: {order_id}
• Issue Type: {issue_type}
• Description: {description}
• Status: Under Investigation
• Priority: {'HIGH' if 'refund' in description.lower() else 'MEDIUM'}
• Expected Resolution: 24-48 hours
"""

def check_refund_eligibility(customer_id: str, order_id: str, claim_amount: float) -> str:
    """Check if customer is eligible for requested refund amount"""
    customer = sandbox_db.get_customer_details(customer_id)
    order = sandbox_db.get_order_details(order_id)
    
    if not customer or not order:
        return "Customer or order not found"
    
    # Calculate eligibility based on various factors
    customer_trust_score = customer['rating']
    complaint_penalty = len(customer['complaint_history']) * 0.1
    final_trust_score = max(0, customer_trust_score - complaint_penalty)
    
    max_eligible_amount = order['total_amount'] * (final_trust_score / 5.0)
    
    eligibility_report = f"""
REFUND ELIGIBILITY ASSESSMENT
• Customer Trust Score: {final_trust_score:.1f}/5.0
• Order Amount: ₹{order['total_amount']}
• Requested Refund: ₹{claim_amount}
• Maximum Eligible: ₹{max_eligible_amount:.0f}
• Eligibility Status: {'APPROVED' if claim_amount <= max_eligible_amount else 'PARTIAL_APPROVAL'}
• Recommended Amount: ₹{min(claim_amount, max_eligible_amount):.0f}
"""
    
    if len(customer['complaint_history']) == 0:
        eligibility_report += "• First-time Issue: Additional goodwill consideration applied\n"
    elif len(customer['complaint_history']) > 2:
        eligibility_report += "• Frequent Complainer: Enhanced verification required\n"
    
    return eligibility_report

def get_merchant_substitute_policy(merchant_id: str, original_item: str) -> str:
    """Check merchant's substitution policy and available alternatives"""
    merchant = sandbox_db.get_merchant_details(merchant_id)
    if not merchant:
        return f"Merchant {merchant_id} not found"
    
    menu = merchant['menu']
    
    policy_info = f"""
MERCHANT SUBSTITUTION POLICY - {merchant['name']}
• Original Item Requested: {original_item}
• Substitution Policy: Items of equal or greater value may be substituted with customer consent
• Available Alternatives:
"""
    
    for item, details in menu.items():
        if details['available'] and item != original_item:
            policy_info += f"  - {item.title()}: ₹{details['price']}\n"
    
    policy_info += f"• Merchant Contact: {merchant['phone']}\n"
    policy_info += f"• Policy Violation: {'YES - Customer consent not obtained' if 'substitution' in str(sandbox_db.get_delivery_log('ORD_001')) else 'NO'}\n"
    
    return policy_info
