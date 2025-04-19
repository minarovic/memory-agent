# Graph Component Documentation

## Základní informace
- **Status:** V PROCESU
- **Popis:** Hlavní komponenta pro workflow orchestraci v Memory Agent projektu. Implementuje LangGraph workflow pro analýzu společností, který zpracovává uživatelské dotazy, získává data z externích zdrojů a generuje strukturované odpovědi.
- **Závislosti:**
  - **Externí knihovny:**
    - `langchain` (chat_models)
    - `langchain_core` (runnables, output_parsers, prompts, messages)
    - `langgraph` (graph, store)
  - **Interní komponenty:**
    - `memory_agent.analyzer`: Pro analýzu dotazů
    - `memory_agent.tools`: Pro API nástroje (Sayari, Supabase)
    - `memory_agent.state`: Pro definici stavových typů
    - `memory_agent.configuration`: Pro konfiguraci běhu
    - `memory_agent.utils`: Pro pomocné funkce

- **Použití v:**
  - Hlavní workflow Memory Agent aplikace
  - Orchestrace procesu analýzy společností

## API

### `analyze_company_input`

- **Signature:**
  ```python
  async def analyze_company_input(state: State, config: RunnableConfig) -> dict
  ```

- **Popis:** Analyzuje vstup uživatele pro identifikaci zmíněných společností a typu požadované analýzy. Jedná se o vstupní uzel grafu, který zpracovává poslední zprávu uživatele.

- **Parametry:**
  - `state` (State): Současný stav workflow obsahující historii zpráv
  - `config` (RunnableConfig): Konfigurace běhu obsahující model a další nastavení

- **Návratová hodnota:**
  - `dict`: Slovník s klíčem `company_analysis`, který obsahuje výsledek analýzy dotazu (AnalysisResult)

- **Zpracování chyb:**
  - Zachycuje všechny výjimky a loguje je
  - V případě chyby vrací prázdný slovník `{}`
  - Používá standard Python logging pro záznam průběhu a chyb

### `fetch_company_data`

- **Signature:**
  ```python
  async def fetch_company_data(state: State, config: RunnableConfig) -> dict
  ```

- **Popis:** Získává data o společnosti pomocí Sayari API. Tento uzel je volán po analýze vstupu, pokud byl identifikován dotaz na společnost.

- **Parametry:**
  - `state` (State): Současný stav workflow obsahující výsledek analýzy
  - `config` (RunnableConfig): Konfigurace běhu

- **Návratová hodnota:**
  - `dict`: Slovník s klíčem `company_data`, který obsahuje data získaná ze Sayari API

- **Zpracování chyb:**
  - Kontroluje, zda existují potřebná vstupní data ve stavu
  - Zachycuje všechny výjimky a loguje je
  - V případě chyby vrací prázdný slovník `{}`

### `fetch_internal_data`

- **Signature:**
  ```python
  async def fetch_internal_data(state: State, config: RunnableConfig) -> dict
  ```

- **Popis:** Získává interní data o společnosti z Supabase. Uzel je volán po získání základních dat o společnosti.

- **Parametry:**
  - `state` (State): Současný stav workflow obsahující informace o společnosti
  - `config` (RunnableConfig): Konfigurace běhu

- **Návratová hodnota:**
  - `dict`: Slovník s klíčem `internal_data`, který obsahuje interní data o společnosti

- **Zpracování chyb:**
  - Kontroluje, zda existují potřebná vstupní data ve stavu
  - Zachycuje všechny výjimky a loguje je
  - V případě chyby vrací prázdný slovník `{}`

### `fetch_relationships`

- **Signature:**
  ```python
  async def fetch_relationships(state: State, config: RunnableConfig) -> dict
  ```

- **Popis:** Získává vztahy společnosti z Sayari API. Uzel je volán po získání interních dat.

- **Parametry:**
  - `state` (State): Současný stav workflow obsahující ID entity společnosti
  - `config` (RunnableConfig): Konfigurace běhu

- **Návratová hodnota:**
  - `dict`: Slovník s klíčem `relationships_data`, který obsahuje data o vztazích společnosti

- **Zpracování chyb:**
  - Kontroluje přítomnost ID entity ve stavu
  - V případě chybějícího ID vrací `{"relationships_data": None}`
  - Zachycuje všechny výjimky a loguje je

