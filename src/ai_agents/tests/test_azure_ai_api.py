"""
Simple test to understand Azure AI Foundry Agent API
"""
import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential

async def test_basic_agent():
    """Test basic agent creation and usage."""
    # Load config
    config_path = Path(__file__).parent.parent / ".env"
    load_dotenv(config_path)
    
    # Create client
    client = AIProjectClient(
        endpoint=os.getenv("PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential()
    )
    
    try:
        with client:
            # Create simple agent
            agent = client.agents.create_agent(
                model=os.getenv("MODEL_DEPLOYMENT_NAME"),
                name="test-agent",
                instructions="You are a helpful assistant."
            )
            
            print(f"Created agent: {agent.id}")
            
            # Create thread
            thread = client.agents.threads.create()
            print(f"Created thread: {thread.id}")
            
            # Add message
            message = client.agents.messages.create(
                thread_id=thread.id,
                role="user",
                content="Hello, what is 2+2?"
            )
            print(f"Created message: {message.id}")
            
            # Run agent
            run = client.agents.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id
            )
            print(f"Run status: {run.status}")
            
            # Get messages
            messages = client.agents.messages.list(thread_id=thread.id)
            print(f"Messages type: {type(messages)}")
            
            # Try to iterate through messages
            for msg in messages:
                print(f"Message role: {msg.role}")
                if msg.role == "assistant" and msg.content:
                    for content in msg.content:
                        if hasattr(content, 'text'):
                            print(f"Response: {content.text.value}")
            
            # Clean up
            client.agents.delete_agent(agent.id)
            print("Agent deleted")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_basic_agent())
