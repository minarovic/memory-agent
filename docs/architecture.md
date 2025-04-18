<!-- filepath: /Users/marekminarovic/claude-code/memory-agent/.github/langchain-documentation/architecture.md -->

# Architektura Memory Agent

Tento dokument popisuje architekturu projektu Memory Agent, který využívá moderní přístupy LangChain a LangGraph pro implementaci inteligentního agenta na analýzu společností.

## Přehled architektury

Memory Agent je implementován jako workflow postavený na architektuře LangGraph, která poskytuje stavové řízení toku dat mezi specializovanými uzly. Využíváme následující klíčové komponenty:

1. **LangGraph** - Pro orchestraci celého workflow
2. **LCEL řetězce** - Pro jednoduché operace zpracování dat
3. **React agenti** - Pro komplexní rozhodování při zpracování dat o více společnostech
4. **Specializované nástroje** - Pro komunikaci s externími API (Sayari, Supabase)

## Hybridní architektura Memory Agenta

Náš projekt používá hybridní přístup kombinující několik architektur pro dosažení optimálního výsledku:

### 1. LangGraph pro orchestraci workflow

LangGraph poskytuje základní kostru celého řešení:

- **Stavovost** - Udržuje stav mezi jednotlivými kroky zpracování
- **Strukturovaný tok dat** - Přehledný a snadno rozšiřitelný tok dat mezi uzly
- **Podmíněné větvení** - Inteligentní rozhodování o dalším postupu na základě stavu
- **Robustnost** - Izolované zpracování chyb v jednotlivých uzlech
- **Asynchronní operace** - Efektivní zpracování pomocí asynchronních funkcí

Příklad definice grafu:

```python
builder = StateGraph(State)
builder.add_node("analyze_company_input", analyze_company_input)
builder.add_node("gather_company_data", gather_company_data_node)
builder.add_node("call_model", call_model)
builder.add_edge("analyze_company_input", "gather_company_data")
builder.add_conditional_edges(
    "gather_company_data",
    route_after_gathering,
    {
        "success": "call_model",
        "error": END
    }
)
```

### 2. React agent pro komplexní rozhodování

V rámci LangGraph workflow využíváme React agenta jako specializovaný uzel pro komplexní operace:

- **Autonomní rozhodování** - Agent sám určuje, jaké nástroje použít a v jakém pořadí
- **Odolnost vůči chybám** - Dokáže reagovat na selhání API a hledat alternativní postupy
- **Flexibilita** - Zpracování různého počtu společností v jednom dotazu
- **Čitelné uvažování** - Agent vysvětluje své rozhodování, což usnadňuje ladění

Implementace vytvoření React agenta:

```python
def create_data_gathering_agent(llm):
    tools = [fetch_company_data, fetch_internal_data, fetch_relationships]
    system_prompt = """Jsi specializovaný agent pro získávání dat o společnostech..."""
    return create_react_agent(llm, tools, prompt=system_prompt)
```

### 3. LCEL řetězce pro jednoduché operace

Pro jednodušší a přímočaré operace používáme LCEL (LangChain Expression Language) řetězce:

- **Přehledná kompozice** - Snadné skládání pomocí operátoru `|`
- **Vysoká čitelnost** - Jasná a jednoduchá definice zpracování
- **Výkonnost** - Efektivní zpracování bez zbytečné režie

Příklad LCEL řetězce:

```python
prompt = ChatPromptTemplate.from_template(ANALYZER_PROMPT)
chain = prompt | llm | StrOutputParser()
response_content = await chain.ainvoke({"user_input": user_input})
```

## Rozhodovací strom pro výběr komponent

Při implementaci nových funkcí Memory Agenta používáme následující rozhodovací strom pro výběr vhodných komponent:

### 1. Jednoduchá transformace dat
Pro přímočaré operace jako je analýza dotazu nebo generování textu:

- **Použít:** LCEL řetězec s operátorem `|`
- **Příklad:** `prompt | llm | StrOutputParser()`
- **Kdy použít:** Pro operace, které nevyžadují složité rozhodování nebo stavovost
- **Konkrétní případ:** Analýza uživatelského vstupu v `analyzer.py`

