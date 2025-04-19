# Tests Documentation for graph.py Component

## Kritéria dokončení
- **100% pokrytí nodů/uzlů grafu** (analyze_company_input, fetch_company_data, fetch_internal_data, fetch_relationships, generate_response, store_memory)
- **95% pokrytí rozhodovacích funkcí** (should_analyze_companies, should_fetch_company_data, should_fetch_relationships)
- **90% pokrytí kódu** pro `graph.py` (včetně chybových větví a výjimek)
- **Minimální typy testů** pro každý uzel grafu:
  - Úspěšné zpracování uzlu s validním stavem
  - Zpracování nevalidního stavu (chybějící data)
  - Ošetření výjimek při chybě externích nástrojů
  - Správná aktualizace stavu
- **Testy struktury grafu**:
  - Validace přechodů mezi uzly
  - Ověření podmíněných přechodů
- **Správné mockování** LLM volání, API nástrojů, BaseStore

## Testovací případy

### Funkce: analyze_company_input

#### test_analyze_company_input_success
- **Popis**: Ověření úspěšné analýzy uživatelského vstupu
- **Status**: V PROCESU
- **Verifikace**:
  - Extrakce zprávy z historického kontextu
  - Správné volání analyze_query funkce s předaným textem
  - Správné předání modelu z konfigurace
  - Ověření výsledného stavu s položkou company_analysis
  - Mockování: analyze_query, Configuration.from_runnable_config

#### test_analyze_company_input_no_user_message
- **Popis**: Ověření chování při chybějící uživatelské zprávě
- **Status**: TODO
- **Verifikace**:
  - Vytvoření stavu s prázdným seznamem zpráv
  - Vytvoření stavu jen se zprávami od systému/AI
  - Ověření správného logování varování
  - Ověření prázdné návratové hodnoty {}
  - Mockování: logger.warning

#### test_analyze_company_input_multimodal
- **Popis**: Ověření zpracování multimodálního obsahu
- **Status**: TODO
- **Verifikace**:
  - Vytvoření zprávy s kombinací textu a jiného obsahu
  - Ověření správné extrakce textového obsahu
  - Ověření předání extrahovaného textu do analyze_query
  - Mockování: analyze_query

#### test_analyze_company_input_exception
- **Popis**: Ověření chování při výjimce
- **Status**: TODO
- **Verifikace**:
  - Simulace výjimky z analyze_query
  - Ověření správného logování chyby
  - Ověření prázdné návratové hodnoty {}
  - Mockování: analyze_query (vyvolání výjimky)

### Funkce: fetch_company_data

#### test_fetch_company_data_success
- **Popis**: Ověření úspěšného získání dat o společnosti
- **Status**: V PROCESU
- **Verifikace**:
  - Vytvoření stavu s company_analysis
  - Správné volání SayariApiTool._arun s názvem společnosti
  - Vrácení získaných dat v klíči company_data
  - Mockování: SayariApiTool._arun

#### test_fetch_company_data_no_company
- **Popis**: Ověření chování bez informací o společnosti
- **Status**: TODO
- **Verifikace**:
  - Vytvoření stavu bez company_analysis
  - Vytvoření stavu s prázdným company_analysis
  - Ověření správného logování varování
  - Ověření prázdné návratové hodnoty
  - Mockování: logger.warning

#### test_fetch_company_data_api_exception
- **Popis**: Ověření zpracování API chyby
- **Status**: TODO
- **Verifikace**:
  - Simulace výjimky z SayariApiTool._arun
  - Ověření správného logování chyby
  - Ověření prázdné návratové hodnoty {}
  - Mockování: SayariApiTool._arun (vyvolání výjimky)

### Funkce: fetch_internal_data

#### test_fetch_internal_data_success
- **Popis**: Ověření úspěšného získání interních dat
- **Status**: V PROCESU
- **Verifikace**:
  - Vytvoření stavu s company_analysis
  - Správné volání SupabaseInternalDataTool._arun s názvem společnosti
  - Vrácení získaných dat v klíči internal_data
  - Mockování: SupabaseInternalDataTool._arun

#### test_fetch_internal_data_no_company
- **Popis**: Ověření chování bez informací o společnosti
- **Status**: TODO
- **Verifikace**:
  - Vytvoření stavu bez company_analysis
  - Vytvoření stavu s prázdným company_analysis
  - Ověření správného logování varování
  - Ověření prázdné návratové hodnoty
  - Mockování: logger.warning

