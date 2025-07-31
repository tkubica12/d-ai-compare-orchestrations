"""Pydantic models for the purchase order processing system."""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PurchaseStrategy(str, Enum):
    """Available purchase strategies for departments."""
    
    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    COMPLEX = "complex"  # For future complex text-based strategies


class User(BaseModel):
    """User entity representing an employee."""
    
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's full name")
    department_id: str = Field(..., description="ID of user's department")


class Department(BaseModel):
    """Department entity with purchasing policies."""
    
    department_id: str = Field(..., description="Unique department identifier")
    name: str = Field(..., description="Department name")
    allowed_categories: List[str] = Field(..., description="Categories this department can purchase")
    purchase_strategy: PurchaseStrategy = Field(..., description="Strategy for supplier selection")
    monthly_budget: float = Field(..., description="Monthly budget limit")
    requires_audit: bool = Field(default=False, description="Whether purchases require audit logging")


class DepartmentBudget(BaseModel):
    """Current budget information for a department."""
    
    department_id: str = Field(..., description="Department identifier")
    monthly_budget: float = Field(..., description="Total monthly budget")
    spent_this_month: float = Field(..., description="Amount spent this month")
    remaining_budget: float = Field(..., description="Remaining budget for the month")
    last_updated: datetime = Field(..., description="When budget was last updated")


class Product(BaseModel):
    """Product entity in the catalog."""
    
    product_id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., description="Product name")
    description: str = Field(..., description="Detailed product description")
    category: str = Field(..., description="Product category")


class Supplier(BaseModel):
    """Supplier entity providing products."""
    
    supplier_id: str = Field(..., description="Unique supplier identifier")
    name: str = Field(..., description="Supplier company name")
    reliability_score: float = Field(..., description="Supplier reliability (0-10)")
    contact_info: str = Field(..., description="Supplier contact information")


class ProductDetails(BaseModel):
    """Product details from a specific supplier."""
    
    product_id: str = Field(..., description="Product identifier")
    supplier_id: str = Field(..., description="Supplier identifier")
    price: float = Field(..., description="Price from this supplier")
    availability: str = Field(..., description="Stock availability status")
    delivery_days: int = Field(..., description="Delivery time in days")
    minimum_order: int = Field(default=1, description="Minimum order quantity")


class AuditRecord(BaseModel):
    """Audit record for purchase decisions."""
    
    timestamp: datetime = Field(..., description="When the audit record was created")
    user_id: str = Field(..., description="User who made the request")
    action: str = Field(..., description="Action taken")
    details: Dict = Field(..., description="Additional details about the action")
    decision_reasoning: Optional[str] = Field(None, description="AI reasoning for the decision")


class PurchaseRecommendation(BaseModel):
    """Final purchase recommendation."""
    
    product: Product = Field(..., description="Recommended product")
    supplier: Supplier = Field(..., description="Recommended supplier")
    product_details: ProductDetails = Field(..., description="Specific pricing and delivery info")
    total_cost: float = Field(..., description="Total cost including any fees")
    justification: str = Field(..., description="Explanation for this recommendation")
    alternative_options: Optional[List[Dict]] = Field(None, description="Other available options")
