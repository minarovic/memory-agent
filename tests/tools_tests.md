# Tests Documentation for tools.py Component

## Kritéria dokončení
- **100% pokrytí metod** všech tříd nástrojů (SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool)
- **95% pokrytí kódu** pro `tools.py` (všechny větve, výjimky)
- **Minimální typy testů** pro každou funkci/metodu:
  - Úspěšné volání s validními daty
  - Zpracování chybových stavů (HTTP chyby, neočekávaná data)
  - Hraniční případy (prázdné vstupy, chybějící data)
- **Správné mockování** všech externích závislostí (HTTP požadavky, BaseStore)
- **Kontrola výstupních struktur** podle očekávaných schémat

## Testovací případy

### SayariApiTool

#### test_sayari_api_tool_success
- **Popis**: Ověření úspěšného volání Sayari API a zpracování odpovědi
- **Status**: DOKONČENO
- **Verifikace**:
  - Správné sestavení URL s parametrem názvu společnosti
  - Parsování a extrakce ID entity
  - Extrakce entit včetně jejich atributů
  - Extrakce dat o riziku včetně risk_score a risk_factors
  - Ověření celkové struktury vráceného objektu

#### test_sayari_api_tool_error
- **Popis**: Ověření chování při HTTP chybě z Sayari API
- **Status**: DOKONČENO
- **Verifikace**:
  - HTTP chyba 404 vyvolává výjimku přes raise_for_status
  - Chyba je zachycena jako Exception
  - API je voláno se správnými parametry

#### test_sayari_api_tool_empty_result
- **Popis**: Ověření chování při prázdné odpovědi z API
- **Status**: TODO
- **Verifikace**:
  - API vrací prázdný objekt bez chyby (HTTP 200)
  - Ověření, že nástroj vrací výchozí hodnoty pro chybějící data
  - Ověření, že entity_id je None
  - Ověření přítomnosti všech očekávaných polí i při prázdné odpovědi

### SupabaseInternalDataTool

#### test_supabase_internal_data_tool_success
- **Popis**: Ověření úspěšného volání interních dat ze Supabase
- **Status**: DOKONČENO
- **Verifikace**:
  - Správné sestavení URL s parametrem názvu společnosti
  - Extrakce tier klasifikace
  - Extrakce HS kódů
  - Extrakce obchodních aktivit
  - Ověření struktury vráceného objektu

#### test_supabase_internal_data_tool_error
- **Popis**: Ověření chování při HTTP chybě z Supabase API
- **Status**: DOKONČENO
- **Verifikace**:
  - HTTP chyba 500 vyvolává výjimku
  - Chyba je zachycena
  - API je voláno se správnými parametry

#### test_supabase_internal_data_tool_empty_data
- **Popis**: Ověření chování při prázdné nebo neúplné odpovědi
- **Status**: TODO
- **Verifikace**:
  - API vrací prázdný objekt nebo objekt bez očekávaných polí
  - Ověření, že _process_internal_data správně zpracovává chybějící data
  - Ověření přítomnosti všech očekávaných polí i při neúplných datech

### SayariRelationshipsTool

#### test_sayari_relationships_tool_success
- **Popis**: Ověření úspěšného volání vztahů z Sayari API
- **Status**: V PROCESU
- **Verifikace**:
  - Správné sestavení URL s ID entity
  - Zpracování entit a vztahů z odpovědi
  - Extrakce suppliers, customers a ownership vztahů
  - Vytvoření vizualizačních dat včetně uzlů a hran
  - Správné mapování barev pro typy uzlů a hran

#### test_sayari_relationships_tool_empty_id
- **Popis**: Ověření chování při volání s prázdným ID
- **Status**: V PROCESU
- **Verifikace**:
  - API není voláno, když ID je prázdné
  - Vrácený objekt obsahuje indikaci absence vztahů (has_relationships=False)
  - Prázdné seznamy pro suppliers, customers, ownership, key_relationships
  - Prázdné vizualizační struktury (nodes=[], links=[])

#### test_sayari_relationships_tool_error
- **Popis**: Ověření chování při HTTP chybě
- **Status**: TODO
- **Verifikace**:
  - HTTP chyba 500 vyvolává výjimku
  - Chyba je zachycena
  - API je voláno se správnými parametry

