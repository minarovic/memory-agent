<!-- filepath: /Users/marekminarovic/claude-code/memory-agent/tests/hybrid_workflow_tests_updated.md -->
# Tests Documentation for hybrid_workflow.py Component

## Kritéria dokončení
- **Pokrytí plánovaných funkcí** a tříd (create_data_gathering_agent, gather_company_data_node)
- **Ověření integrace** React agentů s LangGraph workflow
- **Validace chybových stavů** a ošetření výjimek

## Testovací případy

### Funkce: create_data_gathering_agent

- **Vytvoření agenta s výchozími parametry**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Inicializace bez explicitních parametrů, výchozí model, standardní nástroje

- **Vytvoření agenta s vlastními parametry**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Inicializace s vlastním LLM modelem, vlastními nástroji

- **Nastavení systémového promptu**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Kontrola obsahu systémového promptu, instrukce pro sběr dat

- **Konfigurace nástrojů pro agenta**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Správná inicializace nástrojů, přístup ke všem potřebným nástrojům

### Funkce: gather_company_data_node

- **Úspěšný sběr dat o společnosti**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Volání React agenta s validními vstupy, extrakce dat ze společnosti

- **Chování při chybějících vstupních datech**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Kontrola chování při chybějících údajích o společnosti

- **Integrace výstupu agenta do stavu grafu**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Správná struktura vráceného stavu, aktualizace všech požadovaných polí

- **Chování při výjimce v React agentovi**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Zpracování chyby v agentovi, logování, návratová hodnota

### Integrace do workflow

- **Integrace gather_company_data_node do LangGraph workflow**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Správné přidání do grafu, podmíněné přechody

- **End-to-end test s React agentem**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Průchod celým workflow s React agentem, kontrola výstupu

---

*Poslední aktualizace: 19.4.2025*