### `generate_response`

- **Signature:**
  ```python
  async def generate_response(state: State, config: RunnableConfig) -> dict
  ```

- **Popis:** Generuje odpověď na základě všech sesbíraných dat. Používá LCEL řetězec pro vytvoření strukturované odpovědi.

- **Parametry:**
  - `state` (State): Současný stav workflow obsahující všechna sesbíraná data
  - `config` (RunnableConfig): Konfigurace běhu s modelem

- **Návratová hodnota:**
  - `dict`: Slovník s klíčem `messages`, který obsahuje aktualizovanou historii zpráv včetně nově vygenerované odpovědi

- **Zpracování chyb:**
  - Zachycuje všechny výjimky a loguje je
  - V případě chyby vrací chybovou zprávu jako AIMessage v historii zpráv

### `store_memory`

- **Signature:**
  ```python
  async def store_memory(state: State, config: RunnableConfig, *, store: BaseStore) -> dict
  ```

- **Popis:** Uloží výsledek analýzy do paměti pomocí `upsert_memory`. Poslední uzel v grafu.

- **Parametry:**
  - `state` (State): Současný stav workflow 
  - `config` (RunnableConfig): Konfigurace běhu
  - `store` (BaseStore): Úložiště pro paměti

- **Návratová hodnota:**
  - `dict`: Prázdný slovník nebo případné aktualizace stavu

- **Zpracování chyb:**
  - Kontroluje, zda existuje analýza společnosti
  - Zachycuje všechny výjimky a loguje je

### Pomocné rozhodovací funkce

#### `should_analyze_companies`

- **Signature:**
  ```python
  def should_analyze_companies(state: State) -> str
  ```

- **Popis:** Rozhoduje, zda je potřeba analyzovat společnosti v dotazu. Aktuálně vždy vrací "analyze".

#### `should_fetch_company_data`

- **Signature:**
  ```python
  def should_fetch_company_data(state: State) -> str
  ```

- **Popis:** Rozhoduje, zda je potřeba získat data o společnosti na základě výsledku analýzy.

#### `should_fetch_relationships`

- **Signature:**
  ```python
  def should_fetch_relationships(state: State) -> str
  ```

- **Popis:** Rozhoduje, zda je potřeba získat vztahy společnosti na základě typu analýzy a dostupnosti ID entity.

### `build_company_analysis_graph`

- **Signature:**
  ```python
  def build_company_analysis_graph() -> StateGraph
  ```

- **Popis:** Vytvoří a sestaví kompletní graf workflow pro analýzu společností pomocí LangGraph.

- **Návratová hodnota:**
  - `StateGraph`: Kompilovaný graf workflow připravený k použití

- **Zpracování chyb:**
  - Zachycuje všechny výjimky a loguje je
  - V případě kritické chyby při sestavení grafu propaguje výjimku dále

## Historie změn

### v0.9 (18.4.2025) - Implementace podmíněných přechodů

- **Popis změny:** Přidání podmíněných přechodů pro optimalizaci zpracování dotazů
- **Důvod změny:** Zvýšení efektivity workflow přeskočením nepotřebných kroků
- **Nový kód:**
  ```python
  def should_fetch_company_data(state: State) -> str:
      """Rozhoduje, zda je potřeba získat data o společnosti."""
      if state.company_analysis and state.company_analysis.get("is_company_analysis", False):
          return "fetch"
      else:
          return "skip"

  # V build_company_analysis_graph
  workflow.add_conditional_edges(
      "fetch_company_data",
      should_fetch_company_data,
      {
          "fetch": "fetch_internal_data",
          "skip": "generate_response"
      }
  )
  ```

### v0.8 (15.4.2025) - Implementace ukládání do paměti

- **Popis změny:** Přidání uzlu pro ukládání výsledků analýzy do paměti
- **Důvod změny:** Umožnění ukládání kontextu interakcí pro budoucí využití
- **Nový kód:**
  ```python
  async def store_memory(state: State, config: RunnableConfig, *, store: BaseStore) -> dict:
      """Uloží výsledek analýzy do paměti."""
      try:
          # ... implementace ukládání paměti ...
      except Exception as e:
          logger.error(f"Error in store_memory: {str(e)}")
          return {}
  
  # V build_company_analysis_graph
  workflow.add_node("store_memory", store_memory)
  workflow.add_edge("generate_response", "store_memory")
  workflow.add_edge("store_memory", END)
  ```

