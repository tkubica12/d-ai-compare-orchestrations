#!/usr/bin/env python3
"""
Script to run remote MCP server tests against deployed Azure Container Apps instance.
Uses official MCP Python SDK client with SSE transport.

Usage:
    python run_remote_tests.py <server-url>

Example:
    python run_remote_tests.py https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io
"""

import asyncio
import sys
from urllib.parse import urlparse
from contextlib import asynccontextmanager
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


def validate_url(url: str) -> bool:
    """Validate that the URL is properly formatted."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def normalize_mcp_url(url: str) -> str:
    """Normalize MCP server URL to ensure it has the correct endpoint path.
    
    Args:
        url: The base URL or URL with endpoint
        
    Returns:
        Normalized URL with proper endpoint path
    """
    url = url.rstrip('/')
    
    # If URL already has an MCP endpoint path, use it as-is with trailing slash
    if url.endswith('/sse') or url.endswith('/mcp'):
        return url + '/'
    
    # If URL already has the endpoint with trailing slash, return as-is
    if url.endswith('/sse/') or url.endswith('/mcp/'):
        return url
    
    # If URL doesn't have an endpoint path, assume SSE for Azure Container Apps
    # Check if the URL ends with the domain (no path)
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if not parsed.path or parsed.path == '/':
        return url + '/sse/'
    
    # If there's some other path, add trailing slash if needed
    return url + '/' if not url.endswith('/') else url


@asynccontextmanager
async def mcp_session(server_url: str):
    """Create MCP client session for the remote server using SSE transport."""
    try:
        # Use the full URL as provided (should include /sse or /mcp endpoint)
        async with sse_client(server_url) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                yield session
    except Exception as e:
        raise Exception(f"Could not connect to MCP server at {server_url}: {e}")


async def test_business_workflow(session: ClientSession):
    """Test the complete business workflow."""
    print("🔄 Testing complete business workflow...")
    
    # Step 1: Get user information
    print("   1. Getting user information...")
    user_result = await session.call_tool("get_user", {"user_id": "alice-001"})
    print(f"   ✅ User: {user_result.content[0].text}")
    
    # Step 2: Get department policy
    print("   2. Getting department policy...")
    policy_result = await session.call_tool("get_department_policy", {"department_id": "IT"})
    print(f"   ✅ Policy: {policy_result.content[0].text[:100]}...")
    
    # Step 3: Get department budget
    print("   3. Getting department budget...")
    budget_result = await session.call_tool("get_department_budget", {"department_id": "IT"})
    print(f"   ✅ Budget: {budget_result.content[0].text}")
    
    # Step 4: Search for products
    print("   4. Searching for products...")
    search_result = await session.call_tool("search_products", {"name": "laptop"})
    print(f"   ✅ Found products: {search_result.content[0].text[:100]}...")
    
    # Step 5: Get product details
    print("   5. Getting product details...")
    details_result = await session.call_tool("get_product_details", {"product_id": "LAPTOP-001"})
    print(f"   ✅ Product details: {details_result.content[0].text[:100]}...")
    
    # Step 6: Get supplier info
    print("   6. Getting supplier information...")
    supplier_result = await session.call_tool("get_supplier_info", {"supplier_id": "TECHCORP-001"})
    print(f"   ✅ Supplier: {supplier_result.content[0].text}")
    
    # Step 7: Create audit record
    print("   7. Creating audit record...")
    audit_result = await session.call_tool("create_audit_record", {
        "user_id": "alice-001",
        "action": "purchase_request",
        "details": {
            "product_id": "LAPTOP-001",
            "supplier_id": "TECHCORP-001",
            "amount": 1200
        },
        "decision_reasoning": "Laptop needed for development work"
    })
    print(f"   ✅ Audit record: {audit_result.content[0].text}")
    
    print("\n🎉 Complete business workflow test successful!")


async def run_tests(server_url: str):
    """Run all remote tests against the MCP server."""
    # Normalize the URL to ensure correct endpoint
    mcp_url = normalize_mcp_url(server_url)
    
    print(f"🚀 Testing MCP server at: {mcp_url}")
    print("Using official MCP Python SDK client with SSE transport")
    print("=" * 60)
    
    try:
        async with mcp_session(mcp_url) as session:
            # Test 1: List tools
            print("\n🔄 Test 1: Listing available tools...")
            tools_response = await session.list_tools()
            tools = tools_response.tools
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool.name}")
            
            # Test 2: Individual tool tests
            print("\n🔄 Test 2: Testing individual tools...")
            
            # Test get_user
            result = await session.call_tool("get_user", {"user_id": "alice-001"})
            print(f"✅ get_user: {result.content[0].text}")
            
            # Test search_products
            result = await session.call_tool("search_products", {"name": "laptop"})
            print("✅ search_products: Found products")
            
            # Test 3: Complete business workflow
            print("\n🔄 Test 3: Complete business workflow...")
            await test_business_workflow(session)
            
            print("\n" + "=" * 60)
            print("✅ All remote MCP tests passed!")
            print("🎉 Your deployed MCP server is working correctly!")
            
    except Exception as e:
        print(f"\n❌ Remote tests failed: {e}")
        print("💡 Check that your server supports MCP SSE transport")
        print("💡 Verify the server URL is correct and accessible")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        print("Usage: python run_remote_tests.py <server-url>")
        print("Examples:")
        print("  python run_remote_tests.py https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io")
        print("  python run_remote_tests.py https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io/sse")
        print("  python run_remote_tests.py https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io/sse/")
        print()
        print("Note: This script uses the official MCP Python SDK with SSE transport")
        print("The URL will be automatically normalized to include the correct MCP endpoint.")
        sys.exit(1)
    
    server_url = sys.argv[1]
    
    if not validate_url(server_url):
        print(f"Error: Invalid URL format: {server_url}")
        sys.exit(1)
    
    # Run the async tests
    asyncio.run(run_tests(server_url))


if __name__ == "__main__":
    main()
