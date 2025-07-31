"""
Azure AI Foundry Agent implementation for self-orchestrated purchase order processing.

This module implements a flexible AI agent that uses Azure AI Foundry Agent Service
to orchestrate purchase order workflows using native MCP tools support.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import McpTool


@dataclass
class AgentStep:
    """Represents a single step in the agent's execution."""
    step_number: int
    action: str
    reasoning: str
    mcp_tool_called: Optional[str] = None
    mcp_tool_params: Optional[Dict[str, Any]] = None
    mcp_result: Optional[str] = None
    timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class AgentResult:
    """Final result from the Azure AI Agent."""
    success: bool
    recommendation: str
    reasoning: str
    total_steps: int
    execution_time_seconds: float
    steps: List[AgentStep]
    error_message: Optional[str] = None


class AzureAIFoundryAgent:
    """
    Azure AI Foundry Agent for self-orchestrated purchase order processing.
    
    Uses Azure AI Foundry Agent Service to create agents with MCP tools
    and code interpreter capabilities for intelligent order processing.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the Azure AI Foundry Agent.
        
        Args:
            config_path: Path to the .env configuration file
        """
        self.logger = self._setup_logging()
        self._load_config(config_path)
        self.project_client: Optional[AIProjectClient] = None
        self.agent_id: Optional[str] = None
        self.execution_steps: List[AgentStep] = []
        self.step_counter = 0
        
    def _setup_logging(self) -> logging.Logger:
        """Setup structured logging for the agent."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _load_config(self, config_path: Optional[Path] = None) -> None:
        """Load configuration from environment variables."""
        if config_path is None:
            config_path = Path(__file__).parent / ".env"
        
        if config_path.exists():
            load_dotenv(config_path)
            self.logger.info(f"Loaded configuration from {config_path}")
        else:
            self.logger.warning(f"No .env file found at {config_path}, using environment variables")
        
        # Validate required environment variables
        required_vars = [
            "PROJECT_ENDPOINT",
            "MODEL_DEPLOYMENT_NAME"
        ]
        
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {missing_vars}")
    
    def _setup_project_client(self) -> AIProjectClient:
        """Setup Azure AI Foundry project client."""
        return AIProjectClient(
            endpoint=os.getenv("PROJECT_ENDPOINT"),
            credential=DefaultAzureCredential()
        )
    
    def _add_step(self, action: str, reasoning: str, 
                  mcp_tool_called: Optional[str] = None,
                  mcp_tool_params: Optional[Dict[str, Any]] = None,
                  mcp_result: Optional[str] = None) -> None:
        """Add an execution step to the tracking list."""
        self.step_counter += 1
        step = AgentStep(
            step_number=self.step_counter,
            action=action,
            reasoning=reasoning,
            mcp_tool_called=mcp_tool_called,
            mcp_tool_params=mcp_tool_params,
            mcp_result=mcp_result
        )
        self.execution_steps.append(step)
        
        # Log the step
        self.logger.info(f"Step {self.step_counter}: {action}")
        self.logger.debug(f"Reasoning: {reasoning}")
        if mcp_tool_called:
            self.logger.debug(f"MCP Tool: {mcp_tool_called}({mcp_tool_params})")
    
    def _create_mcp_tool(self) -> McpTool:
        """
        Create Azure AI Foundry native MCP tool.
        
        Returns:
            McpTool instance configured for the business data server
        """
        mcp_url = os.getenv("MCP_SERVER_URL", "https://mcp.ashystone-fba1adc5.swedencentral.azurecontainerapps.io")
        
        # Create MCP tool with native Azure AI Foundry support
        mcp_tool = McpTool(
            server_label="business_data_server",
            server_url=mcp_url,
            allowed_tools=[]  # Allow all tools by default
        )
        
        self.logger.info(f"Created MCP tool for server: {mcp_url}")
        return mcp_tool
    
    def _create_agent_instructions(self) -> str:
        """Create instructions for the Azure AI Foundry Agent."""
        return """You are an intelligent purchase order processing agent. Your job is to help users with purchase requests by analyzing their needs, checking policies, validating budgets, and providing recommendations.

You have access to MCP tools that provide business data access:
- get_user: Get user details including department
- get_department_policy: Get department purchasing policy and allowed categories  
- get_department_budget: Get current budget information
- search_products: Search for products by name (supports fuzzy matching)
- get_product_details: Get detailed product information including suppliers
- get_supplier_info: Get supplier information 
- create_audit_record: Create audit trail

Your approach should be:
1. Understand the user request and identify the user ID
2. Use get_user to get user details and department
3. Use get_department_policy to validate user permissions and check allowed categories
4. Use get_department_budget to check budget constraints
5. Use search_products to find relevant products
6. Use get_product_details and get_supplier_info to analyze supplier options
7. Make a recommendation with clear reasoning
8. Use create_audit_record to create an audit trail

