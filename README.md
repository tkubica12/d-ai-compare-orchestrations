# AI Orchestration Comparison Project

## Overview

This project demonstrates and compares three different levels of autonomy in AI orchestration for internal purchase order processing. We showcase how different approaches handle business logic, adapt to changes, and consume computational resources.

## Business Process

The core business process simulates an internal purchase request system:

1. **User Request**: User submits a text request for a product purchase along with their userId
2. **User Lookup**: System retrieves user information and department association
3. **Policy Check**: Validates department permissions (allowed categories, purchase strategy, budget)
4. **Product Search**: Finds matching products in the catalog
5. **Supplier Analysis**: Retrieves pricing, delivery times, and availability from multiple suppliers
6. **Selection Logic**: Applies department's purchase strategy to recommend optimal supplier
7. **Order Suggestion**: Presents final recommendation with justification

## Orchestration Approaches

### 1. Fixed Graph - LangGraph
- **Autonomy Level**: Low - Static workflow
- **Implementation**: Predefined nodes and edges in a fixed execution graph
- **Advantages**: Predictable, debuggable, fast execution
- **Use Case**: When business logic is stable and well-defined

### 2. Dynamic Planning - Semantic Kernel
- **Autonomy Level**: Medium - AI-planned execution
- **Implementation**: AI planner creates execution strategy using available plugins
- **Advantages**: Flexible planning while maintaining framework structure
- **Use Case**: When some variability in execution flow is needed

### 3. Self-Orchestrated - AI Foundry Agent Service
- **Autonomy Level**: High - Full reasoning with tools
- **Implementation**: Reasoning model thinks through the problem and calls MCP tools
- **Advantages**: Maximum flexibility, natural problem-solving, easy extension
- **Use Case**: When complex reasoning and adaptability are required

## Current Status: ✅ MCP Server Production Ready

### Phase 1 Complete: Business Logic Foundation
- **✅ MCP Server**: FastMCP v2 with 7 business tools deployed to Azure Container Apps
- **✅ Production Endpoint**: https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io/mcp
- **✅ Remote Testing**: Complete business workflow validation with working FastMCP client
- **✅ Data Models**: Realistic business scenarios with users, departments, products, suppliers

### Phase 2 Ready: Orchestration Implementation
Ready to implement three AI orchestration approaches consuming the production MCP server:
1. **LangGraph**: Fixed workflow graphs consuming MCP tools
2. **Semantic Kernel**: Dynamic planning with MCP plugin integration  
3. **AI Foundry Agent Service**: Self-orchestrated reasoning with MCP tool access

### Quick Start
```bash
# Test the production MCP server
cd src/mcp_server
uv run python run_remote_tests.py https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io

# Start local development
uv run python main.py  # Local MCP server on port 8001
```

## Change Case Analysis

We implement two significant business changes to test adaptability:

### 1. Complex Purchase Strategies
**Before**: Simple rules ("cheapest", "fastest")
**After**: Complex text-based logic requiring calculations:
*"Prefer shortest possible delivery time where price is no more than 110% of lowest price of any supplier capable of delivering within 5 days"*

### 2. Conditional Auditing
**Before**: No auditing requirements
**After**: Department-policy-driven audit logging for compliance

## Architecture & Data

### MCP Server Foundation
Deployed production server provides business data through Model Context Protocol:
- **7 Business Tools**: User lookup, department policies, budget tracking, product search, supplier analysis, audit logging
- **Production Ready**: Container Apps deployment with health checks and proper HTTP transport
- **Test Coverage**: Complete business workflow validation via remote testing

### Test Data Ecosystem  
- **3 Users**: Alice (IT), Bob (HR), Carol (Marketing) with realistic department associations
- **3 Departments**: Different policies, budgets ($50K IT, $20K HR, $30K Marketing), and allowed categories
- **5 Products**: Business laptops, office chairs, software licenses, monitors, printers
- **Multiple Suppliers**: 3-5 suppliers per product with varying prices, delivery times, reliability scores
- **Complex Scenarios**: Budget constraints, policy violations, equivalent product matching

## Evaluation Metrics

- **Token Usage**: Measure AI model consumption across approaches
- **Development Effort**: Lines of code and complexity for initial implementation
- **Adaptation Cost**: Effort required to implement change cases
- **Execution Performance**: Response time and resource utilization
- **Business Accuracy**: Correct handling of edge cases and business rules

## Getting Started

### Prerequisites
- Python 3.11+
- uv package manager

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd d-ai-compare-orchestrations

# Install dependencies
uv sync

# Run MCP server
uv run python src/mcp_server/main.py

# Run tests
uv run pytest
```

### Running Orchestration Examples
```bash
# LangGraph approach
uv run python src/orchestration/langgraph_approach.py

# Semantic Kernel approach
uv run python src/orchestration/semantic_kernel_approach.py

# Self-orchestrated approach
uv run python src/orchestration/self_orchestrated_approach.py
```

## Project Structure
```
├── src/
│   ├── mcp_server/          # MCP server implementation
│   ├── orchestration/       # Three orchestration approaches
│   └── models/              # Pydantic data models
├── tests/                   # Test scenarios and unit tests
├── data/                    # Mock business data (JSON)
└── docs/                    # Documentation and analysis
```

## Key Insights

This project demonstrates the trade-offs between different levels of AI autonomy:

- **Fixed workflows** excel in performance and predictability
- **Dynamic planning** balances flexibility with structure
- **Self-orchestration** maximizes adaptability at the cost of resources

The change case analysis reveals how architectural decisions impact long-term maintainability and the ability to evolve business logic.