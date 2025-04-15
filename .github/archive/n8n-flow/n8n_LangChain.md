# Analýza Data AI Agent Workflow a Implementace v LangChainu

## Analýza n8n Workflow

Aktuální n8n workflow představuje PoC (Proof of Concept) pro AI agenta, který analyzuje firmy. Hlavní komponenty workflow jsou:

1. **Rozpoznání záměru a entity** - Identifikace jména firmy a požadovaného typu analýzy pomocí AI
2. **Získání externích dat** - Volání Sayari API pro získání informací o firmě
3. **Získání interních dat** - Získání dat o dodavatelích a HS kódech
4. **Analýza vztahů** - Zpracování vztahů mezi entitami
5. **Generování výsledné analýzy** - Využití AI pro vytvoření strukturované analýzy

## Postup Implementace v LangChainu

### 1. Rozpoznání firmy a typu analýzy ✅ (již implementováno)
- Využití LLM pro extrakci jména firmy a typu analýzy z uživatelského vstupu
- Strukturované vrácení informací ve formátu "Jméno firmy; typ_analýzy"

### 2. Implementace volání externích API
- **Priorita: Vysoká**
- **Cíl:** Získat data o firmě z externích zdrojů (např. Sayari API)
- **Implementace:**
  ```python
  from langchain.tools import Tool
  from langchain.utilities import RequestsWrapper
  
  def fetch_sayari_data(company_name: str) -> dict:
      """Získá data o společnosti z Sayari API."""
      base_url = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/sayari-simulator"
      requests = RequestsWrapper()
      response = requests.get(f"{base_url}/search/entity?q={company_name}")
      return response.json()
      
  sayari_tool = Tool(
      name="fetch_sayari_data",
      func=fetch_sayari_data,
      description="Získá informace o společnosti z Sayari API."
  )
  ```

### 3. Implementace získání interních dat
- **Priorita: Střední**
- **Cíl:** Získat interní klasifikaci firmy, HS kódy a obchodní aktivity
- **Implementace:**
  ```python
  def fetch_internal_data(company_name: str) -> dict:
      """Získá interní data o společnosti."""
      base_url = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/get-supplier-data"
      requests = RequestsWrapper()
      response = requests.get(f"{base_url}?name={company_name}")
      return response.json()
      
  internal_data_tool = Tool(
      name="fetch_internal_data",
      func=fetch_internal_data,
      description="Získá interní data o společnosti včetně tier klasifikace a HS kódů."
  )
  ```

### 4. Implementace analýzy vztahů
- **Priorita: Střední**
- **Cíl:** Získat a zpracovat vztahy mezi entitami (dodavatelé, zákazníci, vlastníci)
- **Implementace:**
  ```python
  def fetch_entity_relationships(entity_id: str) -> dict:
      """Získá vztahy entity z Sayari API."""
      base_url = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/sayari-simulator"
      requests = RequestsWrapper()
      response = requests.get(f"{base_url}/entity/{entity_id}/relationships")
      return response.json()
      
  relationships_tool = Tool(
      name="fetch_entity_relationships",
      func=fetch_entity_relationships,
      description="Získá vztahy pro entitu (firmu) podle ID entity."
  )
  ```

