# Tests Documentation for hybrid_workflow.py Component

## Kritéria dokončení
- **100% pokrytí plánovaných funkcí** a tříd po jejich implementaci (create_data_gathering_agent, gather_company_data_node)
- **95% pokrytí kódu** pro `hybrid_workflow.py` (včetně všech větvení a chybových stavů)
- **Minimální typy testů** pro každou funkci/metodu:
  - Úspěšné volání React agenta s validními vstupy
  - Zpracování chybových stavů (výjimky z agenta, nevalidní vstupy)
  - Hraniční případy (prázdné společnosti, chybějící data)
  - Integrace s LangGraph workflow
- **Správné mockování** React agenta, LLM a nástrojů
- **Vyhodnocení rozhodovací logiky** React agenta v různých scénářích

## Testovací případy

### Funkce: create_data_gathering_agent

#### test_create_data_gathering_agent_default_params
- **Popis**: Ověření vytvoření React agenta s výchozími parametry
- **Status**: TODO
- **Verifikace**:
  - Ověření inicializace agenta bez explicitních parametrů
  - Kontrola, že agent používá výchozí model (Claude)
  - Ověření, že jsou využity standardní nástroje (SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool)
  - Kontrola správné struktury vráceného agenta a nástrojů
  - Mockování: init_chat_model, create_react_agent z langgraph.prebuilt

#### test_create_data_gathering_agent_custom_params
- **Popis**: Ověření vytvoření React agenta s vlastními parametry
- **Status**: TODO
- **Verifikace**:
  - Inicializace s vlastním LLM modelem
  - Inicializace s vlastními nástroji
  - Ověření, že agent používá poskytnuté parametry
  - Mockování: init_chat_model, create_react_agent z langgraph.prebuilt

#### test_create_data_gathering_agent_system_prompt
- **Popis**: Ověření správného nastavení systémového promptu pro React agenta
- **Status**: TODO
- **Verifikace**:
  - Kontrola, že systémový prompt obsahuje instrukce pro sběr dat
  - Ověření, že prompt obsahuje popis dostupných nástrojů
  - Mockování: create_react_agent, kontrola parametrů předaných do create_react_agent

#### test_create_data_gathering_agent_tools_configuration
- **Popis**: Ověření správné konfigurace nástrojů pro React agenta
- **Status**: TODO
- **Verifikace**:
  - Ověření, že nástroje jsou správně inicializovány
  - Kontrola, že agent má přístup ke všem potřebným nástrojům
  - Ověření, že nástroje mají správný název a popis pro použití agentem
  - Mockování: vytvoření mock objektů pro nástroje

### Funkce: gather_company_data_node

#### test_gather_company_data_node_success
- **Popis**: Ověření úspěšného průběhu uzlu pro sběr dat o firmách
- **Status**: TODO
- **Verifikace**:
  - Vytvoření testovacího stavu s validní company_analysis
  - Simulace úspěšného běhu React agenta
  - Ověření, že výstupní stav obsahuje očekávaná data
  - Mockování: create_data_gathering_agent, agent.invoke

#### test_gather_company_data_node_multiple_companies
- **Popis**: Ověření zpracování více společností v jednom dotazu
- **Status**: TODO
- **Verifikace**:
  - Vytvoření testovacího stavu s company_analysis obsahujícím více společností
  - Simulace iterativního zpracování každé společnosti
  - Ověření, že výstupní stav obsahuje data o všech společnostech
  - Mockování: create_data_gathering_agent, agent.invoke

#### test_gather_company_data_node_no_company
- **Popis**: Ověření chování při chybějících datech o společnosti
- **Status**: TODO
- **Verifikace**:
  - Vytvoření testovacího stavu bez company_analysis
  - Ověření, že uzel vrací stav bez změny
  - Kontrola logování varování
  - Mockování: create_data_gathering_agent, agent.invoke

#### test_gather_company_data_node_agent_exception
- **Popis**: Ověření chování při výjimce v React agentu
- **Status**: TODO
- **Verifikace**:
  - Vytvoření testovacího stavu s validní company_analysis
  - Simulace výjimky při volání agenta
  - Ověření správného logování chyby
  - Kontrola, že je vrácena informativní chybová zpráva
  - Mockování: create_data_gathering_agent, agent.invoke (vyvolání výjimky)

