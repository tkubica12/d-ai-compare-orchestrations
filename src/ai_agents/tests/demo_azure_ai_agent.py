#!/usr/bin/env python3
"""
Demonstration script for Azure AI Agent business scenarios.

This script tests the Azure AI Agent against the business scenarios defined in the Design.md.
Since AI output is non-deterministic, this script focuses on logging the agent's reasoning
process and demonstrating the outcomes rather than making strict assertions.

Usage:
    python demo_azure_ai_agent.py
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent / "mcp_server" / "tests"))
from azure_ai_agent import AzureAIFoundryAgent, AgentResult


class BusinessScenarioTester:
    """
    Test runner for business scenarios with the Azure AI Agent.
    
    Focuses on demonstrating agent behavior and logging execution rather than strict assertions.
    """
    
    def __init__(self):
        """Initialize the tester."""
        self.logger = self._setup_logging()
        self.agent = AzureAIFoundryAgent()
        self.results: List[Dict[str, Any]] = []
    
    def _setup_logging(self) -> logging.Logger:
        """Setup detailed logging for demonstration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    def _print_separator(self, title: str) -> None:
        """Print a formatted separator for test sections."""
        print(f"\n{'='*80}")
        print(f"  {title}")
        print(f"{'='*80}")
    
    def _print_result_summary(self, result: AgentResult, scenario_name: str) -> None:
        """Print a detailed summary of the agent result."""
        print(f"\n🎯 SCENARIO: {scenario_name}")
        print(f"✅ Success: {result.success}")
        print(f"⏱️  Execution Time: {result.execution_time_seconds:.2f} seconds")
        print(f"🔢 Total Steps: {result.total_steps}")
        
        if result.error_message:
            print(f"❌ Error: {result.error_message}")
        
        print("\n📝 RECOMMENDATION:")
        print(f"{result.recommendation}")
        
        print("\n🧠 REASONING:")
        print(f"{result.reasoning}")
        
        print("\n🔍 EXECUTION STEPS:")
        for step in result.steps:
            print(f"  Step {step.step_number}: {step.action}")
            print(f"    💭 Reasoning: {step.reasoning}")
            if step.mcp_tool_called:
                print(f"    🔧 MCP Tool: {step.mcp_tool_called}")
                print(f"    📋 Parameters: {step.mcp_tool_params}")
                if step.mcp_result:
                    # Truncate long results for readability
                    result_preview = step.mcp_result[:200] + "..." if len(step.mcp_result) > 200 else step.mcp_result
                    print(f"    📊 Result: {result_preview}")
            print()
    
    def test_scenario_1_unauthorized_product(self) -> None:
        """
        Test Scenario 1: Unauthorized Product Test
        User: Bob (HR), Product: Laptop (Electronics)
        Expected: Rejection with alternative suggestions
        """
        self._print_separator("SCENARIO 1: Unauthorized Product Test")
        
        result = self.agent.process_purchase_request(
            user_id="bob-002",
            product_request="I need a laptop for my work"
        )
        
        self._print_result_summary(result, "Unauthorized Product Test")
        
        # Check if the agent correctly identified the policy violation
        contains_policy_check = any("policy" in step.action.lower() for step in result.steps)
        contains_rejection = any(word in result.recommendation.lower() for word in ["not allowed", "unauthorized", "cannot", "policy"])
        
        print("\n📊 SCENARIO ANALYSIS:")
        print(f"  ✅ Policy Check Performed: {contains_policy_check}")
        print(f"  ✅ Contains Rejection/Policy Message: {contains_rejection}")
        
        self.results.append({
            "scenario": "unauthorized_product",
            "user_id": "bob-002",
            "request": "laptop",
            "success": result.success,
            "policy_check_performed": contains_policy_check,
            "contains_rejection": contains_rejection,
            "execution_time": result.execution_time_seconds,
            "steps": result.total_steps
        })
    
    def test_scenario_2_budget_exceeded(self) -> None:
        """
        Test Scenario 2: Budget Exceeded Test
        User: Bob (HR), Product: Expensive Office Chair
        Expected: Budget explanation with cheaper alternatives
        """
        self._print_separator("SCENARIO 2: Budget Exceeded Test")
        
        result = self.agent.process_purchase_request(
            user_id="bob-002",
            product_request="I need the most expensive ergonomic office chair available"
        )
        
        self._print_result_summary(result, "Budget Exceeded Test")
        
        # Check if the agent checked budget constraints
        contains_budget_check = any("budget" in step.action.lower() for step in result.steps)
        contains_budget_message = any(word in result.recommendation.lower() for word in ["budget", "expensive", "cost", "cheaper", "alternative"])
        
        print("\n📊 SCENARIO ANALYSIS:")
        print(f"  ✅ Budget Check Performed: {contains_budget_check}")
        print(f"  ✅ Contains Budget/Cost Message: {contains_budget_message}")
        
        self.results.append({
            "scenario": "budget_exceeded",
            "user_id": "bob-002",
            "request": "expensive chair",
            "success": result.success,
            "budget_check_performed": contains_budget_check,
            "contains_budget_message": contains_budget_message,
            "execution_time": result.execution_time_seconds,
            "steps": result.total_steps
        })
    
    def test_scenario_3_multiple_suppliers(self) -> None:
        """
        Test Scenario 3: Multiple Suppliers Test
        User: Alice (IT), Product: Laptop
        Expected: Supplier comparison based on "fastest" strategy
        """
        self._print_separator("SCENARIO 3: Multiple Suppliers Test")
        
        result = self.agent.process_purchase_request(
            user_id="alice-001",
            product_request="I need a business laptop for development work"
        )
        
        self._print_result_summary(result, "Multiple Suppliers Test")
        
        # Check if the agent compared suppliers and applied strategy
        contains_supplier_check = any("supplier" in step.action.lower() for step in result.steps)
        contains_strategy_application = any(word in result.recommendation.lower() for word in ["fastest", "delivery", "speed", "quick"])
        
        print("\n📊 SCENARIO ANALYSIS:")
        print(f"  ✅ Supplier Check Performed: {contains_supplier_check}")
        print(f"  ✅ Strategy Applied (fastest): {contains_strategy_application}")
        
        self.results.append({
            "scenario": "multiple_suppliers",
            "user_id": "alice-001",
            "request": "business laptop",
            "success": result.success,
            "supplier_check_performed": contains_supplier_check,
            "strategy_applied": contains_strategy_application,
            "execution_time": result.execution_time_seconds,
            "steps": result.total_steps
        })
    
    def test_scenario_4_equivalent_product(self) -> None:
        """
        Test Scenario 4: Equivalent Product Test
        User: Alice (IT), Search: "Computer"
        Expected: Finds "Laptop" as equivalent
        """
        self._print_separator("SCENARIO 4: Equivalent Product Test")
        
        result = self.agent.process_purchase_request(
            user_id="alice-001",
            product_request="I need a computer for software development"
        )
        
        self._print_result_summary(result, "Equivalent Product Test")
        
        # Check if the agent found equivalent products
        contains_product_search = any("search" in step.action.lower() for step in result.steps)
        contains_laptop_match = any(word in result.recommendation.lower() for word in ["laptop", "computer", "found"])
        
        print("\n📊 SCENARIO ANALYSIS:")
        print(f"  ✅ Product Search Performed: {contains_product_search}")
        print(f"  ✅ Found Equivalent (laptop): {contains_laptop_match}")
        
        self.results.append({
            "scenario": "equivalent_product",
            "user_id": "alice-001",
            "request": "computer",
            "success": result.success,
            "product_search_performed": contains_product_search,
            "found_equivalent": contains_laptop_match,
            "execution_time": result.execution_time_seconds,
            "steps": result.total_steps
        })
    
    def test_scenario_5_successful_purchase(self) -> None:
        """
        Test Scenario 5: Successful Purchase Test
        User: Carol (Marketing), Product: Marketing Materials
        Expected: Successful recommendation with audit trail
        """
        self._print_separator("SCENARIO 5: Successful Purchase Test")
        
        result = self.agent.process_purchase_request(
            user_id="carol-003",
            product_request="I need professional notebooks for marketing campaigns"
        )
        
        self._print_result_summary(result, "Successful Purchase Test")
        
        # Check if the agent completed the full workflow including audit
        contains_audit = any("audit" in step.action.lower() for step in result.steps)
        contains_success_message = any(word in result.recommendation.lower() for word in ["recommend", "approved", "suggest", "purchase"])
        
        print("\n📊 SCENARIO ANALYSIS:")
        print(f"  ✅ Audit Record Created: {contains_audit}")
        print(f"  ✅ Contains Success/Recommendation: {contains_success_message}")
        
        self.results.append({
            "scenario": "successful_purchase",
            "user_id": "carol-003",
            "request": "professional notebooks",
            "success": result.success,
            "audit_created": contains_audit,
            "contains_success": contains_success_message,
            "execution_time": result.execution_time_seconds,
            "steps": result.total_steps
        })
    
    def _print_overall_summary(self) -> None:
        """Print an overall summary of all test results."""
        self._print_separator("OVERALL TEST SUMMARY")
        
        total_scenarios = len(self.results)
        successful_scenarios = sum(1 for r in self.results if r["success"])
        total_execution_time = sum(r["execution_time"] for r in self.results)
        total_steps = sum(r["steps"] for r in self.results)
        
        print("📊 EXECUTION STATISTICS:")
        print(f"  Total Scenarios: {total_scenarios}")
        print(f"  Successful Executions: {successful_scenarios}/{total_scenarios}")
        print(f"  Total Execution Time: {total_execution_time:.2f} seconds")
        print(f"  Average Time per Scenario: {total_execution_time/total_scenarios:.2f} seconds")
        print(f"  Total Steps Executed: {total_steps}")
        print(f"  Average Steps per Scenario: {total_steps/total_scenarios:.1f}")
        
        print("\n🎯 SCENARIO-SPECIFIC RESULTS:")
        for result in self.results:
            print(f"  {result['scenario']}: {'✅' if result['success'] else '❌'} "
                  f"({result['execution_time']:.1f}s, {result['steps']} steps)")
        
        # Save results to JSON for further analysis
        results_file = Path(__file__).parent / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {results_file}")
    
    def run_all_scenarios(self) -> None:
        """Run all business scenario tests."""
        print("🚀 Starting Azure AI Agent Business Scenario Tests")
        print(f"Timestamp: {datetime.now()}")
        
        try:
            self.test_scenario_1_unauthorized_product()
            self.test_scenario_2_budget_exceeded() 
            self.test_scenario_3_multiple_suppliers()
            self.test_scenario_4_equivalent_product()
            self.test_scenario_5_successful_purchase()
            
            self._print_overall_summary()
            
        except Exception as e:
            self.logger.error(f"Error during testing: {e}", exc_info=True)
            print(f"\n❌ Testing failed with error: {e}")
        
        print(f"\n🏁 Testing completed at {datetime.now()}")


def main():
    """Main entry point for the demo script."""
    print("Azure AI Agent Business Scenario Demonstration")
    print("=" * 60)
    
    # Check if .env file exists
    env_file = Path(__file__).parent.parent / ".env"
    if not env_file.exists():
        print("❌ Error: .env file not found!")
        print(f"Please create {env_file} based on .env.example")
        return
    
    tester = BusinessScenarioTester()
    tester.run_all_scenarios()


if __name__ == "__main__":
    main()
