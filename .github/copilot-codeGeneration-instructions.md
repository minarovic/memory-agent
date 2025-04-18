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

## Code Generation Examples

Všechny praktické příklady generování kódu pro Memory Agent najdete v:

- [docs/code_generation_examples.md](../docs/code_generation_examples.md)

Hlavní pravidla, balíčky a architektura jsou popsány v `.github/copilot-instructions.md`.

_For unit/integration test conventions see **copilot-test-instructions.md**._
