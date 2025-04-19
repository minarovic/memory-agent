# Tools Component Documentation

## 1. Základní informace

**Status:** V PROCESU  
**Popis:** Nástroje pro přístup k externím API (Sayari) a interním datovým zdrojům (Supabase) pro získávání informací o společnostech a jejich vztazích.  
**Verze:** 1.1  
**Priorita:** Vysoká  
**Stav implementace:** 80% dokončeno (chybí dokončit testy pro SayariRelationshipsTool a upsert_memory)

### Závislosti
- `httpx`: Pro asynchronní HTTP požadavky
- `uuid`: Pro generování jedinečných identifikátorů
- `langchain_core.tools`: Základní třídy pro nástroje
- `langchain_core.runnables`: Pro typování RunnableConfig
- `langgraph.store.base`: Pro přístup k BaseStore

### Umístění
- Soubor: `src/memory_agent/tools.py`
- Testy: `tests/unit_tests/test_tools.py`, `tests/unit_tests/test_tools_upsert_memory.py`
- Dokumentace: `docs/components/tools.md`

## 2. API

### Funkce

#### `async def upsert_memory`

Ukládá nebo aktualizuje paměť v databázi.

**Parametry:**
- `content` (str): Hlavní obsah paměti
- `context` (str): Dodatečný kontext pro paměť
- `memory_id` (Optional[uuid.UUID]): ID existující paměti (pouze při aktualizaci)
- `config` (Annotated[RunnableConfig, InjectedToolArg]): Konfigurace pro běh
- `store` (Annotated[BaseStore, InjectedToolArg]): Úložiště pro paměti

**Návratová hodnota:** 
- `str`: Zpráva o úspěšném uložení nebo chybě

**Status:** V PROCESU (čeká na dokončení testů)

### Třídy

#### `SayariApiTool`

Nástroj pro volání Sayari API a získání informací o společnosti.

**Vlastnosti:**
- `name` (str): "sayari_api_tool"
- `description` (str): "Získává informace o společnosti z Sayari API"
- `base_url` (ClassVar[str]): URL pro Sayari API

**Metody:**
- `async def _arun(self, company_name: str) -> Dict[str, Any]`: Hlavní asynchronní metoda pro volání API
- `def _extract_entities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]`: Extrakce entit z odpovědi API
- `def _extract_entity_id(self, data: Dict[str, Any]) -> Optional[str]`: Extrakce ID entity
- `def _extract_risk_data(self, data: Dict[str, Any]) -> Dict[str, Any]`: Extrakce dat o riziku

**Status:** DOKONČENO

#### `SupabaseInternalDataTool`

Nástroj pro získání interních dat o společnosti ze Supabase.

**Vlastnosti:**
- `name` (str): "supabase_internal_data_tool"
- `description` (str): "Získává interní data o společnosti včetně tier klasifikace a HS kódů"
- `base_url` (ClassVar[str]): URL pro Supabase API

**Metody:**
- `async def _arun(self, company_name: str) -> Dict[str, Any]`: Hlavní asynchronní metoda pro volání API
- `def _process_internal_data(self, data: Dict[str, Any], company_name: str) -> Dict[str, Any]`: Zpracování interních dat

**Status:** DOKONČENO

#### `SayariRelationshipsTool`

Nástroj pro získání vztahů entity z Sayari API.

**Vlastnosti:**
- `name` (str): "sayari_relationships_tool"
- `description` (str): "Získává vztahy entity (společnosti) z Sayari API"
- `base_url` (ClassVar[str]): URL pro Sayari API

**Metody:**
- `async def _arun(self, entity_id: str) -> Dict[str, Any]`: Hlavní asynchronní metoda pro volání API
- `def _process_relationships(self, data: Dict[str, Any]) -> Dict[str, List[str]]`: Zpracování vztahů z odpovědi API
- `def _create_visualization(self, data: Dict[str, Any]) -> Dict[str, Any]`: Vytvoření vizualizačních dat pro vztahy
- `def _get_node_color(self, node_type: str) -> str`: Určení barvy uzlu podle typu
- `def _get_edge_color(self, edge_type: str) -> str`: Určení barvy hrany podle typu vztahu

**Status:** V PROCESU (čeká na testy pro úspěšnou odpověď a prázdné ID)

