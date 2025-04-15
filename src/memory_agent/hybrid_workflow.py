"""
Hybridní implementace workflow s využitím LangGraph pro celkový tok a React agentů pro komplexní uzly.

Tento modul implementuje workflow pro analýzu společností, kde:
1. Celkový tok dat je řízen LangGraphem
2. Komplexní operace jsou delegovány na specializované React agenty
3. Jednodušší operace jsou implementovány jako jednoduché funkce/LCEL řetězce
"""

import logging
import asyncio
from typing import Dict, List, Literal, Optional, TypedDict, Any, Union, Tuple
import json
import uuid

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool, tool
from langchain_core.pydantic_v1 import BaseModel, Field

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import create_react_agent

from memory_agent.analyzer import analyze_query, AnalysisResult
from memory_agent.tools import SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool

logger = logging.getLogger(__name__)

# Definice stavu pro LangGraph
class State(TypedDict):
    """Stav workflow pro analýzu společností."""
    
    # Vstup, analýza a zpracování
    messages: List[BaseMessage]  # Zprávy v konverzaci
    company_analysis: Optional[AnalysisResult]  # Výsledek analýzy dotazu
    
    # Data o společnostech
    company_data: Dict[str, Any]  # Externí data o společnostech (klíč: jméno společnosti)
    internal_data: Dict[str, Any]  # Interní data o společnostech
    relationships_data: Dict[str, Any]  # Data o vztazích společností
    
    # Výstup
    output: Optional[str]  # Finální výstup pro uživatele
    errors: List[str]  # Seznam chyb během zpracování


# ==================== Implementace React agenta pro získávání dat ====================

@tool
async def fetch_company_data(company: str) -> str:
    """Získá data o společnosti z externího API.
    
    Args:
        company: Název společnosti
    
    Returns:
        Textový popis výsledku získávání dat
    """
    try:
        sayari_tool = SayariApiTool()
        result = await sayari_tool._arun(company)
        return f"Úspěšně získána data o společnosti {company}. Entity ID: {result.get('id', 'N/A')}"
    except Exception as e:
        return f"Chyba při získávání dat o společnosti {company}: {str(e)}"

@tool
async def fetch_internal_data(company: str) -> str:
    """Získá interní data o společnosti.
    
    Args:
        company: Název společnosti
    
    Returns:
        Textový popis výsledku získávání dat
    """
    try:
        internal_tool = SupabaseInternalDataTool()
        result = await internal_tool._arun(company)
        return f"Úspěšně získána interní data o společnosti {company}."
    except Exception as e:
        return f"Chyba při získávání interních dat o společnosti {company}: {str(e)}"

@tool
async def fetch_relationships(entity_id: str, company: str) -> str:
    """Získá data o vztazích společnosti.
    
    Args:
        entity_id: ID entity v Sayari
        company: Název společnosti (pro reference)
    
    Returns:
        Textový popis výsledku získávání dat
    """
    try:
        relationships_tool = SayariRelationshipsTool()
        result = await relationships_tool._arun(entity_id)
        return f"Úspěšně získána data o vztazích pro společnost {company} (ID: {entity_id})."
    except Exception as e:
        return f"Chyba při získávání dat o vztazích pro společnost {company}: {str(e)}"

# Vytvoření React agenta s nástroji pro získávání dat
def create_data_gathering_agent(llm):
    """Vytvoří React agenta pro získávání dat o společnostech.
    
    Args:
        llm: LLM model pro použití v agentovi
    
    Returns:
        React agent připravený pro použití jako uzel v grafu
    """
    tools = [fetch_company_data, fetch_internal_data, fetch_relationships]
    
    # Vytvoření React agenta s nástroji
    system_prompt = """Jsi specializovaný agent pro získávání dat o společnostech. 
    
    Tvým úkolem je získat kompletní data pro všechny uvedené společnosti z dostupných zdrojů:

    1. Pro každou společnost nejprve získej základní externí data pomocí nástroje fetch_company_data
    2. Poté získej interní data pomocí nástroje fetch_internal_data 
    3. Pokud má společnost entity_id (uvedeno v odpovědi z fetch_company_data), získej také data o vztazích pomocí nástroje fetch_relationships

    Pokus se získat co nejvíce dat i v případě, že některé API volání selže. Postupuj systematicky a zkus alternativní způsoby získání dat, pokud je to možné.
    
    Přehledně seřaď výsledky podle společností a shrň, jaká data se podařilo/nepodařilo získat.
    """
    
    return create_react_agent(llm, tools, prompt=system_prompt)

# ==================== Uzly v LangGraph workflow ====================

