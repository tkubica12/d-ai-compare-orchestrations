#!/usr/bin/env python3
"""
Test script for Azure AI Foundry Agent with MCP tools.
"""

import sys
import logging
from pathlib import Path

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from azure_ai_agent import AzureAIFoundryAgent


def main():
    """Test the Azure AI Foundry Agent with a sample purchase request."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("Testing Azure AI Foundry Agent with MCP tools...")
    print("=" * 60)
    
    # Create agent instance
    agent = AzureAIFoundryAgent()
    
    # Test purchase request
    user_id = "user123"
    product_request = "I need 3 high-end laptops for our engineering team"
    
    print(f"User ID: {user_id}")
    print(f"Request: {product_request}")
    print("\nProcessing request...")
    print("-" * 40)
    
    try:
        # Process the request
        result = agent.process_purchase_request(user_id, product_request)
        
        print("\nResult Summary:")
        print(f"Success: {result.success}")
        print(f"Total Steps: {result.total_steps}")
        print(f"Execution Time: {result.execution_time_seconds:.2f} seconds")
        
        if result.success:
            print("\nRecommendation:")
            print(result.recommendation)
            print("\nReasoning:")
            print(result.reasoning)
        else:
            print(f"\nError: {result.error_message}")
        
        print("\nExecution Steps:")
        for step in result.steps:
            print(f"  {step.step_number}. {step.action}")
            if step.mcp_tool_called:
                print(f"     MCP Tool: {step.mcp_tool_called}")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
