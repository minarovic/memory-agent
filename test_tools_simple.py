#!/usr/bin/env python3
"""
Jednoduchý samostatný testovací skript pro testování volání API.
Tento skript používá standardní knihovnu urllib místo httpx.
"""

import asyncio
import json
import argparse
import logging
import urllib.request
import urllib.error
import urllib.parse
from typing import Dict, Any, List, Optional

# Nastavení loggeru pro lepší informace
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("test_tools_simple")

# Definice základních URL pro API podle n8n workflow
SAYARI_API_URL = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/sayari-simulator"
SUPABASE_API_URL = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/get-supplier-data"


async def fetch_url(url: str) -> Dict[str, Any]:
    """Pomocná funkce pro volání REST API pomocí urllib."""
    logger.info(f"Volání API: {url}")
    
    try:
        with urllib.request.urlopen(url) as response:
            data = response.read().decode('utf-8')
            return json.loads(data)
    except urllib.error.HTTPError as e:
        logger.error(f"HTTP chyba: {e.code}")
        return {"error": f"HTTP chyba {e.code}"}
    except urllib.error.URLError as e:
        logger.error(f"URL chyba: {str(e.reason)}")
        return {"error": str(e.reason)}
    except Exception as e:
        logger.error(f"Chyba při volání API: {str(e)}")
        return {"error": str(e)}


async def test_sayari_api(company_name: str) -> Dict[str, Any]:
    """Testuje volání Sayari API pro získání informací o společnosti."""
    logger.info(f"Testování Sayari API pro společnost: {company_name}")
    
    try:
        # Sestavení URL pro vyhledávání entity
        encoded_company = urllib.parse.quote(company_name)
        search_url = f"{SAYARI_API_URL}/search/entity?q={encoded_company}"
        
        # Volání API
        data = await fetch_url(search_url)
        
        if "error" in data:
            return {"error": data["error"], "company": company_name}
        
        logger.info(f"Úspěšně získána data z Sayari API")
        
        # Inicializujeme výsledek s výchozími hodnotami
        result = {
            "company": company_name,
            "external_data": {
                "has_results": False,
                "entities": []
            },
            "entity_id": None,
            "risk_analysis": {
                "sanctions_status": "Žádné aktivní sankce nenalezeny",
                "pep_connections": [],
                "compliance_issues": [],
                "risk_score": "0",
                "risk_factors": []
            }
        }
        
        # Kontrola, zda data obsahují pole "data" a zda toto pole není prázdné
        if "data" in data and isinstance(data["data"], list):
            # Pokud data existují, nastavíme has_results na True
            result["external_data"]["has_results"] = len(data["data"]) > 0
            
            # Pokud existují entity v seznamu data, zpracujeme první z nich
            if len(data["data"]) > 0:
                entity_data = data["data"][0]  # Bereme první entitu ze seznamu
                
                # Extrakce ID entity
                result["entity_id"] = entity_data.get("id")
                
                # Přidání entity do seznamu entit
                result["external_data"]["entities"].append({
                    "id": entity_data.get("id", ""),
                    "name": entity_data.get("label", ""),
                    "type": entity_data.get("type", "Company"),
                    "risk_score": entity_data.get("risk_score", "0")
                })
                
                # Doplnění rizikových dat
                if entity_data.get("risk_score"):
                    result["risk_analysis"]["risk_score"] = entity_data["risk_score"]
                
                if entity_data.get("sanctions_status"):
                    result["risk_analysis"]["sanctions_status"] = entity_data["sanctions_status"]
                
                if entity_data.get("risk_factors") and isinstance(entity_data["risk_factors"], dict):
                    result["risk_analysis"]["risk_factors"] = list(entity_data["risk_factors"].keys())
        
        return result
    except Exception as e:
        logger.error(f"Chyba při volání Sayari API: {str(e)}")
        return {"error": str(e), "company": company_name}


