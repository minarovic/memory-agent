#!/usr/bin/env python3
"""
Testovací skript pro manuální testování workflow analýzy společnosti.
Tento skript umožňuje krok po kroku projít celým workflowem od rozpoznání
společnosti až po získání a vizualizaci všech dat.
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional

from memory_agent.analyzer import analyze_query
from memory_agent.tools import SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool

# Nastavení loggeru pro lepší informace při testování
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("test_company_analysis")


class TestState:
    """Jednoduchý stav pro sledování průběhu workflow."""
    
    def __init__(self):
        self.company_analysis = None
        self.company_data = None
        self.internal_data = None
        self.relationships_data = None
        
    def update(self, **kwargs):
        """Aktualizuje stav novými daty."""
        for key, value in kwargs.items():
            setattr(self, key, value)
            
    def __str__(self):
        """String reprezentace stavu pro zobrazení."""
        return json.dumps({
            "company_analysis": self.company_analysis,
            "company_data": self.company_data,
            "internal_data": self.internal_data,
            "relationships_data": self.relationships_data
        }, indent=2, ensure_ascii=False)


async def test_analyze_company(user_input: str) -> TestState:
    """Otestuje celý workflow analýzy společnosti."""
    state = TestState()
    logger.info(f"Začátek analýzy pro vstup: '{user_input}'")
    
    # Krok 1: Rozpoznání společnosti a typu analýzy
    logger.info("Krok 1: Rozpoznání společnosti a typu analýzy")
    analysis_result = await analyze_query(user_input)
    state.update(company_analysis=analysis_result)
    
    if not analysis_result["is_company_analysis"]:
        logger.warning("Vstup nebyl rozpoznán jako dotaz na firemní analýzu")
        return state
    
    logger.info(f"Rozpoznána společnost: {analysis_result['company']}")
    logger.info(f"Typ analýzy: {analysis_result['analysis_type']}")
    
    # Krok 2: Získání dat o společnosti z Sayari API
    logger.info("Krok 2: Získání dat o společnosti z Sayari API")
    sayari_tool = SayariApiTool()
    try:
        company_data = await sayari_tool._arun(analysis_result["company"])
        state.update(company_data=company_data)
        logger.info(f"Získána data pro společnost, entity_id: {company_data.get('entity_id')}")
    except Exception as e:
        logger.error(f"Chyba při získávání dat z Sayari API: {str(e)}")
    
    # Krok 3: Získání interních dat o společnosti
    logger.info("Krok 3: Získání interních dat o společnosti")
    internal_tool = SupabaseInternalDataTool()
    try:
        internal_data = await internal_tool._arun(analysis_result["company"])
        state.update(internal_data=internal_data)
        logger.info("Získána interní data o společnosti")
    except Exception as e:
        logger.error(f"Chyba při získávání interních dat: {str(e)}")
    
    # Krok 4: Získání vztahů společnosti
    if state.company_data and state.company_data.get("entity_id"):
        logger.info("Krok 4: Získání vztahů společnosti")
        relationships_tool = SayariRelationshipsTool()
        try:
            relationships_data = await relationships_tool._arun(state.company_data["entity_id"])
            state.update(relationships_data=relationships_data)
            logger.info("Získána data o vztazích společnosti")
        except Exception as e:
            logger.error(f"Chyba při získávání vztahů: {str(e)}")
    else:
        logger.warning("Nelze získat vztahy - chybí ID entity")
    
    # Shrnutí analýzy
    logger.info("Analýza dokončena")
    return state


def format_company_report(state: TestState) -> str:
    """Formátuje výsledky analýzy do čitelné zprávy."""
    if not state.company_analysis or not state.company_analysis.get("is_company_analysis"):
        return "Nebyla identifikována žádná firemní analýza."
    
    company = state.company_analysis.get("company", "Neznámá společnost")
    analysis_type = state.company_analysis.get("analysis_type", "general")
    
    report = [
        f"# Analýza společnosti: {company}",
        f"Typ analýzy: {analysis_type}",
        "",
    ]
    
    # Přidání dat o společnosti
    if state.company_data:
        report.append("## Externí data")
        
        # Základní informace
        entity_id = state.company_data.get("entity_id", "Neznámé ID")
        report.append(f"ID entity: {entity_id}")
        
        # Riziková analýza
        risk_analysis = state.company_data.get("risk_analysis", {})
        report.append(f"Rizikové skóre: {risk_analysis.get('risk_score', '0')}")
        report.append(f"Sankce: {risk_analysis.get('sanctions_status', 'Žádné aktivní sankce')}")
        
        risk_factors = risk_analysis.get("risk_factors", [])
        if risk_factors:
            report.append("Rizikové faktory:")
            for factor in risk_factors:
                report.append(f"- {factor}")
        else:
            report.append("Rizikové faktory: Žádné")
        
        report.append("")
    
    # Přidání interních dat
    if state.internal_data:
        report.append("## Interní data")
        
        company_profile = state.internal_data.get("company_profile", {})
        report.append(f"Tier klasifikace: {company_profile.get('tier_classification', 'Neurčeno')}")
        
        hs_codes = company_profile.get("hs_codes", [])
        if hs_codes:
            report.append("HS kódy:")
            for code in hs_codes:
                report.append(f"- {code}")
        else:
            report.append("HS kódy: Žádné")
        
        activities = company_profile.get("business_activities", [])
        if activities:
            report.append("Obchodní aktivity:")
            for activity in activities:
                report.append(f"- {activity}")
        else:
            report.append("Obchodní aktivity: Žádné")
        
        report.append("")
    
    # Přidání vztahů
    if state.relationships_data and state.relationships_data.get("has_relationships"):
        report.append("## Vztahy")
        
        relationships = state.relationships_data.get("relationships", {})
        
        suppliers = relationships.get("suppliers", [])
        if suppliers:
            report.append("Dodavatelé:")
            for supplier in suppliers:
                report.append(f"- {supplier}")
        else:
            report.append("Dodavatelé: Žádní")
        
        customers = relationships.get("customers", [])
        if customers:
            report.append("Zákazníci:")
            for customer in customers:
                report.append(f"- {customer}")
        else:
            report.append("Zákazníci: Žádní")
        
        ownership = relationships.get("ownership", [])
        if ownership:
            report.append("Vlastnické vztahy:")
            for rel in ownership:
                report.append(f"- {rel}")
        
        report.append("")
    
    return "\n".join(report)


async def main():
    """Hlavní funkce pro testování workflow."""
    print("=== Testovací skript pro analýzu společnosti ===")
    
    while True:
        user_input = input("\nZadejte dotaz (nebo 'konec' pro ukončení): ")
        if user_input.lower() in ["konec", "exit", "quit", "q"]:
            break
        
        state = await test_analyze_company(user_input)
        
        print("\n=== Stav workflow ===")
        print(format_company_report(state))
        
        show_details = input("\nZobrazit detailní JSON data? (a/n): ")
        if show_details.lower() in ["a", "ano", "y", "yes"]:
            print("\n=== Detailní data ===")
            print(state)


if __name__ == "__main__":
    asyncio.run(main())