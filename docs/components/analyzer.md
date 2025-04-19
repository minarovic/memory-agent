# Analyzer Component Documentation

## Základní informace
- **Status:** DOKONČENO
- **Popis:** Komponenta pro analýzu uživatelských dotazů, která identifikuje zmíněné společnosti a typ požadované analýzy. Slouží jako první krok ve workflow pro zpracování požadavků na analýzu společností.
- **Závislosti:**
  - Externí knihovny:
    - `langchain_core` (prompts, output_parsers, messages)
    - `langchain` (chat_models)
  - Interní komponenty: Nezávislá na ostatních komponentách

- **Použití v:**
  - `graph.py`: Jako první uzel v LangGraph workflow (`analyze_company_input`)
  - `hybrid_workflow.py`: Pro počáteční analýzu dotazů před použitím React agentů

## API

### `analyze_query`

- **Signature:** 
  ```python
  async def analyze_query(
      user_input: str, 
      config: Optional[RunnableConfig] = None,
      model: Optional[str] = "claude-3-5-sonnet-20240620"
  ) -> AnalysisResult
  ```

- **Popis:** Analyzuje uživatelský vstup a identifikuje zmíněné společnosti a typ analýzy. Používá LLM pro zpracování přirozeného jazyka a extrakci strukturovaných informací.

- **Parametry:**
  - `user_input` (str): Uživatelský dotaz ke zpracování
  - `config` (Optional[RunnableConfig]): Runtime konfigurace, obsahuje např. model, teplotu, atd.
  - `model` (Optional[str]): Model, který se má použít pro analýzu, výchozí hodnota je "claude-3-5-sonnet-20240620"

- **Návratová hodnota:**
  ```python
  AnalysisResult = {
      "companies": List[str],       # Seznam identifikovaných společností
      "company": str,               # Primární společnost (první v seznamu)
      "analysis_type": AnalysisType,# Typ požadované analýzy
      "query": str,                 # Původní dotaz uživatele
      "is_company_analysis": bool,  # Zda jde o analýzu společnosti
      "confidence": float           # Míra jistoty analýzy (0.0 - 1.0)
  }
  ```

- **Zpracování chyb:** 
  - Funkce zachycuje všechny výjimky a loguje je
  - V případě chyby vrací výchozí výsledek s prázdným seznamem společností a typem analýzy "general"
  - Používá standardní Python logging pro záznam průběhu a chyb

### `parse_response`

- **Signature:** 
  ```python
  def parse_response(response: str, original_query: str) -> AnalysisResult
  ```

- **Popis:** Parsuje odpověď z LLM a vytváří strukturovaný výsledek ve formátu AnalysisResult.

- **Parametry:**
  - `response` (str): Odpověď od LLM ve formátu "Company name; analysis_type"
  - `original_query` (str): Původní uživatelský dotaz

- **Návratová hodnota:** 
  - `AnalysisResult`: Strukturovaný výsledek analýzy

- **Zpracování chyb:**
  - Provádí validaci vstupů a ošetřuje neplatné formáty
  - Kontroluje platnost hodnoty analysis_type proti předdefinovaným hodnotám
  - Nastavuje důvěryhodnost výsledku podle množství a kvality extrahovaných dat

### `AnalysisResult` (TypedDict)

- **Popis:** Typovaný slovník definující strukturu výsledků analýzy.

- **Pole:**
  - `companies` (List[str]): Seznam identifikovaných společností v dotazu
  - `company` (str): Primární společnost (první v seznamu)
  - `analysis_type` (AnalysisType): Typ požadované analýzy (risk_comparison, common_suppliers, general)
  - `query` (str): Původní dotaz uživatele
  - `is_company_analysis` (bool): Indikuje, zda se jedná o analýzu společnosti
  - `confidence` (float): Míra jistoty analýzy (0.0 - 1.0)

### `CompanyAnalysisRequest` (BaseModel)

- **Popis:** Pydantic model pro požadavek na analýzu společnosti při předávání do LLM.

- **Pole:**
  - `companies` (List[str]): Seznam identifikovaných společností v dotazu
  - `analysis_type` (AnalysisType): Typ požadované analýzy
  - `is_company_analysis` (bool): Zda se jedná o analýzu společnosti
  - `confidence` (float): Míra jistoty analýzy (0.0 - 1.0)

- **Validace:**
  - `validate_confidence`: Ověřuje, že hodnota confidence je mezi 0.0 a 1.0

## Historie změn

### v1.1 (15.4.2025) - Vylepšení systémového promptu

