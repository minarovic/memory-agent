"""Graphs that extract memories on a schedule."""

import asyncio
import logging
import traceback
from datetime import datetime
from typing import Dict, Any

from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, StateGraph
from langgraph.store.base import BaseStore

from memory_agent import configuration, tools, utils
from memory_agent.analyzer import analyze_query
from memory_agent.state import State
from memory_agent.tools import SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage

# Set up enhanced logging
utils.setup_async_logging()
logger = logging.getLogger(__name__)

# Initialize the language model to be used for memory extraction
llm = init_chat_model()


async def analyze_company_input(state: State, config: RunnableConfig) -> dict:
    """Analyzuje vstup uživatele pro identifikaci společností a typu analýzy."""
    try:
        logger.info("Starting analyze_company_input node")
        
        # Získání posledního uživatelského vstupu
        last_user_msg = None
        for msg in reversed(state.messages):
            if hasattr(msg, 'role') and msg.role == "user":
                last_user_msg = msg
                break
        
        if not last_user_msg:
            logger.warning("No user message found for analysis")
            return {}
        
        # Extrahování textu zprávy
        query = last_user_msg.content
        if isinstance(query, list):
            # Pokud je obsah seznam (může obsahovat multimodální obsah), extrahujeme textovou část
            query = " ".join(item for item in query if isinstance(item, str))
        
        logger.debug(f"Analyzing query: {query[:100]}...")
        
        # Načtení konfigurace a modelu
        configurable = configuration.Configuration.from_runnable_config(config)
        model_name = utils.split_model_and_provider(configurable.model)[1]
        
        # Provedení analýzy
        analysis_result = await analyze_query(query, config, model=model_name)
        logger.info(f"Analysis result: {analysis_result}")
        
        # Aktualizace stavu
        return {"company_analysis": analysis_result}
    except Exception as e:
        logger.error(f"Error in analyze_company_input: {str(e)}")
        logger.error(traceback.format_exc())
        return {}


async def fetch_company_data(state: State, config: RunnableConfig) -> dict:
    """Získá data o společnosti pomocí Sayari API."""
    try:
        logger.info("Starting fetch_company_data node")
        
        # Získání informací o společnosti z předchozího kroku
        if not state.company_analysis or not state.company_analysis.get("company"):
            logger.warning("No company information found for fetching data")
            return {}
        
        company_name = state.company_analysis.get("company", "")
        logger.info(f"Fetching data for company: {company_name}")
        
        # Použití nástroje pro volání API
        sayari_tool = SayariApiTool()
        company_data = await sayari_tool._arun(company_name)
        
        logger.info(f"Successfully fetched data for {company_name}")
        logger.debug(f"Company data: {str(company_data)[:200]}...")
        
        # Aktualizace stavu
        return {"company_data": company_data}
    except Exception as e:
        logger.error(f"Error in fetch_company_data: {str(e)}")
        logger.error(traceback.format_exc())
        return {}


async def fetch_internal_data(state: State, config: RunnableConfig) -> dict:
    """Získá interní data o společnosti ze Supabase."""
    try:
        logger.info("Starting fetch_internal_data node")
        
        # Získání informací o společnosti z předchozího kroku
        if not state.company_analysis or not state.company_analysis.get("company"):
            logger.warning("No company information found for fetching internal data")
            return {}
        
        company_name = state.company_analysis.get("company", "")
        logger.info(f"Fetching internal data for company: {company_name}")
        
        # Použití nástroje pro získání interních dat
        internal_data_tool = SupabaseInternalDataTool()
        internal_data = await internal_data_tool._arun(company_name)
        
        logger.info(f"Successfully fetched internal data for {company_name}")
        logger.debug(f"Internal data: {str(internal_data)[:200]}...")
        
        # Aktualizace stavu
        return {"internal_data": internal_data}
    except Exception as e:
        logger.error(f"Error in fetch_internal_data: {str(e)}")
        logger.error(traceback.format_exc())
        return {}


