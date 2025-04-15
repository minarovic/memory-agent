import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from langchain.schema import AIMessage

from memory_agent.analyzer import analyze_query, parse_response, AnalysisResult 


# Test data for parse_response
parse_response_test_cases = [
    # (Input response, original_query, expected_companies, expected_company, expected_type, expected_is_analysis)
    ("Apple Inc; risk_comparison", "Risk for Apple", ["Apple Inc"], "Apple Inc", "risk_comparison", True),
    ("Apple, Samsung; common_suppliers", "Suppliers for Apple, Samsung", ["Apple", "Samsung"], "Apple", "common_suppliers", True),
    ("tesa; general", "Info about tesa", ["tesa"], "tesa", "general", True),
    ("; general", "Weather in Prague", [], "", "general", False),
    ("  Microsoft ;  risk_comparison  ", "Risk Microsoft", ["Microsoft"], "Microsoft", "risk_comparison", True), # Test with extra spaces
    ("Google,    Meta ;common_suppliers", "Suppliers Google Meta", ["Google", "Meta"], "Google", "common_suppliers", True), # Test with extra spaces in company list
    ("Nokia; invalid_type", "Nokia info", ["Nokia"], "Nokia", "general", True), # Test invalid analysis type fallback
    ("  ; general  ", "Random query", [], "", "general", False), # Test only spaces before semicolon
    ("", "Empty response", [], "", "general", False), # Test empty response string
    ("Just Company Name", "Only company", ["Just Company Name"], "Just Company Name", "general", True), # Test missing semicolon and type
]

@pytest.mark.parametrize(
    "response, original_query, expected_companies, expected_company, expected_type, expected_is_analysis",
    parse_response_test_cases
)
def test_parse_response(response: str, original_query: str, expected_companies: list[str], expected_company: str, expected_type: str, expected_is_analysis: bool):
    '''Testuje parser odpovědi z LLM s různými scénáři.''' # Simple quotes for docstring
    result = parse_response(response, original_query)
    
    assert result["companies"] == expected_companies
    assert result["company"] == expected_company
    assert result["analysis_type"] == expected_type
    assert result["query"] == original_query
    assert result["is_company_analysis"] == expected_is_analysis
    # Confidence check simplified for clarity in parametrization
    if expected_is_analysis:
        assert result["confidence"] >= 0.8
    else:
        assert result["confidence"] == 0.0


# Test data for analyze_query_success
analyze_query_success_test_cases = [
    # (input_query, mock_chain_response, expected_parse_args)
    (
        "Analyze risks for BOS", 
        "BOS; risk_comparison", 
        ("BOS; risk_comparison", "Analyze risks for BOS") # args for parse_response
    ),
    (
        "What are the common suppliers for Fuyao Group and Hauk?", 
        "Fuyao Group, Hauk; common_suppliers", 
        ("Fuyao Group, Hauk; common_suppliers", "What are the common suppliers for Fuyao Group and Hauk?")
    ),
    (
        "Find general information about tesa", 
        "tesa; general", 
        ("tesa; general", "Find general information about tesa")
    ),
]

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_query, mock_chain_response, expected_parse_args",
    analyze_query_success_test_cases
)
@patch("memory_agent.analyzer.init_chat_model") # Mock model init
@patch("memory_agent.analyzer.parse_response") # Mock the parser function
@patch("langchain_core.runnables.base.RunnableSequence.ainvoke") # Mock the chain's invoke
async def test_analyze_query_success(
    mock_chain_ainvoke, mock_parse_response, mock_init_chat_model, 
    input_query: str, mock_chain_response: str, expected_parse_args: tuple
):
    """Testuje úspěšné volání chain.ainvoke a parse_response."""
    
    # Configure mocks
    mock_init_chat_model.return_value = AsyncMock() # Prevent actual model init
    mock_chain_ainvoke.return_value = mock_chain_response
    mock_parse_response.return_value = {"some": "parsed_result"} # Return a dummy result

    # Call the function under test
    result = await analyze_query(input_query)

    # Assertions
    # 1. Check that chain.ainvoke was called correctly
    mock_chain_ainvoke.assert_called_once_with({"user_input": input_query}, None)
    
    # 2. Check that parse_response was called with the chain's output
    mock_parse_response.assert_called_once_with(*expected_parse_args)
    
    # 3. Check that the final result is the one returned by parse_response
    assert result == {"some": "parsed_result"}
    
    # 4. Check that model was initialized
    mock_init_chat_model.assert_called_once()


@pytest.mark.asyncio
@patch("memory_agent.analyzer.init_chat_model")
@patch("langchain_core.runnables.base.RunnableSequence.ainvoke") # Mock the chain's invoke
async def test_analyze_query_exception(mock_chain_ainvoke, mock_init_chat_model):
    """Test chování při výjimce z chain.ainvoke."""
    # Configure mocks
    mock_init_chat_model.return_value = AsyncMock()
    mock_chain_ainvoke.side_effect = Exception("Test chain exception")
    
    input_query = "Najdi rizika pro Apple Inc"
    # Volání funkce
    result = await analyze_query(input_query)
    
    # Ověření výsledku - měl by se vrátit výchozí výsledek
    default_result: AnalysisResult = {
        "companies": [], "company": "", "analysis_type": "general",
        "query": input_query, "is_company_analysis": False, "confidence": 0.0
    }
    assert result == default_result

    # Ověření, že mocky byly volány
    mock_init_chat_model.assert_called_once()
    mock_chain_ainvoke.assert_called_once_with({"user_input": input_query}, None)


# Odstraníme test_analyze_query_non_company_query, protože jeho funkčnost
# je nyní pokryta parametrizovaným test_analyze_query_success
# (pokud bychom přidali případ s "; general" do analyze_query_success_test_cases)
# nebo testem výjimky, pokud by LLM selhal.
# Případně můžeme ponechat test, který ověřuje volání s non-company query
# a mockovanou odpověď "; general"

@pytest.mark.asyncio
@patch("memory_agent.analyzer.init_chat_model")
@patch("memory_agent.analyzer.parse_response")
@patch("langchain_core.runnables.base.RunnableSequence.ainvoke")
async def test_analyze_query_non_company_query_mocked(
    mock_chain_ainvoke, mock_parse_response, mock_init_chat_model
):
    """Testuje volání pro dotaz nesouvisející s firmami s mockováním."""
    input_query = "Jaké je počasí v Praze"
    mock_chain_response = "; general"
    expected_parse_args = ("; general", input_query)
    # Očekávaný výsledek z parse_response pro "; general"
    expected_final_result = {
        "companies": [], "company": "", "analysis_type": "general",
        "query": input_query, "is_company_analysis": False, "confidence": 0.0
    }

    # Configure mocks
    mock_init_chat_model.return_value = AsyncMock()
    mock_chain_ainvoke.return_value = mock_chain_response
    mock_parse_response.return_value = expected_final_result # Mock parse_response to return the expected final dict

    # Call the function under test
    result = await analyze_query(input_query)

    # Assertions
    mock_chain_ainvoke.assert_called_once_with({"user_input": input_query}, None)
    mock_parse_response.assert_called_once_with(*expected_parse_args)
    assert result == expected_final_result
    mock_init_chat_model.assert_called_once()