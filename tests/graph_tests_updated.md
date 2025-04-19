<!-- filepath: /Users/marekminarovic/claude-code/memory-agent/tests/graph_tests_updated.md -->
# Tests Documentation for graph.py Component

## Kritéria dokončení
- **Pokrytí všech nodů/uzlů grafu**: analyze_company_input, fetch_company_data, fetch_internal_data, fetch_relationships, generate_response, store_memory
- **Pokrytí rozhodovacích funkcí**: should_analyze_companies, should_fetch_company_data, should_fetch_relationships
- **Ověření struktury grafu**: validace přechodů mezi uzly, podmíněné přechody
- **Integritní testy**: end-to-end testy celého workflow

## Testovací případy

### Funkce: analyze_company_input

- **Úspěšná analýza uživatelského vstupu**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Extrakce zprávy z kontextu, volání analyze_query, výsledný stav

- **Chování při chybějící uživatelské zprávě**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Stav s prázdným seznamem zpráv, stav jen s systémovými zprávami

- **Zpracování multimodálního obsahu**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Zpráva s kombinací textu a jiného obsahu, extrakce textu

- **Chování při výjimce**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace výjimky z analyze_query, logování chyby

### Funkce: fetch_company_data

- **Úspěšné získání dat o společnosti**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Volání SayariApiTool._arun, vrácení dat v company_data

- **Chování bez informací o společnosti**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Stav bez company_analysis, logování varování

- **Zpracování API chyby**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace výjimky z SayariApiTool._arun, logování chyby

### Funkce: fetch_internal_data

- **Úspěšné získání interních dat**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Volání SupabaseInternalDataTool._arun, vrácení internal_data

- **Chování bez informací o společnosti**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Stav bez company_analysis, logování varování

- **Zpracování API chyby**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace výjimky z API nástroje, logování chyby

### Funkce: fetch_relationships

- **Úspěšné získání vztahů společnosti**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Volání SayariRelationshipsTool._arun, vrácení relationships_data

- **Chování bez ID entity**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Stav bez entity_id, logování varování

- **Zpracování API chyby**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace výjimky z API nástroje, logování chyby

### Funkce: generate_response

- **Úspěšné generování odpovědi**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Sestavení LCEL řetězce, přidání AIMessage do messages

- **Generování odpovědi s minimem dat**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Stav jen s company_analysis, použití výchozích hodnot

- **Chování při výjimce**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace výjimky při volání řetězce, přidání chybové zprávy

### Funkce: store_memory

- **Úspěšné uložení do paměti**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Volání upsert_memory, formát obsahu paměti

- **Chování bez analýzy společnosti**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Stav bez company_analysis, žádné volání upsert_memory

- **Chování při výjimce**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace výjimky z upsert_memory, logování chyby

### Rozhodovací funkce

- **should_analyze_companies**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Funkce vždy vrací "analyze", test s různými stavy

- **should_fetch_company_data**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Testování různých stavů company_analysis

- **should_fetch_relationships**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Testování stavů s entity_id, různými typy analýzy

### Funkce: build_company_analysis_graph

- **Struktura vytvořeného grafu**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Počet uzlů, vstupní uzel, podmíněné přechody, hrany

- **Chování při výjimce**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace výjimky během sestavování grafu, logování chyby

## Integritní testy

- **End-to-end test celého workflow**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace dotazu na společnost, průchod všemi uzly

- **Test workflow s obecným dotazem**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace obecného dotazu, přeskočení uzlů pro získávání dat

- **Test schopnosti zotavit se z chyb**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Simulace chyby v jednom z uzlů, pokračování workflow

---

*Poslední aktualizace: 19.4.2025*