#### test_sayari_relationships_tool_no_relationships
- **Popis**: Ověření chování při prázdném seznamu vztahů
- **Status**: TODO
- **Verifikace**:
  - API vrací objekt s prázdným seznamem relationships
  - Vrácený objekt má has_relationships=False
  - Prázdné seznamy pro suppliers, customers, ownership, key_relationships
  - Prázdné vizualizační struktury

### upsert_memory funkce

#### test_upsert_memory_success
- **Popis**: Ověření úspěšného uložení paměti s explicitním memory_id
- **Status**: DOKONČENO
- **Verifikace**:
  - Správné použití poskytnutého memory_id
  - Správné volání store.aput s očekávanými parametry
  - Správná struktura uložených dat (content, context)
  - Návratová hodnota obsahuje identifikátor uložené paměti

#### test_upsert_memory_auto_id
- **Popis**: Ověření generování UUID při neuvedení memory_id
- **Status**: DOKONČENO
- **Verifikace**:
  - Automatické vygenerování UUID, když memory_id není poskytnuto
  - Správné volání store.aput s validním UUID
  - Správná struktura uložených dat
  - Návratová hodnota obsahuje identifikátor uložené paměti

#### test_upsert_memory_config_error
- **Popis**: Ověření chování při chybě v konfiguraci
- **Status**: DOKONČENO
- **Verifikace**:
  - Zachycení výjimky při získávání user_id z konfigurace
  - store.aput není volán při chybě konfigurace
  - Návratová hodnota obsahuje informaci o chybě

#### test_upsert_memory_database_error
- **Popis**: Ověření chování při chybě databáze
- **Status**: DOKONČENO
- **Verifikace**:
  - Zachycení výjimky při volání store.aput
  - Návratová hodnota obsahuje informaci o chybě databáze

## Integritní testy

### test_tools_workflow_integration
- **Popis**: Ověření spolupráce nástrojů v celkovém workflow
- **Status**: TODO
- **Verifikace**:
  - Sekvenční volání SayariApiTool, SayariRelationshipsTool a SupabaseInternalDataTool
  - Předání ID entity z výstupu SayariApiTool do vstupu SayariRelationshipsTool
  - Sloučení dat z různých zdrojů do jednotné struktury
  - Ověření chování při výpadku jednoho z API zdrojů

### test_memory_persistence
- **Popis**: Ověření ukládání a načítání paměti v reálném prostředí
- **Status**: TODO
- **Verifikace**:
  - Uložení paměti pomocí upsert_memory
  - Pozdější načtení téže paměti pomocí BaseStore
  - Ověření perzistence dat napříč různými běhy

## Poznámky k testování

### Techniky a nástroje
- **Mockování HTTP požadavků**: Využíváme třídu `MockResponse` pro simulaci HTTP odpovědí
- **AsyncMock**: Pro testování asynchronních funkcí a metod
- **patch dekorátor**: Pro nahrazení externích závislostí (httpx.AsyncClient.get)
- **pytest.mark.asyncio**: Pro podporu testování asynchronních funkcí
- **pytest-cov**: Pro měření pokrytí kódu testy

### Známé obtíže
1. **Testování vizualizace**: Je obtížné ověřit správnost generovaných vizualizačních dat (barvy, tvary), protože jde o komplexní strukturu
2. **Chybějící schémata**: Chybí formální definice očekávaných dat, což komplikuje validaci
3. **Závislost na externích API**: Mockování HTTP odpovědí nemusí plně odrážet chování reálného API
4. **Odhalování chyb**: Některé chyby se projevují pouze při integraci více nástrojů, nikoli při jednotkovém testování

### Doporučení pro budoucí testování
1. Implementovat validační schéma pro výstupní data nástrojů
2. Přidat property-based testy pro ověření chování s různými vstupními daty
3. Vytvořit test suite pro integrační testování celého workflow
4. Implementovat mock server pro simulaci Sayari a Supabase API pro komplexnější integrační testy

---

*Poslední aktualizace: 19.4.2025*