async def analyze_company_input(state: State, config: Dict[str, Any]) -> Dict:
    """Analyzuje vstup uživatele a identifikuje společnosti a typ analýzy.
    
    Args:
        state: Aktuální stav grafu
        config: Konfigurace běhu
    
    Returns:
        Aktualizace stavu s výsledky analýzy
    """
    messages = state.get("messages", [])
    if not messages:
        return {"errors": ["Žádné zprávy k analýze"]}
    
    # Získání posledního uživatelského vstupu
    user_input = ""
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            user_input = message.content
            break
    
    if not user_input:
        return {"errors": ["Nenalezen žádný uživatelský vstup"]}
    
    try:
        # Analýza dotazu pomocí funkcí z analyzer.py
        analysis_result = await analyze_query(user_input)
        
        logger.info(f"Analýza dotazu: {analysis_result}")
        
        return {
            "company_analysis": analysis_result
        }
    except Exception as e:
        logger.error(f"Chyba při analýze dotazu: {str(e)}")
        return {
            "company_analysis": {
                "companies": [],
                "company": "",
                "analysis_type": "general",
                "query": user_input,
                "is_company_analysis": False,
                "confidence": 0.0
            },
            "errors": state.get("errors", []) + [f"Chyba při analýze dotazu: {str(e)}"]
        }

async def gather_company_data_node(state: State, config: Dict[str, Any]) -> Dict:
    """Uzel, který orchestruje získávání dat o společnostech pomocí React agenta.
    
    Args:
        state: Aktuální stav grafu
        config: Konfigurace běhu
    
    Returns:
        Aktualizace stavu s daty o společnostech
    """
    analysis = state.get("company_analysis", {})
    companies = analysis.get("companies", [])
    
    if not companies:
        return {
            "company_data": {},
            "internal_data": {},
            "relationships_data": {}
        }
    
    try:
        # Inicializace LLM pro React agenta
        llm = init_chat_model()
        
        # Vytvoření React agenta
        agent = create_data_gathering_agent(llm)
        
        # Vytvoření prompta pro agenta s seznamem společností
        company_list = ", ".join(companies)
        
        # Zavolání React agenta
        agent_result = await agent.ainvoke({
            "messages": [
                HumanMessage(content=f"Získej data pro tyto společnosti: {company_list}")
            ]
        })
        
        # Extrakce výsledků agenta
        # V praxi by zde byla sofistikovanější logika pro extrakci strukturovaných dat z odpovědí agenta
        # Pro ukázku používáme zjednodušený přístup
        
        # Inicializace výsledných datových struktur
        company_data = {}
        internal_data = {}
        relationships_data = {}
        
        # Základ pro ukázkovou implementaci - ve skutečném projektu by byla
        # komplexnější logika pro extrakci dat z odpovědi agenta
        for company in companies:
            # Ukázkové naplnění struktur (v produkčním kódu by byla skutečná data)
            company_data[company] = {
                "id": f"entity_{uuid.uuid4().hex[:8]}",  # simulace entity ID
                "name": company,
                "found": True,
                "meta": "Data získána pomocí React agenta"
            }
            
            internal_data[company] = {
                "tier": "Tier 1",
                "hs_codes": ["8471", "8473"],
                "found": True
            }
            
            if company_data[company]["id"]:
                relationships_data[company] = {
                    "entity_id": company_data[company]["id"],
                    "suppliers": ["Supplier A", "Supplier B"],
                    "customers": ["Customer X", "Customer Y"],
                    "found": True
                }
        
        # Vrátit aktualizaci stavu
        return {
            "company_data": company_data,
            "internal_data": internal_data,
            "relationships_data": relationships_data
        }
    except Exception as e:
        logger.error(f"Chyba při získávání dat o společnostech: {str(e)}")
        return {
            "errors": state.get("errors", []) + [f"Chyba při získávání dat: {str(e)}"]
        }

