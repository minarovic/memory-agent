#!/usr/bin/env python3
"""
Jednoduchý testovací skript pro testování nástrojů v izolaci.
Testuje jednotlivé komponenty (SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool)
bez nutnosti spouštět celý workflow.
"""

import asyncio
import json
import argparse
import logging
import sys
import os
from typing import Dict, Any

# Přidání cesty k balíčku, aby mohl být importován
sys.path.append(os.path.join(os.path.dirname(__file__), "."))
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from memory_agent.tools import SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool

# Nastavení loggeru pro lepší informace
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("test_tools_functional")


async def test_sayari_api_tool(company_name: str) -> Dict[str, Any]:
    """Testuje SayariApiTool s daným jménem společnosti."""
    logger.info(f"Testování SayariApiTool pro společnost: {company_name}")
    
    tool = SayariApiTool()
    try:
        result = await tool._arun(company_name)
        logger.info(f"Úspěšně získána data z Sayari API pro: {company_name}")
        return result
    except Exception as e:
        logger.error(f"Chyba při volání Sayari API: {str(e)}")
        return {"error": str(e)}


async def test_internal_data_tool(company_name: str) -> Dict[str, Any]:
    """Testuje SupabaseInternalDataTool s daným jménem společnosti."""
    logger.info(f"Testování SupabaseInternalDataTool pro společnost: {company_name}")
    
    tool = SupabaseInternalDataTool()
    try:
        result = await tool._arun(company_name)
        logger.info(f"Úspěšně získána interní data pro: {company_name}")
        return result
    except Exception as e:
        logger.error(f"Chyba při získávání interních dat: {str(e)}")
        return {"error": str(e)}


async def test_relationships_tool(entity_id: str) -> Dict[str, Any]:
    """Testuje SayariRelationshipsTool s daným ID entity."""
    logger.info(f"Testování SayariRelationshipsTool pro entitu: {entity_id}")
    
    tool = SayariRelationshipsTool()
    try:
        result = await tool._arun(entity_id)
        logger.info(f"Úspěšně získány vztahy pro entitu: {entity_id}")
        return result
    except Exception as e:
        logger.error(f"Chyba při získávání vztahů: {str(e)}")
        return {"error": str(e)}


async def test_full_flow(company_name: str) -> None:
    """Testuje celý tok dat - od získání dat společnosti až po vztahy."""
    logger.info(f"=== Testování celého toku dat pro: {company_name} ===")
    
    # Krok 1: Získání dat o společnosti z Sayari API
    company_data = await test_sayari_api_tool(company_name)
    print("\n=== Data o společnosti ===")
    print(json.dumps(company_data, indent=2, ensure_ascii=False))
    
    # Krok 2: Získání interních dat
    internal_data = await test_internal_data_tool(company_name)
    print("\n=== Interní data o společnosti ===")
    print(json.dumps(internal_data, indent=2, ensure_ascii=False))
    
    # Krok 3: Získání vztahů (pouze pokud máme ID entity)
    entity_id = company_data.get("entity_id")
    if entity_id:
        relationships_data = await test_relationships_tool(entity_id)
        print("\n=== Vztahy společnosti ===")
        print(json.dumps(relationships_data, indent=2, ensure_ascii=False))
    else:
        print("\n=== Nelze získat vztahy - chybí ID entity ===")


def main():
    """Hlavní funkce pro spuštění testů."""
    parser = argparse.ArgumentParser(description="Testování nástrojů pro získávání dat o společnostech.")
    parser.add_argument("--company", type=str, default="Apple Inc", help="Jméno společnosti pro testování")
    parser.add_argument("--entity-id", type=str, help="ID entity pro přímé testování vztahů (volitelné)")
    parser.add_argument("--tool", type=str, choices=["sayari", "internal", "relationships", "all"], 
                        default="all", help="Který nástroj testovat")
    
    args = parser.parse_args()
    
    if args.tool == "sayari":
        # Testování pouze Sayari API Tool
        result = asyncio.run(test_sayari_api_tool(args.company))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.tool == "internal":
        # Testování pouze nástroje pro interní data
        result = asyncio.run(test_internal_data_tool(args.company))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.tool == "relationships":
        # Testování pouze nástroje pro vztahy
        entity_id = args.entity_id
        if not entity_id:
            print("Pro testování vztahů je potřeba zadat --entity-id")
            return
        
        result = asyncio.run(test_relationships_tool(entity_id))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:  # "all"
        # Testování celého toku
        asyncio.run(test_full_flow(args.company))


if __name__ == "__main__":
    main()