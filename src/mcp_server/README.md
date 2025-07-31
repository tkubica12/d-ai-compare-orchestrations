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

# Run the server
uv run python main.py
```

### Docker Deployment

```bash
# Build the container
docker build -t purchase-order-mcp .

# Run the container
docker run -p 8000:8000 purchase-order-mcp
```

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
# Build and push to Azure Container Registry
az acr build --registry myregistry --image purchase-order-mcp:latest .

# Deploy to Azure Container Apps
az containerapp create \
  --name purchase-order-mcp \
  --resource-group mygroup \
  --environment myenv \
  --image myregistry.azurecr.io/purchase-order-mcp:latest \
  --target-port 8000 \
  --ingress external
```
