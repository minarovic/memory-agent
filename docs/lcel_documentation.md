# LCEL Documentation for Memory Agent

This document provides a comprehensive guide to LangChain Expression Language (LCEL) usage within the Memory Agent project. It combines guidelines, principles, patterns, and examples for effective implementation of LCEL chains.

## Package Versions

This documentation is current for the following versions:
* langchain: 0.3.20
* langchain-core: 0.3.x
* langchain-anthropic: 0.2.x
* langchain-openai: 0.3.4

## Basic Principles of LCEL

### The `|` (Pipe) Operator
* **Always use** the pipe operator (`|`) for sequential composition of LangChain components (`Runnable`).
* The goal is to create declarative, readable, and maintainable data processing flow definitions.
* Example: `chain = prompt | llm | StrOutputParser()`

### Asynchronous Operations
* For operations that interact with external systems (LLMs, APIs, databases), **use asynchronous LCEL methods** (`ainvoke`, `abatch`, `astream`).
* Example from `analyzer.py`:
  ```python
  response_content = await chain.ainvoke(
      {"user_input": user_input},
      config
  )
  ```

## Key Components and Patterns

### Prompt Templates
* Use `ChatPromptTemplate` for most cases as it's more flexible than `PromptTemplate`.
* For multi-turn conversations, use `MessagesPlaceholder` to include message history.
  ```python
  prompt = ChatPromptTemplate.from_template(ANALYZER_PROMPT)
  # Or for conversations:
  prompt = ChatPromptTemplate.from_messages([
      ("system", system_message),
      MessagesPlaceholder(variable_name="history"),
      ("human", "{input}")
  ])
  ```

### Models
* Initialize Claude models using the `init_chat_model` function from your configuration module.
* For standard operations: `model="claude-3-5-sonnet-20240620"`
* For more complex operations: `model="claude-3-7-sonnet-20250219"`
  ```python
  from langchain.chat_models import init_chat_model
  
  llm = init_chat_model(model="claude-3-5-sonnet-20240620")
  ```

### Basic Chain Construction
* The simplest pattern is a three-component chain:
  ```python
  # Example from analyzer.py
  chain = prompt | llm | StrOutputParser()
  ```

### Advanced Chain Components

* **`RunnablePassthrough`**: Passes the original input (or parts of it) further along the chain.
  ```python
  from langchain_core.runnables import RunnablePassthrough
  
  chain = RunnablePassthrough.assign(
      llm_response=prompt | llm | StrOutputParser()
  )
  ```

* **`itemgetter`**: Extracts specific keys from a dictionary input.
  ```python
  from operator import itemgetter
  
  chain = {
      "query": itemgetter("user_query"),
      "context": itemgetter("retrieved_docs")
  } | prompt | llm | StrOutputParser()
  ```

* **`RunnableParallel`**: Runs multiple `Runnable` components in parallel and merges the results.
  ```python
  from langchain_core.runnables import RunnableParallel
  
  chain = RunnableParallel(
      analysis=analyzer_chain,
      original_input=RunnablePassthrough()
  )
  ```

* **`RunnableLambda`**: Wraps Python functions as steps in the chain.
  ```python
  from langchain_core.runnables import RunnableLambda
  
  def post_process(result: dict) -> dict:
      # Transform or enhance the result
      return enhanced_result
  
  chain = base_chain | RunnableLambda(post_process)
  ```

## Integration with LangGraph

When using LCEL chains within a LangGraph workflow, follow these patterns:

### In Graph Nodes
* Graph nodes should accept a `state` parameter and return a dictionary of state updates.
* Use LCEL chains for data processing within nodes:
  ```python
  async def analyze_company_input(state: State, config: Optional[RunnableConfig] = None) -> Dict:
      """Node for analyzing user input to identify companies and analysis types."""
      messages = state.get("messages", [])
      if not messages:
          return {"errors": ["No messages in state"]}
      
      try:
          user_message = messages[-1].content
          
          # Using LCEL chain for analysis
          prompt = ChatPromptTemplate.from_template(ANALYZER_PROMPT)
          llm = init_chat_model()
          chain = prompt | llm | StrOutputParser()
          
          response = await chain.ainvoke({"user_input": user_message}, config)
          
          # Processing the result and updating state
          analysis_result = parse_response(response, user_message)
          
          return {"company_analysis": analysis_result}
      except Exception as e:
          return {"errors": [f"Error analyzing input: {str(e)}"]}
  ```

### Post-processing LCEL Results
* Always analyze and validate LCEL chain results before updating the graph state:
  ```python
  # Example parsing function used in analyzer.py
  def parse_response(response: str, original_query: str) -> AnalysisResult:
      """Parses model response and creates a structured result."""
      # Remove whitespace
      response = response.strip()
      
      # Parse "Company name; analysis_type" format
      parts = response.split(";")
      
      # ... processing logic ...
      
      return {
          "companies": companies,
          "company": companies[0] if companies else "",
          "analysis_type": analysis_type,
          "query": original_query,
          "is_company_analysis": is_company_analysis,
          "confidence": confidence
      }
  ```

## Error Handling
* Always use try-except blocks around chain calls, especially in graph nodes.
* Log both the error message and the full traceback for debugging purposes.
* Return default or error results instead of letting exceptions propagate.
  ```python
  try:
      result = await chain.ainvoke(inputs, config)
      return process_result(result)
  except Exception as e:
      logger.error(f"Chain execution failed: {str(e)}")
      logger.error(traceback.format_exc())
      return default_result  # Or error result
  ```

## Testing LCEL Chains
* Mock model responses for deterministic testing.
* Test the entire chain as well as individual components.
* Verify parsing logic with different input formats (including edge cases).
* For examples of LCEL chain testing, refer to `tests/unit_tests/test_analyzer.py`.

## Example Patterns from Memory Agent

### Simple Analysis Chain (from `analyzer.py`)
```python
async def analyze_query(user_input: str, config: Optional[RunnableConfig] = None):
    # Initialize chat model
    llm = init_chat_model(model="claude-3-5-sonnet-20240620")
    
    # Create prompt template
    prompt = ChatPromptTemplate.from_template(ANALYZER_PROMPT)
    
    # Create LCEL chain: prompt | llm | StrOutputParser
    chain = prompt | llm | StrOutputParser()
    
    # Asynchronous chain invocation
    response_content = await chain.ainvoke(
        {"user_input": user_input},
        config
    )
    
    # Parse and process the result
    result = parse_response(response_content, user_input)
    return result
```

### Complex Chains with Multiple Components
For more complex operations, especially those involving multiple data sources or complex reasoning:

```python
# Fetching data from multiple sources in parallel
data_chain = RunnableParallel(
    company_data=fetch_company_data_chain,
    internal_data=fetch_internal_data_chain,
    relationships=fetch_relationships_chain
)

# Combining with analysis chain
full_chain = RunnableParallel(
    analysis_data=data_chain,
    original_query=RunnablePassthrough()
) | format_prompt | llm | StrOutputParser() | RunnableLambda(parse_final_output)
```

## Anti-patterns to Avoid
* Don't use synchronous I/O in async code (e.g., `time.sleep`, synchronous requests).
* Don't re-implement retry logic; use `tenacity` or LangChain `Retry`.
* Don't mix direct API calls with LangChain abstractions.
* Avoid implementing functionalities that are already provided by LangChain or LangGraph.

## Goal

Create efficient, readable, and flexible chains for data processing and LLM interaction using standard LCEL constructs.
