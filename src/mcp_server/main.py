"""MCP server for purchase order processing business logic."""

import logging
from pathlib import Path
from typing import Any, Dict, List

from fastmcp import FastMCP

from data_store import DataStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize data store
DATA_DIR = Path(__file__).parent / "data"
data_store = DataStore(DATA_DIR)

# Create the MCP server
mcp = FastMCP(
    name="Purchase Order Processing Server",
    instructions="""
    This server provides business data and tools for internal purchase order processing.
    Use get_user() to find user information, get_department_policy() for department rules,
    search_products() to find products, and get_product_details() for supplier information.
    Always check department policies before making recommendations.
    """
)


@mcp.tool()
def get_user(user_id: str) -> Dict[str, Any]:
    """Get user information by user ID.
    
    Args:
        user_id: The unique identifier for the user
        
    Returns:
        User information including name and department ID
        
    Raises:
        ValueError: If user is not found
    """
    user = data_store.get_user(user_id)
    if not user:
        raise ValueError(f"User with ID {user_id} not found")
    
    return user.model_dump()


@mcp.tool()
def get_department_policy(department_id: str) -> Dict[str, Any]:
    """Get department policy information.
    
    Args:
        department_id: The unique identifier for the department
        
    Returns:
        Department policy including allowed categories, purchase strategy, and audit requirements
        
    Raises:
        ValueError: If department is not found
    """
    department = data_store.get_department(department_id)
    if not department:
        raise ValueError(f"Department with ID {department_id} not found")
    
    return department.model_dump()


@mcp.tool()
def get_department_budget(department_id: str) -> Dict[str, Any]:
    """Get current budget information for a department.
    
    Args:
        department_id: The unique identifier for the department
        
    Returns:
        Budget information including total, spent, and remaining amounts
        
    Raises:
        ValueError: If department is not found
    """
    budget = data_store.get_department_budget(department_id)
    if not budget:
        raise ValueError(f"Budget information for department {department_id} not found")
    
    return budget.model_dump()


@mcp.tool()
def search_products(name: str) -> List[Dict[str, Any]]:
    """Search for products by name or description.
    
    Args:
        name: Product name or description to search for (case-insensitive)
        
    Returns:
        List of matching products with their details
    """
    products = data_store.search_products(name)
    return [product.model_dump() for product in products]


@mcp.tool()
def get_product_details(product_id: str, supplier_id: str = None) -> List[Dict[str, Any]]:
    """Get product details from suppliers.
    
    Args:
        product_id: The unique identifier for the product
        supplier_id: Optional supplier ID to filter by specific supplier
        
    Returns:
        List of product details including pricing, availability, and delivery information
        
    Raises:
        ValueError: If product is not found
    """
    details = data_store.get_product_details(product_id, supplier_id)
    if not details:
        raise ValueError(f"No product details found for product {product_id}")
    
    return [detail.model_dump() for detail in details]


@mcp.tool()
def get_supplier_info(supplier_id: str) -> Dict[str, Any]:
    """Get supplier information.
    
    Args:
        supplier_id: The unique identifier for the supplier
        
    Returns:
        Supplier information including name, reliability score, and contact info
        
    Raises:
        ValueError: If supplier is not found
    """
    supplier = data_store.get_supplier(supplier_id)
    if not supplier:
        raise ValueError(f"Supplier with ID {supplier_id} not found")
    
    return supplier.model_dump()


@mcp.tool()
def create_audit_record(user_id: str, action: str, details: Dict[str, Any], 
                       decision_reasoning: str = None) -> Dict[str, Any]:
    """Create an audit record for a purchase decision.
    
    Args:
        user_id: The user who made the request
        action: The action taken (e.g., "purchase_approved", "purchase_denied")
        details: Additional details about the decision
        decision_reasoning: Optional reasoning for the decision
        
    Returns:
        The created audit record
    """
    record = data_store.create_audit_record(user_id, action, details, decision_reasoning)
    return record.model_dump()


if __name__ == "__main__":
    import os
    
    logger.info("Starting Purchase Order MCP Server...")
    
    # Get port from environment variable or default to 8000
    port = int(os.getenv("PORT", "8000"))
    
    # Get transport mode from environment variable
    # Azure AI Foundry uses SSE, modern clients use streamable-http
    transport = os.getenv("MCP_TRANSPORT", "streamable-http")
    
    logger.info(f"Starting HTTP server on port {port} with transport: {transport}")
    
    # Run with specified transport mode
    mcp.run(transport=transport, host="0.0.0.0", port=port)
