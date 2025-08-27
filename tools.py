# tools.py
# This file contains the simulated tools our AI agent can use.
# All functions are modified to accept a single string input to be compatible with the agent.

def collect_evidence(query: str) -> str:
    """
    Use this tool to collect evidence like photos and questionnaire answers 
    from the customer and driver when a dispute is reported. This tool should 
    be used first in any dispute to gather facts. The input is the user's query.
    """
    print(f"--- Calling Tool: collect_evidence with query: {query} ---")
    if "spilled" in query.lower() and "sealed" in query.lower():
        return "Evidence collected: Photos from the customer show a spilled drink. Photos from the driver show the bag's seal was intact upon delivery."
    elif "unavailable" in query.lower():
        return "Evidence collected: GPS data confirms driver is at the location. Driver has sent a photo showing the recipient's door is closed. No response to chat messages."
    return "Evidence collected: Standard procedure followed. No specific details to report."

def issue_instant_refund(details: str) -> str:
    """
    Use this tool to issue an instant refund to a customer. 
    The input should be a comma-separated string of two values: customer_id,amount (e.g., 'C123,15.00').
    Only use this tool when you have confirmed the company or merchant is at fault.
    """
    try:
        customer_id, amount_str = details.split(',')
        amount = float(amount_str.strip())
        print(f"--- Calling Tool: issue_instant_refund for customer {customer_id} with amount {amount} ---")
        return f"Successfully issued a refund of ${amount:.2f} to customer {customer_id}."
    except Exception as e:
        return f"Error using issue_instant_refund tool. Please check the input format. Details: {e}"


def exonerate_driver(driver_id: str) -> str:
    """
    Use this tool to clear a driver of any fault for an incident. 
    It takes a single driver_id as a string input. Use this when evidence shows the driver was not at fault.
    """
    print(f"--- Calling Tool: exonerate_driver for driver {driver_id} ---")
    return f"Driver {driver_id.strip()} has been cleared of fault for this incident. No impact on their record."

def log_merchant_packaging_feedback(details: str) -> str:
    """
    Use this tool to log feedback about a merchant's packaging for quality review. 
    The input should be a comma-separated string of two values: merchant_id,feedback_details (e.g., 'M789,Item was spilled due to poor sealing').
    """
    try:
        merchant_id, feedback = details.split(',', 1)
        print(f"--- Calling Tool: log_merchant_packaging_feedback for merchant {merchant_id} ---")
        return f"Feedback logged for merchant {merchant_id.strip()}: '{feedback.strip()}'. This will be reviewed by the quality team."
    except Exception as e:
        return f"Error using log_merchant_packaging_feedback tool. Please check the input format. Details: {e}"