#### test_fetch_internal_data_api_exception
- **Popis**: Ověření zpracování API chyby
- **Status**: TODO
- **Verifikace**:
  - Simulace výjimky z SupabaseInternalDataTool._arun
  - Ověření správného logování chyby
  - Ověření prázdné návratové hodnoty {}
  - Mockování: SupabaseInternalDataTool._arun (vyvolání výjimky)

### Funkce: fetch_relationships

#### test_fetch_relationships_success
- **Popis**: Ověření úspěšného získání vztahů společnosti
- **Status**: V PROCESU
- **Verifikace**:
  - Vytvoření stavu s company_data obsahujícím entity_id
  - Správné volání SayariRelationshipsTool._arun s ID entity
  - Vrácení získaných dat v klíči relationships_data
  - Mockování: SayariRelationshipsTool._arun

#### test_fetch_relationships_no_entity_id
- **Popis**: Ověření chování bez ID entity
- **Status**: TODO
- **Verifikace**:
  - Vytvoření stavu bez company_data
  - Vytvoření stavu s prázdným company_data (bez entity_id)
  - Ověření správného logování varování
  - Ověření návratové hodnoty {"relationships_data": None}
  - Mockování: logger.warning

#### test_fetch_relationships_api_exception
- **Popis**: Ověření zpracování API chyby
- **Status**: TODO
- **Verifikace**:
  - Simulace výjimky z SayariRelationshipsTool._arun
  - Ověření správného logování chyby
  - Ověření prázdné návratové hodnoty {}
  - Mockování: SayariRelationshipsTool._arun (vyvolání výjimky)

### Funkce: generate_response

#### test_generate_response_success
- **Popis**: Ověření úspěšného generování odpovědi
- **Status**: V PROCESU
- **Verifikace**:
  - Vytvoření stavu s potřebnými daty (company_analysis, company_data, internal_data, relationships_data)
  - Správné sestavení a volání LCEL řetězce
  - Správné přidání odpovědi jako AIMessage do messages
  - Vrácení aktualizovaného seznamu messages
  - Mockování: init_chat_model, chain.ainvoke

#### test_generate_response_minimal_data
- **Popis**: Ověření generování odpovědi s minimem dat
- **Status**: TODO
- **Verifikace**:
  - Vytvoření stavu jen s company_analysis
  - Ověření, že chybějící data jsou nahrazena prázdnými objekty
  - Správné použití výchozích hodnot při mapování dat do promptu
  - Mockování: init_chat_model, chain.ainvoke

#### test_generate_response_exception
- **Popis**: Ověření chování při výjimce během generování
- **Status**: TODO
- **Verifikace**:
  - Simulace výjimky při volání řetězce
  - Ověření správného logování chyby
  - Ověření přidání chybové zprávy jako AIMessage do messages
  - Mockování: chain.ainvoke (vyvolání výjimky)

### Funkce: store_memory

#### test_store_memory_success
- **Popis**: Ověření úspěšného uložení do paměti
- **Status**: V PROCESU
- **Verifikace**:
  - Vytvoření stavu s company_analysis (is_company_analysis=True)
  - Správné volání upsert_memory s očekávanými parametry
  - Ověření formátu obsahu paměti
  - Mockování: tools.upsert_memory

#### test_store_memory_no_company_analysis
- **Popis**: Ověření chování bez analýzy společnosti
- **Status**: TODO
- **Verifikace**:
  - Vytvoření stavu bez company_analysis
  - Vytvoření stavu s company_analysis (is_company_analysis=False)
  - Ověření, že upsert_memory není volána
  - Ověření prázdné návratové hodnoty {}
  - Mockování: logger.info

#### test_store_memory_exception
- **Popis**: Ověření chování při výjimce
- **Status**: TODO
- **Verifikace**:
  - Simulace výjimky z upsert_memory
  - Ověření správného logování chyby
  - Ověření prázdné návratové hodnoty {}
  - Mockování: tools.upsert_memory (vyvolání výjimky)

### Rozhodovací funkce

#### test_should_analyze_companies
- **Popis**: Ověření rozhodovací funkce pro analýzu
- **Status**: TODO
- **Verifikace**:
  - Ověření, že funkce vždy vrací "analyze"
  - Test s různými stavy

