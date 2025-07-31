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
Run the comprehensive business scenario tests with detailed markdown reports:
```bash
cd src/ai_agents
uv sync

# Run all scenarios with detailed markdown logging
uv run python tests/demo_azure_ai_agent_markdown.py

# Or specify the agent mode (future: langchain, semantickernel)
uv run python tests/demo_azure_ai_agent_markdown.py --mode azureai
```

This will generate detailed markdown reports in the `results/` directory with the naming pattern:
- `azureai-scenario1.md` - Unauthorized Product Test
- `azureai-scenario2.md` - Budget Exceeded Test  
- `azureai-scenario3.md` - Multiple Suppliers Test
- `azureai-scenario4.md` - Equivalent Product Test
- `azureai-scenario5.md` - Successful Purchase Test

Each report includes:
- **Executive Summary** with final recommendation and reasoning
- **Detailed Execution Log** showing each step with timestamps
- **MCP Tools Usage** with parameters and responses  
- **Performance Metrics** including execution time and step counts
- **Technical Details** and future token usage tracking

### Report Structure

Each markdown report provides comprehensive visibility into:

```markdown
# Scenario X: Description - MODE
- Execution metadata (timestamp, user, request, status)
- Executive summary with final recommendation
- Step-by-step execution log with timestamps
- MCP tool calls with parameters and responses
- Performance metrics and technical details
- Token usage (planned for future implementation)
```

### Testing Approach

Since AI output is non-deterministic, our testing approach focuses on:

- **Process Validation**: Ensuring the agent follows logical steps
- **Tool Usage**: Verifying appropriate MCP tools are called
- **Outcome Analysis**: Checking for expected keywords and patterns
- **Execution Logging**: Detailed tracking of reasoning process
- **Metrics Collection**: Performance and behavior statistics
- **Markdown Reports**: Human-readable execution traces with tool interactions

Rather than strict assertions, tests demonstrate agent behavior and generate detailed markdown reports for human evaluation and comparison between different agent implementations.

### Results Analysis

The markdown reports enable comprehensive analysis:

1. **Cross-Mode Comparison**: Compare `azureai-scenario1.md` vs `langchain-scenario1.md` vs `semantickernel-scenario1.md`
2. **Tool Usage Patterns**: Analyze which MCP tools each mode uses and how
3. **Performance Metrics**: Compare execution times and step counts across modes
4. **Decision Quality**: Evaluate recommendation quality and reasoning depth
5. **Error Handling**: Review how each mode handles edge cases and errors

#### Troubleshooting
- **Connection Issues**: Verify MCP server URL and network connectivity
- **Azure Auth**: Run `az login` and check `.env` configuration
- **Empty Results**: Check agent permissions and model deployment access
- **Slow Performance**: Agent creation adds 10-20 seconds overhead per scenario

### Running Tests

```bash
# Quick start - run all scenarios with markdown reports
cd src/ai_agents
uv sync
uv run python tests/demo_azure_ai_agent_markdown.py --mode azureai

# View results in results/ directory
ls results/
# azureai-scenario1.md, azureai-scenario2.md, etc.
```

#### Test Configuration
- Ensure MCP server is running: `https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io/sse/`
- Configure Azure AI credentials in `.env` file
- Use `--mode azureai` (future: `langchain`, `semantickernel`)

#### Expected Results
- **Scenario 1**: Should fail gracefully (unauthorized product)
- **Scenarios 2-5**: Should complete successfully with recommendations
- **Execution time**: 15-45 seconds per scenario
- **Steps**: 7-12 actions including agent lifecycle management

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
