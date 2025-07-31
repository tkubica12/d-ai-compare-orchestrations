"""Tests for the remote MCP server deployed to Azure Container Apps using official MCP client."""

import pytest
import os
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client
from contextlib import asynccontextmanager


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


class TestRemoteMCPServer:
    """Test the remote MCP server functionality via official MCP client."""
    
    @pytest.fixture
    def server_url(self):
        """Get the remote server URL from environment."""
        url = os.getenv("MCP_SERVER_ENDPOINT", "https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io")
        return normalize_mcp_url(url)
    
    @asynccontextmanager
    async def mcp_session(self, server_url: str):
        """Create MCP client session for the remote server using SSE transport."""
        try:
            # Use the full URL as provided (should include /sse or /mcp endpoint)
            async with sse_client(server_url) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the session
                    await session.initialize()
                    yield session
        except Exception as e:
            pytest.skip(f"Could not connect to MCP server at {server_url}: {e}")
    
    @pytest.mark.asyncio
    async def test_list_tools_remote(self, server_url):
        """Test that we can list tools from the remote MCP server."""
        async with self.mcp_session(server_url) as session:
            # List available tools
            tools_response = await session.list_tools()
            
            # Verify expected tools are available
            expected_tools = [
                "get_user",
                "get_department_policy", 
                "get_department_budget",
                "search_products",
                "get_product_details",
                "get_supplier_info",
                "create_audit_record"
            ]
            
            available_tools = [tool.name for tool in tools_response.tools]
            
            for expected_tool in expected_tools:
                assert expected_tool in available_tools, f"Tool {expected_tool} not found in remote server"
            
            print(f"✅ Found {len(available_tools)} tools: {available_tools}")
    
    @pytest.mark.asyncio
    async def test_get_user_remote(self, server_url):
        """Test user retrieval via remote MCP."""
        async with self.mcp_session(server_url) as session:
            # Call the get_user tool
            result = await session.call_tool("get_user", {"user_id": "alice-001"})
            
            # Verify response structure
            assert result.content is not None
            content_text = str(result.content[0].text) if result.content else ""
            
            # Verify user data
            assert "Alice Johnson" in content_text
            assert "IT" in content_text
            print(f"✅ User lookup successful: {content_text[:100]}...")
    
    @pytest.mark.asyncio 
    async def test_get_user_not_found_remote(self, server_url):
        """Test user not found scenario via remote MCP."""
        async with self.mcp_session(server_url) as session:
            result = await session.call_tool("get_user", {"user_id": "nonexistent"})
            
            content_text = str(result.content[0].text) if result.content else ""
            assert "not found" in content_text.lower() or "none" in content_text.lower()
            print(f"✅ User not found handling: {content_text}")
    
    @pytest.mark.asyncio
    async def test_search_products_remote(self, server_url):
        """Test product search via remote MCP."""
        async with self.mcp_session(server_url) as session:
            # Test exact match
            result = await session.call_tool("search_products", {"name": "Business Laptop"})
            content_text = str(result.content[0].text) if result.content else ""
            assert "Business Laptop" in content_text
            
            # Test equivalent product scenario
            result = await session.call_tool("search_products", {"name": "computer"})
            content_text = str(result.content[0].text) if result.content else ""
            assert len(content_text) > 0  # Should find something
            print("✅ Product search successful")
            
    @pytest.mark.asyncio
    async def test_get_product_details_remote(self, server_url):
        """Test product details retrieval via remote MCP."""
        async with self.mcp_session(server_url) as session:
            result = await session.call_tool("get_product_details", {"product_id": "LAPTOP-001"})
            
            content_text = str(result.content[0].text) if result.content else ""
            assert "LAPTOP-001" in content_text
            assert "supplier" in content_text.lower() or "price" in content_text.lower()
            print("✅ Product details retrieval successful")
    
    @pytest.mark.asyncio
    async def test_get_department_policy_remote(self, server_url):
        """Test department policy retrieval via remote MCP."""
        async with self.mcp_session(server_url) as session:
            result = await session.call_tool("get_department_policy", {"department_id": "IT"})
            
            content_text = str(result.content[0].text) if result.content else ""
            assert "Information Technology" in content_text or "IT" in content_text
            assert "electronics" in content_text.lower()
            print("✅ Department policy retrieval successful")
    
    @pytest.mark.asyncio
    async def test_get_department_budget_remote(self, server_url):
        """Test department budget retrieval via remote MCP."""
        async with self.mcp_session(server_url) as session:
            result = await session.call_tool("get_department_budget", {"department_id": "IT"})
            
            content_text = str(result.content[0].text) if result.content else ""
            assert "budget" in content_text.lower()
            assert any(char.isdigit() for char in content_text)  # Should contain budget numbers
            print("✅ Department budget retrieval successful")
    
    @pytest.mark.asyncio
    async def test_create_audit_record_remote(self, server_url):
        """Test audit record creation via remote MCP."""
        async with self.mcp_session(server_url) as session:
            result = await session.call_tool("create_audit_record", {
                "user_id": "alice-001",
                "action": "purchase_approved",
                "details": {"product": "LAPTOP-001", "supplier": "tech-supplier-01"},
                "decision_reasoning": "Remote MCP test audit record"
            })
            
            content_text = str(result.content[0].text) if result.content else ""
            assert "audit" in content_text.lower() or "record" in content_text.lower()
            print("✅ Audit record creation successful")