async def call_model(state: State, config: Dict[str, Any]) -> Dict:
    """Generuje finální odpověď na základě všech získaných dat.
    
    Args:
        state: Aktuální stav grafu
        config: Konfigurace běhu
    
    Returns:
        Aktualizace stavu s finální odpovědí
    """
    try:
        # Získání dat ze stavu
        analysis = state.get("company_analysis", {})
        company_data = state.get("company_data", {})
        internal_data = state.get("internal_data", {})
        relationships_data = state.get("relationships_data", {})
        
        companies = analysis.get("companies", [])
        analysis_type = analysis.get("analysis_type", "general")
        
        # Pokud nemáme společnosti k analýze, vrátíme obecnou odpověď
        if not companies:
            return {
                "output": "Nepodařilo se identifikovat společnosti k analýze. Můžete svůj dotaz upřesnit?"
            }
        
        # Inicializace LLM modelu
        llm = init_chat_model()
        
        # Implementace LCEL řetězce pro generování odpovědi
        prompt = ChatPromptTemplate.from_template("""
        Jsi špičkový analytik specializující se na analýzu společností a dodavatelských řetězců.
        
        Na základě následujících dat proveď {analysis_type} pro společnosti: {companies_list}.
        
        Externí data:
        {external_data}
        
        Interní data:
        {internal_data}
        
        Vztahy:
        {relationships_data}
        
        Poskytni strukturovanou a detailní analýzu:
        1. Přehled základních údajů o společnostech
        2. Specifickou analýzu podle požadovaného typu ({analysis_type})
        3. Identifikované rizikové faktory a příležitosti
        4. Doporučení pro další kroky
        
        Pokud některá data chybí, upozorni na to, ale pokus se poskytnout co nejlepší analýzu na základě dostupných dat.
        """)
        
        # Formátování vstupních dat pro prompt
        external_data_str = json.dumps(company_data, indent=2, ensure_ascii=False)
        internal_data_str = json.dumps(internal_data, indent=2, ensure_ascii=False)
        relationships_data_str = json.dumps(relationships_data, indent=2, ensure_ascii=False)
        
        # LCEL řetězec
        chain = (
            prompt 
            | llm 
            | StrOutputParser()
        )
        
        # Volání řetězce
        result = await chain.ainvoke({
            "analysis_type": analysis_type,
            "companies_list": ", ".join(companies),
            "external_data": external_data_str,
            "internal_data": internal_data_str,
            "relationships_data": relationships_data_str
        })
        
        # Vrácení výsledku
        return {
            "output": result,
            "messages": state.get("messages", []) + [AIMessage(content=result)]
        }
    except Exception as e:
        error_msg = f"Chyba při generování odpovědi: {str(e)}"
        logger.error(error_msg)
        return {
            "output": "Omlouváme se, při zpracování vaší žádosti došlo k chybě. Zkuste to prosím znovu.",
            "errors": state.get("errors", []) + [error_msg]
        }

# ==================== Definice grafu ====================

def create_analysis_graph():
    """Vytvoří graf workflow pro analýzu společností.
    
    Returns:
        Kompilovaný LangGraph pro workflow analýzy
    """
    # Vytvoření stavového grafu
    builder = StateGraph(State)
    
    # Přidání uzlů grafu
    builder.add_node("analyze_company_input", analyze_company_input)
    builder.add_node("gather_company_data", gather_company_data_node)
    builder.add_node("call_model", call_model)
    
    # Definice hran
    builder.add_edge("analyze_company_input", "gather_company_data")
    builder.add_edge("gather_company_data", "call_model")
    builder.add_edge("call_model", END)
    
    # Definice routeru pro podmíněné větvení
    def route_after_analysis(state: State):
        """Rozhoduje o dalším kroku na základě výsledku analýzy."""
        analysis = state.get("company_analysis", {})
        
        # Pokud nemáme společnosti k analýze, můžeme přeskočit sběr dat
        if not analysis.get("companies") or not analysis.get("is_company_analysis", False):
            return "call_model"
        
        return "gather_company_data"
    
    # Přidání podmíněného větvení
    builder.add_conditional_edges(
        "analyze_company_input",
        route_after_analysis,
        {
            "gather_company_data": "gather_company_data",
            "call_model": "call_model"
        }
    )
    
    # Kompilace grafu
    return builder.compile()

# Funkce pro vytvoření a spuštění workflow
async def process_user_query(user_query: str):
    """Zpracuje uživatelský dotaz a vrátí odpověď.
    
    Args:
        user_query: Dotaz uživatele
    
    Returns:
        Odpověď na dotaz uživatele
    """
    # Vytvoření grafu
    graph = create_analysis_graph()
    
    # Inicializace stavu
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "company_analysis": None,
        "company_data": {},
        "internal_data": {},
        "relationships_data": {},
        "output": None,
        "errors": []
    }
    
    # Spuštění grafu
    result = await graph.ainvoke(initial_state)
    
    # Vrácení výstupu
    return result.get("output", "Nepodařilo se zpracovat váš dotaz.")

# Příklad použití
if __name__ == "__main__":
    import asyncio
    
    async def main():
        # Příklad dotazu
        query = "Analyzuj rizika společností Apple a Samsung"
        print(f"Dotaz: {query}")
        
        # Zpracování dotazu
        response = await process_user_query(query)
        print(f"\nOdpověď:\n{response}")
    
    # Spuštění ukázkového kódu
    asyncio.run(main())
