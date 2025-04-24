# upsert_memory

## Účel a kontext

Funkce `upsert_memory` je základním prvkem Memory Agent systému, který zajišťuje ukládání a aktualizaci paměťových záznamů v databázi. Tato funkce implementuje tzv. "upsert" operaci (kombinace insert a update), která umožňuje buď vytvoření nového záznamu, nebo aktualizaci existujícího, pokud je nalezena shoda podle identifikátoru.

### Role v celkovém workflow

V rámci Memory Agent systému plní funkce `upsert_memory` následující role:

1. **Perzistence paměťových záznamů** - zajišťuje, že informace získané nebo odvozené agentem jsou trvale uloženy pro budoucí interakce
2. **Prevence duplicit** - umožňuje aktualizaci existujících záznamů místo vytváření duplicitních informací
3. **Korekce informací** - podporuje mechanismus pro opravu nebo upřesnění dříve uložených informací na základě nových zjištění
4. **Kontextuální ukládání** - umožňuje uchovat nejen samotný obsah paměti, ale i kontext, ve kterém byla informace získána

Funkce je typicky volána po zpracování uživatelského vstupu nebo po analýze dat, kdy agent identifikuje informaci, kterou je vhodné si zapamatovat. Díky propojení s `BaseStore` a konfigurací agenta může být paměť uchovávána v různých typech úložišť a asociována s konkrétním uživatelem.

## Implementační šablona

```python
async def upsert_memory(
    content: str,
    context: str,
    *,
    memory_id: Optional[uuid.UUID] = None,
    # Hide these arguments from the model.
    config: Annotated[RunnableConfig, InjectedToolArg],
    store: Annotated[BaseStore, InjectedToolArg],
) -> str:
    """Upsert a memory in the database.

    If a memory conflicts with an existing one, then just UPDATE the
    existing one by passing in memory_id - don't create two memories
    that are the same. If the user corrects a memory, UPDATE it.

    Args:
        content: The main content of the memory. For example:
            "User expressed interest in learning about French."
        context: Additional context for the memory. For example:
            "This was mentioned while discussing career options in Europe."
        memory_id: ONLY PROVIDE IF UPDATING AN EXISTING MEMORY.
        The memory to overwrite.
        config: Runnable configuration injected automatically, contains user_id.
        store: BaseStore instance injected automatically, provides database access.
        
    Returns:
        A confirmation message with the memory ID.
        
    Raises:
        ValueError: When user_id cannot be extracted from config.
        RuntimeError: When database operation fails.
    """
    try:
        # Log start of operation with truncated content for brevity
        logger.info(f"Upserting memory: content='{content[:50]}...'")
        
        # Generate new UUID if not provided, otherwise use the existing one for update
        mem_id = memory_id or uuid.uuid4()
        logger.debug(f"Memory ID: {mem_id}")
        
        # Extract user ID from the injected configuration
        try:
            # Configuration helper extracts user_id from runnable config
            user_id = Configuration.from_runnable_config(config).user_id
            logger.debug(f"User ID: {user_id}")
        except Exception as e:
            # Log detailed error for debugging
            logger.error(f"Error extracting user_id from config: {str(e)}")
            logger.error(traceback.format_exc())
            # Re-raise as ValueError with clear message
            raise ValueError(f"Failed to get user_id from configuration: {str(e)}")
        
        # Create memory data structure with content and context
        memory_data = {"content": content, "context": context}
        logger.debug(f"Memory data: {memory_data}")
        
        # Store memory in the database using BaseStore interface
        try:
            logger.info(f"Storing memory {mem_id} for user {user_id}")
            # Use composite key structure (memories, user_id) with memory ID as the key
            await store.aput(
                ("memories", user_id),  # Collection identifier
                key=str(mem_id),       # Memory ID as string
                value=memory_data,     # Memory content and context
            )
            logger.info(f"Successfully stored memory {mem_id}")
        except Exception as e:
            # Log detailed database error
            logger.error(f"Database error storing memory: {str(e)}")
            logger.error(traceback.format_exc())
            # Re-raise as RuntimeError for database issues
            raise RuntimeError(f"Failed to store memory in database: {str(e)}")
        
        # Return confirmation message with memory ID
        return f"Stored memory {mem_id}"
    except Exception as e:
        # Catch-all for any other exceptions
        error_msg = f"Error in upsert_memory: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        # Return error message instead of raising to prevent workflow disruption
        return f"Failed to store memory: {str(e)}"
```

## Omezení a hranice

### Technická omezení

1. **Asynchronní provádění** - funkce je implementována jako asynchronní (`async`), což vyžaduje její volání v asynchronním kontextu
2. **Závislost na externích službách** - funkce vyžaduje konfiguraci a BaseStore instanci, které jsou do ní injektovány
3. **Omezení formátu dat** - paměťové záznamy jsou ukládány pouze s obsahem a kontextem, bez pokročilé struktury nebo metadat
4. **Ošetření chyb** - globální zachytávání výjimek může skrýt specifické problémy ve vnitřním kódu

