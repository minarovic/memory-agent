# Hybrid Workflow Component Documentation

## Základní informace
- **Status:** V PROCESU
- **Popis:** Hybridní implementace workflow s využitím LangGraph pro celkový tok a React agentů pro komplexní uzly. Tato komponenta rozšiřuje základní LangGraph workflow o specializované React agenty, kteří jsou schopni řešit složitější úlohy vyžadující kombinaci nástrojů, rozhodování a plánování kroků při analýze společností.
- **Závislosti:**
  - **Externí knihovny:**
    - `langchain.chat_models`: Pro inicializaci chat modelů
    - `langchain_core.messages`: Pro typování zpráv v konverzaci
    - `langchain_core.output_parsers`: Pro zpracování výstupů
    - `langchain_core.prompts`: Pro definici promptů
    - `langchain_core.tools`: Pro implementaci nástrojů pro agenty
    - `langchain_core.pydantic_v1`: Pro strukturované datové modely
    - `langgraph.graph`: Pro definici stavového grafu
    - `langgraph.prebuilt`: Pro použití předpřipravených agentů (create_react_agent)
  - **Interní komponenty:**
    - `memory_agent.analyzer`: Pro analýzu dotazů
    - `memory_agent.tools`: Pro nástroje přístupu k API (Sayari, Supabase)
    - `memory_agent.state`: (nepřímo) Pro typy stavu grafu

- **Použití v:**
  - Rozšíření základního workflow pro komplexní scénáře
  - Zpracování analýz více společností
  - Iterativní sběr informací s využitím agentů

## API

### `create_data_gathering_agent`

- **Signature:**
  ```python
  def create_data_gathering_agent(
      llm: Optional[Any] = None,
      tools: List[BaseTool] = None
  ) -> Tuple[Any, List[BaseTool]]
  ```

- **Popis:** Vytváří React agenta specializovaného na sběr dat o společnostech. Agent je schopen iterativně používat dostupné nástroje pro získávání dat z různých zdrojů a jejich analýzu.

- **Parametry:**
  - `llm` (Optional[Any]): Instance LLM modelu, který bude agent používat. Pokud není specifikován, použije se výchozí Claude model.
  - `tools` (List[BaseTool]): Seznam nástrojů dostupných pro agenta. Pokud není specifikován, použijí se standardní nástroje pro práci s API (Sayari a Supabase).

- **Návratová hodnota:**
  - `Tuple[Any, List[BaseTool]]`: Dvojice obsahující React agenta a seznam nástrojů, které používá.

- **Zpracování chyb:**
  - Logování chyb při inicializaci agenta
  - Ošetření výjimek při volání nástrojů

### `gather_company_data_node`

- **Signature:**
  ```python
  async def gather_company_data_node(state: Any, config: Any) -> Dict[str, Any]:
  ```

- **Popis:** Uzel grafu pro dávkové zpracování více společností pomocí React agenta. Tento uzel přebírá kontrolu nad workflow, když je potřeba zpracovat více společností najednou nebo provést komplexní analýzu vyžadující iterativní rozhodování.

- **Parametry:**
  - `state` (Any): Současný stav workflow, obsahující historii zpráv a analýzu dotazu
  - `config` (Any): Konfigurace běhu s nastavením modelu a dalšími parametry

- **Návratová hodnota:**
  - `Dict[str, Any]`: Aktualizovaná část stavu obsahující výsledky sběru dat o společnostech 

- **Zpracování chyb:**
  - Zachycení výjimek při selhání agenta
  - Logování průběhu zpracování
  - Ošetření situací, kdy agent nemůže získat potřebná data

## Historie změn

### v0.5 (15.4.2025) - Základní struktura

