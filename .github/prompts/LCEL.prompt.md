# LCEL Chains - Practical Patterns and Examples

## Basic LCEL Patterns

### Simple Chain
```python
prompt = ChatPromptTemplate.from_template(TEMPLATE)
llm = init_chat_model(model="claude-3-5-sonnet-20240620")
chain = prompt | llm | StrOutputParser()

# Asynchronní volání
result = await chain.ainvoke({"user_input": user_input}, config)
```

### Conversation Chain
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", system_message),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm | StrOutputParser()
```

## Advanced Chain Components

### RunnablePassthrough
```python
chain = RunnablePassthrough.assign(
    llm_response=prompt | llm | StrOutputParser()
)
```

### itemgetter
```python
from operator import itemgetter

chain = {
    "query": itemgetter("user_query"),
    "context": itemgetter("retrieved_docs")
} | prompt | llm | StrOutputParser()
```

### RunnableParallel
```python
chain = RunnableParallel(
    analysis=analyzer_chain,
    original_input=RunnablePassthrough()
)
```

### RunnableLambda
```python
def post_process(result: dict) -> dict:
    # Transform result
    return enhanced_result

chain = base_chain | RunnableLambda(post_process)
```

## Integration with LangGraph

```python
async def analyze_company_input(state: State, config: Optional[RunnableConfig] = None) -> Dict:
    """Node pro analýzu vstupu uživatele."""
    messages = state.get("messages", [])
    if not messages:
        return {"errors": ["No messages in state"]}
    
    try:
        user_message = messages[-1].content
        
        # Použití LCEL řetězce pro analýzu
        prompt = ChatPromptTemplate.from_template(ANALYZER_PROMPT)
        llm = init_chat_model()
        chain = prompt | llm | StrOutputParser()
        
        response = await chain.ainvoke({"user_input": user_message}, config)
        
        # Zpracování výsledku
        analysis_result = parse_response(response, user_message)
        
        return {"company_analysis": analysis_result}
    except Exception as e:
        return {"errors": [f"Error analyzing input: {str(e)}"]}
```

## Error Handling Best Practices
```python
try:
    result = await chain.ainvoke(inputs, config)
    return process_result(result)
except Exception as e:
    logger.error(f"Chain execution failed: {str(e)}")
    logger.error(traceback.format_exc())
    return default_result  # Nebo výsledek s chybou
```

## Complex Examples

### Parallel Data Fetching with Analysis
```python
# Paralelní získávání dat z více zdrojů
data_chain = RunnableParallel(
    company_data=fetch_company_data_chain,
    internal_data=fetch_internal_data_chain,
    relationships=fetch_relationships_chain
)

# Kombinace s řetězcem pro analýzu
full_chain = RunnableParallel(
    analysis_data=data_chain,
    original_query=RunnablePassthrough()
) | format_prompt | llm | StrOutputParser() | RunnableLambda(parse_final_output)
```