async def test_internal_data(company_name: str) -> Dict[str, Any]:
    """Testuje volání API pro získání interních dat o společnosti."""
    logger.info(f"Testování interních dat pro společnost: {company_name}")
    
    try:
        # Sestavení URL pro získání dat o dodavateli
        encoded_company = urllib.parse.quote(company_name)
        url = f"{SUPABASE_API_URL}?name={encoded_company}"
        
        # Volání API
        data = await fetch_url(url)
        
        if "error" in data:
            return {"error": data["error"], "company": company_name}
        
        logger.info(f"Úspěšně získána interní data")
        
        # Extrakce dat ze supplier_info
        supplier_info = data.get("supplier_info", {})
        
        # Extrakce tier klasifikace
        tier_classification = supplier_info.get("primary_tier", "Neurčeno")
        
        # Extrakce HS kódů
        hs_codes = []
        if "hs_code_matches" in supplier_info and isinstance(supplier_info["hs_code_matches"], list):
            hs_codes = [match.get("hsCode", "") for match in supplier_info["hs_code_matches"] if match.get("hsCode")]
        
        # Extrakce obchodních aktivit
        business_activities = []
        if "identified_activities" in supplier_info and isinstance(supplier_info["identified_activities"], list):
            business_activities = [activity.get("activity", "") for activity in supplier_info["identified_activities"] if activity.get("activity")]
        
        # Strukturování výstupu
        return {
            "company": company_name,
            "company_profile": {
                "tier_classification": tier_classification,
                "hs_codes": hs_codes,
                "business_activities": business_activities,
                "geographic_presence": []
            }
        }
    except Exception as e:
        logger.error(f"Chyba při získávání interních dat: {str(e)}")
        return {"error": str(e), "company": company_name}


async def test_relationships(entity_id: str) -> Dict[str, Any]:
    """Testuje volání API pro získání vztahů entity."""
    logger.info(f"Testování vztahů pro entitu: {entity_id}")
    
    if not entity_id:
        logger.warning("Prázdné ID entity - nelze získat vztahy")
        return {
            "has_relationships": False,
            "relationships": {
                "suppliers": [],
                "customers": [],
                "ownership": [],
                "key_relationships": []
            },
            "visualization": {"nodes": [], "links": []}
        }
    
    try:
        # Sestavení URL pro získání vztahů
        url = f"{SAYARI_API_URL}/entity/{entity_id}/relationships"
        
        # Volání API
        data = await fetch_url(url)
        
        if "error" in data:
            return {
                "error": data["error"],
                "has_relationships": False,
                "relationships": {"suppliers": [], "customers": [], "ownership": [], "key_relationships": []},
                "visualization": {"nodes": [], "links": []}
            }
        
        logger.info(f"Úspěšně získána data o vztazích")
        
        # Kategorizace vztahů podle typu
        suppliers = []
        customers = []
        ownership = []
        
        # Zpracování vztahů
        relationships = data.get("relationships", [])
        for rel in relationships:
            rel_type = rel.get("type", "")
            source_label = rel.get("source", {}).get("label", "")
            target_label = rel.get("target", {}).get("label", "")
            
            if rel_type in ["has_supplier", "supplies_to"]:
                if source_label and rel_type == "has_supplier":
                    suppliers.append(source_label)
                if target_label and rel_type == "supplies_to":
                    customers.append(target_label)
            elif rel_type in ["has_subsidiary", "subsidiary_of", "has_shareholder", "shareholder_of"]:
                if source_label and target_label:
                    ownership.append(f"{source_label} -> {target_label} ({rel_type})")
        
        # Strukturování výstupu
        return {
            "has_relationships": bool(relationships),
            "relationships": {
                "suppliers": list(set(suppliers)),
                "customers": list(set(customers)),
                "ownership": ownership,
                "key_relationships": []
            },
            "visualization": {
                "nodes": [],  # Pro jednoduchost vynecháváme vizualizační data
                "links": []
            }
        }
    except Exception as e:
        logger.error(f"Chyba při získávání vztahů: {str(e)}")
        return {
            "error": str(e),
            "has_relationships": False,
            "relationships": {"suppliers": [], "customers": [], "ownership": [], "key_relationships": []},
            "visualization": {"nodes": [], "links": []}
        }


async def analyze_company(company_name: str) -> Dict[str, Any]:
    """Analyzuje společnost - od získání dat až po vztahy, vrací strukturovaná data."""
    logger.info(f"Analýza společnosti: {company_name}")
    
    # 1. Získání dat o společnosti z Sayari API
    company_data = await test_sayari_api(company_name)
    
    # 2. Získání interních dat o společnosti
    internal_data = await test_internal_data(company_name)
    
    # 3. Získání vztahů pouze pokud máme ID entity
    entity_id = company_data.get("entity_id")
    relationships_data = None
    if entity_id:
        relationships_data = await test_relationships(entity_id)
    else:
        relationships_data = {
            "has_relationships": False,
            "relationships": {"suppliers": [], "customers": [], "ownership": [], "key_relationships": []},
            "visualization": {"nodes": [], "links": []}
        }
    
    # 4. Kombinace všech dat do jednoho objektu
    result = {
        "company": company_name,
        "companies": [company_name],
        "analysis_type": "risk_comparison",
        "external_data": company_data.get("external_data", {}),
        "risk_analysis": company_data.get("risk_analysis", {}),
        "internal_data": internal_data.get("company_profile", {}),
        "relationships": relationships_data
    }
    
    return result


