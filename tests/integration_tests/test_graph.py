from typing import List

import langsmith as ls
import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore

from memory_agent.graph import builder
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from memory_agent.graph import (
    analyze_company_input,
    fetch_company_data,
    fetch_internal_data,
    fetch_relationships,
    should_analyze_company,
    should_fetch_company_data,
    should_fetch_internal_data,
    should_fetch_relationships,
    route_input,
    route_after_analysis,
    route_after_company_data,
    route_after_internal_data
)

# Mock State pro testování
class MockState:
    """Mock State třída pro testování grafu."""
    
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        
    def __getattr__(self, name):
        return None
        
    def get(self, name, default=None):
        return getattr(self, name, default)


# Testovací data
MOCK_MESSAGES = [
    {"role": "system", "content": "System message"},
    {"role": "user", "content": "Najdi rizika pro Apple Inc"}
]

MOCK_ANALYSIS_RESULT = {
    "companies": ["Apple Inc"],
    "company": "Apple Inc",
    "analysis_type": "risk_comparison",
    "query": "Najdi rizika pro Apple Inc",
    "is_company_analysis": True,
    "confidence": 0.9
}

MOCK_COMPANY_DATA = {
    "company": "Apple Inc",
    "external_data": {
        "has_results": True,
        "entities": [
            {
                "id": "entity-123",
                "name": "Apple Inc",
                "type": "Company",
                "risk_score": "15"
            }
        ]
    },
    "entity_id": "entity-123",
    "risk_analysis": {
        "sanctions_status": "Žádné aktivní sankce nenalezeny",
        "pep_connections": [],
        "compliance_issues": [],
        "risk_score": "15",
        "risk_factors": ["operating_in_high_risk_jurisdiction"]
    }
}

MOCK_INTERNAL_DATA = {
    "company": "Apple Inc",
    "company_profile": {
        "tier_classification": "Tier 1",
        "hs_codes": ["8471.30", "8517.62"],
        "business_activities": ["Electronics Manufacturing", "Software Development"],
        "geographic_presence": []
    }
}

MOCK_RELATIONSHIPS_DATA = {
    "has_relationships": True,
    "relationships": {
        "suppliers": ["Supplier A", "Supplier B"],
        "customers": ["Customer X", "Customer Y"],
        "ownership": [],
        "key_relationships": []
    },
    "visualization": {
        "nodes": [],
        "links": []
    }
}


@pytest.mark.asyncio
@ls.unit
@pytest.mark.parametrize(
    "conversation",
    [
        ["My name is Alice and I love pizza. Remember this."],
        [
            "Hi, I'm Bob and I enjoy playing tennis. Remember this.",
            "Yes, I also have a pet dog named Max.",
            "Max is a golden retriever and he's 5 years old. Please remember this too.",
        ],
        [
            "Hello, I'm Charlie. I work as a software engineer and I'm passionate about AI. Remember this.",
            "I specialize in machine learning algorithms and I'm currently working on a project involving natural language processing.",
            "My main goal is to improve sentiment analysis accuracy in multi-lingual texts. It's challenging but exciting.",
            "We've made some progress using transformer models, but we're still working on handling context and idioms across languages.",
            "Chinese and English have been the most challenging pair so far due to their vast differences in structure and cultural contexts.",
        ],
    ],
    ids=["short", "medium", "long"],
)
async def test_memory_storage(conversation: List[str]):
    mem_store = InMemoryStore()

    graph = builder.compile(store=mem_store, checkpointer=MemorySaver())
    user_id = "test-user"
    config = {
        "configurable": {},
        "user_id": user_id,
    }

    for content in conversation:
        await graph.ainvoke(
            {"messages": [("user", content)]},
            {**config, "thread_id": "thread"},
        )

    namespace = ("memories", user_id)
    memories = mem_store.search(namespace)

    ls.expect(len(memories)).to_be_greater_than(0)

    bad_namespace = ("memories", "wrong-user")
    bad_memories = mem_store.search(bad_namespace)
    ls.expect(len(bad_memories)).to_equal(0)


@pytest.mark.asyncio
@patch("memory_agent.analyzer.analyze_query")
async def test_analyze_company_input(mock_analyze_query):
    """Test funkce analyze_company_input."""
    # Setup mock
    mock_analyze_query.return_value = MOCK_ANALYSIS_RESULT
    
    # Vytvoření stavu
    state = MockState(messages=MOCK_MESSAGES)
    
    # Volání funkce
    result = await analyze_company_input(state, {})
    
    # Ověření volání analyze_query
    mock_analyze_query.assert_called_once()
    assert "Apple Inc" in mock_analyze_query.call_args[0][0]
    
    # Ověření výsledku
    assert "company_analysis" in result
    assert result["company_analysis"] == MOCK_ANALYSIS_RESULT


