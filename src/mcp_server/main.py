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
    logger.info(f"🔍 MCP TOOL CALL: get_user(user_id='{user_id}')")
    
    try:
        user = data_store.get_user(user_id)
        if not user:
            error_msg = f"User with ID {user_id} not found"
            logger.error(f"❌ MCP TOOL ERROR: get_user -> {error_msg}")
            raise ValueError(error_msg)
        
        result = user.model_dump()
        logger.info(f"✅ MCP TOOL RESPONSE: get_user -> {result}")
        return result
    except Exception as e:
        logger.error(f"❌ MCP TOOL ERROR: get_user -> {str(e)}")
        raise


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
    logger.info(f"🔍 MCP TOOL CALL: get_department_policy(department_id='{department_id}')")
    
    try:
        department = data_store.get_department(department_id)
        if not department:
            error_msg = f"Department with ID {department_id} not found"
            logger.error(f"❌ MCP TOOL ERROR: get_department_policy -> {error_msg}")
            raise ValueError(error_msg)
        
        result = department.model_dump()
        logger.info(f"✅ MCP TOOL RESPONSE: get_department_policy -> {result}")
        return result
    except Exception as e:
        logger.error(f"❌ MCP TOOL ERROR: get_department_policy -> {str(e)}")
        raise


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
    logger.info(f"🔍 MCP TOOL CALL: get_department_budget(department_id='{department_id}')")
    
    try:
        budget = data_store.get_department_budget(department_id)
        if not budget:
            error_msg = f"Budget information for department {department_id} not found"
            logger.error(f"❌ MCP TOOL ERROR: get_department_budget -> {error_msg}")
            raise ValueError(error_msg)
        
        result = budget.model_dump()
        logger.info(f"✅ MCP TOOL RESPONSE: get_department_budget -> {result}")
        return result
    except Exception as e:
        logger.error(f"❌ MCP TOOL ERROR: get_department_budget -> {str(e)}")
        raise


@mcp.tool()
def search_products(name: str) -> List[Dict[str, Any]]:
    """Search for products by name or description.
    
    Args:
        name: Product name or description to search for (case-insensitive)
        
    Returns:
        List of matching products with their details
    """
    logger.info(f"🔍 MCP TOOL CALL: search_products(name='{name}')")
    
    try:
        products = data_store.search_products(name)
        result = [product.model_dump() for product in products]
        logger.info(f"✅ MCP TOOL RESPONSE: search_products -> Found {len(result)} products")
        return result
    except Exception as e:
        logger.error(f"❌ MCP TOOL ERROR: search_products -> {str(e)}")
        raise


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
    logger.info(f"🔍 MCP TOOL CALL: get_product_details(product_id='{product_id}', supplier_id='{supplier_id}')")
    
    try:
        details = data_store.get_product_details(product_id, supplier_id)
        if not details:
            error_msg = f"No product details found for product {product_id}"
            logger.error(f"❌ MCP TOOL ERROR: get_product_details -> {error_msg}")
            raise ValueError(error_msg)
        
        result = [detail.model_dump() for detail in details]
        logger.info(f"✅ MCP TOOL RESPONSE: get_product_details -> Found {len(result)} supplier options")
        return result
    except Exception as e:
        logger.error(f"❌ MCP TOOL ERROR: get_product_details -> {str(e)}")
        raise


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
    logger.info(f"🔍 MCP TOOL CALL: get_supplier_info(supplier_id='{supplier_id}')")
    
    try:
        supplier = data_store.get_supplier(supplier_id)
        if not supplier:
            error_msg = f"Supplier with ID {supplier_id} not found"
            logger.error(f"❌ MCP TOOL ERROR: get_supplier_info -> {error_msg}")
            raise ValueError(error_msg)
        
        result = supplier.model_dump()
        logger.info(f"✅ MCP TOOL RESPONSE: get_supplier_info -> {result}")
        return result
    except Exception as e:
        logger.error(f"❌ MCP TOOL ERROR: get_supplier_info -> {str(e)}")
        raise


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
    logger.info(f"🔍 MCP TOOL CALL: create_audit_record(user_id='{user_id}', action='{action}')")
    
    try:
        record = data_store.create_audit_record(user_id, action, details, decision_reasoning)
        result = record.model_dump()
        logger.info(f"✅ MCP TOOL RESPONSE: create_audit_record -> Created audit record with ID {result.get('id', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"❌ MCP TOOL ERROR: create_audit_record -> {str(e)}")
        raise


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
