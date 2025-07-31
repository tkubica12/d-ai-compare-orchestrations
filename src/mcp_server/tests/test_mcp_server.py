"""Tests for the MCP server functionality."""

import pytest
from pathlib import Path
import sys

# Add the mcp_server directory to Python path for testing
mcp_server_dir = Path(__file__).parent.parent
sys.path.insert(0, str(mcp_server_dir))

from data_store import DataStore


class TestDataStore:
    """Test the data store functionality."""
    
    @pytest.fixture
    def data_store(self):
        """Create a data store instance for testing."""
        data_dir = Path(__file__).parent.parent / "data"
        return DataStore(data_dir)
    
    def test_get_user(self, data_store):
        """Test user retrieval."""
        user = data_store.get_user("alice-001")
        assert user is not None
        assert user.name == "Alice Johnson"
        assert user.department_id == "IT"
    
    def test_get_user_not_found(self, data_store):
        """Test user not found scenario."""
        user = data_store.get_user("nonexistent")
        assert user is None
    
    def test_get_department(self, data_store):
        """Test department retrieval."""
        dept = data_store.get_department("IT")
        assert dept is not None
        assert dept.name == "Information Technology"
        assert "electronics" in dept.allowed_categories
    
    def test_search_products(self, data_store):
        """Test product search functionality."""
        # Test exact match
        products = data_store.search_products("Business Laptop")
        assert len(products) >= 1
        assert any(p.name == "Business Laptop" for p in products)
        
        # Test partial match
        products = data_store.search_products("laptop")
        assert len(products) >= 1
        
        # Test equivalent product scenario
        products = data_store.search_products("computer")
        assert len(products) >= 1  # Should find laptop
    
    def test_get_product_details(self, data_store):
        """Test product details retrieval."""
        details = data_store.get_product_details("LAPTOP-001")
        assert len(details) >= 1  # Should have at least one supplier
        
        # Test filtering by supplier - check if any suppliers exist first
        if details:
            first_supplier_id = details[0].supplier_id
            filtered_details = data_store.get_product_details("LAPTOP-001", first_supplier_id)
            assert len(filtered_details) == 1
            assert filtered_details[0].supplier_id == first_supplier_id
    
    def test_department_budget(self, data_store):
        """Test budget calculation."""
        budget = data_store.get_department_budget("IT")
        assert budget is not None
        assert budget.monthly_budget > 0
        assert budget.remaining_budget >= 0
    
    def test_create_audit_record(self, data_store):
        """Test audit record creation."""
        initial_count = len(data_store.audit_records)
        
        record = data_store.create_audit_record(
            user_id="alice-001",
            action="purchase_approved",
            details={"product": "LAPTOP-001", "supplier": "tech-supplier-01"},
            decision_reasoning="Best price and delivery time combination"
        )
        
        assert record is not None
        assert record.user_id == "alice-001"
        assert record.action == "purchase_approved"
        assert len(data_store.audit_records) == initial_count + 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