#### test_should_fetch_company_data
- **Popis**: Ověření rozhodovací funkce pro získání dat o společnosti
- **Status**: TODO
- **Verifikace**:
  - Test s validní company_analysis (is_company_analysis=True) -> "fetch"
  - Test bez company_analysis -> "skip"
  - Test s company_analysis (is_company_analysis=False) -> "skip"

#### test_should_fetch_relationships
- **Popis**: Ověření rozhodovací funkce pro získání vztahů
- **Status**: TODO
- **Verifikace**:
  - Test s validním stavem (company_analysis, entity_id, vhodný typ analýzy) -> "fetch"
  - Testy s různými neúplnými stavy -> "skip"
  - Test s nevhodným typem analýzy -> "skip"
  - Test bez entity_id -> "skip"

### Funkce: build_company_analysis_graph

#### test_build_company_analysis_graph_structure
- **Popis**: Ověření správné struktury vytvořeného grafu
- **Status**: TODO
- **Verifikace**:
  - Ověření správného počtu uzlů
  - Ověření správného vstupního uzlu
  - Ověření správných podmíněných přechodů
  - Ověření příslušných hran
  - Mockování: StateGraph

#### test_build_company_analysis_graph_exception
- **Popis**: Ověření chování při výjimce během sestavování grafu
- **Status**: TODO
- **Verifikace**:
  - Simulace výjimky během sestavování grafu
  - Ověření správného logování chyby
  - Ověření re-propagace výjimky
  - Mockování: StateGraph (vyvolání výjimky)

## Integritní testy

### test_company_analysis_flow_success
- **Popis**: End-to-end test celého workflow s mockovanými externími službami
- **Status**: TODO
- **Verifikace**:
  - Vytvoření kompletního grafu
  - Simulace vstupu uživatele s dotazem na společnost
  - Ověření průchodu přes všechny očekávané uzly
  - Ověření finálního stavu s vygenerovanou odpovědí
  - Mockování: všechny externí nástroje a služby

### test_company_analysis_flow_non_company_query
- **Popis**: Test průchodu workflow s dotazem nesouvisejícím s firmou
- **Status**: TODO
- **Verifikace**:
  - Simulace vstupu uživatele s obecným dotazem
  - Ověření přeskočení uzlů pro získávání dat
  - Ověření generování obecné odpovědi
  - Mockování: analyze_query (vrací is_company_analysis=False)

### test_company_analysis_flow_error_recovery
- **Popis**: Test schopnosti workflow zotavit se z chyb
- **Status**: TODO
- **Verifikace**:
  - Simulace chyby v jednom z uzlů (např. fetch_company_data)
  - Ověření, že workflow pokračuje ke generate_response
  - Ověření, že odpověď obsahuje informaci o chybějících datech
  - Mockování: SayariApiTool._arun (vyvolání výjimky)

## Poznámky k testování

### Techniky a nástroje
- **Mockování LangGraph komponent**: Pro testování jednotlivých uzlů grafu bez závislosti na skutečném grafu
- **MockState**: Třída pro jednoduché vytváření testovacích stavů s požadovanými vlastnostmi
- **AsyncMock**: Pro mockování asynchronních funkcí v nástrojích
- **InMemoryStore**: Pro testování paměťových operací bez reálného úložiště
- **pytest.mark.asyncio**: Pro podporu testování asynchronních funkcí
- **pytest-cov**: Pro měření pokrytí kódu testy

### Známé obtíže
1. **Testování workflow s cykly**: LangGraph umožňuje cykly v grafu, které je obtížné testovat deterministicky
2. **Mockování vs. reálné chování**: Mockované nástroje nemusí přesně replikovat chování reálných API
3. **Stavovost grafu**: Nutnost správného sestavení stavu před a po každém kroku workflow
4. **Kreativita LLM**: Při testování generate_response je obtížné deterministicky ověřit výstup
5. **Asynchronní zpracování**: Testování paralelizovaných částí grafu může být náročné

### Doporučení pro budoucí testování
1. Vytvořit mock implementace všech externích API nástrojů speciálně pro účely testování
2. Přidat integrační testy různých typů analýzy (risk_comparison, common_suppliers, general)
3. Implementovat property-based testy pro ověření rozhodovacích funkcí s různými stavy
4. Přidat testy pro ověření serializace/deserializace stavu při ukládání checkpointů
5. Implementovat vizualizaci grafu pro snazší analýzu a debugging workflow

---

*Poslední aktualizace: 19.4.2025*