- **Popis změny:** Aktualizace systémového promptu s inspirací z React přístupu pro lepší strukturované uvažování
- **Důvod změny:** Zlepšení přesnosti identifikace společností a typů analýzy
- **Původní kód:**
```python
ANALYZER_PROMPT = """You are a specialized query analyzer that identifies companies and analysis types.
For each input, identify companies and determine the analysis type (risk_comparison, common_suppliers, general).
Respond in the format "Company name; analysis_type".
"""
```
- **Nový kód:**
```python
ANALYZER_PROMPT = """You are a specialized query analyzer that identifies companies and analysis types in user queries.

For each input, follow these steps:
1. REASONING: Identify whether the query relates to company analysis, and if so, which companies are mentioned.
2. ANALYSIS: Determine what type of analysis the user is requesting, based on keywords and context.
3. FORMATTING: Provide a response in the exact format "Company name; analysis_type"

The analysis type can be one of these:
- risk_comparison (for risk analysis and security factors)
- common_suppliers (for supplier-customer relationship analysis)
- general (for general information about the company or other queries)

Examples:
- Input: "Find risks for Fuyao Group"
  Reasoning: The query is about risk analysis for Fuyao Group.
  Output: "Fuyao Group; risk_comparison"
  
- Input: "What are the risks of Hauk compared to Fuyao Group?"
  Reasoning: The query requests a comparison of risks between two companies: Hauk and Fuyao Group.
  Output: "Hauk, Fuyao Group; risk_comparison"
"""
```

### v1.0 (1.4.2025) - Základní implementace

- **Popis změny:** Prvotní implementace analyzátoru dotazů s využitím LCEL architektury
- **Důvod změny:** Vytvoření základní funkčnosti pro analýzu dotazů a identifikaci společností
- **Nový kód:** Kompletní implementace funkcí `analyze_query` a `parse_response` s využitím LCEL

## Vyzkoušené přístupy

### 1. Architektury pro analýzu dotazů

- ✅ **LCEL Chain (Implementováno)**: Jednoduchý řetězec prompt | llm | parser
  - **Výhody:** Jednoduchá implementace, snadná udržitelnost, rychlé zpracování
  - **Použití:** `prompt | llm | StrOutputParser()`

- ❌ **LangChain ReAct Agent**:
  - **Proč nefunguje:** Zbytečně komplexní pro jednoduchý úkol analýzy, pomalejší zpracování
  - **Omezení:** Vyžaduje definici nástrojů, které nejsou potřebné pro jednoduchou analýzu

- ❌ **Strukturovaný výstup (přímý JSON parsing)**:
  - **Proč nefunguje:** Nestabilní při změnách formátu, vyšší míra chyb
  - **Omezení:** LLM někdy vrací nevalidní JSON, což vede k chybám při parsování

### 2. Formáty odpovědí

- ✅ **Jednoduchý string formát** (`"Company name; analysis_type"`):
  - **Výhody:** Konzistentní, snadno parsovatelné, odolné vůči chybám
  - **Použití:** `parts = response.split(";")`

- ❌ **JSON Formát**:
  - **Proč nefunguje:** Častější chyby syntaxe při generování z LLM
  - **Omezení:** Vyžaduje složitější zpracování chyb a validaci

### 3. Implementace confidence score

- ✅ **Postupné navyšování na základě nalezených entit**:
  - **Výhody:** Jednoduchá ale účinná heuristika, odráží kvalitu analýzy
  - **Použití:** 
    ```python
    if companies:
        confidence = 0.8  # Base confidence level when we have identified companies
        if analysis_type != "general":
            confidence = 0.9  # Higher confidence with specific analysis type
    ```

- ❌ **Získávání confidence přímo z LLM**:
  - **Proč nefunguje:** Nekonzistentní hodnoty, vyžaduje složitější prompt
  - **Omezení:** LLM může vracet nesmyslné hodnoty confidence

## Známé problémy

### 1. Omezení při detekci společností

- **Problém:** Horší rozpoznávání méně známých nebo méně častých názvů společností
- **Řešení:** Budoucí verze by mohla zahrnovat schopnost učit se nové společnosti z uživatelské interakce

### 2. Ambiguity v analýze typu dotazu

- **Problém:** Některé dotazy mohou být interpretovány více způsoby
- **Řešení:** Zvážit implementaci zpětných dotazů pro ujasnění nejasných požadavků

### 3. Jazyková omezení

- **Problém:** Lepší výsledky při analýze anglických dotazů než českých
- **Plánované vylepšení:** Optimalizace promptu pro dvojjazyčnou analýzu (CZ/EN)

### 4. Plánovaná vylepšení

- Implementace zpětné vazby pro postupné zlepšování analýzy
- Rozšíření typů analýz o další kategorie
- Vylepšení zpracování více společností v jednom dotazu a jejich vzájemných vztahů

---

*Poslední aktualizace: 19.4.2025*
