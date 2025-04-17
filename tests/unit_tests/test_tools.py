# V PROCESU(A4): Implementace unit testů pro SayariApiTool, SupabaseInternalDataTool a SayariRelationshipsTool
import pytest
import json
from unittest.mock import patch, AsyncMock, MagicMock

from memory_agent.tools import SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool


class MockResponse:
    """Mock HTTP response pro testování."""
    
    def __init__(self, json_data, status_code=200):
        self.json_data = json_data
        self.status_code = status_code
    
    async def json(self):
        return self.json_data
    
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP error {self.status_code}")


# Testovací data
MOCK_SAYARI_DATA = {
    "data": {
        "id": "test-entity-id-123",
        "label": "Test Company",
        "type": "Company",
        "risk_score": "23",
        "sanctions_status": "No active sanctions",
        "risk_factors": {
            "operating_in_high_risk_jurisdiction": True,
            "politically_exposed_connections": False
        }
    }
}

MOCK_SUPABASE_DATA = {
    "supplier_info": {
        "supplier_name": "Test Company",
        "primary_tier": "Tier 1",
        "hs_code_matches": [
            {"hsCode": "8471.30", "description": "Computer parts"},
            {"hsCode": "8517.62", "description": "Electronic components"}
        ],
        "identified_activities": [
            {"activity": "IT Services"},
            {"activity": "Hardware Manufacturing"}
        ]
    }
}

MOCK_RELATIONSHIPS_DATA = {
    "relationships": [
        {
            "id": "rel-1",
            "type": "has_supplier",
            "source": {"id": "source-1", "label": "Supplier A", "type": "company"},
            "target": {"id": "test-entity-id-123", "label": "Test Company", "type": "company"}
        },
        {
            "id": "rel-2",
            "type": "supplies_to",
            "source": {"id": "test-entity-id-123", "label": "Test Company", "type": "company"},
            "target": {"id": "target-1", "label": "Customer X", "type": "company"}
        }
    ]
}


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_sayari_api_tool_success(mock_get):
    """Test úspěšného volání Sayari API."""
    # Setup mock response
    mock_get.return_value = MockResponse(MOCK_SAYARI_DATA)
    
    # Vytvoření nástroje a volání metody
    tool = SayariApiTool()
    result = await tool._arun("Test Company")
    
    # Ověření volání
    mock_get.assert_called_once()
    assert "search/entity?q=Test Company" in mock_get.call_args[0][0]
    
    # Ověření vrácených dat
    assert result["company"] == "Test Company"
    assert result["entity_id"] == "test-entity-id-123"
    assert len(result["external_data"]["entities"]) == 1
    assert "risk_analysis" in result
    assert "risk_factors" in result["risk_analysis"]
    assert "operating_in_high_risk_jurisdiction" in result["risk_analysis"]["risk_factors"]


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_sayari_api_tool_error(mock_get):
    """Test chování při chybě Sayari API."""
    # Setup mock response s chybou
    mock_get.return_value = MockResponse({}, 404)
    
    # Vytvoření nástroje
    tool = SayariApiTool()
    
    # Ověření, že výjimka je zachycena
    with pytest.raises(Exception):
        await tool._arun("Test Company")
    
    # Ověření volání
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_supabase_internal_data_tool_success(mock_get):
    """Test úspěšného volání interních dat ze Supabase."""
    # Setup mock response
    mock_get.return_value = MockResponse(MOCK_SUPABASE_DATA)
    
    # Vytvoření nástroje a volání metody
    tool = SupabaseInternalDataTool()
    result = await tool._arun("Test Company")
    
    # Ověření volání
    mock_get.assert_called_once()
    assert "?name=Test Company" in mock_get.call_args[0][0]
    
    # Ověření vrácených dat
    assert result["company"] == "Test Company"
    assert result["company_profile"]["tier_classification"] == "Tier 1"
    assert len(result["company_profile"]["hs_codes"]) == 2
    assert "8471.30" in result["company_profile"]["hs_codes"]
    assert len(result["company_profile"]["business_activities"]) == 2
    assert "IT Services" in result["company_profile"]["business_activities"]


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_supabase_internal_data_tool_error(mock_get):
    """Test chování při chybě API interních dat."""
    # Setup mock response s chybou
    mock_get.return_value = MockResponse({}, 500)
    
    # Vytvoření nástroje
    tool = SupabaseInternalDataTool()
    
    # Ověření, že výjimka je zachycena
    with pytest.raises(Exception):
        await tool._arun("Test Company")
    
    # Ověření volání
    mock_get.assert_called_once()


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_sayari_relationships_tool_success(mock_get):
    """Test úspěšného volání vztahů z Sayari API."""
    # Setup mock response
    mock_get.return_value = MockResponse(MOCK_RELATIONSHIPS_DATA)
    
    # Vytvoření nástroje a volání metody
    tool = SayariRelationshipsTool()
    result = await tool._arun("test-entity-id-123")
    
    # Ověření volání
    mock_get.assert_called_once()
    assert "entity/test-entity-id-123/relationships" in mock_get.call_args[0][0]
    
    # Ověření vrácených dat
    assert result["has_relationships"] == True
    assert "relationships" in result
    assert "visualization" in result
    assert "suppliers" in result["relationships"]
    assert "customers" in result["relationships"]
    assert "Supplier A" in result["relationships"]["suppliers"]
    assert "Customer X" in result["relationships"]["customers"]


@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_sayari_relationships_tool_empty_id(mock_get):
    """Test volání vztahů s prázdným ID."""
    # Vytvoření nástroje a volání metody
    tool = SayariRelationshipsTool()
    result = await tool._arun("")
    
    # Ověření, že API nebylo voláno
    mock_get.assert_not_called()
    
    # Ověření vrácených dat
    assert result["has_relationships"] == False
    assert len(result["relationships"]) == 0
    assert "visualization" in result