Be methodical, explain your reasoning step by step, and provide helpful suggestions. Always use the MCP tools to gather the necessary business data before making recommendations."""

    def process_purchase_request(self, user_id: str, product_request: str) -> AgentResult:
        """
        Process a purchase request using Azure AI Foundry Agent Service with native MCP support.
        
        Args:
            user_id: ID of the user making the request
            product_request: Description of what the user wants to purchase
            
        Returns:
            AgentResult containing the recommendation and execution details
        """
        start_time = datetime.now()
        self.execution_steps = []
        self.step_counter = 0
        
        self.logger.info(f"Starting purchase request processing for user {user_id}: {product_request}")
        
        agent = None
        try:
            # Setup project client
            self.project_client = self._setup_project_client()
            
            self._add_step(
                action="Initialize Azure AI Foundry Client",
                reasoning="Setting up connection to Azure AI Foundry Agent Service"
            )
            
            # Create MCP tool with native support
            mcp_tool = self._create_mcp_tool()
            
            self._add_step(
                action="Create MCP Tool",
                reasoning="Setup native MCP integration for business data access"
            )
            
            with self.project_client:
                # Create agent with MCP tool
                agent = self.project_client.agents.create_agent(
                    model=os.getenv("MODEL_DEPLOYMENT_NAME"),
                    name="purchase-order-agent",
                    instructions=self._create_agent_instructions(),
                    tools=mcp_tool.definitions
                )
                
                self.agent_id = agent.id
                
                self._add_step(
                    action="Create Azure AI Foundry Agent",
                    reasoning="Created agent with native MCP tool support"
                )
                
                try:
                    # Create thread for conversation
                    thread = self.project_client.agents.threads.create()
                    
                    # Add initial message
                    self.project_client.agents.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=f"I need help with a purchase request. User ID: {user_id}, Request: {product_request}"
                    )
                    
                    self._add_step(
                        action="Create Conversation Thread",
                        reasoning="Started conversation thread with user request"
                    )
                    
                    # Configure MCP tool approval mode before running
                    mcp_tool.set_approval_mode("never")
                    
                    # Create tool resources with proper MCP configuration
                    tool_resources = {
                        "business_data_server": {
                            "headers": {},
                            "require_approval": "never"
                        }
                    }
                    
                    # Run the agent with proper MCP tool resources
                    run = self.project_client.agents.runs.create_and_process(
                        thread_id=thread.id,
                        agent_id=agent.id,
                        tool_resources=tool_resources
                    )
                    
                    self._add_step(
                        action="Execute Agent Run",
                        reasoning=f"Agent completed with status: {run.status}"
                    )
                    
                    if run.status == "failed":
                        error_msg = f"Agent run failed: {run.last_error}"
                        self.logger.error(error_msg)
                        raise Exception(error_msg)
                    
                    # Get the final response
                    messages = self.project_client.agents.messages.list(thread_id=thread.id)
                    
                    # Find the assistant's response
                    recommendation = "No response from agent"
                    for msg in messages:
                        if msg.role == "assistant" and msg.content:
                            # Get the text content
                            for content in msg.content:
                                if hasattr(content, 'text') and content.text:
                                    recommendation = content.text.value
                                    break
                            break
                    
                    self._add_step(
                        action="Get Agent Response",
                        reasoning="Retrieved final recommendation from agent"
                    )
                
                finally:
                    # Always clean up the agent, even if there was an error
                    if agent and agent.id:
                        try:
                            self.project_client.agents.delete_agent(agent.id)
                            self._add_step(
                                action="Clean Up Agent",
                                reasoning="Deleted temporary agent instance"
                            )
                            self.logger.info(f"Successfully deleted agent {agent.id}")
                        except Exception as cleanup_error:
                            self.logger.error(f"Failed to clean up agent {agent.id}: {cleanup_error}")
                
                end_time = datetime.now()
                
                return AgentResult(
                    success=True,
                    recommendation=recommendation,
                    reasoning="Azure AI Foundry Agent completed purchase request analysis using native MCP tools",
                    total_steps=len(self.execution_steps),
                    execution_time_seconds=(end_time - start_time).total_seconds(),
                    steps=self.execution_steps
                )
            
        except Exception as e:
            error_msg = f"Unexpected error during processing: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            
            # Emergency cleanup - try to delete agent if it was created
            if self.project_client and agent and agent.id:
                try:
                    with self.project_client:
                        self.project_client.agents.delete_agent(agent.id)
                        self.logger.info(f"Emergency cleanup: Successfully deleted agent {agent.id}")
                except Exception as cleanup_error:
                    self.logger.error(f"Emergency cleanup failed for agent {agent.id}: {cleanup_error}")
            
            end_time = datetime.now()
            return AgentResult(
                success=False,
                recommendation="Failed to process request due to unexpected error",
                reasoning=error_msg,
                total_steps=len(self.execution_steps),
                execution_time_seconds=(end_time - start_time).total_seconds(),
                steps=self.execution_steps,
                error_message=error_msg
            )


# Convenience function for standalone usage
def process_purchase_request(user_id: str, product_request: str, config_path: Optional[Path] = None) -> AgentResult:
    """
    Convenience function to process a purchase request with a new agent instance.
    
    Args:
        user_id: ID of the user making the request
        product_request: Description of what the user wants to purchase
        config_path: Optional path to configuration file
        
    Returns:
        AgentResult containing the recommendation and execution details
    """
    agent = AzureAIFoundryAgent(config_path)
    return agent.process_purchase_request(user_id, product_request)


# Legacy alias for backward compatibility
AzureAIAgent = AzureAIFoundryAgent
