"""Data access layer for the MCP server."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from models import (
    AuditRecord,
    Department,
    DepartmentBudget,
    Product,
    ProductDetails,
    Supplier,
    User,
)

logger = logging.getLogger(__name__)


class DataStore:
    """In-memory data store for business entities."""
    
    def __init__(self, data_dir: Path):
        """Initialize the data store by loading JSON files.
        
        Args:
            data_dir: Path to directory containing JSON data files
        """
        self.data_dir = data_dir
        self.users: Dict[str, User] = {}
        self.departments: Dict[str, Department] = {}
        self.products: Dict[str, Product] = {}
        self.suppliers: Dict[str, Supplier] = {}
        self.product_details: Dict[str, List[ProductDetails]] = {}
        self.audit_records: List[AuditRecord] = []
        
        self._load_all_data()
    
    def _load_all_data(self) -> None:
        """Load all data from JSON files."""
        try:
            self._load_users()
            self._load_departments()
            self._load_products()
            self._load_suppliers()
            self._load_product_details()
            logger.info("Successfully loaded all business data")
        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            raise
    
    def _load_users(self) -> None:
        """Load users from JSON file."""
        file_path = self.data_dir / "users.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for user_data in data:
            # Convert camelCase to snake_case for Pydantic
            user = User(
                user_id=user_data["userId"],
                name=user_data["name"], 
                department_id=user_data["departmentId"]
            )
            self.users[user.user_id] = user
    
    def _load_departments(self) -> None:
        """Load departments from JSON file."""
        file_path = self.data_dir / "departments.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for dept_data in data:
            # Convert camelCase to snake_case for Pydantic
            department = Department(
                department_id=dept_data["departmentId"],
                name=dept_data["name"],
                allowed_categories=dept_data["allowedCategories"],
                purchase_strategy=dept_data["purchaseStrategy"],
                monthly_budget=dept_data["monthlyBudget"],
                requires_audit=dept_data.get("requiresAudit", False)
            )
            self.departments[department.department_id] = department
    
    def _load_products(self) -> None:
        """Load products from JSON file."""
        file_path = self.data_dir / "products.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for product_data in data:
            # Convert camelCase to snake_case for Pydantic
            product = Product(
                product_id=product_data["productId"],
                name=product_data["name"],
                description=product_data["description"],
                category=product_data["category"]
            )
            self.products[product.product_id] = product
    
    def _load_suppliers(self) -> None:
        """Load suppliers from JSON file."""
        file_path = self.data_dir / "suppliers.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for supplier_data in data:
            # Convert camelCase to snake_case for Pydantic
            supplier = Supplier(
                supplier_id=supplier_data["supplierId"],
                name=supplier_data["name"],
                reliability_score=supplier_data.get("reliabilityScore", 7.0),
                contact_info=supplier_data.get("contactInfo", "")
            )
            self.suppliers[supplier.supplier_id] = supplier
    
    def _load_product_details(self) -> None:
        """Load product details from JSON file."""
        file_path = self.data_dir / "product_details.json"
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        for detail_data in data:
            # Convert camelCase to snake_case for Pydantic
            detail = ProductDetails(
                product_id=detail_data["productId"],
                supplier_id=detail_data["supplierId"],
                price=detail_data["price"],
                availability=detail_data["availability"],
                delivery_days=detail_data["deliveryDays"],
                minimum_order=detail_data.get("minimumOrder", 1)
            )
            product_id = detail.product_id
            
            if product_id not in self.product_details:
                self.product_details[product_id] = []
            
            self.product_details[product_id].append(detail)
    
    # User operations
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    # Department operations
    def get_department(self, department_id: str) -> Optional[Department]:
        """Get department by ID."""
        return self.departments.get(department_id)
    
    def get_department_budget(self, department_id: str) -> Optional[DepartmentBudget]:
        """Get current budget information for a department."""
        department = self.get_department(department_id)
        if not department:
            return None
        
        # For demo purposes, simulate budget tracking
        spent_this_month = 2500.0  # Mock spent amount
        remaining = department.monthly_budget - spent_this_month
        
        return DepartmentBudget(
            department_id=department_id,
            monthly_budget=department.monthly_budget,
            spent_this_month=spent_this_month,
            remaining_budget=remaining,
            last_updated=datetime.now()
        )
    
    # Product operations
    def search_products(self, name: str) -> List[Product]:
        """Search products by name (case-insensitive partial match)."""
        search_term = name.lower()
        results = []
        
        # First, direct name and description search
        for product in self.products.values():
            if (search_term in product.name.lower() or 
                search_term in product.description.lower()):
                results.append(product)
        
        # Handle equivalent product scenarios
        equivalent_mappings = {
            "computer": ["laptop", "pc", "workstation"],
            "chair": ["chair", "seat"],
            "printer paper": ["notebook", "paper"],
            "paper": ["notebook", "paper"]
        }
        
        if search_term in equivalent_mappings:
            for equivalent_term in equivalent_mappings[search_term]:
                for product in self.products.values():
                    if (equivalent_term in product.name.lower() or 
                        equivalent_term in product.description.lower()):
                        if product not in results:  # Avoid duplicates
                            results.append(product)
        
        return results
    
    def get_product(self, product_id: str) -> Optional[Product]:
        """Get product by ID."""
        return self.products.get(product_id)
    
    # Supplier operations
    def get_supplier(self, supplier_id: str) -> Optional[Supplier]:
        """Get supplier by ID."""
        return self.suppliers.get(supplier_id)
    
    # Product details operations
    def get_product_details(self, product_id: str, supplier_id: Optional[str] = None) -> List[ProductDetails]:
        """Get product details, optionally filtered by supplier."""
        details = self.product_details.get(product_id, [])
        
        if supplier_id:
            details = [d for d in details if d.supplier_id == supplier_id]
        
        return details
    
    def get_all_suppliers_for_product(self, product_id: str) -> List[ProductDetails]:
        """Get all supplier options for a product."""
        return self.product_details.get(product_id, [])
    
    # Audit operations
    def create_audit_record(self, user_id: str, action: str, details: Dict, 
                          decision_reasoning: Optional[str] = None) -> AuditRecord:
        """Create a new audit record."""
        record = AuditRecord(
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            details=details,
            decision_reasoning=decision_reasoning
        )
        
        self.audit_records.append(record)
        logger.info(f"Created audit record for user {user_id}: {action}")
        
        return record