### v0.7 (10.4.2025) - Refaktoring pro asynchronní operace

- **Popis změny:** Přepracování všech uzlů grafu na asynchronní funkce
- **Důvod změny:** Zvýšení výkonu a efektivity při čekání na externí API
- **Původní kód:**
  ```python
  def fetch_company_data(state: State, config: RunnableConfig) -> dict:
      # Synchronní implementace
  ```
- **Nový kód:**
  ```python
  async def fetch_company_data(state: State, config: RunnableConfig) -> dict:
      # Asynchronní implementace
  ```

## Vyzkoušené přístupy

### 1. Architektura grafu

- ✅ **Conditionals v LangGraph**: Použití podmíněných přechodů pro dynamické větvení workflow
  - **Výhody:** Efektivnější zpracování, možnost přeskočit nepotřebné kroky
  - **Použití:** `workflow.add_conditional_edges(node, condition_fn, {outcomes})`

- ✅ **Asynchronní uzly**: Všechny uzly implementovány jako asynchronní funkce
  - **Výhody:** Lepší výkon při volání externích API, neblokující operace
  - **Použití:** `async def node_function(state, config)`

- ❌ **Subgrafy pro různé typy analýz**:
  - **Proč nefunguje:** Zbytečně komplikovaná struktura, složitější údržba
  - **Omezení:** Ztížená sledovatelnost datového toku, složitější debugging

### 2. Zpracování chyb

- ✅ **Try-except v každém uzlu s návratem prázdného stavu**:
  - **Výhody:** Robustnost workflow, který pokračuje i při selhání některého uzlu
  - **Použití:** 
    ```python
    try:
        # Logika uzlu
        return {"key": value}
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {}
    ```

- ❌ **Centralizované zpracování chyb**:
  - **Proč nefunguje:** V LangGraph je obtížné implementovat, ztrácí se kontext chyby
  - **Omezení:** Omezená flexibilita při zpracování chyb specifických pro konkrétní uzly

### 3. Generování odpovědí

- ✅ **LCEL Chain s přímým přístupem ke stavu**:
  - **Výhody:** Přehledný kód, snadná údržba, flexibilita při extrakci dat ze stavu
  - **Použití:** 
    ```python
    chain = (
        {
            "key1": lambda s: s["data"].get("value", "default"),
            # další mapování...
        }
        | prompt_template 
        | llm 
        | StrOutputParser()
    )
    ```

- ❌ **Manuální sestavení promptu**:
  - **Proč nefunguje:** Nepřehledný kód, obtížná údržba, náchylnost k chybám
  - **Omezení:** Špatná škálovatelnost při změnách struktury dat

## Známé problémy

### 1. Ošetření chybějících dat

- **Problém:** Pokud API vrátí neúplná data, workflow může generovat neúplné nebo zavádějící odpovědi
- **Řešení:** Implementovat důkladnější validaci dat v každém uzlu a poskytovat explicitní informace o chybějících datech v odpovědi

### 2. Odolnost vůči selhání API

- **Problém:** Pokud externí API (Sayari nebo Supabase) není dostupné, workflow se spoléhá pouze na try-except bloky
- **Plánované vylepšení:** Implementace retry mechanismu a fallback strategií

### 3. Cache a optimalizace výkonu

- **Problém:** Opakované dotazy na stejnou společnost způsobují redundantní API volání
- **Plánované vylepšení:** Implementace caching vrstvy pro výsledky API volání

### 4. Podmíněné přechody

- **Problém:** Současná implementace podmíněných přechodů je statická a neadaptuje se na kontextové informace
- **Plánované vylepšení:** Implementace sofistikovanějších rozhodovacích funkcí s využitím větší části stavu

### 5. Plánovaná vylepšení

- Implementace paralelního zpracování pro nezávislé API volání
- Přidání podpory pro dávkové zpracování více společností
- Vylepšení generování odpovědí s využitím strukturovaného výstupu místo volného textu
- Integrace průběžné zpětné vazby během zpracování dlouhých workflow

---

*Poslední aktualizace: 19.4.2025*
