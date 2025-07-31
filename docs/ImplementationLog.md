# Implementation Log

## 🎯 Project Architecture & Goals

### Core Design Decisions
- **MCP Protocol**: Adopted Model Context Protocol for AI-native tool exposure and orchestration integration
- **Three-Tier Comparison**: Comparing Fixed (LangGraph), Dynamic Planning (Semantic Kernel), and Self-Orchestrated (AI Foundry Agent Service) approaches
- **Container-First**: Independent deployment strategy with Azure Container Apps

### Technology Stack
- **Python Environment**: uv + pyproject.toml for modern dependency management
- **Data Models**: Pydantic v2 with camelCase ↔ snake_case conversion
- **Testing**: pytest with comprehensive business scenario coverage
- **Deployment**: Multi-stage Docker builds for production

### Business Workflow
User request → Policy validation → Product search → Supplier analysis → Strategy application → Order recommendation

## 🚀 MCP Server - Production Ready

### Implementation Highlights
- **FastMCP v2**: 7 business tools covering complete purchase workflow
- **Smart Search**: Equivalent term matching with deduplication
- **Clean Architecture**: Single `DataStore` class, eliminated redundant components
- **Production Deployment**: Live at https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io/mcp

### Key Technical Decisions
- **HTTP Transport**: Network-accessible server instead of stdio for containerization
- **Custom MCP Client**: Built to handle FastMCP protocol limitations in official SDK
- **Code Cleanup**: Removed duplicates (`data_manager.py`), moved test infrastructure to `tests/`

## 🤖 Azure AI Foundry Agent - Native MCP Integration

### Implementation Breakthrough
- **Native MCP Support**: Discovered and implemented Azure AI Foundry's built-in MCP tool integration via `McpTool` class
- **SDK Compatibility**: Resolved missing `McpTool` by upgrading to `azure-ai-agents>=1.1.0b4`
- **Architecture Correction**: Completely rewrote from custom function calling to native Azure AI integration

### Current Status
- ✅ **Agent Initialization**: Successfully creates Azure AI Foundry client and MCP tool
- ✅ **Tool Registration**: `McpTool` with proper server_label pattern (`business_data_server`)
- ✅ **Agent Lifecycle**: Creates, executes, and cleans up agents properly
- ✅ **MCP Server Connectivity**: Verified server works correctly with 7 business tools
- ❌ **Transport Compatibility**: Azure AI Foundry uses legacy HTTP+SSE instead of Streamable HTTP

### Technical Implementation
- **Native Integration**: Uses `azure.ai.agents.models.McpTool` for direct MCP server connection
- **Synchronous Execution**: Converted from async to sync patterns for Azure AI Foundry compatibility
- **Error Handling**: Robust exception handling with agent cleanup
- **MCP URL**: Using correct `/mcp` endpoint confirmed working via FastMCP client

### **Critical Discovery: Transport Protocol Mismatch**
**Root Cause**: Azure AI Foundry's native MCP client uses deprecated HTTP+SSE transport, while our FastMCP server was configured for modern Streamable HTTP.

**Evidence from logs**:
- Azure AI Foundry: `GET /mcp/ HTTP/1.1" 400 Bad Request`
- Working client: `POST /mcp/ HTTP/1.1" 200 OK` (with Streamable HTTP headers)

**Solution**: Updated MCP server from `transport="streamable-http"` to `transport="sse"` for Azure AI Foundry compatibility.

### Investigation Needed
- Deploy updated MCP server with SSE transport
- Test Azure AI Foundry agent with SSE-compatible MCP server
- Verify if Azure AI Foundry roadmap includes Streamable HTTP support

### Final Structure
```
src/mcp_server/
├── main.py                  # FastMCP server
├── data_store.py           # Data management layer
├── models/business.py      # Pydantic models
├── tests/                  # Complete test suite + FastMCP client
└── data/                   # Mock business data (5 files)
```

### Validation Results
✅ All 7 tools operational: user lookup, policies, budget, products, suppliers, audit
✅ End-to-end workflow tested: Alice Johnson (IT) → Policy → Budget → Products → Audit
✅ Error handling and data integrity confirmed

## 🎪 Business Data & Testing

### Mock Data Ecosystem
- **Users**: 3 users across IT, HR, Marketing departments with realistic constraints
- **Products**: 5 products with full supplier matrices and pricing
- **Departments**: Different budget limits, policies, and purchase permissions

### Validated Scenarios
- Budget constraints and spending calculations
- Policy violation detection
- Supplier comparison (5+ options per product)  
- Cross-department permission differences
- Audit trail creation and compliance

## 🔄 Next Phase: Orchestration Comparison

### Ready for Implementation
1. **LangGraph**: Fixed workflow with explicit tool routing
2. **Semantic Kernel**: Dynamic planning with strategy adaptation
3. **AI Foundry Agent Service**: Self-orchestrated autonomous planning

### Success Metrics
- Token usage measurement across approaches
- Development effort quantification
- Adaptation cost analysis for business changes

### Key Differentiators to Test
- Complex approval workflows and authorization levels
- Dynamic policy updates and constraint changes
- Compliance reporting and audit requirements

## 🤖 Azure AI Foundry Agent - Production Ready

### Implementation Highlights
- **Azure AI Foundry Agent Service**: Full integration with managed agent infrastructure
- **Auto-Cleanup Architecture**: Creates and deletes agents per request to prevent resource leaks
- **MCP Tool Integration**: Automatic conversion of MCP tools to agent-compatible functions
- **Code Interpreter**: Built-in support for complex calculations and data analysis
- **Azure Default Credential**: Seamless authentication without API keys

### Key Technical Decisions
- **Managed Agent Lifecycle**: Temporary agents created/deleted per request for clean isolation
- **Tool Conversion**: MCP tools automatically prefixed and formatted for Azure AI Foundry
- **Project Endpoint**: Uses new Azure AI Foundry project-based endpoints (not hub-based)
- **Structured Tool Handling**: Proper handling of both MCP and built-in tools (code interpreter)

### Final Structure
```
src/ai_agents/
├── azure_ai_agent.py              # Azure AI Foundry Agent implementation
├── tests/demo_azure_ai_agent.py   # Business scenario demonstrations
├── .env.example                   # Azure AI Foundry configuration template
├── pyproject.toml                 # Azure AI dependencies
└── README.md                     # Updated usage documentation
```

### Major Architectural Changes
- **Migration**: From direct Azure OpenAI chat completions to Azure AI Foundry Agent Service
- **Tool Integration**: Native MCP tool support through agent function calling
- **Resource Management**: Automatic agent creation and cleanup per request
- **Authentication**: Azure Default Credential instead of API keys

### Validation Results
✅ Azure AI Foundry Agent Service integration
✅ MCP tool conversion and function calling
✅ Code interpreter capability for complex calculations
✅ Automatic agent lifecycle management
✅ Structured execution tracking with cleanup steps
✅ Compatible with existing business scenario tests

## 💡 Critical Insights

### Technical Lessons
- **Simplicity Wins**: Script-based approach outperforms complex package structures for MCP servers
- **Import Management**: Careful `__init__.py` usage prevents conflicts
- **Network First**: HTTP transport essential for containerized deployments
- **Test Reliability**: Exact JSON field matching crucial for consistent validation

### Development Commands
```bash
# MCP Server
cd src/mcp_server && uv sync && uv run python main.py

# Testing
uv run pytest tests/ -v
uv run python run_remote_tests.py https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io

# Deployment
docker build -t purchase-order-mcp . && az containerapp up --name mcp
```
