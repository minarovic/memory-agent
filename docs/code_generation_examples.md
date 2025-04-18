# Code Generation Examples for Memory Agent

Tento dokument obsahuje praktické příklady generování kódu pro Memory Agent projekt.

## LCEL Chain Example
```python
prompt = ChatPromptTemplate.from_template(TEMPLATE)
llm = init_chat_model(model="claude-3-5-sonnet-20240620")
chain = prompt | llm | StrOutputParser()
result = await chain.ainvoke({"user_input": user_input}, config)
```

## Node Implementation Example (graph.py)
```python
async def analyze_company_input(state: State, config: RunnableConfig) -> dict:
    ...
```

## Tool Implementation Example (tools.py)
```python
class SayariApiTool(BaseTool):
    ...
```

## React Agent Node Example
```python
def create_data_gathering_agent(llm):
    ...
```

## Hybrid Architecture Example
```python
# Definice stavového grafu
builder = StateGraph(State)
...
```
## Anti‑patterns
* Don’t call sync I/O in async LangChain nodes.
* Don’t re‑implement retry logic; use tenacity.
