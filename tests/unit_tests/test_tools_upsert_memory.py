"""
Unit tests for the upsert_memory function in tools.py
"""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock, patch

from langgraph.store.base import BaseStore
from langchain_core.runnables import RunnableConfig

from memory_agent.tools import upsert_memory
from memory_agent.configuration import Configuration


@pytest.mark.asyncio
async def test_upsert_memory_success():
    """Test successful memory storage with upsert_memory function."""
    # Test data
    test_content = "User is interested in electric vehicles"
    test_context = "This was mentioned during a discussion about Tesla"
    test_user_id = "test-user-123"
    test_mem_id = uuid.uuid4()
    
    # Mock store and config
    mock_store = AsyncMock(spec=BaseStore)
    mock_store.aput = AsyncMock(return_value=None)
    
    # Mock configuration
    mock_config = {"configurable": {"user_id": test_user_id}}
    
    # Mock Configuration.from_runnable_config to return an object with user_id
    mock_from_runnable_config = MagicMock()
    mock_from_runnable_config.user_id = test_user_id
    
    with patch("memory_agent.tools.Configuration.from_runnable_config", 
               return_value=mock_from_runnable_config):
        # Call the function with provided memory_id
        result = await upsert_memory(
            content=test_content,
            context=test_context,
            memory_id=test_mem_id,
            config=mock_config,
            store=mock_store
        )
    
    # Verify mock store was called correctly
    mock_store.aput.assert_called_once_with(
        ("memories", test_user_id),
        key=str(test_mem_id),
        value={"content": test_content, "context": test_context}
    )
    
    # Verify return message includes memory ID
    assert str(test_mem_id) in result
    assert "Stored memory" in result


@pytest.mark.asyncio
async def test_upsert_memory_auto_id():
    """Test upsert_memory creates a UUID when memory_id is not provided."""
    # Test data
    test_content = "Company XYZ reported increased revenue"
    test_context = "Mentioned during financial analysis"
    test_user_id = "test-user-456"
    
    # Mock store and config
    mock_store = AsyncMock(spec=BaseStore)
    mock_store.aput = AsyncMock(return_value=None)
    
    # Mock config
    mock_config = {"configurable": {"user_id": test_user_id}}
    
    # Mock Configuration.from_runnable_config
    mock_from_runnable_config = MagicMock()
    mock_from_runnable_config.user_id = test_user_id
    
    with patch("memory_agent.tools.Configuration.from_runnable_config", 
               return_value=mock_from_runnable_config):
        # Call without memory_id
        result = await upsert_memory(
            content=test_content,
            context=test_context,
            memory_id=None,  # No memory_id provided
            config=mock_config,
            store=mock_store
        )
    
    # Verify store was called with a generated UUID
    mock_store.aput.assert_called_once()
    # Get the args that were passed to mock_store.aput
    call_args = mock_store.aput.call_args[0]
    call_kwargs = mock_store.aput.call_args[1]
    
    # Check that the key parameter is a valid UUID string
    assert isinstance(uuid.UUID(call_kwargs["key"]), uuid.UUID)
    
    # Verify other parameters
    assert call_args[0] == ("memories", test_user_id)
    assert call_kwargs["value"] == {"content": test_content, "context": test_context}
    
    # Verify result contains "Stored memory"
    assert "Stored memory" in result


@pytest.mark.asyncio
async def test_upsert_memory_config_error():
    """Test handling of configuration errors in upsert_memory."""
    # Test data
    test_content = "Memory content"
    test_context = "Memory context"
    
    # Mock store
    mock_store = AsyncMock(spec=BaseStore)
    
    # Mock configuration that raises an exception
    with patch("memory_agent.tools.Configuration.from_runnable_config", 
               side_effect=ValueError("Config error")):
        # Call function and expect it to handle the error
        result = await upsert_memory(
            content=test_content,
            context=test_context,
            config={},
            store=mock_store
        )
    
    # Verify store was not called
    mock_store.aput.assert_not_called()
    
    # Verify error message in result
    assert "Failed to store memory" in result
    assert "Config error" in result


@pytest.mark.asyncio
async def test_upsert_memory_database_error():
    """Test handling of database errors in upsert_memory."""
    # Test data
    test_content = "Test content"
    test_context = "Test context"
    test_user_id = "test-user-789"
    
    # Mock store that raises an exception on aput
    mock_store = AsyncMock(spec=BaseStore)
    mock_store.aput.side_effect = Exception("Database connection error")
    
    # Mock configuration
    mock_from_runnable_config = MagicMock()
    mock_from_runnable_config.user_id = test_user_id
    
    with patch("memory_agent.tools.Configuration.from_runnable_config", 
               return_value=mock_from_runnable_config):
        # Call function
        result = await upsert_memory(
            content=test_content,
            context=test_context,
            config={},
            store=mock_store
        )
    
    # Verify aput was called
    mock_store.aput.assert_called_once()
    
    # Verify error handling in result
    assert "Failed to store memory" in result
    assert "Database connection error" in result