### Designová omezení

1. **Jednoduchá datová struktura** - ukládány jsou pouze dva textové řetězce (content, context) bez možnosti ukládat složitější struktury
2. **Absence validace** - funkce neprovádí žádnou validaci vstupních dat (např. maximální délka, formátování)
3. **Bez kontroly duplicit** - detekce potenciálních duplicit je ponechána na volajícím kódu
4. **Absence tagování** - chybí možnost přiřadit paměti tagy nebo kategorie pro lepší organizaci a vyhledávání

## Postup implementace

### Příprava závislostí

1. **Import potřebných knihoven**:
   ```python
   import logging
   import traceback
   import uuid
   from typing import Annotated, Dict, Any, Optional

   from langchain_core.runnables import RunnableConfig
   from langchain_core.tools import InjectedToolArg, BaseTool
   from langgraph.store.base import BaseStore

   from memory_agent.configuration import Configuration
   ```

2. **Nastavení loggeru**:
   ```python
   logger = logging.getLogger(__name__)
   ```

### Vlastní implementace

1. **Definice funkce s anotacemi**:
   - Definovat hlavičku funkce s odpovídajícími parametry
   - Pro parametry injektované automaticky použít Annotated s InjectedToolArg

2. **Implementace hlavního bloku**:
   - Obalit kód do try-except pro zachycení všech výjimek
   - Připravit identifikátor paměti (existující nebo nový)
   - Získat uživatelské ID z konfigurace
   - Vytvořit strukturu paměťového záznamu
   - Uložit záznam do databáze
   - Vrátit potvrzující zprávu

3. **Ošetření chybových stavů**:
   - Implementovat vnořené try-except bloky pro zachycení specifických výjimek
   - Logovat chyby s dostatečným detailem pro diagnostiku problémů
   - Převádět nízkoúrovňové výjimky na smysluplnější chybová hlášení

### Testování implementace

1. **Unit testy**:
   - Test úspěšného vložení nové paměti
   - Test aktualizace existující paměti
   - Test chování při chybějícím user_id
   - Test chování při selhání databáze

2. **Integrační testy**:
   - Test integrace s reálným BaseStore
   - Test v rámci workflow grafu

## Struktura vstupních a výstupních dat

### Vstupní parametry

1. **content** (str):
   - Hlavní obsah paměti
   - Příklad: "User expressed interest in learning about French."
   - Povinný parametr

2. **context** (str):
   - Dodatečný kontext k paměti
   - Příklad: "This was mentioned while discussing career options in Europe."
   - Povinný parametr

3. **memory_id** (Optional[uuid.UUID]):
   - Identifikátor existující paměti pro aktualizaci
   - Nepovinný parametr, výchozí hodnota None
   - Pokud není zadán, vygeneruje se nový UUID

4. **config** (RunnableConfig):
   - Automaticky injektovaná konfigurace
   - Obsahuje user_id a další nastavení
   - Neposkytuje se při volání, injektuje se automaticky

5. **store** (BaseStore):
   - Automaticky injektovaná instance úložiště
   - Poskytuje metody pro práci s databází
   - Neposkytuje se při volání, injektuje se automaticky

### Výstupní data

Funkce vrací řetězec (str) s potvrzující zprávou, který obsahuje identifikátor uložené paměti:

- Úspěch: `"Stored memory 123e4567-e89b-12d3-a456-426614174000"`
- Chyba: `"Failed to store memory: [popis chyby]"`

### Struktura uložených dat

Data ukládaná do databáze mají následující strukturu:

```python
{
    "content": "User expressed interest in learning about French.",
    "context": "This was mentioned while discussing career options in Europe."
}
```

Data jsou ukládána pod klíčem ve formátu:

```
("memories", "user-id-123") -> {"memory-id-456": {"content": "...", "context": "..."}}
```

## Výsledná implementace

_Toto místo je vyhrazeno pro finální implementaci po schválení a kódové revizi._

## Instrukce pro dokumentaci

1. Dokumentace by měla obsahovat příklady volání funkce v různých scénářích
2. Popsat, jak vhodně formulovat obsah a kontext paměťových záznamů
3. Vysvětlit strategii aktualizace záznamů vs. vytváření nových
4. Popsat způsob vyhledávání existujících paměťových záznamů
5. Uvést příklady zpracování chyb a jejich řešení
6. Zdokumentovat integraci s ostatními komponentami Memory Agent systému

## Dokumentace implementace

_Toto místo je vyhrazeno pro dokumentaci finální implementace po jejím dokončení._
