#!/usr/bin/env python3
"""
Basic validation script for Azure AI Agent structure.

This script validates the agent structure and configuration without requiring
Azure OpenAI credentials. Use this to verify the implementation before
running the full demo.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def validate_structure():
    """Validate the AI agents project structure."""
    print("🔍 Validating Azure AI Agent Structure")
    print("=" * 50)
    
    base_path = Path(__file__).parent.parent
    
    # Check required files
    required_files = [
        "azure_ai_agent.py",
        ".env.example", 
        "pyproject.toml",
        "README.md",
        "tests/__init__.py",
        "tests/demo_azure_ai_agent.py"
    ]
    
    missing_files = []
    for file in required_files:
        file_path = base_path / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
        return False
    
    print("\n✅ All required files present")
    return True


def validate_imports():
    """Validate that the Azure AI Agent can be imported."""
    print("\n🔍 Validating Imports")
    print("=" * 50)
    
    try:
        from azure_ai_agent import AzureAIFoundryAgent, AgentResult, AgentStep
        print("✅ Main classes imported successfully")
        
        # Check class structure
        agent_methods = [method for method in dir(AzureAIFoundryAgent) if not method.startswith('_')]
        print(f"✅ AzureAIFoundryAgent methods: {agent_methods}")
        
        # Check dataclass fields
        agent_result_fields = AgentResult.__dataclass_fields__.keys()
        print(f"✅ AgentResult fields: {list(agent_result_fields)}")
        
        agent_step_fields = AgentStep.__dataclass_fields__.keys()
        print(f"✅ AgentStep fields: {list(agent_step_fields)}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 This is expected if dependencies are not installed")
        print("   Run: cd src/ai_agents && uv sync")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def validate_configuration():
    """Validate configuration template."""
    print("\n🔍 Validating Configuration")
    print("=" * 50)
    
    env_example = Path(__file__).parent.parent / ".env.example"
    
    if not env_example.exists():
        print("❌ .env.example not found")
        return False
    
    with open(env_example, 'r') as f:
        content = f.read()
    
    required_vars = [
        "PROJECT_ENDPOINT",
        "MODEL_DEPLOYMENT_NAME",
        "MCP_SERVER_URL"
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in content:
            missing_vars.append(var)
        else:
            print(f"✅ {var}")
    
    if missing_vars:
        print(f"❌ Missing configuration variables: {missing_vars}")
        return False
    
    print("✅ Configuration template complete")
    print("\n💡 Next steps for Azure AI Foundry Agent:")
    print("1. Copy .env.example to .env")
    print("2. Create Azure AI Foundry project and deploy a model")
    print("3. Fill in PROJECT_ENDPOINT and MODEL_DEPLOYMENT_NAME")
    print("4. Authenticate with Azure: az login")
    print("5. Install dependencies: uv sync")
    print("6. Run demo: uv run python tests/demo_azure_ai_agent.py")
    return True
def main():
    """Main validation function."""
    print("Azure AI Agent Validation")
    print("=" * 60)
    
    results = [
        validate_structure(),
        validate_imports(),
        validate_configuration()
    ]
    
    if all(results):
        print("\n🎉 All validations passed!")
        print("\n📋 Next steps for Azure AI Foundry:")
        print("1. Create Azure AI Foundry project and deploy a model")
        print("2. Copy .env.example to .env")
        print("3. Fill in your Azure AI Foundry project details")
        print("4. Authenticate with Azure: az login")
        print("5. Install dependencies: uv sync")
        print("6. Run demo: uv run python tests/demo_azure_ai_agent.py")
    else:
        print("\n❌ Some validations failed")
        print("Please fix the issues before proceeding")


if __name__ == "__main__":
    main()
