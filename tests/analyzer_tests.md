# Tests Documentation for analyzer.py Component

## Kritéria dokončení
- **100% pokrytí funkcí** (analyze_query, parse_response)
- **95% pokrytí kódu** pro `analyzer.py` (včetně všech logických větví a chybových stavů)
- **Minimální typy testů** pro každou funkci/metodu:
  - Úspěšné volání s validními daty (různé dotazy k analýze)
  - Zpracování chybových stavů (výjimky z LLM, nevalidní odpovědi)
  - Hraniční případy (prázdné odpovědi, nevalidní formáty, dotazy nesouvisející s firmami)
- **Správné mockování** LLM volání a modelů
- **Kontrola výstupních struktur** podle očekávaného TypedDict AnalysisResult

## Testovací případy

### Funkce: parse_response

#### test_parse_response (parametrizovaný test)
- **Popis**: Ověření parsování různých formátů odpovědí z LLM
- **Status**: DOKONČENO
- **Verifikace**:
  - Extrakce seznamu společností z odpovědi LLM (companies)
  - Nastavení primární společnosti (první v seznamu)
  - Správné určení typu analýzy (risk_comparison, common_suppliers, general)
  - Správné nastavení příznaku is_company_analysis
  - Výpočet hodnoty confidence na základě detekovaných dat
  - Ověření správného chování s extra mezerami
  - Ověření zpracování nevalidních typů analýzy
  - Ošetření prázdných odpovědí

### Funkce: analyze_query

#### test_analyze_query_success (parametrizovaný test)
- **Popis**: Ověření úspěšného volání a zpracování odpovědi z LLM
- **Status**: DOKONČENO
- **Verifikace**:
  - Správné sestavení a volání LCEL řetězce s dotazem
  - Předání odpovědi do funkce parse_response
  - Použití správného modelu pro analýzu
  - Ověření, že výsledek z parse_response je správně vrácen
  - Mockování: init_chat_model, chain.ainvoke, parse_response

#### test_analyze_query_exception
- **Popis**: Ověření chování při výjimce během volání LLM
- **Status**: DOKONČENO
- **Verifikace**:
  - Simulace výjimky z chain.ainvoke
  - Vrácení výchozího výsledku při chybě
  - Kontrola struktury výchozího výsledku
  - Mockování: init_chat_model, chain.ainvoke

#### test_analyze_query_non_company_query_mocked
- **Popis**: Ověření chování pro dotazy nesouvisející s firmami
- **Status**: DOKONČENO
- **Verifikace**:
  - Simulace odpovědi "; general" pro obecný dotaz
  - Ověření správného nastavení is_company_analysis=False
  - Ověření confidence=0.0 pro dotaz nesouvisející s firmami
  - Mockování: init_chat_model, chain.ainvoke, parse_response

#### test_analyze_query_custom_model
- **Popis**: Ověření použití vlastního modelu
- **Status**: TODO
- **Verifikace**:
  - Volání s vlastním parametrem model (např. "claude-3-opus")
  - Ověření, že init_chat_model je volán se správným parametrem
  - Mockování: init_chat_model, chain.ainvoke, parse_response

### Třída: CompanyAnalysisRequest (BaseModel)

#### test_company_analysis_request_validation
- **Popis**: Ověření validace Pydantic modelu CompanyAnalysisRequest
- **Status**: TODO
- **Verifikace**:
  - Vytvoření validní instance modelu
  - Ověření validace confidence v rozsahu 0.0-1.0
  - Test chyby při zadání nevalidní hodnoty confidence
  - Správná definice výchozích hodnot

## Integritní testy

### test_analyzer_prompt_format
- **Popis**: Ověření formátu a správnosti systémového promptu
- **Status**: TODO
- **Verifikace**:
  - Ověření, že prompt obsahuje instrukce ve správném formátu
  - Ověření, že prompt obsahuje všechny potřebné typy analýzy
  - Ověření, že příklady v promptu pokrývají všechny očekávané formáty

### test_end_to_end_analyze_query
- **Popis**: Integrační test kompletní funkce analyze_query s reálným LLM
- **Status**: TODO
- **Verifikace**:
  - Volání analyze_query s minimálním mockováním
  - Ověření, že LLM správně rozpoznává společnosti v různých dotazech
  - Ověření, že LLM správně rozpoznává typy analýzy
  - Poznámka: Spouštět jen při významných změnách promptu vzhledem k nákladům

## Poznámky k testování

### Techniky a nástroje
- **Parametrizované testy** (pytest.mark.parametrize): Pro efektivní testování různých vstupů a očekávaných výstupů
- **AsyncMock**: Pro testování asynchronních funkcí
- **patch dekorátor**: Pro nahrazení externích závislostí (init_chat_model, chain.ainvoke)
- **pytest.mark.asyncio**: Pro podporu testování asynchronních funkcí analyze_query
- **pytest-cov**: Pro měření pokrytí kódu testy

### Známé obtíže
1. **Nestabilita LLM odpovědí**: Reálné LLM mohou vracet mírně odlišné formáty odpovědí, což vyžaduje robustní parsování
2. **Balance mezi mocky a reálným testováním**: Příliš mnoho mocků může vést k falešné jistotě, zatímco reálné testy s LLM jsou nákladné
3. **Systémový prompt**: Změny v promptu mohou změnit formát odpovědí, což vyžaduje aktualizaci testů
4. **Zpracování nespecifikovaných formátů**: LLM může někdy vrátit neočekávaný formát, který testy nepokrývají

### Doporučení pro budoucí testování
1. Implementovat property-based testy s knihovnou hypothesis pro ověření robustnosti parsování
2. Vytvořit snapshot testování promptů pro zachycení neplánovaných změn
3. Přidat test, který ověřuje, že všechny tři typy analýzy jsou správně rozpoznány a zpracovány
4. Zlepšit měření a vyhodnocení hodnoty confidence pro přesnější indikaci jistoty analýzy

---

*Poslední aktualizace: 19.4.2025*
