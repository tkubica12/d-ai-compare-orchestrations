"""Working MCP client wrapper that handles FastMCP Streamable HTTP protocol correctly."""

import asyncio
import httpx
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class MCPTool:
    """Represents an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass 
class MCPToolResult:
    """Represents the result of calling an MCP tool."""
    content: List[Dict[str, Any]]
    is_error: bool = False


class FastMCPClient:
    """A working MCP client for FastMCP Streamable HTTP servers."""
    
    def __init__(self, base_url: str):
        """Initialize the client with the base URL."""
        self.base_url = base_url.rstrip('/') + '/'
        self.session_id: Optional[str] = None
        self.client: Optional[httpx.AsyncClient] = None
        self.message_id = 0
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient()
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for MCP requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "User-Agent": "fastmcp-client/1.0.0"
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        return headers
    
    def _next_message_id(self) -> int:
        """Get the next message ID."""
        self.message_id += 1
        return self.message_id
    
    async def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send an MCP request and parse the response."""
        message = {
            "jsonrpc": "2.0",
            "id": self._next_message_id(),
            "method": method,
            "params": params or {}
        }
        
        response = await self.client.post(
            self.base_url,
            json=message,
            headers=self._get_headers(),
            timeout=30
        )
        
        if response.status_code not in [200, 202]:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
        
        # Parse SSE response
        if "data: " in response.text:
            data_line = [line for line in response.text.split('\n') if line.startswith('data: ')][0]
            data = json.loads(data_line[6:])  # Remove 'data: ' prefix
            
            if "error" in data:
                raise Exception(f"MCP Error {data['error']['code']}: {data['error']['message']}")
            
            return data.get("result", data)
        
        return {}
    
    async def _send_notification(self, method: str, params: Dict[str, Any] = None):
        """Send an MCP notification (no response expected)."""
        message = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {}
        }
        
        response = await self.client.post(
            self.base_url,
            json=message,
            headers=self._get_headers(),
            timeout=30
        )
        
        if response.status_code not in [200, 202]:
            raise Exception(f"HTTP {response.status_code}: {response.text}")
    
    async def initialize(self):
        """Initialize the MCP session."""
        # Step 1: Initialize
        result = await self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "fastmcp-client",
                "version": "1.0.0"
            }
        })
        
        # Extract session ID from response headers (we need to do this differently)
        # For now, let's assume the server sends it in the last response
        if hasattr(self.client, '_last_response'):
            self.session_id = self.client._last_response.headers.get("mcp-session-id")
        
        # Get session ID from the most recent response
        # This is a bit hacky, but we need the session ID from the initialize call
        response = await self.client.post(
            self.base_url,
            json={
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "fastmcp-client", "version": "1.0.0"}
                }
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "User-Agent": "fastmcp-client/1.0.0"
            },
            timeout=30
        )
        
        self.session_id = response.headers.get("mcp-session-id")
        
        # Step 2: Send initialized notification
        await self._send_notification("notifications/initialized")
        
        return result
    
    async def list_tools(self) -> List[MCPTool]:
        """List available tools from the server."""
        result = await self._send_request("tools/list")
        
        tools = []
        for tool_data in result.get("tools", []):
            tools.append(MCPTool(
                name=tool_data["name"],
                description=tool_data["description"],
                input_schema=tool_data["inputSchema"]
            ))
        
        return tools
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> MCPToolResult:
        """Call a tool with the given arguments."""
        result = await self._send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })
        
        content = result.get("content", [])
        if isinstance(content, str):
            content = [{"type": "text", "text": content}]
        elif not isinstance(content, list):
            content = [{"type": "text", "text": str(content)}]
        
        return MCPToolResult(content=content)


# Convenience function for easy testing
async def test_fastmcp_client(server_url: str):
    """Test the FastMCP client."""
    async with FastMCPClient(server_url) as client:
        print("🔄 Listing tools...")
        tools = await client.list_tools()
        print(f"✅ Found {len(tools)} tools:")
        
        for tool in tools:
            print(f"   - {tool.name}: {tool.description[:100]}...")
        
        print("\n🔄 Testing get_user tool...")
        result = await client.call_tool("get_user", {"user_id": "alice-001"})
        print(f"✅ Tool result: {result.content}")
        
        print("\n🎉 FastMCP client test successful!")


if __name__ == "__main__":
    server_url = "https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io/mcp"
    asyncio.run(test_fastmcp_client(server_url))
