"""
Define the shared state management for Memory Agent workflow.

Tento modul obsahuje State třídu, která slouží jako centrální systém
správy stavu pro Memory Agent. Využívá moderní vzory správy stavu LangGraph
včetně struktur podobných TypedDict s implementací dataclass a specializovaných
reducerů stavu prostřednictvím Annotated typů.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated

from memory_agent.analyzer import AnalysisResult


def merge_dict_values(left: Dict[str, Any], right: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sloučí hodnoty slovníků pro aktualizaci stavu.
    
    Tato reducer funkce kombinuje dva slovníky, zachovává hodnoty z obou,
    když nejsou v konfliktu, a používá hodnoty z pravé strany, když jsou.
    
    Args:
        left: Původní slovník ve stavu
        right: Nový slovník, který má být sloučen do stavu
        
    Returns:
        Dict[str, Any]: Aktualizovaný sloučený slovník
    """
    if not right:
        return left
    
    result = left.copy() if left else {}
    result.update(right)
    return result


# BLOKOVÁNO(B1): Implementace stavového grafu čeká na dokončení unit testů pro tools.py (A4)
@dataclass(kw_only=True)
class State:
    """
    Hlavní stav grafu pro workflow Memory Agent.
    
    Tato třída definuje celou strukturu správy stavu pro Memory Agent,
    která zpracovává historii konverzace, výsledky analýz, data společností a chybové stavy.
    Každé pole používá vhodné typové anotace a reducery k zajištění správné
    správy stavu v průběhu workflow LangGraph.
    """

    messages: Annotated[list[AnyMessage], add_messages]
    """
    Zprávy v konverzaci.
    
    Toto pole používá reducer add_messages z LangGraph k správnému
    připojení nových zpráv k historii konverzace při zachování
    jejich správného pořadí a vztahů. Reducer zpracovává různé
    typy zpráv (uživatel, asistent, nástroj) a zajišťuje jejich správné formátování.
    """
    
    company_analysis: Optional[AnalysisResult] = None
    """
    Výsledek analýzy společností z uživatelského dotazu.
    
    Obsahuje výsledky analýzy entit společností extrahovaných z uživatelských dotazů,
    včetně identifikovaných názvů společností, asociací a případných disambiguací.
    """
    
    # Nové atributy pro rozšířenou funkcionalitu
    company_data: Annotated[Dict[str, Any], merge_dict_values] = field(default_factory=dict)
    """
    Strukturovaná data o společnostech získaná z různých zdrojů.
    
    Obsahuje detailní informace o společnostech včetně identifikátorů, 
    metadat a informací o zdroji. Používá reducer merge_dict_values
    pro správné kombinování informací z více zdrojů nebo analytických kroků.
    """
    
    internal_data: Annotated[Dict[str, Any], merge_dict_values] = field(default_factory=dict)
    """
    Interní data používaná workflow, která nejsou přímo součástí výstupu.
    
    Zahrnuje informace pro interní správu stavu, dočasné výsledky výpočtů
    a další data potřebná během provádění workflow, ale nezahrnutá do konečných výstupů.
    """
    
    relationships_data: Annotated[Dict[str, List[Dict[str, Any]]], merge_dict_values] = field(default_factory=dict)
    """
    Data o vztazích mezi entitami identifikovanými ve workflow.
    
    Mapuje identifikátory entit na seznamy dat o vztazích, což umožňuje workflow
    sledovat komplexní sítě vztahů mezi společnostmi a dalšími entitami.
    """
    
    error_state: Dict[str, Any] = field(default_factory=dict)
    """
    Informace o chybách, když workflow narazí na problémy.
    
    Obsahuje detailní informace o chybách včetně typu chyby, zprávy,
    komponenty, která chybu vygenerovala, a případných pokusů o zotavení.
    """
    
    output: Dict[str, Any] = field(default_factory=dict)
    """
    Finální zpracovaný výstup workflow.
    
    Obsahuje strukturovaná výstupní data připravená k prezentaci uživateli,
    včetně zpracovaných informací o společnostech, dat o vztazích a případně
    vygenerovaných postřehů nebo doporučení.
    """


__all__ = [
    "State",
]
