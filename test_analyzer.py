"""Test pro ověření funkčnosti analyzátoru společností."""

import asyncio
import os
import sys
import logging

# Přidání cesty k modulům
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from memory_agent.analyzer import analyze_query

# Nastavení loggování
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def test_analyzer():
    """Otestuje analyzátor společností s různými vstupy."""
    
    test_queries = [
        "Analyze risks for BOS",
        "What are the common suppliers for Fuyao Group and Hauk?",
        "Compare the risks of MB Tool and Adis Tachov",
        "Find general information about tesa",
        "What's the weather like in Berlin?", # Example of non-company query
        "Tell me about Flidr Plast", # General query
        "Risk analysis for Klippan Safety", # Risk query
        "Suppliers of LyondellBasell", # Suppliers query
    ]
    
    print("\\n===== TEST ANALYZÁTORU SPOLEČNOSTÍ =====\\n")
    
    for query in test_queries:
        print(f"\nDotaz: {query}")
        result = await analyze_query(query)
        
        print(f"Společnosti: {result['companies']}")
        print(f"Typ analýzy: {result['analysis_type']}")
        print(f"Je to firemní analýza? {result['is_company_analysis']}")
        print(f"Jistota: {result['confidence']:.2f}")
        print("=" * 50)
    
    print("\nTest dokončen!")

if __name__ == "__main__":
    asyncio.run(test_analyzer())