### Třída: CompanyDataAgent (plánováno)

#### test_company_data_agent_tool_usage
- **Popis**: Ověření, že agent používá správné nástroje pro různé typy dat
- **Status**: TODO
- **Verifikace**:
  - Simulace vstupního dotazu vyžadujícího základní data o společnosti
  - Ověření, že agent používá SayariApiTool
  - Simulace dotazu na interní data a ověření použití SupabaseInternalDataTool
  - Simulace dotazu na vztahy a ověření použití SayariRelationshipsTool
  - Mockování: agent.invoke, nástroje s monitorováním volání

#### test_company_data_agent_reasoning
- **Popis**: Ověření schopnosti agenta plánovat a zdůvodňovat své kroky
- **Status**: TODO
- **Verifikace**:
  - Analýza intermediate_steps v React agentu
  - Ověření, že agent správně identifikuje potřebné kroky
  - Kontrola, že agent dokáže zhodnotit získaná data a vyžádat další informace
  - Mockování: agent.invoke s podrobnou kontrolou intermediate_steps

## Integritní testy

### test_hybrid_workflow_integration
- **Popis**: Ověření integrace hybridního workflow s LangGraph
- **Status**: TODO
- **Verifikace**:
  - Vytvoření jednoduchého grafu s uzlem gather_company_data_node
  - Simulace průchodu stavu grafem
  - Ověření správného předávání dat mezi standardními uzly a React agentem
  - Mockování: StateGraph, React agent, nástroje

### test_react_agent_in_langgraph_context
- **Popis**: Testování chování React agenta v kontextu LangGraph
- **Status**: TODO
- **Verifikace**:
  - Definice grafu s React agentem jako uzlem
  - Ověření, že stav je správně aktualizován po průchodu React agentem
  - Testování větvení na základě výstupu React agenta
  - Mockování: StateGraph, create_react_agent

### test_end_to_end_complex_query
- **Popis**: End-to-end test komplexního dotazu vyžadujícího React agenta
- **Status**: TODO
- **Verifikace**:
  - Simulace složitého dotazu vyžadujícího iterativní rozhodování
  - Ověření celého flow od analýzy dotazu po generování odpovědi
  - Kontrola, že React agent byl použit pro komplexní části workflow
  - Mockování: external APIs, LLM

## Poznámky k testování

### Techniky a nástroje
- **Testování React agentů**: Využití langgraph.prebuilt.testing pro simulaci chování agentů
- **Agentové intermediate_steps**: Analýza průběžných kroků agenta pro testování rozhodovací logiky
- **Simulace LLM odpovědí**: Předpřipravené odpovědi pro simulaci různých cest v rozhodování agenta
- **Deterministické simulace**: Použití fixed_seed pro zajištění reprodukovatelnosti testů s LLM
- **Gedachtenexperiment**: Simulace myšlenkových pochodů agenta pro komplexní scénáře

### Známé obtíže
1. **Testování rozhodovacího procesu**: React agent dělá komplexní rozhodnutí, která je těžké předvídat a testovat deterministicky
2. **Variabilita LLM odpovědí**: I se stejným vstupem může LLM generovat různé plány kroků
3. **Integrace s LangGraph**: Testování interakce mezi stavovým grafem a bezstavovým React agentem vyžaduje komplexní mocking
4. **Časová náročnost**: Testy s React agentem jsou pomalejší než standardní jednotkové testy
5. **Komplexní stavy**: Sledování a validace mezistavu při iterativním rozhodovacím procesu agenta

### Doporučení pro budoucí testování
1. Vytvořit standardizovanou sadu mock odpovědí pro simulaci React agenta
2. Implementovat "behaviors" testy, které ověřují schopnost agenta reagovat na různé situace
3. Používat snapshot testování intermediate_steps pro zachycení změn v logice rozhodování
4. Vytvořit vizualizaci průběhu React agenta pro analýzu neúspěšných testů
5. Implementovat parametrizované testy s různými konfiguracemi nástrojů pro otestování flexibility agenta

---

*Poslední aktualizace: 19.4.2025*
