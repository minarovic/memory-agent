# Komponenta Tools

## Přehled komponenty

Komponenta `tools.py` představuje kolekci nástrojů (tools), které rozšiřují schopnosti Memory Agent o interakci s externími systémy a zajišťují perzistenci dat. Hlavní zodpovědností této komponenty je:

1. **Komunikace s externími API** - poskytuje nástroje pro získávání dat ze Sayari API a Supabase
2. **Ukládání dat** - implementuje funkcionalitu pro ukládání paměťových záznamů do databáze
3. **Transformace dat** - zpracovává surové API odpovědi do strukturovaného formátu vhodného pro další použití v systému

Komponenta tools tvoří klíčovou část Memory Agent systému, která umožňuje agentu získávat informace z různých datových zdrojů a ukládat výsledky své činnosti. Nástroje jsou navrženy pro asynchronní provoz, což umožňuje efektivně zpracovávat více požadavků současně bez blokování hlavního provádění.

V rámci celkového workflow Memory Agent, nástroje z této komponenty jsou invokované hybridním workflow systémem, kde mohou být volány jak v rámci sekvenčního zpracování LangChain modelu, tak přímo jako součást reaktivního grafu pro zpracování konkrétních úloh.

## Datové struktury

Komponenta tools pracuje s následujícími klíčovými datovými strukturami:

### Vstupní parametry

- **UUID** - univerzální identifikátory používané pro jednoznačnou identifikaci paměťových záznamů
- **Řetězce** - textové vstupy jako názvy společností, kontextové informace, obsah paměti
- **Konfigurační objekty** - obsahující uživatelské ID a další nastavení

### Návratové hodnoty

- **Strukturované slovníky** - nástroje vracejí hierarchické slovníky (Dict[str, Any]) obsahující:
  - **Metadata entity** - základní informace o entitě (název, ID, typ)
  - **Rizikové analýzy** - hodnocení rizik, sankční status a rizikové faktory
  - **Interní klasifikace** - tier kategorizace, HS kódy a obchodní aktivity
  - **Vztahové struktury** - informace o vztazích mezi entitami včetně dat pro vizualizaci

### Výjimky

- **ToolException** - standardizovaný formát výjimek pro propagaci chyb z nástrojů
- **HTTPStatusError** - výjimky související s chybami při volání externích API
- **RequestError** - výjimky spojené s problémy při komunikaci s externími službami

## Tok dat

### 1. Komunikace s externími API

1. **Inicializace požadavku**
   - Formátování URL včetně query parametrů
   - Nastavení HTTP klienta (httpx.AsyncClient)

2. **Odeslání požadavku**
   - Asynchronní volání GET metody
   - Zpracování odpovědi a kontrola statusu

3. **Zpracování odpovědi**
   - Deserializace JSON odpovědi
   - Extrakce relevantních informací pomocí pomocných metod
   - Transformace do standardizovaného formátu pro další použití

4. **Ošetření chyb**
   - Zachycení a logování HTTP výjimek
   - Převod výjimek na ToolException pro konzistentní zpracování

### 2. Ukládání dat do paměti

1. **Validace vstupu**
   - Kontrola poskytnutých parametrů
   - Generování UUID pokud není poskytnuto

2. **Příprava dat**
   - Extrakce user_id z konfigurace
   - Formátování obsahu a kontextu do standardní struktury

3. **Persistentní uložení**
   - Volání store.aput pro uložení dat
   - Ukládání pod kombinovaným klíčem (memories, user_id) a identifikátorem záznamu

4. **Potvrzení operace**
   - Vytvoření potvrzující zprávy o uložení
   - Logování výsledku operace

## Seznam nástrojů a metod

Komponenta tools implementuje následující hlavní nástroje:

