#!/usr/bin/env python3
"""
Test Azure AI Agent without MCP tools to isolate the issue.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from azure_ai_agent import AzureAIFoundryAgent


def test_agent_without_mcp():
    """Test if the agent works without MCP tools."""
    print("=== Testing Azure AI Agent WITHOUT MCP Tools ===")
    
    try:
        # Initialize the agent
        agent = AzureAIFoundryAgent()
        
        # Test with a simple request that doesn't require MCP tools
        print("Testing basic agent functionality...")
        
        # We'll need to create a version without MCP tools
        print("❌ Need to create a test version without MCP tools")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    test_agent_without_mcp()
