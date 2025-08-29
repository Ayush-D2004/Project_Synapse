# sandbox_database.py
# Realistic sandbox environment with merchants, drivers, customers, and orders

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid

class SandboxDatabase:
    def __init__(self):
        self.customers = {}
        self.merchants = {}
        self.drivers = {}
        self.orders = {}
        self.transactions = {}
        self.complaints = {}
        self.delivery_logs = {}
        self._initialize_data()
    
    def _initialize_data(self):
        """Initialize the sandbox with minimal realistic data"""
        
        # Single customer for testing
        self.customers = {
            "C001": {
                "id": "C001",
                "name": "John Smith",
                "phone": "+91-9876543210",
                "email": "john.smith@gmail.com",
                "address": "Block A, Sector 15, Noida",
                "rating": 4.5,
                "total_orders": 25,
                "complaint_history": [],
                "account_status": "active",
                "wallet_balance": 500.0,
                "preferred_payment": "wallet",
                "joined_date": "2023-06-15"
            }
        }
        
        # Single merchant with flexible menu
        self.merchants = {
            "M001": {
                "id": "M001",
                "name": "Food Corner",
                "type": "multi_cuisine",
                "rating": 4.2,
                "address": "Main Market, Local Area",
                "phone": "+91-1147823456",
                "total_orders": 500,
                "complaint_rate": 0.05,
                "avg_preparation_time": 15,
                "status": "active",
                "menu": {
                    # Generic items that can represent any food
                    "item_1": {"price": 150, "available": True, "category": "main"},
                    "item_2": {"price": 250, "available": True, "category": "main"},
                    "item_3": {"price": 100, "available": True, "category": "side"},
                    "item_4": {"price": 80, "available": True, "category": "beverage"},
                    "item_5": {"price": 200, "available": True, "category": "dessert"}
                },
                "substitution_policy": {
                    "unavailable_items": "contact_customer"
                },
                "quality_issues": [],
                "last_inspection": "2024-08-01"
            }
        }
        
        # Single driver
        self.drivers = {
            "D001": {
                "id": "D001",
                "name": "Mike Wilson",
                "phone": "+91-9123456789",
                "vehicle_type": "bike",
                "rating": 4.6,
                "total_deliveries": 200,
                "current_status": "available",
                "location": "Local Area",
                "incidents": [],
                "delivery_time_avg": 20,
                "cancellation_rate": 0.03,
                "earnings_today": 300.0,
                "joined_date": "2023-04-10"
            }
        }
        
        # No predefined orders - will be created dynamically based on user input
        self.orders = {}
        self.delivery_logs = {}
        self.transactions = {}
    
    def get_customer_details(self, customer_id: str) -> Optional[Dict]:
        """Get customer information"""
        return self.customers.get(customer_id)
    
    def get_merchant_details(self, merchant_id: str) -> Optional[Dict]:
        """Get merchant information"""
        return self.merchants.get(merchant_id)
    
    def get_driver_details(self, driver_id: str) -> Optional[Dict]:
        """Get driver information"""
        return self.drivers.get(driver_id)
    
    def get_order_details(self, order_id: str) -> Optional[Dict]:
        """Get order information"""
        return self.orders.get(order_id)
    
    def get_delivery_log(self, order_id: str) -> Optional[Dict]:
        """Get delivery log for an order"""
        return self.delivery_logs.get(order_id)
    
    def get_customer_order_history(self, customer_id: str) -> List[Dict]:
        """Get all orders for a customer"""
        return [order for order in self.orders.values() if order["customer_id"] == customer_id]
    
    def get_merchant_recent_issues(self, merchant_id: str) -> List[str]:
        """Get recent quality issues for a merchant"""
        merchant = self.merchants.get(merchant_id)
        return merchant["quality_issues"] if merchant else []
    
    def process_refund(self, customer_id: str, amount: float, reason: str) -> Dict:
        """Process a refund transaction"""
        txn_id = f"REF_{len(self.transactions) + 1:03d}"
        refund_txn = {
            "id": txn_id,
            "customer_id": customer_id,
            "amount": amount,
            "type": "refund",
            "reason": reason,
            "status": "processed",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "reference": f"REFUND_REF_{random.randint(10000, 99999)}"
        }
        self.transactions[txn_id] = refund_txn
        
        # Update customer wallet balance
        if customer_id in self.customers:
            self.customers[customer_id]["wallet_balance"] += amount
        
        return refund_txn
    
    def log_complaint(self, customer_id: str, order_id: str, issue_type: str, details: str) -> str:
        """Log a customer complaint"""
        complaint_id = f"COMP_{len(self.complaints) + 1:03d}"
        complaint = {
            "id": complaint_id,
            "customer_id": customer_id,
            "order_id": order_id,
            "issue_type": issue_type,
            "details": details,
            "status": "open",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "resolution": None
        }
        self.complaints[complaint_id] = complaint
        
        # Update customer complaint history
        if customer_id in self.customers:
            self.customers[customer_id]["complaint_history"].append(complaint_id)
        
        return complaint_id
    
    def log_merchant_feedback(self, merchant_id: str, issue: str, severity: str) -> bool:
        """Log feedback against a merchant"""
        if merchant_id in self.merchants:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            feedback_entry = f"{timestamp}: {severity.upper()} - {issue}"
            
            if "feedback_log" not in self.merchants[merchant_id]:
                self.merchants[merchant_id]["feedback_log"] = []
            
            self.merchants[merchant_id]["feedback_log"].append(feedback_entry)
            return True
        return False
    
    def exonerate_driver(self, driver_id: str, reason: str) -> bool:
        """Clear driver of fault"""
        if driver_id in self.drivers:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            exoneration_entry = f"{timestamp}: EXONERATED - {reason}"
            
            if "exoneration_log" not in self.drivers[driver_id]:
                self.drivers[driver_id]["exoneration_log"] = []
            
            self.drivers[driver_id]["exoneration_log"].append(exoneration_entry)
            return True
        return False
    
    def create_order_from_description(self, customer_description: str, amount: float = None) -> str:
        """Create an order dynamically based on customer description"""
        order_id = f"ORD_{len(self.orders) + 1:03d}"
        
        # Extract basic details or use defaults
        customer_id = "C001"  # Default customer
        merchant_id = "M001"  # Default merchant
        driver_id = "D001"    # Default driver
        
        # Create a generic order based on description
        order = {
            "id": order_id,
            "customer_id": customer_id,
            "merchant_id": merchant_id,
            "driver_id": driver_id,
            "description": customer_description,
            "amount": amount or 200.0,  # Default amount if not specified
            "order_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "status": "delivered",
            "payment_method": "wallet",
            "delivery_address": self.customers[customer_id]["address"],
            "issue_reported": None
        }
        
        self.orders[order_id] = order
        return order_id

# Global sandbox instance
sandbox_db = SandboxDatabase()
