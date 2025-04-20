# Copilot Instructions for Memory Agent Project

This guide provides basic instructions for AI assistants working with the Memory Agent project code.

## 1. Basic Principles of Code Analysis

- **Project Architecture:** When analyzing, always consider the hybrid architecture of the project (LangGraph workflow + React Agents + LCEL chains)
- **Workflow Components:** Identify whether the analyzed code belongs to workflow orchestration (LangGraph), tools (Tools), or chains (Chains)
- **Standards Compliance:** Check whether the code correctly uses LangChain and LangGraph components according to current versions (≥0.3.x)
- **Asynchronous Operations:** Verify that the code properly implements asynchronous calls using `async/await` and not synchronous calls
- **State Management:** When analyzing workflow components, pay attention to state management using the `State` object in LangGraph

## 2. How to Work with Component Documentation

- **Documentation Location:** All component documentation is located in the `docs/components/` directory
- **Documentation Structure:** Each component should contain:
  - Purpose and basic description
  - Input and output data structures
  - Dependencies on other components
  - Usage examples
- **Documentation Updates:** When changes are made to the implementation, the corresponding documentation must be updated as well
- **API References:** When working with external APIs (Sayari, Supabase), always refer to the current documentation in `docs/`

## 3. How to Verify Implementation

- **Unit Tests:** Each new function must have corresponding unit tests in the `tests/unit_tests/` directory
- **Integration Tests:** More complex workflows must have integration tests in `tests/integration_tests/`
- **Type Checks:** Use type annotations and verify correctness using `mypy`
- **Checkpoints:**
  - Are the correct LangChain/LangGraph components being used?
  - Are all operations asynchronous where appropriate?
  - Are graph states properly updated?
  - Is compatibility with existing workflow maintained?
  - Are error states and exceptions properly handled?

## 4. Task Status

### IN PROGRESS
- Implementation of company relationship analysis
- Improvement of memory storage and retrieval
- Optimization of prompts for analysis

### COMPLETED
- Basic structure of LangGraph workflow
- Integration of Sayari API for retrieving company data
- Implementation of Supabase for storing internal data
- Analysis of user input for extracting companies and analysis type
- Generating responses based on collected data
