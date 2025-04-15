"""Jednoduchý test pro ověření funkčnosti analyzátoru společností."""

import asyncio
import logging
import sys
import os

# Nastavení loggování
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Kopie testovacího kódu analyzátoru
async def analyze_query_test(query: str):
    """Zjednodušená verze analyze_query pro testování."""
    
    # Jednoduchá implementace detekce společností
    company_keywords = [
        'apple', 'microsoft', 'google', 'amazon', 'facebook', 'tesla', 
        'čez', 'škoda', 'komerční banka', 'vodafone', 'o2', 't-mobile',
        'samsung', 'ibm', 'oracle', 'intel', 'amd', 'nvidia', 'cisco'
    ]
    
    # Detekce typu analýzy
    risk_keywords = ['riziko', 'rizika', 'nebezpečí', 'porovnej']
    supplier_keywords = ['dodavatel', 'dodavatelé', 'vztahy', 'dodávky']
    
    # Převod textu na malá písmena pro snadnější vyhledávání
    text = query.lower()
    
    # Vyhledání společností
    companies = []
    for company in company_keywords:
        if company in text:
            companies.append(company.title())  # Převod prvního písmene na velké
    
    # Určení typu analýzy
    if any(kw in text for kw in risk_keywords):
        analysis_type = "risk_comparison"
    elif any(kw in text for kw in supplier_keywords):
        analysis_type = "common_suppliers"
    else:
        analysis_type = "general"
    
    # Určení, zda jde o firemní analýzu a míry jistoty
    is_company_analysis = len(companies) > 0
    confidence = 0.8 if is_company_analysis else 0.0
    
    # Vytvoření výsledku
    return {
        "companies": companies,
        "company": companies[0] if companies else "",
        "analysis_type": analysis_type,
        "query": query,
        "is_company_analysis": is_company_analysis,
        "confidence": confidence
    }

async def test_analyzer():
    """Otestuje analyzátor společností s různými vstupy."""
    
    test_queries = [
        "Potřebuji analyzovat rizika společnosti Apple",
        "Jaké jsou vztahy mezi dodavateli Tesla a Apple?",
        "Porovnej rizika firem Microsoft a Google",
        "Najdi mi informace o IBM",
        "Jaké bude zítra počasí v Praze?",
    ]
    
    print("\n===== TEST ANALYZÁTORU SPOLEČNOSTÍ =====\n")
    
    for query in test_queries:
        print(f"\nDotaz: {query}")
        result = await analyze_query_test(query)
        
        print(f"Společnosti: {result['companies']}")
        print(f"Typ analýzy: {result['analysis_type']}")
        print(f"Je to firemní analýza? {result['is_company_analysis']}")
        print(f"Jistota: {result['confidence']:.2f}")
        print("=" * 50)
    
    print("\nTest dokončen!")

if __name__ == "__main__":
    asyncio.run(test_analyzer())