async def fetch_relationships(state: State, config: RunnableConfig) -> dict:
    """Získá vztahy společnosti z Sayari API."""
    try:
        logger.info("Starting fetch_relationships node")
        
        # Kontrola, zda máme ID entity 
        if not state.company_data or not state.company_data.get("entity_id"):
            logger.warning("No entity ID found for fetching relationships")
            return {"relationships_data": None}
        
        entity_id = state.company_data.get("entity_id")
        logger.info(f"Fetching relationships for entity ID: {entity_id}")
        
        # Použití nástroje pro získání vztahů
        relationships_tool = SayariRelationshipsTool()
        relationships_data = await relationships_tool._arun(entity_id)
        
        logger.info(f"Successfully fetched relationships for entity ID: {entity_id}")
        logger.debug(f"Relationships data: {str(relationships_data)[:200]}...")
        
        # Aktualizace stavu
        return {"relationships_data": relationships_data}
    except Exception as e:
        logger.error(f"Error in fetch_relationships: {str(e)}")
        logger.error(traceback.format_exc())
        return {}


async def generate_response(state: State, config: RunnableConfig) -> dict:
    """Generuje odpověď na základě všech sesbíraných dat."""
    try:
        logger.info("Starting generate_response node")
        
        # Načtení konfigurace a modelu
        configurable = configuration.Configuration.from_runnable_config(config)
        model_name = utils.split_model_and_provider(configurable.model)[1]
        llm = init_chat_model(model=model_name)
        
        # Příprava dat pro prompt - extrakce relevantních informací ze stavu
        company_analysis = state.get("company_analysis") or {}
        company_data = state.get("company_data") or {}
        internal_data = state.get("internal_data") or {}
        relationships_data = state.get("relationships_data") or {}
        
        company_name = company_analysis.get("company", "N/A")
        analysis_type = company_analysis.get("analysis_type", "general")
        
        # Vytvoření promptu
        # (Můžeme ho později přesunout do prompts.py pro lepší organizaci)
        prompt_template = ChatPromptTemplate.from_template("""
        Analyzuj následující informace o společnosti {company} pro typ analýzy {analysis_type}.
        
        Externí data (Sayari): {external_data}
        
        Interní data (Supabase): {internal_data}
        
        Vztahy (Sayari): {relationships_data}
        
        Poskytni strukturovanou a detailní analýzu v češtině.
        """)
        
        # Vytvoření LCEL řetězce
        chain = (
            {
                "company": lambda s: s["company_analysis"].get("company", "N/A"),
                "analysis_type": lambda s: s["company_analysis"].get("analysis_type", "general"),
                "external_data": lambda s: s.get("company_data", {}),
                "internal_data": lambda s: s.get("internal_data", {}),
                "relationships_data": lambda s: s.get("relationships_data", {})
            }
            | prompt_template 
            | llm 
            | StrOutputParser()
        )
        
        # Generování odpovědi pomocí řetězce
        logger.debug("Invoking generation chain with state data")
        response_content = await chain.ainvoke(state, config)
        
        logger.info("Successfully generated response")
        logger.debug(f"Generated response content: {response_content[:200]}...")
        
        # Aktualizace stavu s novou odpovědí
        # Přidáme odpověď jako AIMessage do historie
        # (Předpokládáme, že state['messages'] existuje a je seznam)
        updated_messages = state.get("messages", []) + [AIMessage(content=response_content)]
        
        return {"messages": updated_messages} # Vracíme aktualizovanou historii zpráv
    
    except Exception as e:
        logger.error(f"Error in generate_response: {str(e)}")
        logger.error(traceback.format_exc())
        error_message = "Omlouvám se, při generování odpovědi došlo k chybě. Zkuste prosím svůj dotaz přeformulovat."
        # Vracíme chybu v poli messages, aby byla vidět v historii
        updated_messages = state.get("messages", []) + [AIMessage(content=error_message)]
        return {"messages": updated_messages}


