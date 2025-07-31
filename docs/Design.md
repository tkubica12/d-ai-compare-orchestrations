# Architecture Design

## Overview
This project demonstrates three different approaches to AI self-orchestration for order processing scenarios. The architecture consists of a mock MCP server providing business data services and three different orchestration implementations.

## Mock MCP Server Architecture

### Data Model
The MCP server will provide tools for accessing business data with Pydantic models and maintain mock data in memory.

#### Core Entities
- **User**: `userId`, `name`, `departmentId`
- **Department**: `departmentId`, `name`, `allowedCategories[]`, `purchaseStrategy`, `monthlyBudget`
- **Product**: `productId`, `name`, `category`, `supplierId`
- **Supplier**: `supplierId`, `name`, `products[]`
- **ProductDetails**: `productId`, `supplierId`, `price`, `availability`, `deliveryDays`
- **AuditRecord**: `timestamp`, `userId`, `action`, `details`

#### Purchase Strategies
- `"cheapest"`: Select supplier with lowest price
- `"fastest"`: Select supplier with shortest delivery time
- `"complex"`: Text-based complex strategies using reasoning and calculations

### MCP Tools
- `get_user(userId)`: Returns user details including department
- `get_department_policy(departmentId)`: Returns department policy
- `get_department_budget(departmentId)`: Returns current budget info
- `search_products(name)`: Search products by name
- `get_product_details(productId, supplierId)`: Get product details from specific supplier
- `create_audit_record(userId, action, details)`: Create audit record

### Mock Data Design
The mock data will be stored in JSON files within the `data/` folder for easy modification and maintenance.

#### Data Structure Overview
- **users.json**: 3 users with different departments and roles
- **departments.json**: 3 departments with distinct policies and budgets
- **products.json**: 5 products across different categories
- **suppliers.json**: 5+ suppliers with company information
- **product_details.json**: Each product available from at least 5 suppliers with varying:
  - Prices (to test budget constraints and cheapest strategy)
  - Delivery times (to test fastest strategy)
  - Stock availability (to test availability scenarios)

#### User Profiles
1. **Alice** (IT Department) - Generous budget, tech products allowed
2. **Bob** (HR Department) - Limited budget, office supplies only  
3. **Carol** (Marketing Department) - Medium budget, marketing materials allowed

#### Department Policies
1. **IT Department**: `allowedCategories: ["electronics", "software"]`, `purchaseStrategy: "fastest"`
2. **HR Department**: `allowedCategories: ["office-supplies"]`, `purchaseStrategy: "cheapest"`
3. **Marketing Department**: `allowedCategories: ["marketing-materials", "office-supplies"]`, `purchaseStrategy: "cheapest"`

#### Product Categories & Supplier Variety
Each of the 5 products will be available from at least 5 suppliers with diverse characteristics:
- **Price ranges**: From budget-friendly to premium options
- **Delivery times**: From same-day to 2+ weeks
- **Stock levels**: In-stock, limited stock, out-of-stock scenarios
- **Supplier reliability**: Mix of established and newer suppliers

#### Equivalent Product Scenarios
The LLM will need to intelligently match search terms to product names and descriptions:
- Search for "Computer" → Should find "Business Laptop"
- Search for "Chair" → Should find "Ergonomic Office Chair"  
- Search for "Printer Paper" → Should find "Professional Notebooks"

## Orchestration Approaches

### 1. LangGraph Approach (`langgraph_approach.py`)
- **Framework**: LangGraph with predefined workflow
- **Architecture**: Static graph with nodes for each business step
- **Nodes**: 
  - User validation
  - Policy check
  - Budget validation
  - Product search
  - Supplier comparison
  - Decision making
- **Edges**: Fixed transitions between nodes
- **Advantages**: Predictable flow, easy to debug
- **Disadvantages**: Rigid, requires manual updates for changes

### 2. Semantic Kernel Approach (`semantic_kernel_approach.py`)
- **Framework**: Microsoft Semantic Kernel
- **Architecture**: AI-planned execution with flexible planning
- **Components**:
  - Kernel with plugins for each API
  - Planner that creates execution strategy
  - Function calling for API interactions
- **Advantages**: More flexible than static graphs
- **Disadvantages**: Still framework-dependent

### 3. Self-Orchestrated Approach (`self_orchestrated_approach.py`)
- **Framework**: AI Foundry Agent Service with reasoning model
- **Architecture**: AI reasons through the problem using available MCP tools
- **Tools**:
  - MCP client for business data access
  - Code interpreter for complex calculations
  - Memory for context tracking
- **Advantages**: Maximum flexibility, natural reasoning, easy to extend
- **Disadvantages**: Less predictable, requires careful prompt engineering, higher token usage

## Testing Strategy