### 5. Implementace analýzy pomocí LangGraph (doporučeno)
- **Priorita: Vysoká**
- **Cíl:** Vytvoření grafu, který řídí tok zpracování dat a generuje finální analýzu
- **Implementace:**
  ```python
  from typing import TypedDict, Optional, Dict, Any
  from langgraph.graph import StateGraph, END
  
  # Definice stavu grafu pro uchování dat mezi kroky
  class State(TypedDict):
      company_analysis: Dict[str, Any]  # Výsledek analýzy dotazu
      company_data: Optional[Dict]      # Externí data o společnosti
      internal_data: Optional[Dict]     # Interní data o společnosti
      relationships_data: Optional[Dict]  # Data o vztazích
      messages: list                    # Seznam zpráv v konverzaci
      output: Optional[str]             # Finální odpověď pro uživatele

  # Funkce pro uzly grafu
  async def analyze_company_input(state: State, config: Dict[str, Any]) -> Dict:
      """Analyzuje vstup uživatele pro identifikaci společností a typu analýzy."""
      # Logika pro extrakci společnosti a typu analýzy z uživatelského vstupu
      return {"company_analysis": analysis_result}
  
  async def fetch_company_data(state: State, config: Dict[str, Any]) -> Dict:
      """Získá data o společnosti pomocí Sayari API."""
      company_name = state.get("company_analysis", {}).get("company", "")
      data = await sayari_tool._arun(company_name)
      return {"company_data": data}
  
  async def fetch_internal_data(state: State, config: Dict[str, Any]) -> Dict:
      """Získá interní data o společnosti."""
      company_name = state.get("company_analysis", {}).get("company", "")
      data = await internal_data_tool._arun(company_name)
      return {"internal_data": data}
      
  async def fetch_relationships(state: State, config: Dict[str, Any]) -> Dict:
      """Získá vztahy společnosti."""
      entity_id = state.get("company_data", {}).get("entity_id")
      if not entity_id:
          return {}
      data = await relationships_tool._arun(entity_id)
      return {"relationships_data": data}
  
  async def call_model(state: State, config: Dict[str, Any]) -> Dict:
      """Generuje finální analýzu na základě získaných dat."""
      # Implementace LCEL řetězce pro zpracování dat a generování odpovědi
      prompt = ChatPromptTemplate.from_template("""
      Analyzuj následující informace o společnosti {company} pro typ analýzy {analysis_type}.
      
      Externí data: {external_data}
      
      Interní data: {internal_data}
      
      Vztahy: {relationships_data}
      
      Poskytni strukturovanou a detailní analýzu.
      """)
      
      chain = (
          {"company": lambda s: s["company_analysis"]["company"],
           "analysis_type": lambda s: s["company_analysis"]["analysis_type"],
           "external_data": lambda s: s["company_data"],
           "internal_data": lambda s: s["internal_data"],
           "relationships_data": lambda s: s["relationships_data"]} 
          | prompt 
          | llm 
          | StrOutputParser()
      )
      
      result = await chain.ainvoke(state, config)
      return {"output": result, "messages": state["messages"] + [AIMessage(content=result)]}
  
  # Vytvoření grafu
  builder = StateGraph(State)
  
  # Přidání uzlů do grafu
  builder.add_node("analyze_company_input", analyze_company_input)
  builder.add_node("fetch_company_data", fetch_company_data)
  builder.add_node("fetch_internal_data", fetch_internal_data)
  builder.add_node("fetch_relationships", fetch_relationships)
  builder.add_node("call_model", call_model)
  
  # Definice směrování v grafu
  builder.add_edge("analyze_company_input", "fetch_company_data")
  builder.add_edge("fetch_company_data", "fetch_internal_data")
  builder.add_edge("fetch_internal_data", "fetch_relationships")
  builder.add_edge("fetch_relationships", "call_model")
  builder.add_edge("call_model", END)
  
  # Definice podmíněného směrování (pokud je potřeba)
  def route_after_analysis(state: State):
      """Rozhoduje o dalším kroku na základě výsledku analýzy."""
      if state.get("company_analysis", {}).get("is_company_analysis", False):
          return "fetch_company_data"
      else:
          return "call_model"  # Přeskočí získávání dat, pokud nejde o firemní analýzu
  
  builder.add_conditional_edges("analyze_company_input", route_after_analysis, 
                              {"fetch_company_data": "fetch_company_data", 
                               "call_model": "call_model"})
  
  # Kompilace grafu
  graph = builder.compile()
  ```

### 6. Propojení s uživatelským rozhraním
- **Priorita: Střední**
- **Cíl:** Vytvoření API endpointů pro interakci s grafem
- **Implementace:**
  ```python
  from fastapi import FastAPI, Request
  from langserve import add_routes
  
  app = FastAPI()
  
  # Přidání routes pro graf
  add_routes(
      app,
      graph,
      path="/company-analysis",
  )
  
  @app.post("/chat")
  async def chat_endpoint(request: Request):
      """Endpoint pro chatovací rozhraní."""
      data = await request.json()
      user_message = data.get("message", "")
      session_id = data.get("session_id", "default")
      
      # Příprava vstupu pro graf
      inputs = {
          "messages": [HumanMessage(content=user_message)]
      }
      
      # Asynchronní volání grafu
      result = await graph.ainvoke(inputs)
      
      return {"response": result.get("output", ""), "session_id": session_id}
  ```

## Další Kroky a Rozšíření

1. **Optimalizace promptů** - Vylepšení promptů pro LLM, aby lépe extrahovaly a strukturovaly informace
2. **Caching výsledků API** - Implementace cachování pro snížení počtu volání API
3. **Rozšíření typů analýz** - Podpora dalších typů analýz (např. environmentální dopad, geopolitická rizika)
4. **Vizualizace vztahů** - Implementace vizualizace vztahů mezi entitami
5. **Integrovaná paměť** - Přidání paměti, která umožní agentovi učit se z předchozích analýz

## Implementace v LangGraph

Pro pokročilejší verzi navrhuji použít LangGraph, který umožňuje vytvářet komplexnější grafy stavů a přechodů:

```python
# Definice grafu pro analýzu firem
def create_company_analysis_graph(llm):
    graph = StateGraph(AgentState)
    
    # Definice nástrojů
    tools = [
        fetch_sayari_data_tool,
        fetch_internal_data_tool,
        fetch_relationships_tool,
        analyze_risks_tool,
        analyze_relationships_tool
    ]
    
    # Definice uzlů
    graph.add_node("parse_input", parse_input_node(llm))
    graph.add_node("fetch_external_data", fetch_external_data_node())
    graph.add_node("fetch_internal_data", fetch_internal_data_node())
    graph.add_node("fetch_relationships", fetch_relationships_node())
    graph.add_node("analyze", analyze_node(llm, tools))
    
    # Definice toku
    graph.add_edge("parse_input", "fetch_external_data")
    graph.add_edge("fetch_external_data", "fetch_internal_data")
    graph.add_conditional_edges(...)
    
    return graph.compile()