- [upsert_memory](/docs/components/tools/upsert_memory_tools.md) - Asynchronní funkce pro ukládání paměťových záznamů do databáze
- [SayariApiTool](/docs/components/tools/SayariApiTool_tools.md) - Nástroj pro získávání informací o společnostech z Sayari API
- [SupabaseInternalDataTool](/docs/components/tools/SupabaseInternalDataTool_tools.md) - Nástroj pro získávání interních dat o společnostech ze Supabase
- [SayariRelationshipsTool](/docs/components/tools/SayariRelationshipsTool_tools.md) - Nástroj pro získávání vztahů mezi entitami z Sayari API

## Interakce nástrojů

### Integrace s ostatními komponentami

1. **Interakce s analyzátorem** (analyzer.py)
   - Nástroje poskytují data, která jsou následně zpracována a analyzována v komponentě analyzer
   - Výsledky analýz jsou strukturovány tak, aby odpovídaly očekávanému formátu pro analýzu

2. **Interakce se stavem** (state.py)
   - Nástroj `upsert_memory` ukládá data do stavového objektu (store)
   - Stav je sdílen mezi voláními a umožňuje perzistenci informací

3. **Interakce s workflow grafem** (graph.py)
   - Nástroje jsou registrovány jako uzly v reaktivním grafu
   - Výstupy nástrojů jsou předávány dalším uzlům grafu pro další zpracování
   - Stav vrácený nástroji je součástí celkového stavu grafu

### Využití v rámci workflow

1. **Sekvenční zpracování**
   - Nástroje jsou volány v definované posloupnosti v rámci hybridního workflow
   - Výstup jednoho nástroje může sloužit jako vstup pro další

2. **Paralelní zpracování**
   - Některé nástroje mohou být volány paralelně pro urychlení získávání dat
   - Například současné získávání dat ze Sayari API a interních dat ze Supabase

3. **Podmíněné volání**
   - Na základě analyzovaných dat mohou být volány další specifické nástroje
   - Například pokud je nalezeno ID entity, může být volán `SayariRelationshipsTool`

## Testování komponenty

### Přístupy k testování

1. **Unit testy**
   - Testování jednotlivých nástrojů izolovaně
   - Využití pytest frameworku pro asynchronní testování
   - Implementace pomocných tříd (MockResponse) pro simulaci HTTP odpovědí

2. **Mock testování**
   - Využití unittest.mock pro simulaci externích závislostí
   - Vytváření mock objektů pro httpx.AsyncClient a jeho metody
   - Simulace různých scénářů odpovědí (úspěšné i chybové stavy)

3. **Funkcionální testy**
   - Testování integrace nástrojů s ostatními komponentami
   - Ověřování celkového workflow s využitím nástrojů

### Klíčové testovací scénáře

1. **Ukládání paměti**
   - Úspěšné uložení nového záznamu
   - Aktualizace existujícího záznamu
   - Chybové stavy při ukládání (chybějící user_id, chyba databáze)

2. **API nástroje**
   - Úspěšné volání API a zpracování odpovědi
   - Zpracování prázdných nebo neúplných odpovědí
   - Správné formátování výstupů pro další zpracování
   - Ošetření HTTP chyb (404, 500) a výjimek při komunikaci

3. **Vztahové nástroje**
   - Extrakce a kategorizace vztahů z API odpovědí
   - Generování vizualizačních dat pro grafy vztahů
   - Zpracování prázdných vztahových dat

### Příklady mock testování API volání

```python
@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_sayari_api_tool_success(mock_get):
    """Test úspěšného volání Sayari API."""
    # Setup mock response s testovacími daty
    mock_get.return_value = MockResponse(MOCK_SAYARI_DATA)
    
    # Vytvoření nástroje a volání metody
    tool = SayariApiTool()
    result = await tool._arun("Test Company")
    
    # Ověření volání a výsledků
    mock_get.assert_called_once()
    assert "search/entity" in mock_get.call_args[0][0]
    assert result["entity_id"] == "test-entity-id-123"
```

Výše uvedený příklad ukazuje, jak lze pomocí mock objektů simulovat volání externích API a ověřit správné chování nástroje bez skutečného zasílání požadavků na vzdálené servery.
