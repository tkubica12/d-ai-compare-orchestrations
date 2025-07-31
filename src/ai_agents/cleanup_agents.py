"""
Utility script to clean up orphaned Azure AI Foundry agents.

This script lists and optionally deletes agents that may have been left
running due to unexpected errors or incomplete cleanup.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential


def cleanup_agents(delete_all=False, name_filter="purchase-order-agent"):
    """
    Clean up orphaned Azure AI Foundry agents.
    
    Args:
        delete_all: If True, delete all matching agents. If False, just list them.
        name_filter: Only consider agents with names containing this string.
    """
    # Load configuration
    config_path = Path(__file__).parent / ".env"
    if config_path.exists():
        load_dotenv(config_path)
    
    # Validate required environment variables
    if not os.getenv("PROJECT_ENDPOINT"):
        print("❌ PROJECT_ENDPOINT not found in environment variables")
        return
    
    try:
        # Create client
        client = AIProjectClient(
            endpoint=os.getenv("PROJECT_ENDPOINT"),
            credential=DefaultAzureCredential()
        )
        
        with client:
            # List all agents
            agents = client.agents.list_agents()
            
            # Filter agents by name
            matching_agents = []
            for agent in agents:
                if name_filter in agent.name:
                    matching_agents.append(agent)
            
            if not matching_agents:
                print(f"✅ No agents found with name containing '{name_filter}'")
                return
            
            print(f"🔍 Found {len(matching_agents)} agent(s) matching '{name_filter}':")
            
            for agent in matching_agents:
                print(f"  - Agent ID: {agent.id}")
                print(f"    Name: {agent.name}")
                print(f"    Model: {agent.model}")
                print(f"    Created: {agent.created_at}")
                print()
            
            if delete_all:
                print(f"🗑️  Deleting {len(matching_agents)} agent(s)...")
                
                deleted_count = 0
                for agent in matching_agents:
                    try:
                        client.agents.delete_agent(agent.id)
                        print(f"✅ Deleted agent {agent.id} ({agent.name})")
                        deleted_count += 1
                    except Exception as e:
                        print(f"❌ Failed to delete agent {agent.id}: {e}")
                
                print(f"🎉 Successfully deleted {deleted_count}/{len(matching_agents)} agents")
            else:
                print("ℹ️  To delete these agents, run with --delete flag")
    
    except Exception as e:
        print(f"❌ Error accessing Azure AI Foundry: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Main function to handle command line arguments."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up Azure AI Foundry agents")
    parser.add_argument("--delete", action="store_true", help="Actually delete the agents (default: just list them)")
    parser.add_argument("--name-filter", default="purchase-order-agent", help="Filter agents by name containing this string")
    
    args = parser.parse_args()
    
    print("Azure AI Foundry Agent Cleanup Utility")
    print("=" * 50)
    
    if args.delete:
        print("⚠️  WARNING: This will permanently delete matching agents!")
        response = input("Are you sure you want to continue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    cleanup_agents(delete_all=args.delete, name_filter=args.name_filter)


if __name__ == "__main__":
    main()
