# Memory Agent Documentation

This directory contains comprehensive documentation for the Memory Agent project, covering architecture, components, integration guides, and best practices.

## Documentation Structure

- **[architecture.md](./architecture.md)** - Overview of the Memory Agent's hybrid architecture (LangGraph + React Agents + LCEL)
- **[lcel_documentation.md](./lcel_documentation.md)** - Comprehensive guide to using LangChain Expression Language in the project
- **[react_agent.md](./react_agent.md)** - Implementation details for React Agents within the Memory Agent framework
- **[components/](./components/)** - Detailed documentation for individual system components

## Components Documentation

The [components/](./components/) directory contains documentation for specific system components:

- **[analyzer.md](./components/analyzer.md)** - Query analysis and company identification component
- **[graph.md](./components/graph.md)** - LangGraph workflow orchestration component
- **[hybrid_workflow.md](./components/hybrid_workflow.md)** - Hybrid implementation using both LangGraph and React agents
- **[state.md](./components/state.md)** - State management for the workflow graph
- **[tools.md](./components/tools.md)** - Tools for accessing external APIs and internal data sources

## External Links and Resources

### LangChain

* [LangChain Python Homepage](https://python.langchain.com/docs/introduction/)
* [LangChain Tutorials](https://python.langchain.com/docs/tutorials/)
* [LangChain Concepts](https://python.langchain.com/docs/concepts/)
* [LangChain API Reference](https://python.langchain.com/api_reference/)

### LangGraph

* [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
* [LangGraph Tutorials](https://langchain-ai.github.io/langgraph/tutorials/)
* [LangGraph Concepts](https://langchain-ai.github.io/langgraph/concepts/)
* [LangGraph API Reference](https://langchain-ai.github.io/langgraph/reference/)
* [Prebuilt ReAct Agent (LangGraph)](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)

## Development Guidelines

When working with the Memory Agent codebase:

1. **Follow the hybrid architecture pattern** - Use LangGraph for workflow orchestration, React Agents for complex decisions, and LCEL for simple data transformations
2. **Use asynchronous patterns** - All external API calls and LLM operations should use async/await
3. **Implement proper error handling** - Every node should handle exceptions and provide meaningful error information
4. **Maintain documentation** - Update component documentation when making changes to the codebase
