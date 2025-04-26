# Instrukce pro GitHub Copilot - Memory Agent Projekt

## Kontext
Projekt Memory Agent implementuje inteligentního agenta pomocí frameworků LangChain a LangGraph se zaměřením na analýzu společností a správu paměti.

## Používané knihovny a verze
* **langchain**: 0.3.20 - Hlavní framework
* **langchain-core**: 0.3.x - Core komponenty
* **langchain-anthropic**: 0.2.x - Pro Claude modely
* **langchain-openai**: 0.3.4 - Pro OpenAI modely
* **langgraph**: 0.2.70 - Pro workflow orchestraci

## Hlavní pravidlo: Používej LangChain s LangGraph!
Při generování Python kódu pro práci s LLM, agenty, RAG, prompty, nástroji nebo řetězci **vždy používej standardní komponenty a postupy frameworků LangChain a LangGraph pro workflow orchestraci.**

* **Preferuj LangGraph** pro vytváření workflow agentů se stavovou správou. Starší `AgentExecutor` je zastaralý.
* **Používej LCEL** (LangChain Expression Language) pro jednodušší, bezstavové operace.
* **Nepoužívej** alternativní knihovny (Haystack, LlamaIndex), pokud nejsou explicitně požadovány.
* **Neimplementuj znovu** existující funkcionalitu LangChain nebo LangGraph.

## Architektura projektu
Memory Agent používá **hybridní architekturu**, která kombinuje:

1. **LangGraph** pro celkovou orchestraci workflow a správu stavu
2. **React Agenty** pro komplexní rozhodování s více nástroji
3. **LCEL řetězce** pro jednodušší transformace dat

## Preferované LLM modely
* Pro většinu operací: **Claude 3.7 Sonnet** (`model="claude-3-7-sonnet-20250219"`)
* Pro standardní úlohy: **Claude 3.5 Sonnet** (`model="claude-3-5-sonnet-20240620"`)

## Rozhodovací strom pro výběr komponent
* **Jednoduchá transformace dat**: Použij LCEL chain s operátorem (`|`)
* **Komplexní rozhodování s nástroji**: Použij React Agent s vlastními nástroji
* **Vícekroková orchestrace**: Použij LangGraph s uzly a podmíněnými hranami
* **Práce se strukturovanými daty**: Použij dataclass modely a TypedDict
* **Integrace s externími systémy**: Použij specializované nástroje jako `BaseTool`

## Vzory kódu a doporučené praktiky

### LCEL pattern
```python
# Vždy preferuj tento moderní vzor pro skládání komponent
prompt = ChatPromptTemplate.from_template(TEMPLATE)
chain = prompt | llm | StrOutputParser()
result = await chain.ainvoke({"input": query}, config)
```

### Definice stavu grafu
```python
# Používej @dataclass místo TypedDict
@dataclass(kw_only=True)
class State:
    """Hlavní stav grafu."""
    messages: Annotated[list[AnyMessage], add_messages]
    analysis_result: Optional[Dict[str, Any]] = None
```

### Uzly grafu jako asynchronní funkce
```python
async def analyze_input(state: State, config: RunnableConfig) -> dict:
    """Asynchronní uzel grafu pro analýzu vstupu."""
    try:
        # Zpracování stavu
        return {"key": "value"}  # Vrať slovník s aktualizacemi stavu
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {}  # Prazdný slovník nebo slovník s chybovým stavem
```

### StateGraph workflow
```python
# Vytvoření grafu
builder = StateGraph(State)
builder.add_node("analyze", analyze_input)
builder.add_conditional_edges(
    "analyze",
    route_function,
    {"option1": "next_node", "option2": END}
)
graph = builder.compile()
```

### React Agent
```python
# Vytvoření React agenta
tools = [custom_tool1, custom_tool2]
agent = create_react_agent(llm, tools, system_prompt)
```

### Nástroje (Tools)
```python
@tool
def custom_tool(param1: str, param2: int) -> str:
    """Dokumentace nástroje s popisem parametrů a návratové hodnoty."""
    # Implementace nástroje
    return "výsledek"
```

### Anti-patterns (nepoužívej!)

- Nepoužívej synchronní IO v async kódu (např. time.sleep, synchronní requests)
- Nepoužívej zastaralý AgentExecutor
- Neimplementuj znovu funkce poskytované LangChain nebo LangGraph
- Nemíchej přímé volání API s LangChain abstrakcemi
- Nepiš vlastní retry logiku, použij tenacity nebo LangChain Retry

## Dokumentační styl

- Vždy poskytuj jasné docstringy pro třídy a funkce
- U komplexních funkcí dokumentuj i parametry a návratové hodnoty
- Vysvětluj klíčové koncepty a interakce mezi komponentami
- Uváděj příklady použití pro komplexní komponenty