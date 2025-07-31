# Purchase Order MCP Server

This MCP server provides business data and tools for internal purchase order processing.

## Features

- User lookup and department information
- Product search with intelligent matching
- Supplier details with pricing and delivery information
- Department budget tracking
- Audit logging for compliance

## Setup

### Local Development

```bash
# Install dependencies
uv sync

# Run the server (default: streamable-http transport)
uv run python main.py

# Run with SSE transport (for Azure AI Foundry compatibility)
MCP_TRANSPORT=sse uv run python main.py

# Run with custom port
PORT=9000 uv run python main.py
```

### Environment Variables

- `PORT`: Server port (default: 8000)
- `MCP_TRANSPORT`: Transport protocol - `streamable-http` (default) or `sse` (for Azure AI Foundry)

### Docker Deployment

```bash
# Build the container
docker build -t purchase-order-mcp .

# Run with streamable-http (default)
docker run -p 8000:8000 purchase-order-mcp

# Run with SSE transport for Azure AI Foundry
docker run -p 8000:8000 -e MCP_TRANSPORT=sse purchase-order-mcp
```

## Testing

### Local Testing

```bash
# Run local unit tests
uv run pytest tests/test_mcp_server.py -v
```

### Remote Testing (Azure Container Apps)

Test your deployed MCP server using the official MCP Python SDK client:

```bash
# Install dev dependencies (includes official MCP client)
uv sync --extra dev

# Test against deployed server using the test runner
python run_remote_tests.py https://mcp.YOUR_DOMAIN.azurecontainerapps.io

# Or set environment variable and run pytest directly
$env:MCP_SERVER_ENDPOINT="https://mcp.YOUR_DOMAIN.azurecontainerapps.io"
uv run pytest tests/test_remote_mcp_server.py -v
```

The remote tests use the **official MCP Python SDK client** and verify:
- MCP protocol compliance and tool availability
- All 7 business tools functionality via MCP Streamable HTTP transport  
- Complete purchase workflow integration
- Proper MCP session management and error handling

**Note:** The remote tests use MCP's SSE (Server-Sent Events) transport, not simple HTTP requests. This ensures proper protocol compliance and realistic testing of your deployed MCP server.

## Tools Available

### `get_user(user_id: str)`
Get user information including name and department association.

### `get_department_policy(department_id: str)`
Get department policy including allowed categories, purchase strategy, and audit requirements.

### `get_department_budget(department_id: str)`
Get current budget information including spent and remaining amounts.

### `search_products(name: str)`
Search for products by name or description. Handles equivalent product scenarios (e.g., "computer" finds "laptop").

### `get_product_details(product_id: str, supplier_id: str = None)`
Get detailed product information from suppliers including pricing, availability, and delivery times.

### `get_supplier_info(supplier_id: str)`
Get supplier information including reliability score and contact details.

### `create_audit_record(user_id: str, action: str, details: Dict, decision_reasoning: str = None)`
Create an audit record for compliance tracking.

## Test Data

The server includes comprehensive test data:

- **3 Users**: Alice (IT), Bob (HR), Carol (Marketing)
- **3 Departments**: Different policies, budgets, and allowed categories
- **5 Products**: Available from multiple suppliers with varying prices/delivery
- **Complex Scenarios**: Budget constraints, policy violations, equivalent products

## Business Logic

The server enforces business rules through its data structure:

1. **Department Policies**: Each department has allowed product categories
2. **Purchase Strategies**: "cheapest", "fastest", or "complex" text-based rules
3. **Budget Tracking**: Monthly budget limits with spending tracking
4. **Audit Requirements**: Some departments require audit logging

## Docker Deployment to Azure Container Apps

This server is designed to run in Azure Container Apps for production use:

```bash
# Deploy to Azure Container Apps
az group create -n d-ai-compare-orchestrations -l swedencentral
az containerapp env create -n mcp-env -g d-ai-compare-orchestrations -l swedencentral
az containerapp create -n mcp -g d-ai-compare-orchestrations -i ghcr.io/tkubica12/d-ai-compare-orchestrations/mcp-server:latest --target-port 8000 --ingress external --environment mcp-env --min-replicas 1 --env-vars MCP_TRANSPORT=sse
```
