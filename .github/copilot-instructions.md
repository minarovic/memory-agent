# Base Instructions for GitHub Copilot - Memory Agent Project

## Context
Project: Memory Agent (Python) - AI agent for company analysis.

## Packages and Versions
Use these packages with their minimum versions:
* **langchain**: 0.2.1 - Main framework
* **langchain-core**: 0.2.1 - Core components
* **langchain-anthropic**: 0.1.1 - For Claude integration
* **langchain-openai**: 0.1.1 - For OpenAI integration
* **langgraph**: 0.0.18 - For workflow orchestration

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
* For most operations: **Claude 3.5 Sonnet** (`model="claude-3-5-sonnet-20240620"`)
* For complex reasoning: **Claude 3 Opus** (`model="claude-3-opus-20240229"`)
* For simple operations: **Claude 3 Haiku** (`model="claude-3-haiku-20240307"`)

## Decision Tree for Component Selection
* **Simple data transformation**: Use LCEL chain with pipe operator (`|`)
* **Complex decision-making with tools**: Use React Agent with custom tools
* **Multi-step orchestration**: Use LangGraph with nodes and conditional edges
* **Structured data handling**: Use Pydantic models and TypedDict
* **External system integration**: Use specialized tools as `BaseTool` subclasses

## Specific Instructions
For detailed instructions on specific tasks, consult the relevant files in `.github/` (if they exist):

* Code Generation: `copilot-codeGeneration-instructions.md`.
* LCEL Chains: `copilot-LCEL-Chain-instructions.md`.
* LangGraph Workflow: `prompts/LangGraph.prompt.md`.
* Testing: `copilot-test-instructions.md`.
* Implementation Plan: `langchain-documentation/Plan_0412.md`.
* Architecture: `langchain-documentation/architecture.md`.

## Style
Follow PEP 8, use type hints, and write clear comments.