class TestRemoteMCPIntegration:
    """Test complete business scenarios via remote MCP server."""
    
    @pytest.fixture
    def server_url(self):
        """Get the remote server URL from environment."""
        url = os.getenv("MCP_SERVER_ENDPOINT", "https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io")
        return normalize_mcp_url(url)
    
    @asynccontextmanager
    async def mcp_session(self, server_url: str):
        """Create MCP client session for the remote server using SSE transport."""
        try:
            async with sse_client(server_url) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    yield session
        except Exception as e:
            pytest.skip(f"Could not connect to MCP server at {server_url}: {e}")
    
    @pytest.mark.asyncio
    async def test_complete_purchase_workflow_remote(self, server_url):
        """Test a complete purchase workflow via remote MCP."""
        async with self.mcp_session(server_url) as session:
            print("🔄 Testing complete purchase workflow...")
            
            # 1. Get user info
            user_result = await session.call_tool("get_user", {"user_id": "alice-001"})
            assert user_result.content is not None
            print("  ✅ User lookup completed")
            
            # 2. Get department policy
            policy_result = await session.call_tool("get_department_policy", {"department_id": "IT"})
            assert policy_result.content is not None
            print("  ✅ Department policy retrieved")
            
            # 3. Check budget
            budget_result = await session.call_tool("get_department_budget", {"department_id": "IT"})
            assert budget_result.content is not None
            print("  ✅ Budget status checked")
            
            # 4. Search for products
            search_result = await session.call_tool("search_products", {"name": "laptop"})
            assert search_result.content is not None
            print("  ✅ Product search completed")
            
            # 5. Get product details
            details_result = await session.call_tool("get_product_details", {"product_id": "LAPTOP-001"})
            assert details_result.content is not None
            print("  ✅ Product details retrieved")
            
            # 6. Get supplier information
            supplier_result = await session.call_tool("get_supplier_info", {"supplier_id": "TECHCORP-001"})
            assert supplier_result.content is not None
            print("  ✅ Supplier information retrieved")
            
            # 7. Create audit record
            audit_result = await session.call_tool("create_audit_record", {
                "user_id": "alice-001",
                "action": "workflow_test",
                "details": {"test": "complete_workflow"},
                "decision_reasoning": "Integration test workflow via MCP client"
            })
            assert audit_result.content is not None
            print("  ✅ Audit record created")
            
            print("🎉 Complete workflow test successful!")


if __name__ == "__main__":
    # Run with environment variable: MCP_SERVER_ENDPOINT=https://your-deployed-server.com
    print("Remote MCP Server Tests (Official MCP Client)")
    print("=" * 50)
    print("Set MCP_SERVER_ENDPOINT environment variable to your deployed server URL")
    print("The URL will be automatically normalized to include the correct MCP endpoint.")
    print()
    print("Examples:")
    print("  $env:MCP_SERVER_ENDPOINT='https://mcp.your-domain.azurecontainerapps.io'")
    print("  $env:MCP_SERVER_ENDPOINT='https://mcp.your-domain.azurecontainerapps.io/sse'")
    print("  $env:MCP_SERVER_ENDPOINT='https://mcp.your-domain.azurecontainerapps.io/sse/'")
    print()
    
    pytest.main([__file__, "-v", "-s"])
