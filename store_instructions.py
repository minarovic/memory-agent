"""Skript pro uložení pokynů do paměti pro další instanci."""

import asyncio
import os
import sys

# Přidáme cestu k balíčku
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from memory_agent.tools import upsert_memory
from langgraph.store.base import BaseStore
from langgraph.store.postgres import PostgresSaver

async def store_instructions():
    """Uloží instrukce do paměti pro další instanci."""
    # Inicializace úložiště paměti (pomocí PostgresSaver pro připojení k běžícímu kontejneru)
    store = PostgresSaver(uri="postgresql://postgres:postgres@localhost:5433/postgres")
    
    # Obsah pokynů
    instructions = """
    Důležité pokyny pro implementaci v memory-agent:
    
    1) Vždy pracuj v rámci existující struktury
    2) Přidávej kód přímo do adresáře /memory-agent/src/memory_agent/
    3) Nevytvářej paralelní adresářovou strukturu
    4) Nové funkce integruj do existujících modulů
    5) Neupravuj soubor langgraph.json
    6) Rozšiřuj existující StateGraph v graph.py
    7) Dodržuj konvence kódu - české docstringy, typové anotace, ošetření chyb
    
    Plán implementace analyzátoru společností:
    1. Vytvoř analyzer.py v adresáři memory_agent
    2. Implementuj funkci analyze_query pro identifikaci společností a typu analýzy
    3. Rozšiř state.py o pole pro výsledky analýzy
    4. Přidej uzel analyze_company_input do graph.py
    5. Uprav route_message pro detekci dotazů o společnostech
    6. Propoj nový uzel s existujícím grafem
    """
    
    context = "Tyto pokyny jsou určeny pro zapamatování správného přístupu k implementaci nových funkcí."
    
    # Vytvoření konfigurace
    config = {'configurable': {'user_id': 'default'}}
    
    # Uložení do paměti
    try:
        result = await upsert_memory(
            content=instructions,
            context=context,
            config=config,
            store=store
        )
        print(f"Úspěšně uloženy instrukce do paměti: {result}")
    except Exception as e:
        print(f"Chyba při ukládání instrukcí: {str(e)}")

if __name__ == "__main__":
    asyncio.run(store_instructions())