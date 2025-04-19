# Tests Documentation for state.py Component

## Kritéria dokončení
- **100% pokrytí tříd a metod** v `state.py`
- **90% pokrytí kódu** pro `state.py` (včetně edge cases)
- **Minimální typy testů**:
  - Inicializace State s různými kombinacemi parametrů
  - Ověření správného fungování anotace `add_messages`
  - Kompatibilita s LangGraph operacemi
  - Typová bezpečnost a kontrola validace typů
- **Validace chování v grafu** - ověření správné funkce při použití v LangGraph workflow

## Testovací případy

### Třída: State

#### test_state_initialization
- **Popis**: Ověření správné inicializace State objektu
- **Status**: TODO
- **Verifikace**:
  - Vytvoření instance State s minimálními povinnými parametry (pouze messages)
  - Ověření, že company_analysis je None
  - Kontrola, že messages obsahuje očekávané hodnoty
  - Ověření, že kw_only funguje správně (nelze vytvořit instanci bez pojmenovaných argumentů)

#### test_state_with_company_analysis
- **Popis**: Ověření inicializace s company_analysis parametrem
- **Status**: TODO
- **Verifikace**:
  - Vytvoření mock AnalysisResult objektu
  - Inicializace State s messages a company_analysis
  - Ověření, že company_analysis obsahuje očekávaná data

#### test_state_type_validation
- **Popis**: Ověření typové validace při vytváření State
- **Status**: TODO
- **Verifikace**:
  - Pokus o vytvoření State s nesprávnými typy parametrů (např. string místo listu u messages)
  - Ověření, že je vyhozena příslušná typová chyba
  - Kontrola typů při přiřazení nevalidní hodnoty do company_analysis

#### test_state_kw_only_enforcement
- **Popis**: Ověření, že je vynuceno použití pojmenovaných parametrů
- **Status**: TODO
- **Verifikace**:
  - Pokus o vytvoření State pomocí poziční argumentů
  - Ověření, že je vyhozena správná výjimka (TypeError)
  - Kontrola chybové hlášky při nesprávném volání

### Anotace: add_messages

#### test_add_messages_annotation
- **Popis**: Testování funkčnosti anotace add_messages pro správné sloučení zpráv
- **Status**: TODO
- **Verifikace**:
  - Vytvoření dvou instancí State s různými zprávami
  - Simulace aktualizace stavu v LangGraph (dict merge)
  - Ověření, že zprávy jsou správně sloučeny (připojeny na konec seznamu)
  - Kontrola, že původní instance zůstaly nezměněny (immutability)

#### test_add_messages_empty_lists
- **Popis**: Testování sloučení s prázdnými seznamy zpráv
- **Status**: TODO
- **Verifikace**:
  - Vytvoření State s prázdným seznamem zpráv
  - Vytvoření State s neprázdným seznamem zpráv
  - Ověření správného chování při sloučení prázdného seznamu s neprázdným
  - Ověření správného chování při sloučení neprázdného seznamu s prázdným

#### test_add_messages_order_preservation
- **Popis**: Ověření zachování pořadí zpráv při sloučení
- **Status**: TODO
- **Verifikace**:
  - Vytvoření dvou instancí State s očíslovanými zprávami
  - Simulace sloučení stavů
  - Kontrola, že pořadí zpráv je zachováno po sloučení

### Integrace s LangGraph

#### test_state_in_langgraph_node
- **Popis**: Ověření kompatibility State se standardními uzly LangGraph
- **Status**: TODO
- **Verifikace**:
  - Definice jednoduchého uzlu grafu, který přijímá a aktualizuje State
  - Simulace volání uzlu s instancí State
  - Ověření, že aktualizace stavu je korektně zpracována
  - Kontrola, že uzel dokáže správně přistupovat k atributům State

#### test_state_company_analysis_update
- **Popis**: Testování aktualizace company_analysis v grafu
- **Status**: TODO
- **Verifikace**:
  - Vytvoření výchozího stavu s prázdným company_analysis
  - Definice uzlu, který nastaví company_analysis
  - Ověření, že nový stav obsahuje správně aktualizovaný company_analysis
  - Kontrola, že další uzly v grafu mohou číst aktualizovanou hodnotu

## Integritní testy

### test_state_serialization_deserialization
- **Popis**: Ověření serializace a deserializace State objektu
- **Status**: TODO
- **Verifikace**:
  - Vytvoření komplexní instance State
  - Serializace do JSON pomocí langchain_core serializačních utilit
  - Deserializace zpět na State objekt
  - Ověření, že všechny atributy byly zachovány

### test_state_in_complete_workflow
- **Popis**: Testování chování State v kompletním workflow
- **Status**: TODO
- **Verifikace**:
  - Integrace State do jednoduchého testovacího workflow
  - Spuštění workflow s inicializovaným state
  - Ověření, že stav je správně předáván mezi uzly
  - Kontrola finálního stavu po průchodu workflow

### test_state_with_different_message_types
- **Popis**: Ověření kompatibility s různými typy zpráv
- **Status**: TODO
- **Verifikace**:
  - Vytvoření State s různými typy zpráv (HumanMessage, AIMessage, SystemMessage)
  - Simulace průchodu takového stavu workflowem
  - Ověření, že všechny typy zpráv jsou správně zpracovány

## Poznámky k testování

### Techniky a nástroje
- **Dataclass validator** - pro testování invariantů dataclass objektů
- **Pytest fixtures** - pro sdílení testovacích instancí State
- **Mock objekty** - pro simulaci různých implementací AnalysisResult
- **LangGraph TestClient** - pro testování chování State v grafu
- **Frozen dataclasses** - zvážit testy s `frozen=True` pro ověření immutability

### Známé obtíže
1. **Komplexní objekty v State** - testování deserializace komplexních typů jako AnalysisResult
2. **Anotace v runtime** - LangGraph anotace jako `add_messages` fungují až při běhu grafu
3. **Typové kontroly** - Python runtime nevaliduje typy automaticky, je třeba to testovat explicitně
4. **LangGraph kompatibilita** - nutnost synchronizovat testy s aktuální verzí LangGraph (≥0.2.70)

### Doporučení pro budoucí testování
1. Přidat property-based testy pro ověření chování State s náhodnými daty
2. Implementovat benchmarky pro měření výkonnosti při velkém počtu zpráv
3. Testovat State v kombinaci s checkpointingem a perzistencí v LangGraph
4. Doplnit testy pro edge-case situace jako jsou cyklické reference nebo velmi velké objekty

---

*Poslední aktualizace: 19.4.2025*