async def store_memory(state: State, config: RunnableConfig, *, store: BaseStore) -> dict:
    """Uloží výsledek analýzy do paměti."""
    try:
        logger.info("Starting store_memory node")
        
        # Kontrola, zda máme analýzu společnosti
        if not state.company_analysis or not state.company_analysis.get("is_company_analysis"):
            logger.info("No company analysis to store in memory")
            return {}
        
        # Extrakce dat pro uložení
        ca = state.company_analysis
        companies = ca.get("companies", [])
        analysis_type = ca.get("analysis_type", "general")
        
        if not companies:
            logger.info("No companies found to store in memory")
            return {}
        
        # Formátování obsahu paměti
        memory_content = f"User asked about companies: {', '.join(companies)}. Analysis type: {analysis_type}."
        
        # Kontext z odpovědi
        context = ""
        if state.response:
            context = f"Response included information about {', '.join(companies)}."
        
        # Uložení paměti
        await tools.upsert_memory(
            content=memory_content,
            context=context,
            config=config,
            store=store
        )
        
        logger.info(f"Successfully stored memory about companies: {', '.join(companies)}")
        return {}
    except Exception as e:
        logger.error(f"Error in store_memory: {str(e)}")
        logger.error(traceback.format_exc())
        return {}


def should_analyze_companies(state: State) -> str:
    """Rozhoduje, zda je potřeba analyzovat společnosti v dotazu."""
    # Vždy nejprve analyzujeme vstup
    return "analyze"


def should_fetch_company_data(state: State) -> str:
    """Rozhoduje, zda je potřeba získat data o společnosti."""
    if state.company_analysis and state.company_analysis.get("is_company_analysis", False):
        return "fetch"
    else:
        return "skip"


def should_fetch_relationships(state: State) -> str:
    """Rozhoduje, zda je potřeba získat vztahy společnosti."""
    if (state.company_analysis and 
        state.company_analysis.get("is_company_analysis", False) and
        state.company_analysis.get("analysis_type") in ["common_suppliers", "risk_comparison"] and
        state.company_data and 
        state.company_data.get("entity_id")):
        return "fetch"
    else:
        return "skip"


def build_company_analysis_graph() -> StateGraph:
    """Vytvoří graf pro analýzu společností."""
    try:
        logger.info("Building company analysis graph")
        
        # Vytvoření grafu s výchozím stavem
        workflow = StateGraph(State)
        
        # Definice uzlů grafu
        workflow.add_node("analyze_input", analyze_company_input)
        workflow.add_node("fetch_company_data", fetch_company_data)
        workflow.add_node("fetch_internal_data", fetch_internal_data)
        workflow.add_node("fetch_relationships", fetch_relationships)
        workflow.add_node("generate_response", generate_response)
        workflow.add_node("store_memory", store_memory)
        
        # Definice hran grafu
        workflow.set_entry_point("analyze_input")
        
        workflow.add_conditional_edges(
            "analyze_input",
            should_analyze_companies,
            {
                "analyze": "fetch_company_data"
            }
        )
        
        workflow.add_conditional_edges(
            "fetch_company_data",
            should_fetch_company_data,
            {
                "fetch": "fetch_internal_data",
                "skip": "generate_response"
            }
        )
        
        workflow.add_edge("fetch_internal_data", "fetch_relationships")
        
        workflow.add_conditional_edges(
            "fetch_relationships",
            should_fetch_relationships,
            {
                "fetch": "generate_response",
                "skip": "generate_response"
            }
        )
        
        workflow.add_edge("generate_response", "store_memory")
        workflow.add_edge("store_memory", END)
        
        logger.info("Successfully built company analysis graph")
        return workflow.compile()
    except Exception as e:
        logger.error(f"Error building graph: {str(e)}")
        logger.error(traceback.format_exc())
        raise
