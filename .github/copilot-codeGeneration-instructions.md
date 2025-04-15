# Base Instructions for GitHub Copilot - Memory Agent Project

## Context
Project: Memory Agent (Python) - AI agent for company analysis.

## Packages and Versions
Use these packages with their minimum versions:
* **langchain**: 0.3.20 - Main framework
* **langchain-core**: 0.3.x - Core components
* **langchain-anthropic**: 0.2.x - For Claude integration
* **langchain-openai**: 0.3.4 - For OpenAI integration
* **langgraph**: 0.2.70 - For workflow orchestration

## Main Rule: Use LangChain with LangGraph!
When generating Python code for working with LLMs, agents, RAG, prompts, tools, or chains, **always prioritize and use standard components and practices of the LangChain framework and LangGraph for workflow orchestration.**

* **Prefer LangGraph** for building agent workflows with state management. Legacy `AgentExecutor` is deprecated.
* **Use LCEL** (LangChain Expression Language) for simpler, stateless operations.
* **Avoid** alternative libraries (Haystack, LlamaIndex) unless explicitly requested.
* **Do not reimplement** existing LangChain or LangGraph functionality.

## Project Architecture
Memory Agent uses a **hybrid architecture** that combines:

1. **LangGraph** for overall workflow orchestration and state management
2. **React Agents** for complex decision-making with multiple tools
3. **LCEL chains** for simpler data transformations

For detailed architecture information, see `langchain-documentation/architecture.md`.

## Preferred LLM Models
* For most operations: **Claude 3.7 Sonnet** (`model="claude-3-7-sonnet-20250219"`)
* For standard tasks: **Claude 3.5 Sonnet** (`model="claude-3-5-sonnet-20240620"`)
* For specialized operations requiring legacy models: Contact team lead

## Decision Tree for Component Selection
* **Simple data transformation**: Use LCEL chain with pipe operator (`|`)
* **Complex decision-making with tools**: Use React Agent with custom tools
* **Multi-step orchestration**: Use LangGraph with nodes and conditional edges
* **Structured data handling**: Use Pydantic models and TypedDict
* **External system integration**: Use specialized tools as `BaseTool` subclasses

## Code Generation Guidelines

When generating code for specific tasks, adhere to these concise guidelines:

* **Testing:** See detailed instructions in `copilot-test-instructions.md`.
* **LangGraph (`graph.py`):**
    * Define State using `TypedDict`.
    * Nodes are `async` functions accepting `state` and returning update dictionaries.
    * Use conditional edges (`add_conditional_edges`) based on `state` for routing.
* **Tools (`tools.py`):**
    * Implement as `BaseTool` subclasses with `name`, `description`.
    * Use `args_schema` (Pydantic) for complex inputs if needed.
    * Prefer `async def _arun(...)` for I/O operations; implement core logic there. Handle errors using `ToolException` or return error messages.
* **LCEL Chains:**
    * Compose chains using the pipe operator (`|`).
    * Combine standard `Runnable` components (Prompts, Models, Parsers, `RunnableParallel`, `RunnableLambda`, `itemgetter`).
* **Analyzer (`analyzer.py`):**
    * Use an LCEL chain (`ChatPromptTemplate | ChatModel | StrOutputParser`) to extract "Company; type" string from the user query.
    * Parse the string result robustly into the `AnalysisResult` TypedDict.
* **React Agents (in LangGraph):**
    * Use `langgraph.prebuilt.create_react_agent` to create React agents as specialized nodes.
    * Implement tools as functions decorated with `@tool`.
    * Design system prompts that guide the agent through complex decision trees.

## Hybrid Architecture Implementation

For complex workflows requiring both orchestration and flexible tool use:

1. **Define a TypedDict-based State** that captures all relevant data flow through the workflow
2. **Create specialized tools** using either `@tool` decorator or `BaseTool` subclasses
3. **Implement React Agent node** that can make complex decisions with multiple tools
4. **Create LangGraph workflow** with regular nodes and React Agent nodes
5. **Use conditional edges** to route between different processing paths based on state changes

See detailed implementation examples in `langchain-documentation/react_agent_implementation.md`.

## Style
* Follow PEP 8.
* Use type hints (`typing`).
* Write clear comments, especially for complex LangChain/LangGraph logic.

## Additional References
For detailed instructions on specific aspects, consult:
* LCEL Chains: `copilot-LCEL-Chain-instructions.md`
* LangGraph Workflow: `prompts/LangGraph.prompt.md`
* Testing: `copilot-test-instructions.md`
* Implementation Plan: `langchain-documentation/Plan_0412.md`
* Architecture: `langchain-documentation/architecture.md`