- **Popis změny:** Vytvoření základní struktury souboru s importy a komentáři
- **Důvod změny:** Příprava na implementaci React agentů v rámci LangGraph workflow
- **Nový kód:**
  ```python
  """
  Hybridní implementace workflow s využitím LangGraph pro celkový tok a React agentů pro komplexní uzly.

  Tento modul implementuje workflow pro analýzu společností, kde:
  1. Celkový tok dat je řízen LangGraphem
  2. Komplexní operace jsou delegovány na specializované React agenty
  3. Jednodušší operace jsou implementovány jako jednoduché funkce/LCEL řetězce
  """

  import logging
  import asyncio
  from typing import Dict, List, Literal, Optional, TypedDict, Any, Union, Tuple
  import json
  import uuid

  from langchain.chat_models import init_chat_model
  from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
  from langchain_core.output_parsers import StrOutputParser
  from langchain_core.prompts import ChatPromptTemplate
  from langchain_core.tools import BaseTool, tool
  from langchain_core.pydantic_v1 import BaseModel, Field

  from langgraph.graph import StateGraph, END
  from langgraph.prebuilt import create_react_agent

  from memory_agent.analyzer import analyze_query, AnalysisResult
  from memory_agent.tools import SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool

  logger = logging.getLogger(__name__)

  # BLOKOVÁNO(C1-C2): React agent pro komplexní scénáře čeká na dokončení implementace LangGraph workflow (B1-B5)
  ```

## Vyzkoušené přístupy

### 1. Architektura pro komplexní operace

- ✅ **Hybridní přístup s React agentem v LangGraph**
  - **Výhody:** Kombinuje strukturovanost LangGraph s flexibilitou React agentů
  - **Použití:** Agent řeší komplexní úlohy v rámci workflow jako specializovaný uzel

- ❌ **Samostatný React agent mimo LangGraph workflow**
  - **Proč nefunguje:** Ztráta výhod stavového managementu LangGraph
  - **Omezení:** Složitá integrace výsledků zpět do workflow, duplikace kódu

- ❌ **Čistě stavový automat v LangGraph bez agentů**
  - **Proč nefunguje:** Nedostatečná flexibilita pro komplexní rozhodování
  - **Omezení:** Nadměrná složitost grafu, obtížná údržba logiky

### 2. Integrace React agentů

- ✅ **langgraph.prebuilt.create_react_agent**
  - **Výhody:** Oficiální implementace React agentů v LangGraph
  - **Použití:** `agent = create_react_agent(llm, tools, system_prompt)`

- ❌ **Vlastní implementace ReAct logiky**
  - **Proč nefunguje:** Zbytečná reimplementace funkcionality
  - **Omezení:** Chybí optimalizace a funkčnost oficiální implementace

### 3. Předávání dat mezi LangGraph a React agentem

- ✅ **Přímé předání stavu jako kontextu agentu**
  - **Výhody:** Jednoduchá implementace, přehledný kód
  - **Použití:** Extrakce relevantních dat ze stavu do kontextového promptu agenta

- ❌ **Serializace/deserializace celého stavu**
  - **Proč nefunguje:** Neefektivní, přenáší zbytečně velké množství dat
  - **Omezení:** Zbytečná režie, riziko překročení limitů kontextu

## Známé problémy

### 1. Integrace výsledků agenta

- **Problém:** React agent může generovat nekonzistentní formát výsledků 
- **Řešení:** Implementace normalizační vrstvy pro zpracování výstupu agenta

### 2. Limity kontextu

- **Problém:** Při analýze velkého množství společností může dojít k překročení kontextového limitu modelu
- **Plánované vylepšení:** Implementace průběžného ukládání mezivýsledků a zpracování po částech

### 3. Kontrola nad průběhem

- **Problém:** React agent pracuje jako "black box" s omezenou možností řízení průběhu
- **Plánované vylepšení:** Implementace mechanismů pro průběžné sledování a případné přerušení dlouhých procesů

### 4. Plánovaná vylepšení

- Implementace `create_data_gathering_agent` funkce pro specializovaného agenta
- Implementace `gather_company_data_node` uzlu pro integraci agenta do workflow
- Přidání podpory pro paralelní sběr dat o více společnostech
- Vytvoření specializovaných nástrojů pro agenty
- Implementace systému meziukládání výsledků pro efektivní práci s kontextem

---

*Poslední aktualizace: 19.4.2025*
