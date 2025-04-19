# State Component Documentation

## Základní informace
- **Status:** DOKONČENO
- **Popis:** Definice typů pro stavový graf v Memory Agent projektu. Tato komponenta poskytuje základní datové struktury používané pro správu stavu ve workflow grafu LangGraph, především třídu State, která udržuje konverzační historii a výsledky analýz.
- **Závislosti:**
  - **Externí knihovny:**
    - `langchain_core.messages`: Pro typování zpráv v konverzaci
    - `langgraph.graph`: Pro anotace specifické pro LangGraph (`add_messages`)
    - `typing_extensions`: Pro podporu pokročilých typových anotací
  - **Interní komponenty:**
    - `memory_agent.analyzer`: Pro import typu `AnalysisResult`

- **Použití v:**
  - `graph.py`: Jako základní stavový objekt pro LangGraph workflow
  - `hybrid_workflow.py`: Pro rozšíření základního workflow o React agenty
  - Všechny uzly grafu: Pro typování parametrů a přístup k datům

## API

### `State` (dataclass)

- **Signature:**
  ```python
  @dataclass(kw_only=True)
  class State:
      messages: Annotated[list[AnyMessage], add_messages]
      company_analysis: Optional[AnalysisResult] = None
  ```

- **Popis:** Hlavní třída pro uchování stavu workflow grafu. Udržuje historii zpráv a výsledky analýzy společností. Třída je implementována jako dataclass s povinným použitím pojmenovaných argumentů (kw_only=True).

- **Atributy:**
  - `messages` (Annotated[list[AnyMessage], add_messages]): Seznam zpráv v konverzaci. Anotace `add_messages` je specifická pro LangGraph a zajišťuje správné sloučení zpráv při aktualizaci stavu.
  - `company_analysis` (Optional[AnalysisResult]): Výsledek analýzy společností z uživatelského dotazu. Obsahuje identifikované společnosti, typ analýzy a další metadata. Výchozí hodnota je None.

- **Použití:**
  ```python
  # Vytvoření nového stavu
  state = State(messages=[HumanMessage(content="Analyzuj firmu Acme")])
  
  # Aktualizace stavu v uzlu grafu
  def my_node(state: State, config: RunnableConfig) -> dict:
      # Zpracování stavu
      return {"company_analysis": analysis_result}
  ```

- **Zpracování chyb:**
  - Dataclass zajišťuje validaci typů při vytváření a aktualizaci stavu
  - Při chybějících povinných atributech vyvolá TypeError
  - Neprovádí dodatečné validace obsahu - za validaci odpovídají jednotlivé uzly grafu

### `AnalysisResult` (TypedDict, importováno z analyzer)

- **Popis:** Importovaný typ z `memory_agent.analyzer` definující strukturu výsledků analýzy dotazu.

- **Struktura:**
  ```python
  TypedDict {
      "companies": List[str]       # Seznam identifikovaných společností
      "company": str               # Primární společnost (první v seznamu)
      "analysis_type": str         # Typ požadované analýzy
      "query": str                 # Původní dotaz uživatele
      "is_company_analysis": bool  # Zda se jedná o analýzu společnosti
      "confidence": float          # Míra jistoty analýzy (0.0 - 1.0)
  }
  ```

## Historie změn

### v1.1 (17.4.2025) - Optimalizace pro LangGraph

- **Popis změny:** Přidání anotace `add_messages` pro pole messages
- **Důvod změny:** Zajištění správného chování při aktualizaci záznamů v historii konverzace
- **Původní kód:**
  ```python
  @dataclass(kw_only=True)
  class State:
      messages: list[AnyMessage]
      company_analysis: Optional[AnalysisResult] = None
  ```
- **Nový kód:**
  ```python
  @dataclass(kw_only=True)
  class State:
      messages: Annotated[list[AnyMessage], add_messages]
      company_analysis: Optional[AnalysisResult] = None
  ```

### v1.0 (1.4.2025) - Základní implementace

- **Popis změny:** Prvotní implementace State třídy pro LangGraph workflow
- **Důvod změny:** Definice základních datových struktur pro stavový graf
- **Nový kód:**
  ```python
  @dataclass(kw_only=True)
  class State:
      messages: list[AnyMessage]
      company_analysis: Optional[AnalysisResult] = None
  ```

## Vyzkoušené přístupy

### 1. Struktura stavu

- ✅ **Dataclasses (Implementováno)**
  - **Výhody:** Jednoduchá definice, automatická implementace `__init__`, `__repr__` a dalších metod, dobrá podpora typové kontroly
  - **Použití:** `@dataclass(kw_only=True)`

- ❌ **Pydantic model**
  - **Proč nefunguje:** Složitější integrace s LangGraph, který je optimalizovaný pro práci s dataclasses
  - **Omezení:** Přidává nepotřebnou závislost, komplikuje rozšiřitelnost

- ❌ **Dict s TypedDict**
  - **Proč nefunguje:** Neumožňuje anotace specifické pro LangGraph, složitější kontrola typů za běhu
  - **Omezení:** Nedostatečná vývojářská zkušenost, chybí metody jako `__repr__`

### 2. Správa atributů

- ✅ **Minimalistický přístup s omezeným počtem atributů**
  - **Výhody:** Přehledný kód, snadná orientace, jednodušší správa stavu
  - **Použití:** Pouze nejnutnější atributy (`messages`, `company_analysis`)

- ❌ **Vše ve stavu**
  - **Proč nefunguje:** Vede k přílišné složitosti, jednotlivé uzly grafu potřebují přístup jen k části stavu
  - **Omezení:** Ztížené testování, neefektivní kopírování velkých datových struktur

### 3. Implementace field anotací

- ✅ **Použití LangGraph anotací** (`add_messages`)
  - **Výhody:** Zajišťuje správné sloučení seznamů zpráv při aktualizaci stavu
  - **Použití:** `Annotated[list[AnyMessage], add_messages]`

- ❌ **Vlastní reduktory**
  - **Proč nefunguje:** Zbytečná reimplementace funkcionality již poskytované v LangGraph
  - **Omezení:** Potenciální nekompatibilita s budoucími verzemi LangGraph

## Známé problémy

### 1. Omezená flexibilita

- **Problém:** State třída musí být dopředu definovaná, což ztěžuje dynamické přidávání nových polí za běhu
- **Řešení:** Pro skutečně dynamické vlastnosti zvážit použití obecného slovníku jako doplňku ke staticky typovaným polím

### 2. Serializace/Deserializace

- **Problém:** Při ukládání a načítání stavu mohou nastat komplikace s komplexními typy
- **Plánované vylepšení:** Implementace metod `to_dict` a `from_dict` pro bezproblémovou serializaci

### 3. Chybějící validace

- **Problém:** Dataclass neprovádí validaci obsahu (pouze typovou kontrolu)
- **Plánované vylepšení:** Přidat validační metody pro kontrolu integrity dat

### 4. Plánovaná vylepšení

- Rozšíření stavu o další atributy pro ukládání dílčích výsledků analýzy
- Implementace monitoringu změn stavu pro lepší debugging
- Přidání podpory pro transakční aktualizace stavu (commit/rollback)
- Optimalizace serializace pro efektivní ukládání a načítání stavu z úložiště

---

*Poslední aktualizace: 19.4.2025*
