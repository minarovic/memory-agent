# Specific Instructions for Copilot: Testing in Memory Agent Project

When generating or modifying tests in this project, follow these guidelines:

## Framework Used: pytest
* Write all new tests using the `pytest` framework.
* Use `pytest` fixtures for preparing test data or resources.
* For asynchronous code, use `pytest-asyncio` and the `@pytest.mark.asyncio` decorator.
* Always follow PEP 8 style guide and include comprehensive type hints.

## Types of Tests
* **Unit Tests:** Focus on testing individual functions and classes in isolation. Use mocking for external dependencies (LLM, API, database). The goal is to verify the component's logic. Location: `tests/unit_tests/`.
* **Integration Tests:** Test the collaboration of several components (e.g., calling a tool from a LangGraph node). Mock only necessary external services (e.g., LLM). Location: `tests/integration_tests/`.
* **Functional API Tests:** To verify the functionality of calling *simulated* API endpoints, use or get inspired by the `test_tools_simple.py` script, which calls the API directly (using `urllib.request`).
* **LangGraph Workflow Tests:** Test the state transitions and conditional edge logic in the LangGraph workflow. Verify that the workflow follows expected paths based on different input conditions.

## Mocking
* **LLM:** For testing logic that depends on an LLM, mock the model calls (`llm.ainvoke`, `chain.ainvoke`). Use `unittest.mock.AsyncMock` or `MagicMock`. Define expected model responses for different scenarios beforehand. When testing with Claude models, use the default model (`claude-3-5-sonnet-20240620`) in tests unless specifically testing model-specific behavior.
* **API Tools:** When testing components that *use* tools (e.g., LangGraph nodes), mock the `_arun` or `_run` methods of these tools (`unittest.mock.patch`). Define mocked return values corresponding to the expected data structure from the API.
* **Database/State:** If testing interaction with state (e.g., `BaseStore` in LangGraph), consider mocking `aput`, `aget`, `asearch` methods.
* **React Agents:** For testing React agents, mock both the agent creation function and tool calls separately to validate the correct interaction flow.

## Assertions
* Use standard `pytest` `assert` statements.
* Verify not only the return values but also whether mocked objects were called with the correct arguments (`mock_object.assert_called_once_with(...)`).
* In integration tests, verify expected changes in the state (if relevant).

## Test Data
* Use realistic but simple test data. Get inspired by the mock data structure in `sayari-simulator/mock_data/`.
* For more complex data, consider using `pytest` fixtures.

**Remember:** The goal of the tests is to ensure the correct functionality and robustness of the LangChain components and workflow in this project.
