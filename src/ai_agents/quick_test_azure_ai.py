#!/usr/bin/env python3
"""
Quick test for Azure AI Agent with MCP tools.

This script performs a basic test to verify the Azure AI Agent can:
1. Initialize properly
2. Connect to the MCP server
3. Execute a simple purchase order task

Usage:
    uv run python quick_test_azure_ai.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from azure_ai_agent import AzureAIFoundryAgent


def main():
    """Run a quick test of the Azure AI Agent."""
    print("=== Azure AI Agent Quick Test ===")
    
    try:
        # Initialize the agent
        print("1. Initializing Azure AI Agent...")
        agent = AzureAIFoundryAgent()
        print("   ✓ Agent initialized successfully")
        
        # Test a simple purchase request with valid user ID
        print("2. Testing basic purchase request...")
        result = agent.process_purchase_request(
            user_id="alice-001",  # Use valid user ID from our test data
            product_request="I need to order 3 high-end laptops for our development team"
        )
        
        print("3. Agent Response:")
        print(f"   Success: {result.success}")
        print(f"   Recommendation: {result.recommendation}")
        print(f"   Reasoning: {result.reasoning}")
        
        if result.error_message:
            print(f"   Error: {result.error_message}")
        
        if result.steps:
            print("4. Execution Steps:")
            for step in result.steps:
                print(f"   Step {step.step_number}: {step.action}")
                if step.mcp_tool_called:
                    print(f"      Tool: {step.mcp_tool_called}")
        
        print("\n=== Test Complete ===")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
