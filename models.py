"""
Data models for the Vehicle Repair Workshop Management System
"""
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    address: str = ""
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class Vehicle:
    id: Optional[int] = None
    license_plate: str = ""
    brand: str = ""
    model: str = ""
    customer_phone: str = ""
    customer_name: str = ""  # For joined queries
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class WorkOrder:
    id: Optional[int] = None
    vehicle_id: int = 0
    entry_date: str = ""
    status: str = "Open"
    total_cost: float = 0.0
    payment_status: str = "Unpaid"
    created_at: Optional[datetime] = None
    
    # Joined fields
    license_plate: str = ""
    brand: str = ""
    model: str = ""
    customer_name: str = ""
    customer_phone: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if not self.entry_date:
            self.entry_date = datetime.now().strftime('%Y-%m-%d')

@dataclass
class Service:
    id: Optional[int] = None
    work_order_id: int = 0
    name: str = ""
    description: str = ""
    quantity: int = 1
    price: float = 0.0
    
    @property
    def total_price(self) -> float:
        return self.quantity * self.price

@dataclass
class SparePart:
    id: Optional[int] = None
    work_order_id: int = 0
    name: str = ""
    description: str = ""
    quantity: int = 1
    price: float = 0.0
    
    @property
    def total_price(self) -> float:
        return self.quantity * self.price

@dataclass
class Invoice:
    id: Optional[int] = None
    work_order_id: int = 0
    invoice_date: str = ""
    total_amount: float = 0.0
    status: str = "Unpaid"
    created_at: Optional[datetime] = None
    
    # Joined fields
    entry_date: str = ""
    license_plate: str = ""
    customer_name: str = ""
    customer_phone: str = ""
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if not self.invoice_date:
            self.invoice_date = datetime.now().strftime('%Y-%m-%d')

@dataclass
class ReportStats:
    total_orders: int = 0
    completed_orders: int = 0
    open_orders: int = 0
    total_revenue: float = 0.0
    avg_order_value: float = 0.0
    top_services: List[dict] = None
    top_customers: List[dict] = None
    
    def __post_init__(self):
        if self.top_services is None:
            self.top_services = []
        if self.top_customers is None:
            self.top_customers = []