@pytest.mark.asyncio
@patch("memory_agent.tools.SayariApiTool._arun")
async def test_fetch_company_data(mock_sayari_tool):
    """Test funkce fetch_company_data."""
    # Setup mock
    mock_sayari_tool.return_value = MOCK_COMPANY_DATA
    
    # Vytvoření stavu
    state = MockState(company_analysis=MOCK_ANALYSIS_RESULT)
    
    # Volání funkce
    result = await fetch_company_data(state, {})
    
    # Ověření volání Sayari API
    mock_sayari_tool.assert_called_once_with("Apple Inc")
    
    # Ověření výsledku
    assert "company_data" in result
    assert result["company_data"] == MOCK_COMPANY_DATA


@pytest.mark.asyncio
@patch("memory_agent.tools.SupabaseInternalDataTool._arun")
async def test_fetch_internal_data(mock_internal_tool):
    """Test funkce fetch_internal_data."""
    # Setup mock
    mock_internal_tool.return_value = MOCK_INTERNAL_DATA
    
    # Vytvoření stavu
    state = MockState(company_analysis=MOCK_ANALYSIS_RESULT)
    
    # Volání funkce
    result = await fetch_internal_data(state, {})
    
    # Ověření volání nástroje
    mock_internal_tool.assert_called_once_with("Apple Inc")
    
    # Ověření výsledku
    assert "internal_data" in result
    assert result["internal_data"] == MOCK_INTERNAL_DATA


@pytest.mark.asyncio
@patch("memory_agent.tools.SayariRelationshipsTool._arun")
async def test_fetch_relationships(mock_relationships_tool):
    """Test funkce fetch_relationships."""
    # Setup mock
    mock_relationships_tool.return_value = MOCK_RELATIONSHIPS_DATA
    
    # Vytvoření stavu
    state = MockState(company_data=MOCK_COMPANY_DATA)
    
    # Volání funkce
    result = await fetch_relationships(state, {})
    
    # Ověření volání nástroje
    mock_relationships_tool.assert_called_once_with("entity-123")
    
    # Ověření výsledku
    assert "relationships_data" in result
    assert result["relationships_data"] == MOCK_RELATIONSHIPS_DATA


def test_routing_functions():
    """Test směrovacích funkcí pro graf."""
    # Test should_analyze_company
    # Pozitivní případ - zpráva obsahuje klíčová slova pro firmu
    state_with_company = MockState(
        messages=[{"role": "user", "content": "Najdi informace o firmě Apple"}]
    )
    assert should_analyze_company(state_with_company) == True
    
    # Negativní případ - zpráva neobsahuje klíčová slova
    state_without_company = MockState(
        messages=[{"role": "user", "content": "Jaké je dnes počasí?"}]
    )
    assert should_analyze_company(state_without_company) == False
    
    # Negativní případ - již máme analýzu
    state_already_analyzed = MockState(
        messages=[{"role": "user", "content": "Najdi informace o firmě Apple"}],
        company_analysis=MOCK_ANALYSIS_RESULT
    )
    assert should_analyze_company(state_already_analyzed) == False
    
    # Test should_fetch_company_data
    # Pozitivní případ - máme analýzu, ale nemáme data
    state_needs_data = MockState(company_analysis=MOCK_ANALYSIS_RESULT)
    assert should_fetch_company_data(state_needs_data) == True
    
    # Negativní případ - již máme data
    state_has_data = MockState(
        company_analysis=MOCK_ANALYSIS_RESULT,
        company_data=MOCK_COMPANY_DATA
    )
    assert should_fetch_company_data(state_has_data) == False
    
    # Test should_fetch_internal_data
    # Pozitivní případ - máme analýzu, ale nemáme interní data
    state_needs_internal = MockState(company_analysis=MOCK_ANALYSIS_RESULT)
    assert should_fetch_internal_data(state_needs_internal) == True
    
    # Negativní případ - již máme interní data
    state_has_internal = MockState(
        company_analysis=MOCK_ANALYSIS_RESULT,
        internal_data=MOCK_INTERNAL_DATA
    )
    assert should_fetch_internal_data(state_has_internal) == False
    
    # Test should_fetch_relationships
    # Pozitivní případ - máme ID entity, ale nemáme vztahy
    state_needs_relationships = MockState(company_data=MOCK_COMPANY_DATA)
    assert should_fetch_relationships(state_needs_relationships) == True
    
    # Negativní případ - již máme vztahy
    state_has_relationships = MockState(
        company_data=MOCK_COMPANY_DATA,
        relationships_data=MOCK_RELATIONSHIPS_DATA
    )
    assert should_fetch_relationships(state_has_relationships) == False
    
    # Test route_input
    assert route_input(state_with_company) == "analyze_company_input"
    assert route_input(state_without_company) == "call_model"
    
    # Test route_after_analysis
    assert route_after_analysis(state_needs_data) == "fetch_company_data"
    
    # Test route_after_company_data
    state_after_company = MockState(
        company_analysis=MOCK_ANALYSIS_RESULT,
        company_data=MOCK_COMPANY_DATA
    )
    assert route_after_company_data(state_after_company) == "fetch_internal_data"
    
    # Test route_after_internal_data
    state_after_internal = MockState(
        company_analysis=MOCK_ANALYSIS_RESULT,
        company_data=MOCK_COMPANY_DATA,
        internal_data=MOCK_INTERNAL_DATA
    )
    assert route_after_internal_data(state_after_internal) == "fetch_relationships"