### Unit Tests
- API service endpoints
- Individual orchestration components
- Mock data integrity

### Integration Tests
- End-to-end orchestration flows
- MCP server functionality
- Error handling scenarios

### AI Agent Testing Approach
Since AI output is non-deterministic, traditional unit testing with assertions is not suitable. Instead, we use:

#### Demonstration-Based Testing
- **Process Validation**: Verify agents follow logical reasoning steps
- **Tool Usage Analysis**: Ensure appropriate MCP tools are called in sequence
- **Outcome Pattern Matching**: Check for expected keywords and decision patterns
- **Execution Logging**: Detailed tracking of reasoning process and tool calls
- **Performance Metrics**: Measure execution time, steps, and token usage

#### Test Script Format
Rather than pytest with assertions, we use demonstration scripts that:
- Run business scenarios and log detailed execution traces
- Analyze agent behavior patterns (e.g., "Did it check policies?")
- Generate structured reports with metrics for comparison
- Save results to JSON for further analysis
- Provide human-readable summaries of agent performance

#### Evaluation Criteria
- **Correctness**: Does the agent reach appropriate conclusions?
- **Completeness**: Are all necessary steps performed?
- **Efficiency**: Optimal number of steps and tool calls?
- **Reasoning Quality**: Clear explanations and logical flow?

### Business Scenario Tests
Located in `src/ai_agents/tests/demo_azure_ai_agent.py`:

1. **Unauthorized Product Test**
   - User: Bob (HR), Product: Laptop (Electronics)
   - Expected: Rejection with alternative suggestions

2. **Budget Exceeded Test**
   - User: Bob (HR), Product: Expensive Office Chair
   - Expected: Budget explanation with cheaper alternatives

3. **Multiple Suppliers Test**
   - User: Alice (IT), Product: Laptop
   - Expected: Supplier comparison based on "fastest" strategy

4. **Equivalent Product Test**
   - User: Alice (IT), Search: "Computer"
   - Expected: Finds "Laptop" as equivalent

5. **Successful Purchase Test**
   - User: Carol (Marketing), Product: Professional Notebooks
   - Expected: Complete workflow with audit trail

### Change Case Testing
Test cases for adaptation scenarios:
1. **Complex Purchase Strategies**: From simple "cheapest" to text-based complex logic like "prefer shortest possible delivery time where price is no more than 110% of lowest price of any supplier capable of delivering within 5 days"
2. **Enhanced Audit Requirements**: Adding conditional auditing based on department policy
3. **MCP Protocol Changes**: Schema evolution and backward compatibility

## Implementation Phases

### Phase 1: Mock MCP Server
1. Set up MCP server with business data tools
2. Implement Pydantic models for data validation
3. Create JSON data files with comprehensive mock data
4. Create mock data loading and management system
5. Implement all MCP tools
6. Add basic logging and error handling

### Phase 2: Orchestration Implementations
1. LangGraph approach (static workflow)
2. Semantic Kernel approach (AI planning)
3. Self-orchestrated approach (AI Foundry Agent Service with reasoning)

### Phase 3: Testing & Validation
1. Unit tests for all components
2. Business scenario tests
3. Token usage measurement and comparison
4. Performance comparison
5. Documentation updates

### Phase 4: Change Case Implementation
1. Complex purchase strategies with code interpreter
2. Enhanced audit requirements
3. Adaptation comparison between approaches

## Technical Decisions

### Package Management
- **uv**: Chosen for fast dependency resolution and virtual environment management
- **pyproject.toml**: Modern Python project configuration

### API Framework
- **MCP Protocol**: Model Context Protocol for exposing business tools
- **Pydantic**: Data validation and serialization
- **Python MCP SDK**: For server implementation

### Testing Framework
- **pytest**: Comprehensive testing with fixtures and parametrization
- **pytest-asyncio**: For testing async FastAPI endpoints

### Logging
- **Python logging**: Built-in logging with structured output
- **Log levels**: DEBUG for development, INFO for operations, WARNING/ERROR for issues

### Data Storage
- **JSON files**: Structured data storage for easy modification and version control
- **In-memory loading**: Data loaded into memory at startup for fast access
- **Thread-safe**: Using appropriate locking for concurrent access

## Success Metrics

### Implementation Comparison
- **Development Time**: Lines of code, setup complexity
- **Token Usage**: Total tokens consumed per orchestration approach
- **Execution Cost**: Processing time, resource utilization
- **Adaptability**: Effort required for change cases (complex strategies, auditing)

### Business Validation
- **Accuracy**: Correct decision making for test cases
- **Error Handling**: Graceful failure modes
- **User Experience**: Clear explanations and suggestions

This design provides a solid foundation for implementing and comparing the three orchestration approaches while maintaining clean architecture and comprehensive testing.