## 3. Historie změn

### v1.1 (19.4.2025)
- Přidáno ošetření chyb při volání API
- Vylepšena vizualizace vztahů společností
- Implementace cachování výsledků API pro zrychlení opakovaných požadavků

#### Příklad použití SayariApiTool:
```python
# Inicializace nástroje
sayari_tool = SayariApiTool()

# Asynchronní volání 
company_data = await sayari_tool._arun("Acme Corporation")

# Data obsahují strukturované informace:
# {
#    "company": "Acme Corporation",
#    "external_data": { "has_results": True, "entities": [...] },
#    "entity_id": "abc123",
#    "risk_analysis": {
#        "sanctions_status": "Žádné aktivní sankce nenalezeny",
#        "risk_score": "10",
#        "risk_factors": ["location_risk", "ownership_obscurity"]
#    }
# }
```

### v1.0 (1.4.2025)
- Základní implementace SayariApiTool
- Základní implementace SupabaseInternalDataTool
- Základní implementace SayariRelationshipsTool
- Počáteční verze upsert_memory funkce

#### Příklad integrační implementace ve workflow:
```python
async def fetch_company_data(state: State, config: RunnableConfig) -> dict:
    """Získá data o společnosti pomocí Sayari API."""
    try:
        # Získání informací o společnosti z předchozího kroku
        company_name = state.company_analysis.get("company", "")
        
        # Použití nástroje pro volání API
        sayari_tool = SayariApiTool()
        company_data = await sayari_tool._arun(company_name)
        
        # Aktualizace stavu
        return {"company_data": company_data}
    except Exception as e:
        logger.error(f"Error in fetch_company_data: {str(e)}")
        return {}
```

## 4. Vyzkoušené přístupy

### 1. Synchronní vs. Asynchronní implementace
Původně jsme implementovali nástroje se synchronními voláními API pomocí `requests`. To však způsobovalo blokování celého workflow. Následně jsme přešli na asynchronní implementaci pomocí `httpx`, což výrazně zlepšilo výkon.

**Před:**
```python
def _run(self, company_name: str) -> Dict[str, Any]:
    response = requests.get(f"{self.base_url}?q={company_name}")
    data = response.json()
    # Zpracování dat...
```

**Po:**
```python
async def _arun(self, company_name: str) -> Dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{self.base_url}?q={company_name}")
        data = response.json()
    # Zpracování dat...
```

### 2. Extrakce a zpracování dat
Pro extrakci a zpracování dat jsme vyzkoušeli dva přístupy:
1. Zpracování dat přímo v metodě `_arun`
2. Vyčlenění zpracování dat do samostatných metod

Druhý přístup se ukázal jako lepší z hlediska udržitelnosti kódu a testovatelnosti. Umožnil nám izolovaně testovat logiku zpracování dat bez nutnosti mockování HTTP požadavků.

### 3. Vizualizace vztahů
Pro vizualizaci vztahů jsme experimentovali s různými formáty dat:
1. Jednoduchý seznam hran
2. Graph objekt v D3.js formátu
3. Komplexní struktura s uzly a hranami včetně vizuálních atributů

Nakonec jsme zvolili třetí přístup, který poskytuje nejvíce flexibility pro vizualizaci na frontend straně.

## 5. Známé problémy

### 1. Omezení API
- Sayari API má limit 10 požadavků za minutu. Při překročení vrací HTTP 429.
- Supabase má omezení na velikost odpovědi (10MB), což může být problém při velmi rozsáhlých datových sadách.

### 2. Zpracování chyb
- Při chybě v jednom nástroji může dojít k přerušení celého workflow. Potřebujeme robustnější přístup s graceful degradation.

### 3. Validace dat
- Chybí schémata pro validaci dat získaných z API.
- V některých případech API vrací neočekávaný formát dat, což způsobuje chyby při zpracování.

### 4. Otevřené úkoly
- Dokončit testy pro `SayariRelationshipsTool._arun` s validním ID a prázdným ID
- Implementovat testy pro `upsert_memory` funkci
- Přidat cachování výsledků API pro snížení počtu volání
- Vytvořit mock server pro testování bez závislosti na externích API

---

*Poslední aktualizace: 19.4.2025*
