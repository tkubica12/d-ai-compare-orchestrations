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

## Architecture

### MCP Server
Provides business data through Model Context Protocol tools:
- User and department information
- Product catalog and supplier details
- Budget tracking and audit logging

### Test Data
- **3 Users**: Alice (IT), Bob (HR), Carol (Marketing)
- **3 Departments**: Different policies, budgets, and allowed categories
- **5 Products**: Available from multiple suppliers with varying prices/delivery
- **Complex Scenarios**: Budget constraints, policy violations, equivalent products

## Change Case Analysis

We implement two significant business changes to test adaptability:

### 1. Complex Purchase Strategies
**Before**: Simple rules ("cheapest", "fastest")
**After**: Complex text-based logic requiring calculations:
*"Prefer shortest possible delivery time where price is no more than 110% of lowest price of any supplier capable of delivering within 5 days"*

### 2. Conditional Auditing
**Before**: No auditing requirements
**After**: Department-policy-driven audit logging for compliance

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