### 2. Komplexní rozhodování s nástroji
Pro operace vyžadující sofistikované rozhodování s použitím více nástrojů:

- **Použít:** React Agent s vlastními nástroji
- **Příklad:** `create_react_agent(llm, tools, prompt=system_prompt)`
- **Kdy použít:** Když je potřeba inteligentně kombinovat více nástrojů, zpracovávat neúspěchy, nebo sekvenčně budovat výsledek
- **Konkrétní případ:** Získávání dat o více společnostech v `hybrid_workflow.py`

### 3. Orchestrace více kroků
Pro řízení celkového workflow s podmíněným rozhodováním:

- **Použít:** LangGraph s uzly a podmíněnými hranami
- **Příklad:** `builder.add_conditional_edges("node", router_function, {"path1": "target1", "path2": "target2"})`
- **Kdy použít:** Pro vytvoření hlavního workflow s více kroky, potřebou stavovosti, nebo podmíněného větvení
- **Konkrétní případ:** Hlavní workflow v `graph.py`

### 4. Strukturované zpracování dat
Pro práci se strukturovanými daty a entitami:

- **Použít:** Pydantic modely a TypedDict
- **Příklad:** `class State(TypedDict): messages: List[BaseMessage]`
- **Kdy použít:** Pro definici struktury stavů, požadavků nebo výsledků
- **Konkrétní případ:** Definice stavu grafu v `state.py`

### 5. Komunikace s externími systémy
Pro integraci s externími API a službami:

- **Použít:** Specializované nástroje implementované jako `BaseTool`
- **Příklad:** `class SayariApiTool(BaseTool): async def _arun(self, query: str) -> Dict[str, Any]:`
- **Kdy použít:** Pro zapouzdření volání API a zpracování jejich výsledků
- **Konkrétní případ:** Implementace nástrojů v `tools.py`

## Datový model

Klíčovou roli v architektuře hraje dobře definovaný datový model pro tok informací:

### Stav (State)

Stav je definován jako `TypedDict` a obsahuje:

```python
class State(TypedDict):
    messages: List[BaseMessage]  # Zprávy v konverzaci
    company_analysis: Optional[AnalysisResult]  # Výsledek analýzy dotazu
    company_data: Dict[str, Any]  # Externí data o společnostech
    internal_data: Dict[str, Any]  # Interní data o společnostech
    relationships_data: Dict[str, Any]  # Data o vztazích společností
    output: Optional[str]  # Finální výstup pro uživatele
    errors: List[str]  # Seznam chyb během zpracování
```

### Výsledek analýzy (AnalysisResult)

Strukturovaný výsledek analýzy dotazu:

```python
class AnalysisResult(TypedDict):
    companies: List[str]  # Seznam identifikovaných společností
    company: str  # Primární společnost (první v seznamu)
    analysis_type: Literal["risk_comparison", "common_suppliers", "general"]
    query: str  # Původní dotaz
    is_company_analysis: bool  # Zda se jedná o analýzu společnosti
    confidence: float  # Úroveň důvěry (0.0 - 1.0)
```

## Shrnutí klíčových výhod architektury

1. **Flexibilita** - Snadné přidávání nových uzlů, nástrojů nebo typů analýz
2. **Robustnost** - Izolované zpracování chyb v jednotlivých uzlech
3. **Škálovatelnost** - Možnost paralelizace zpracování dat o více společnostech
4. **Čitelnost** - Přehledná struktura kódu a jasný tok dat
5. **Udržitelnost** - Jednotlivé komponenty lze testovat a aktualizovat nezávisle

## Decision Tree (components)
| Use‑case                 | Component    |
|--------------------------|-------------|
| Simple transform         | LCEL        |
| Complex multi‑tool       | React Agent |
| Multi‑step orchestration | LangGraph   |

## Anti‑patterns
- Nepoužívej synchronní IO v async kódu (např. `time.sleep`, synchronní requests).
- Nepoužívej zastaralý `AgentExecutor`.
- Neimplementuj znovu funkce, které poskytuje LangChain nebo LangGraph.
- Nemíchej přímé volání API s LangChain abstrakcemi.
- Nepiš vlastní retry logiku, použij `tenacity` nebo LangChain `Retry`.

_For unit/integration test conventions see **copilot-test-instructions.md**._
