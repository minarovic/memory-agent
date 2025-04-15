# Specific Instructions for Copilot: LangGraph in Memory Agent Project

When working with the LangGraph workflow in the `graph.py` file or related components, follow these guidelines:

## State Definition (`State`)
* The graph state **must** be defined using `typing.TypedDict`.
* Clearly define all fields the graph will use for passing data between nodes (e.g., `messages: List[BaseMessage]`, `company_analysis: Optional[AnalysisResult]`, `company_data: Optional[Dict]`, `internal_data: Optional[Dict]`, `relationships_data: Optional[Dict]`, `output: Optional[str]`).
* Use `Optional` for fields that may not always be present.
* For more complex structures nested within the state, consider defining additional `TypedDict`s.

## Graph Nodes (Nodes)
* Nodes **must** be implemented as `async` functions.
* Each node function **must** accept the state (`state: State`) as its first argument and optionally `config: RunnableConfig`.
* The node function **must** return a dictionary (`Dict[str, Any]`), where the keys correspond to the fields in the `State` that should be updated. LangGraph automatically merges this dictionary into the current state.
    * Example: `return {"company_data": fetched_data}`
* **Node Logic:**
    * Get necessary data from the passed `state`. Always check for the existence of required data before using it.
    * Perform the specific action of the node (e.g., call a tool, invoke an LLM chain).
    * Process the result.
    * Return the dictionary to update the state.
* **Error Handling:** Implement `try...except` blocks for robustness. In case of an error, log it and return an empty dictionary (`{}`) or a dictionary with error information, so the graph can continue (if desired).
* **Logging:** Use `logger` for informative messages about the node's execution progress.

## Graph Edges (Edges)
* **`set_entry_point("node_name")`:** Clearly define the entry point node of the graph.
* **`add_edge("node_A", "node_B")`:** Use for defining simple sequential transitions.
* **`add_conditional_edges("source_node", router_function, {"path1": "target_node1", "path2": "target_node2", ...})`:**
    * **Use for controlling the flow** based on the current graph state.
    * The router function (`router_function`) must accept `state: State` and return a string corresponding to one of the keys in the path dictionary (e.g., `"path1"`).
    * Keep the router logic simple and readable.
* **`END`:** Use the special constant `END` from `langgraph.graph` as the target of an edge to terminate the graph's execution.

## Compilation and Execution
* Compile the graph using `graph = builder.compile()`.
* Use the asynchronous method `await graph.ainvoke(input, config=...)` to run the graph.

**Goal:** Create clear, robust, and stateful workflows using LangGraph that correspond to the company analysis logic defined in this project.
