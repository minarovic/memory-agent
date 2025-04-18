# Base Instructions for GitHub Copilot - Memory Agent Project

## Context
Project: Memory Agent (Python) - AI agent for company analysis that uses external and internal data sources to provide insights on companies and their relationships.

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

## Model Reasoning Behavior

When responding to complex questions or generating code:

1. **Take time to think step‑by‑step** before providing answers.  
2. **Break down problems** into manageable components.  
3. **Consider edge cases and potential issues** with any proposed solution.  
4. **Explore multiple approaches** before settling on a final recommendation.  
5. **Provide reasoning** for architectural and implementation decisions.  
6. **Self‑review** generated code for bugs or inefficiencies before presenting.

For especially complex problems involving system design, algorithm selection, or optimization, employ thorough reasoning by explicitly:

- **Defining** the problem space and constraints.  
- **Identifying** potential solution approaches.  
- **Evaluating** trade‑offs between approaches.  
- **Selecting and justifying** the optimal solution path.  


## Project Architecture
Memory Agent uses a **hybrid architecture** that combines:

1. **LangGraph** for overall workflow orchestration and state management
2. **React Agents** for complex decision-making with multiple tools
3. **LCEL chains** for simpler data transformations

For detailed architecture information, see `langchain-documentation/architecture.md`.

## Preferred LLM Models
* For most operations: **Claude 3.7 Sonnet** (`model="claude-3-7-sonnet-20250219"`)


## Decision Tree for Component Selection
* **Simple data transformation**: Use LCEL chain with pipe operator (`|`)
* **Complex decision-making with tools**: Use React Agent with custom tools
* **Multi-step orchestration**: Use LangGraph with nodes and conditional edges
* **Structured data handling**: Use Pydantic models and TypedDict
* **External system integration**: Use specialized tools as `BaseTool` subclasses

## References to Additional Documentation
For detailed instructions and examples, consult these files:

* LangGraph Workflow: `prompts/LangGraph.prompt.md`
* Testing Guidelines: `copilot-test-instructions.md`
* Project Architecture: `docs/architecture.md`
* React Agent: `docs/react_agent.md`
* Implementation Plan: `plans/PROJECT_PLAN.yaml`

## Style
Follow PEP 8, use type hints, and write clear comments.

## Anti-patterns (do NOT do)
* **Don't** call `openai.ChatCompletion.create` synchronně – vždy používej async varianty.
* **Don't** re-implement retry logiku; používej `tenacity` nebo LangChain `Retry` wrapper.
* **Don't** importuj `AgentExecutor`; je zastaralý v LangChain ≥0.3.
* **Don't** používej `time.sleep` v asynchronním kódu; preferuj `asyncio.sleep`.
* **Don't** vytvářej vlastní implementace funkcí, které již existují v LangChain nebo LangGraph.
* **Don't** používej synchronní IO operace v asynchronním kódu.
* **Don't** míchej přímé volání API (`client.chat.completions.create`) s vysokoúrovňovými abstrakcemi LangChain.

_For unit/integration test conventions see **copilot-test-instructions.md**._
