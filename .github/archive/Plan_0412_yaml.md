# Plán Implementace: Migrace PoC z n8n do LangChain/LangGraph

```yaml
název: Plán Implementace - Migrace PoC z n8n do LangChain/LangGraph
datum: 2025-04-15
verze: 1.2
cíl: >
  Naučit se LangChain/LangGraph replikací funkčnosti n8n PoC workflow pro sledování 
  dodavatelského řetězce v automotive s využitím simulovaných dat.
  Připravit základ pro budoucí produkční řešení v Databricks.

koncept_architektury:
  popis: >
    Cílová architektura je hybridní, kombinující LangGraph pro orchestraci a React Agenty 
    pro specifické úkoly (zejména sběr dat o více společnostech). 
    LCEL se používá pro jednodušší kroky.
  
  langgraph_workflow:
    popis: Hlavní workflow řízené pomocí LangGraph se stavovým grafem.
  
  react_agent:
    popis: Specializovaný agent pro sběr dat o více společnostech.
  
  lcel_chains:
    popis: Použití pro analýzu vstupu a generování finální odpovědi.
  
  simulovaná_data:
    popis: Projekt využívá simulovaná data pro Sayari API (přes Supabase funkci) a interní data (z SQL souboru).
    zdroje:
      - Sayari Simulator: sayari-simulator/index.ts a sayari-simulator/mock_data/
      - Interní data: sayari-simulator/mock_data/supplier_analysis_internal.sql

fáze_implementace:
  fáze_1:
    název: Základní komponenty a analýza vstupu
    priorita: Vysoká
    kroky:
      - status: dokončeno
        název: Implementace `analyzer.py` (LCEL řetězec)
        popis: >
          Vytvoření LCEL řetězce pro analýzu uživatelského dotazu, extrakci firem 
          a typu analýzy (kombinuje logiku několika n8n uzlů).
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/analyzer.py
        dokončeno_dne: 2025-04-14
      
      - status: dokončeno
        název: Unit testy pro `analyzer.py`
        popis: >
          Vytvoření a rozšíření unit testů pro ověření správné funkčnosti analyzátoru 
          s různými vstupy (včetně mockování LLM volání).
        reference: /Users/marekminarovic/claude-code/memory-agent/tests/unit_tests/test_analyzer.py
        pokrok: 100%
      
      - status: dokončeno
        název: Definice stavu grafu (`state.py`)
        popis: Vytvoření `TypedDict` pro reprezentaci stavu LangGraph workflow.
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/state.py
        dokončeno_dne: 2025-04-14
      
      - status: dokončeno
        název: Implementace nástrojů pro simulovaná API (`tools.py`)
        popis: >
          Vytvoření `SayariApiTool`, `SupabaseInternalDataTool`, `SayariRelationshipsTool` 
          jako `BaseTool` podtříd pro interakci se simulovanými daty.
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/tools.py
        dokončeno_dne: 2025-04-15
      
      - status: v_procesu
        název: Unit testy pro `tools.py`
        popis: Vytvoření unit testů pro ověření správné funkčnosti nástrojů (volání simulovaných API).
        reference: /Users/marekminarovic/claude-code/memory-agent/tests/unit_tests/test_tools.py
        pokrok: 50%
  
  fáze_2:
    název: Implementace LangGraph Workflow (Základní tok)
    priorita: Vysoká
    kroky:
      - status: v_procesu
        název: Implementace uzlu `analyze_company_input`
        popis: Vytvoření LangGraph uzlu volajícího `analyzer.analyze_query`.
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/graph.py
        pokrok: 90%
      
      - status: v_procesu
        název: Implementace uzlů pro sběr dat (jedna společnost)
        popis: >
          Vytvoření uzlů `fetch_company_data`, `fetch_internal_data`, `fetch_relationships` 
          volajících příslušné nástroje.
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/graph.py
        pokrok: 70%
      
      - status: plánováno
        název: Implementace uzlu `call_model` (LCEL řetězec)
        popis: >
          Vytvoření uzlu s LCEL řetězcem, který vezme data ze stavu 
          a vygeneruje finální odpověď pomocí LLM.
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/graph.py
        návodka: /Users/marekminarovic/claude-code/memory-agent/.github/copilot-LCEL-Chain-instructions.md
      
      - status: v_procesu
        název: Definice základních hran grafu
        popis: >
          Propojení uzlů pro základní sekvenční tok: 
          analyze -> fetch_company -> fetch_internal -> fetch_relationships -> call_model -> END.
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/graph.py
        pokrok: 80%
      
      - status: plánováno
        název: Implementace podmíněných hran
        popis: >
          Přidání routovací funkce a hran pro větvení 
          (např. přeskočení sběru dat, pokud `is_company_analysis` je False).
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/graph.py
  
  fáze_3:
    název: Implementace React Agenta (Zpracování více společností)
    priorita: Střední
    popis: Tato fáze implementuje pokročilejší scénář pro porovnání více společností.
    kroky:
      - status: plánováno
        název: Vytvoření React Agenta
        popis: >
          Použití `create_react_agent` s nástroji pro sběr dat 
          (fetch_company_data, fetch_internal_data, fetch_relationships).
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/hybrid_workflow.py
        návodka: /Users/marekminarovic/claude-code/memory-agent/.github/langchain-documentation/react_agent.md
      
      - status: plánováno
        název: Implementace uzlu `gather_company_data_node`
        popis: >
          Vytvoření LangGraph uzlu, který spustí React agenta pro sběr dat 
          o všech společnostech identifikovaných v `analyzer.py`.
        reference: /Users/marekminarovic/claude-code/memory-agent/src/memory_agent/hybrid_workflow.py
      
      - status: plánováno
        název: Integrace do hlavního grafu
        popis: >
          Úprava podmíněných hran v hlavním grafu (`graph.py` nebo `hybrid_workflow.py`) tak, 
          aby se volal `gather_company_data_node` pokud `len(state.company_analysis['companies']) > 1`.
      
      - status: plánováno
        název: Testování React Agenta
        popis: Vytvoření testů specificky pro scénář s více společnostmi.
  
  fáze_4:
    název: Testování a Dokončení PoC
    priorita: Vysoká
    kroky:
      - status: plánováno
        název: Integrační testy
        popis: >
          Vytvoření end-to-end testů pro celé workflow 
          (pro scénář s jednou i více společnostmi) s mockovanými API.
        reference: /Users/marekminarovic/claude-code/memory-agent/tests/integration_tests/test_graph.py
      
      - status: plánováno
        název: Ladění promptů
        popis: Revize a případná optimalizace promptů v `analyzer.py` a pro uzel `call_model`.
      
      - status: plánováno
        název: Revize zpracování chyb
        popis: Zajištění robustního zpracování chyb v jednotlivých uzlech a nástrojích.
  
  fáze_5:
    název: Dokumentace a Příprava na další kroky
    priorita: Střední
    kroky:
      - status: v_procesu
        název: Aktualizace `README.md`
        popis: Doplnění sekcí "Jak začít" a "Použití" v hlavním README.
        pokrok: 50%
      
      - status: plánováno
        název: Vytvoření diagramu workflow
        popis: Vizualizace finálního LangGraph workflow.
      
      - status: plánováno
        název: Zhodnocení PoC a další kroky
        popis: >
          Shrnutí poznatků z migrace a návrh dalších kroků pro produkční verzi v Databricks
          (řešení stavovosti, reálná API, caching, atd.).

dalsi_kroky:
  popis: Následující kroky jsou mimo rámec tohoto PoC a týkají se budoucího produkčního řešení.
  
  optimalizace:
    název: Optimalizace výkonu
    kroky:
      - Implementace cachingu pro API volání
      - Optimalizace velikosti přenášených dat
      - Paralelní zpracování API volání (asyncio)
  
  rozšíření:
    název: Rozšíření funkcionalit
    kroky:
      - Přidání podpory pro nové typy analýz
      - Implementace personalizovaných odpovědí
      - Vektorové úložiště pro historické analýzy (např. Databricks Vector Search)
      - Implementace reálné paměti agenta
  
  nasazeni_databricks:
    název: Nasazení v Databricks
    kroky:
      - Implementace řešení pro stavovost (např. PostgresSaver)
      - Integrace s reálnými API
      - Integrace s MLflow pro monitoring
      - Integrace s Databricks AI Gateway

reference:
  dokumenty:
    - název: README.md
      popis: Hlavní popis projektu a jeho cílů.
      cesta: /Users/marekminarovic/claude-code/memory-agent/README.md
    
    - název: LCEL-Chain-instructions.md
      popis: Návod pro implementaci LCEL řetězců.
      cesta: /Users/marekminarovic/claude-code/memory-agent/.github/copilot-LCEL-Chain-instructions.md
    
    - název: documentation_links.md
      popis: Odkazy na externí dokumentaci LangChain/LangGraph.
      cesta: /Users/marekminarovic/claude-code/memory-agent/.github/langchain-documentation/documentation_links.md
    
    - název: react_agent.md
      popis: Příklad použití React Agenta.
      cesta: /Users/marekminarovic/claude-code/memory-agent/.github/langchain-documentation/react_agent.md
    
    - název: n8n_LangChain.md (Archiv)
      popis: Původní mapování migrace z N8N.
      cesta: /Users/marekminarovic/claude-code/memory-agent/.github/archive/n8n-flow/n8n_LangChain.md
    
    - název: Data_ai_agent.json (Archiv)
      popis: Původní n8n workflow.
      cesta: /Users/marekminarovic/claude-code/memory-agent/.github/archive/n8n-flow/Data_ai_agent.json
```

---

Tento plán bude průběžně aktualizován s postupem implementace a novými poznatky.
