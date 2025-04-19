<!-- filepath: /Users/marekminarovic/claude-code/memory-agent/tests/tools_tests_updated.md -->
# Tests Documentation for tools.py Component

## Kritéria dokončení
- **Pokrytí metod** všech tříd nástrojů (SayariApiTool, SupabaseInternalDataTool, SayariRelationshipsTool)
- **Pokrytí funkce** upsert_memory
- **Typy testů** pro každou funkci/metodu:
  - Úspěšné volání s validními daty
  - Zpracování chybových stavů
  - Hraniční případy

## Testovací případy

### SayariApiTool

- **Úspěšné volání Sayari API**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Správná struktura URL, extrakce dat, formát výstupu

- **Chování při HTTP chybě**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Zachycení HTTP chyby, ošetření výjimky

- **Chování při prázdné odpovědi**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Zpracování prázdného objektu, výchozí hodnoty

### SupabaseInternalDataTool

- **Úspěšné získání interních dat**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Sestavení URL, extrakce tier klasifikace, formát výstupu

- **Chování při HTTP chybě**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Zachycení HTTP chyby, ošetření výjimky

- **Chování při prázdné odpovědi**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Zpracování prázdného objektu, výchozí hodnoty

### SayariRelationshipsTool

- **Úspěšné získání vztahů**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Sestavení URL s entity_id, extrakce vztahů, formát výstupu

- **Chování při HTTP chybě**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Zachycení HTTP chyby, ošetření výjimky

- **Chování při prázdné odpovědi**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Zpracování prázdného objektu, výchozí hodnoty

### Funkce: upsert_memory

- **Úspěšné uložení nové paměti**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Generování UUID, volání store.upsert, návratová hodnota

- **Úspěšná aktualizace existující paměti**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Použití předaného memory_id, volání store.upsert

- **Chování při výjimce**
  - **Status**: PLÁNOVANÉ
  - **Ověření**: Zachycení výjimky, logování chyby, návratová hodnota

---

*Poslední aktualizace: 19.4.2025*
