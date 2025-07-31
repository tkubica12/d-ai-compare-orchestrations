#!/usr/bin/env python3
"""
Business scenario tester for Azure AI Agent with detailed markdown logging.

This script tests the Azure AI Agent against business scenarios and generates
detailed markdown reports showing the agent's decision-making process, tool usage,
and execution details.

Usage:
    uv run python tests/demo_azure_ai_agent_markdown.py
"""

import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from azure_ai_agent import AzureAIFoundryAgent, AgentResult


class MarkdownLogger:
    """Enhanced logger that captures agent execution details for markdown reports."""
    
    def __init__(self, scenario_name: str, mode: str = "azureai"):
        self.scenario_name = scenario_name
        self.mode = mode
        self.logs = []
        self.start_time = datetime.now()
        self.mcp_tool_calls = []
        
    def log_step(self, step_number: int, action: str, reasoning: str, 
                 tool_called: Optional[str] = None, tool_params: Optional[Dict] = None,
                 tool_result: Optional[str] = None):
        """Log a step in the agent execution."""
        step_info = {
            "step_number": step_number,
            "timestamp": datetime.now(),
            "action": action,
            "reasoning": reasoning,
            "tool_called": tool_called,
            "tool_params": tool_params,
            "tool_result": tool_result
        }
        self.logs.append(step_info)
        
        if tool_called:
            self.mcp_tool_calls.append({
                "tool": tool_called,
                "params": tool_params,
                "result": tool_result,
                "step": step_number
            })
    
    def generate_markdown_report(self, result: AgentResult, user_request: str, 
                               user_id: str) -> str:
        """Generate a comprehensive markdown report."""
        
        execution_time = (datetime.now() - self.start_time).total_seconds()
        
        # Header
        report = f"""# {self.scenario_name} - {self.mode.upper()} Mode

**Execution Date:** {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}  
**Mode:** {self.mode.upper()}  
**User ID:** `{user_id}`  
**Request:** "{user_request}"  
**Status:** {'✅ SUCCESS' if result.success else '❌ FAILED'}  
**Execution Time:** {execution_time:.2f} seconds  
**Total Steps:** {result.total_steps}  

---

## 📋 Executive Summary

**Final Recommendation:**
{result.recommendation}

**Agent Reasoning:**
{result.reasoning}

{"**Error Details:**" if result.error_message else ""}
{result.error_message if result.error_message else ""}

---

## 🔍 Detailed Execution Log

"""
        
        # Step-by-step execution
        for i, step in enumerate(result.steps, 1):
            report += f"""### Step {step.step_number}: {step.action}

**Timestamp:** {step.timestamp.strftime('%H:%M:%S') if step.timestamp else 'N/A'}  
**Reasoning:** {step.reasoning}  

"""
            
            if step.mcp_tool_called:
                report += f"""**🔧 MCP Tool Called:** `{step.mcp_tool_called}`  
**Parameters:** 
```json
{json.dumps(step.mcp_tool_params, indent=2) if step.mcp_tool_params else 'None'}
```

"""
                
                if step.mcp_result:
                    # Truncate very long results for readability
                    result_text = step.mcp_result
                    if len(result_text) > 500:
                        result_text = result_text[:500] + "... (truncated)"
                    
                    report += f"""**Tool Response:**
```
{result_text}
```

"""
            
            report += "---\n\n"
        
        # MCP Tools Summary
        if self.mcp_tool_calls:
            report += """## 🛠️ MCP Tools Usage Summary

| Step | Tool | Parameters | Status |
|------|------|------------|---------|
"""
            for call in self.mcp_tool_calls:
                params_summary = json.dumps(call['params'])[:50] + "..." if call['params'] and len(json.dumps(call['params'])) > 50 else json.dumps(call['params'])
                status = "✅ Success" if call['result'] else "❌ Error"
                report += f"| {call['step']} | `{call['tool']}` | `{params_summary}` | {status} |\n"
            
            report += "\n---\n\n"
        
        # Performance Metrics
        report += f"""## 📊 Performance Metrics

- **Total Execution Time:** {execution_time:.2f} seconds
- **Steps Executed:** {result.total_steps}
- **MCP Tool Calls:** {len(self.mcp_tool_calls)}
- **Average Time per Step:** {execution_time / result.total_steps:.2f} seconds
- **Success Rate:** {'100%' if result.success else '0%'}

"""
        
        # Technical Details
        report += f"""## 🔧 Technical Details

**Agent Mode:** {self.mode.upper()}  
**Implementation:** Azure AI Foundry Agent Service  
**MCP Server:** Business Data Server  
**Model:** GPT-4o (via Azure AI Foundry)  

"""
        
        # Tokens (placeholder for future implementation)
        report += """## 💰 Token Usage

*Token usage metrics will be implemented in future versions*

**Estimated Costs:**
- Input Tokens: N/A
- Output Tokens: N/A  
- Total Cost: N/A

---

*Report generated by Azure AI Agent Business Scenario Tester*
"""
        
        return report


