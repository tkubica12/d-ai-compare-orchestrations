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