async def test_full_flow(company_name: str) -> None:
    """Testuje celý tok dat - od získání dat společnosti až po vztahy."""
    logger.info(f"=== Testování celého toku dat pro: {company_name} ===")
    
    # Krok 1: Získání dat o společnosti z Sayari API
    company_data = await test_sayari_api(company_name)
    print("\n=== Data o společnosti ===")
    print(json.dumps(company_data, indent=2, ensure_ascii=False))
    
    # Krok 2: Získání interních dat
    internal_data = await test_internal_data(company_name)
    print("\n=== Interní data o společnosti ===")
    print(json.dumps(internal_data, indent=2, ensure_ascii=False))
    
    # Krok 3: Získání vztahů (pouze pokud máme ID entity)
    entity_id = company_data.get("entity_id")
    if entity_id:
        relationships_data = await test_relationships(entity_id)
        print("\n=== Vztahy společnosti ===")
        print(json.dumps(relationships_data, indent=2, ensure_ascii=False))
    else:
        print("\n=== Nelze získat vztahy - chybí ID entity ===")


def format_company_report(result: Dict[str, Any]) -> str:
    """Formátuje výsledky analýzy do čitelné zprávy."""
    company = result.get("company", "Neznámá společnost")
    
    report = [
        f"# Analýza společnosti: {company}",
        f"Typ analýzy: {result.get('analysis_type', 'general')}",
        "",
    ]
    
    # Přidání dat o společnosti
    external_data = result.get("external_data", {})
    risk_analysis = result.get("risk_analysis", {})
    
    if external_data or risk_analysis:
        report.append("## Externí data")
        
        # Základní informace
        entity_id = result.get("entity_id", "Neznámé ID")
        report.append(f"ID entity: {entity_id}")
        
        # Riziková analýza
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
    internal_data = result.get("internal_data", {})
    if internal_data:
        report.append("## Interní data")
        
        report.append(f"Tier klasifikace: {internal_data.get('tier_classification', 'Neurčeno')}")
        
        hs_codes = internal_data.get("hs_codes", [])
        if hs_codes:
            report.append("HS kódy:")
            for code in hs_codes:
                report.append(f"- {code}")
        else:
            report.append("HS kódy: Žádné")
        
        activities = internal_data.get("business_activities", [])
        if activities:
            report.append("Obchodní aktivity:")
            for activity in activities:
                report.append(f"- {activity}")
        else:
            report.append("Obchodní aktivity: Žádné")
        
        report.append("")
    
    # Přidání vztahů
    relationships_data = result.get("relationships", {})
    if relationships_data and relationships_data.get("has_relationships"):
        report.append("## Vztahy")
        
        relationships = relationships_data.get("relationships", {})
        
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


async def test_combined_analysis(company_name: str) -> None:
    """Testuje kombinovanou analýzu společnosti s formátovaným výstupem."""
    logger.info(f"=== Kombinovaná analýza pro: {company_name} ===")
    
    # Získání všech dat v jednom kroku
    result = await analyze_company(company_name)
    
    # Výpis formátované zprávy
    print("\n=== Formátovaná zpráva ===")
    print(format_company_report(result))
    
    # Výpis kompletních JSON dat
    print("\n=== Kompletní JSON data ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """Hlavní funkce pro spuštění testů."""
    parser = argparse.ArgumentParser(description="Testování nástrojů pro získávání dat o společnostech.")
    parser.add_argument("--company", type=str, default="Apple Inc", help="Jméno společnosti pro testování")
    parser.add_argument("--entity-id", type=str, help="ID entity pro přímé testování vztahů (volitelné)")
    parser.add_argument("--tool", type=str, choices=["sayari", "internal", "relationships", "all", "combined"], 
                        default="all", help="Který nástroj testovat")
    
    args = parser.parse_args()
    
    if args.tool == "sayari":
        # Testování pouze Sayari API Tool
        result = asyncio.run(test_sayari_api(args.company))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.tool == "internal":
        # Testování pouze nástroje pro interní data
        result = asyncio.run(test_internal_data(args.company))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.tool == "relationships":
        # Testování pouze nástroje pro vztahy
        entity_id = args.entity_id
        if not entity_id:
            print("Pro testování vztahů je potřeba zadat --entity-id")
            return
        
        result = asyncio.run(test_relationships(entity_id))
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.tool == "combined":
        # Testování kombinované analýzy
        asyncio.run(test_combined_analysis(args.company))
    
    else:  # "all"
        # Testování celého toku
        asyncio.run(test_full_flow(args.company))


if __name__ == "__main__":
    main()