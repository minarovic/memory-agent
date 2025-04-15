# Memory Agent: Migrace PoC z n8n do LangChain/LangGraph

[![CI](https://github.com/langchain-ai/memory-agent/actions/workflows/unit-tests.yml/badge.svg)](https://github.com/langchain-ai/memory-agent/actions/workflows/unit-tests.yml)
[![Integration Tests](https://github.com/langchain-ai/memory-agent/actions/workflows/integration-tests.yml/badge.svg)](https://github.com/langchain-ai/memory-agent/actions/workflows/integration-tests.yml)
[![Open in - LangGraph Studio](https://img.shields.io/badge/Open_in-LangGraph_Studio-00324d.svg?logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4NS4zMzMiIGhlaWdodD0iODUuMzMzIiB2ZXJzaW9uPSIxLjAiIHZpZXdCb3g9IjAgMCA2NCA2NCI+PHBhdGggZD0iTTEzIDcuOGMtNi4zIDMuMS03LjEgNi4zLTYuOCAyNS43LjQgMjQuNi4zIDI0LjUgMjUuOSAyNC41QzU3LjUgNTggNTggNTcuNSA1OCAzMi4zIDU4IDcuMSAzLjcgMy4xIDEzIDcuOHoiIGZpbGw9IiMwMDMyNGQiLz48cGF0aCBkPSJNMzIgMGMxNy43IDAgMzIgMTQuMyAzMiAzMnMtMTQuMyAzMi0zMiAzMlMzMiAwIDMyIDB6TTQgMzJjMC0xNS41IDEyLjUtMjggMjgtMjh2NTZjLTE1LjUgMC0yOC0xMi41LTI4LTI4eiIgZmlsbD0iIzAwYTlkYyIvPjxwYXRoIGQ9Ik01NiAzMnYtOC41YzAtNC43LTEuOC05LjEtNC44LTEyLjRsLTIuMS0yLjFjLS42LS42LTEuNS0uNi0yLjEgMC0uNi42LS42IDEuNSAwIDIuMWwyLjEgMi4xYzIuMyAyLjMgMy43IDUuMyAzLjcgOC41VjMyYzAgLjgtLjcgMS41LTEuNSAxLjVzLTEuNS0uNy0xLjUtMS41di04LjNWMTljLS4xLS4xLS4xLS4yLS4yLS4zLTEuMS0xLjktMi42LTMuNS00LjQtNC43bC0xLjktMS4zYy0uNy0uNS0xLjctLjQtMi4yLjNsLTEuOSAxLjNjLTEuOCA4LjktOC45IDE1LjktMTcuOSAxNS45cy0xNi4xLTctMTcuOS0xNS45bC0xLjktMS4zYy0uNS0uOC0xLjUtLjgtMi4yLS4zbC0xLjkgMS4zYy0xLjggMS4yLTMuMyAyLjctNC40IDQuN2wtLjIuM3Y0LjdWNDhjMCAuOC0uNyAxLjUtMS41IDEuNXMtMS41LS4七LTEuNS0xLjVWMzJjMC0xNS41IDEyLjUtMjggMjgtMjhWMEMzNS44IDAgNDggNS44IDU2IDguNXYyMy41eiIgZmlsbD0iIzAwMzI0ZCIvPjwvc3ZnPg==)](https://langchain-ai.github.io/langgraph-studio/)

## 1. Cíl projektu

Tento projekt slouží jako **studijní cvičení a Proof of Concept (PoC)** pro migraci jednoduchého workflow pro analýzu společností z platformy **n8n** do moderního frameworku **LangChain** s využitím **LangGraph** pro orchestraci.

Původní n8n workflow (viz `Data_ai_agent.json`) ověřovalo možnosti spojování dat z různých simulovaných zdrojů. Cílem této implementace je:

*   **Naučit se** pracovat s klíčovými komponentami LangChain a LangGraph (LCEL, Tools, StateGraph, React Agents).
*   **Replikovat** základní funkčnost n8n workflow v Pythonu s využitím LangChain best practices.
*   **Připravit základ** pro budoucí, robustnější produkční řešení, které poběží na platformě **Databricks**.

**Důležité:** Tento projekt aktuálně využívá **simulovaná data** a není určen pro produkční nasazení v současné podobě.

## 2. Původní n8n Workflow a Simulovaná Data

Původní n8n workflow (popsané v `Data_ai_agent.json` a `.github/langchain-documentation/n8n-flow/n8n_LangChain.md`) simulovalo následující kroky:

1.  **Rozpoznání záměru:** Identifikace firmy a typu analýzy.
2.  **Získání externích dat (simulované Sayari API):**
    *   Využívá Supabase edge funkci (`sayari-simulator/index.ts`) pro simulaci odpovědí Sayari API.
    *   Mock data pro simulaci jsou v adresáři `sayari-simulator/mock_data/` (např. `entity_search.json`, `relationships.json`). Sayari API je RESTové a vrací JSON.
3.  **Získání interních dat (simulované):**
    *   Simuluje připojení k interní databázi.
    *   Testovací data jsou definována v `sayari-simulator/mock_data/supplier_analysis_internal.sql`.
4.  **Spojení dat a generování analýzy:** Kombinace dat a využití AI pro výstup.

## 3. Cílová Architektura (LangChain/LangGraph)

Plánovaná architektura v LangChain/LangGraph (viz `Plan_0412.md`) je **hybridní**:

*   **LangGraph:** Orchestruje celkový workflow, spravuje stav (`State`) a řídí tok dat mezi uzly.
*   **React Agent:** Specializovaný agent (`langgraph.prebuilt.create_react_agent`) pro komplexnější úlohy, jako je sběr dat o více společnostech.
*   **LCEL (LangChain Expression Language):** Pro jednodušší kroky, jako je analýza vstupu (`analyzer.py`) a formátování finální odpovědi.
*   **Nástroje (Tools):** Vlastní nástroje (`tools.py`) pro interakci se simulovanými API (Sayari, interní data).

## 4. Aktuální Stav Migrace

*   Implementován analyzátor vstupního dotazu (`analyzer.py`).
*   Vytvořeny základní nástroje pro simulovaná API (`tools.py`).
*   Vytvořena základní struktura LangGraph grafu (`graph.py`) a hybridního workflow (`hybrid_workflow.py`).
*   Probíhá implementace jednotlivých uzlů grafu a jejich propojení.

*(Pro detailní stav viz aktuální [Plán implementace](./.github/langchain-documentation/Plan_0412.md).)*

## 5. Spuštění PoC

Jelikož se jedná o PoC ve vývoji s minimálními externími závislostmi (kromě Python balíčků a případně běžící Supabase instance pro simulaci Sayari API), spuštění je primárně určeno pro lokální vývoj a testování.

1.  **Instalace závislostí:**
    ```bash
    pip install -r requirements.txt
    ```
2.  **Konfigurace:** Vytvořte `.env` soubor (z `.env.example`) a nastavte případné API klíče (např. Anthropic). Pro simulovaná data nejsou externí klíče nutně potřeba.
3.  **Spuštění (příklad):**
    *   Spuštění testů: `make test` (viz `Makefile`)
    *   Spuštění specifického skriptu (např. pro testování grafu - bude doplněno): `python -m memory_agent.graph ...`

## 6. Budoucí Cíle (Produkční řešení v Databricks)

Tento PoC slouží jako základ pro budoucí produkční systém v Databricks. Produkční řešení bude pravděpodobně následovat podobné principy (analýza vstupu -> sběr dat -> syntéza), ale bude využívat reálná API, robustnější zpracování chyb, perzistenci stavu (např. pomocí LangGraph checkpointerů jako `PostgresSaver`) a integraci s nástroji Databricks (např. MLflow pro monitoring, Vector Search, AI Gateway).

## 7. Další dokumentace

*   **Plán implementace:** [.github/langchain-documentation/Plan_0412.md](./.github/langchain-documentation/Plan_0412.md)
*   **Odkazy na externí dokumentaci:** [.github/langchain-documentation/documentation_links.md](./.github/langchain-documentation/documentation_links.md)
*   **Instrukce pro Copilota (LCEL):** [.github/copilot-LCEL-Chain-instructions.md](./.github/copilot-LCEL-Chain-instructions.md)
*   **Příklad React Agenta:** [.github/langchain-documentation/react_agent.md](./.github/langchain-documentation/react_agent.md)
*   **Mapování n8n -> LangChain:** [.github/langchain-documentation/n8n-flow/n8n_LangChain.md](./.github/langchain-documentation/n8n-flow/n8n_LangChain.md)
*   **Původní n8n workflow:** [.github/langchain-documentation/n8n-flow/Data_ai_agent.json](./.github/langchain-documentation/n8n-flow/Data_ai_agent.json) (pro historický kontext)

---
*Tento dokument popisuje cíl a kontext projektu Memory Agent jako PoC migrace z n8n do LangChain/LangGraph.*