class BusinessScenarioTester:
    """Enhanced tester with markdown logging capabilities."""
    
    def __init__(self, mode: str = "azureai"):
        self.mode = mode.lower()
        self.logger = self._setup_logging()
        self.agent = AzureAIFoundryAgent()
        self.results_dir = Path(__file__).parent.parent / "results"
        self.results_dir.mkdir(exist_ok=True)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for the tester."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _save_markdown_report(self, scenario_number: int, report: str):
        """Save the markdown report to the results directory."""
        filename = f"{self.mode}-scenario{scenario_number}.md"
        filepath = self.results_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        self.logger.info(f"📄 Report saved: {filepath}")
        return filepath
    
    def test_scenario_1_unauthorized_product(self) -> None:
        """Test Scenario 1: Unauthorized Product Test"""
        scenario_name = "Scenario 1: Unauthorized Product Access"
        user_id = "bob-002"
        user_request = "I need a laptop for my work"
        
        print(f"\n🧪 Testing: {scenario_name}")
        print(f"👤 User: {user_id} | Request: {user_request}")
        
        markdown_logger = MarkdownLogger(scenario_name, self.mode)
        
        try:
            result = self.agent.process_purchase_request(user_id, user_request)
            
            # Generate and save report
            report = markdown_logger.generate_markdown_report(result, user_request, user_id)
            filepath = self._save_markdown_report(1, report)
            
            # Quick summary
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"📊 Result: {status} | Time: {result.execution_time_seconds:.1f}s | Steps: {result.total_steps}")
            print(f"📄 Report: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Scenario 1 failed: {e}")
            
            # Create error report
            error_result = AgentResult(
                success=False,
                recommendation="Test failed due to unexpected error",
                reasoning=f"Error occurred: {str(e)}",
                total_steps=0,
                execution_time_seconds=0.0,
                steps=[],
                error_message=str(e)
            )
            
            report = markdown_logger.generate_markdown_report(error_result, user_request, user_id)
            self._save_markdown_report(1, report)
    
    def test_scenario_2_budget_exceeded(self) -> None:
        """Test Scenario 2: Budget Exceeded Test"""
        scenario_name = "Scenario 2: Budget Constraints"
        user_id = "bob-002"
        user_request = "I need the most expensive ergonomic office chair available"
        
        print(f"\n🧪 Testing: {scenario_name}")
        print(f"👤 User: {user_id} | Request: {user_request}")
        
        markdown_logger = MarkdownLogger(scenario_name, self.mode)
        
        try:
            result = self.agent.process_purchase_request(user_id, user_request)
            
            report = markdown_logger.generate_markdown_report(result, user_request, user_id)
            filepath = self._save_markdown_report(2, report)
            
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"📊 Result: {status} | Time: {result.execution_time_seconds:.1f}s | Steps: {result.total_steps}")
            print(f"📄 Report: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Scenario 2 failed: {e}")
    
    def test_scenario_3_multiple_suppliers(self) -> None:
        """Test Scenario 3: Multiple Suppliers Test"""
        scenario_name = "Scenario 3: Supplier Comparison"
        user_id = "alice-001"
        user_request = "I need a business laptop for development work"
        
        print(f"\n🧪 Testing: {scenario_name}")
        print(f"👤 User: {user_id} | Request: {user_request}")
        
        markdown_logger = MarkdownLogger(scenario_name, self.mode)
        
        try:
            result = self.agent.process_purchase_request(user_id, user_request)
            
            report = markdown_logger.generate_markdown_report(result, user_request, user_id)
            filepath = self._save_markdown_report(3, report)
            
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"📊 Result: {status} | Time: {result.execution_time_seconds:.1f}s | Steps: {result.total_steps}")
            print(f"📄 Report: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Scenario 3 failed: {e}")
    
    def test_scenario_4_equivalent_product(self) -> None:
        """Test Scenario 4: Equivalent Product Test"""
        scenario_name = "Scenario 4: Product Search Intelligence"
        user_id = "alice-001"
        user_request = "I need a computer for software development"
        
        print(f"\n🧪 Testing: {scenario_name}")
        print(f"👤 User: {user_id} | Request: {user_request}")
        
        markdown_logger = MarkdownLogger(scenario_name, self.mode)
        
        try:
            result = self.agent.process_purchase_request(user_id, user_request)
            
            report = markdown_logger.generate_markdown_report(result, user_request, user_id)
            filepath = self._save_markdown_report(4, report)
            
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"📊 Result: {status} | Time: {result.execution_time_seconds:.1f}s | Steps: {result.total_steps}")
            print(f"📄 Report: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Scenario 4 failed: {e}")
    
    def test_scenario_5_successful_purchase(self) -> None:
        """Test Scenario 5: Successful Purchase Test"""
        scenario_name = "Scenario 5: Complete Purchase Workflow"
        user_id = "carol-003"
        user_request = "I need professional notebooks for marketing campaigns"
        
        print(f"\n🧪 Testing: {scenario_name}")
        print(f"👤 User: {user_id} | Request: {user_request}")
        
        markdown_logger = MarkdownLogger(scenario_name, self.mode)
        
        try:
            result = self.agent.process_purchase_request(user_id, user_request)
            
            report = markdown_logger.generate_markdown_report(result, user_request, user_id)
            filepath = self._save_markdown_report(5, report)
            
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            print(f"📊 Result: {status} | Time: {result.execution_time_seconds:.1f}s | Steps: {result.total_steps}")
            print(f"📄 Report: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Scenario 5 failed: {e}")
    
    def run_all_scenarios(self) -> None:
        """Run all business scenario tests with markdown logging."""
        print("🚀 Azure AI Agent Business Scenario Testing")
        print("=" * 60)
        print(f"Mode: {self.mode.upper()}")
        print(f"Timestamp: {datetime.now()}")
        print(f"Results Directory: {self.results_dir}")
        
        try:
            self.test_scenario_1_unauthorized_product()
            self.test_scenario_2_budget_exceeded()
            self.test_scenario_3_multiple_suppliers()
            self.test_scenario_4_equivalent_product()
            self.test_scenario_5_successful_purchase()
            
            print("\n✅ All scenarios completed!")
            print(f"📁 Reports saved to: {self.results_dir}")
            print(f"📄 File pattern: {self.mode}-scenario[1-5].md")
            
        except Exception as e:
            self.logger.error(f"❌ Testing failed: {e}")
            print(f"❌ Testing failed with error: {e}")


def main():
    """Main entry point for the markdown demo script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Azure AI Agent business scenarios with markdown logging')
    parser.add_argument('--mode', choices=['azureai', 'langchain', 'semantickernel'], 
                       default='azureai', help='Agent implementation mode')
    args = parser.parse_args()
    
    print("Azure AI Agent Business Scenario Testing with Markdown Logging")
    print("=" * 70)
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("❌ Error: .env file not found!")
        print(f"Please create {env_file} based on .env.example")
        return
    
    if args.mode != 'azureai':
        print(f"⚠️  Mode '{args.mode}' not yet implemented. Using 'azureai' mode.")
        args.mode = 'azureai'
    
    tester = BusinessScenarioTester(args.mode)
    tester.run_all_scenarios()


if __name__ == "__main__":
    main()
