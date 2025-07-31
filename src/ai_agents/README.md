# AI Agents for Purchase Order Processing

This module implements three different approaches to AI orchestration for purchase order processing:

1. **Azure AI Foundry Agent** (`azure_ai_agent.py`) - Self-orchestrated using Azure AI Foundry Agent Service
2. **LangGraph Agent** (coming soon) - Predefined workflow with static graph
3. **Semantic Kernel Agent** (coming soon) - AI planning with flexible execution

## Azure AI Foundry Agent

The Azure AI Foundry Agent uses Azure AI Foundry Agent Service to create intelligent agents with MCP tools and code interpreter capabilities. It creates temporary agents for each request and automatically cleans them up after processing.

### Features

- **Agent Service Integration**: Uses Azure AI Foundry Agent Service for managed agent lifecycle
- **MCP Tools**: Automatically converts MCP tools to agent-compatible functions
- **Code Interpreter**: Built-in support for complex calculations and data analysis
- **Auto-Cleanup**: Creates and deletes agents for each request to avoid resource leaks
- **Detailed Logging**: Tracks every step of the agent execution process
- **Azure Authentication**: Uses Azure Default Credential for secure access

### Configuration

1. Copy `.env.example` to `.env`
2. Fill in your Azure AI Foundry project details:
   ```
   PROJECT_ENDPOINT=https://your-resource.services.ai.azure.com/api/projects/your-project
   MODEL_DEPLOYMENT_NAME=gpt-4o
   ```
3. Ensure you're authenticated with Azure: `az login`

### Usage

#### Direct Usage
```python
from azure_ai_agent import AzureAIFoundryAgent

agent = AzureAIFoundryAgent()
result = await agent.process_purchase_request(
    user_id="alice-001",
    product_request="I need a laptop for development work"
)

print(f"Recommendation: {result.recommendation}")
print(f"Execution time: {result.execution_time_seconds:.2f}s")
```

#### Demo Script
Run the comprehensive business scenario tests:
```bash
cd src/ai_agents
uv sync
uv run python tests/demo_azure_ai_agent.py
```

### Testing Approach

Since AI output is non-deterministic, our testing approach focuses on:

- **Process Validation**: Ensuring the agent follows logical steps
- **Tool Usage**: Verifying appropriate MCP tools are called
- **Outcome Analysis**: Checking for expected keywords and patterns
- **Execution Logging**: Detailed tracking of reasoning process
- **Metrics Collection**: Performance and behavior statistics

Rather than strict assertions, tests demonstrate agent behavior and log outcomes for human evaluation.

### Business Scenarios

The demo script tests these scenarios from `Design.md`:

1. **Unauthorized Product**: User requests product outside their department's allowed categories
2. **Budget Exceeded**: User requests expensive item that exceeds budget limits
3. **Multiple Suppliers**: Agent compares suppliers using department's purchase strategy
4. **Equivalent Products**: Agent finds alternative products for general search terms
5. **Successful Purchase**: Complete workflow from request to audit trail

### Architecture

```
AzureAIFoundryAgent
├── Configuration (.env)
├── Azure AI Projects Client
├── Agent Creation (temporary)
├── MCP Tool Integration
├── Code Interpreter
├── Execution Tracking
├── Step-by-Step Logging
├── Agent Cleanup
└── Structured Results
```

### Installation

```bash
cd src/ai_agents
uv sync
```

### Dependencies

- `azure-ai-projects>=1.0.0b4` - Azure AI Foundry Agent Service
- `azure-identity>=1.15.0` - Azure authentication
- `python-dotenv>=1.0.0` - Environment configuration
- `httpx>=0.25.0` - HTTP client for MCP
- `pydantic>=2.0.0` - Data validation

### Performance

Typical execution metrics:
- **Steps per scenario**: 8-12 actions (includes agent creation/cleanup)
- **Execution time**: 15-45 seconds depending on complexity and agent provisioning
- **Resource usage**: Temporary agents are created and immediately deleted

### Azure AI Foundry Requirements

- Azure AI Foundry project with deployed model (GPT-4o recommended)
- Azure AI User role at project scope
- Model deployment accessible via the project endpoint

### Limitations

- Requires Azure AI Foundry project setup and appropriate permissions
- Agent creation/deletion adds overhead compared to persistent connections
- Response time includes agent provisioning time
- Non-deterministic output requires human evaluation of results
