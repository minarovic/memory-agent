# Komponenta Analyzer

## Přehled komponenty

Komponenta **Analyzer** je zodpovědná za analýzu uživatelských dotazů a extrakci důležitých informací, které jsou dále využívány v rámci Memory Agent systému. Slouží jako vstupní brána pro porozumění uživatelského záměru a identifikaci klíčových entit (především společností) v textu dotazu. 

Hlavní funkcí této komponenty je transformovat nestrukturovaný text od uživatele do strukturované podoby, která umožňuje systému rozhodnout, jaký typ analýzy má být proveden a na které společnosti se má zaměřit. Analyzer využívá pokročilé jazykové modely (LLM) pro porozumění přirozenému jazyku a extrakci relevantních informací.

Komponenta je navržena s důrazem na:
- Přesnou identifikaci zmíněných společností/firem
- Správné rozpoznání požadovaného typu analýzy
- Zhodnocení úrovně jistoty této analýzy
- Robustní zpracování chybových stavů

## Datové struktury

Komponenta Analyzer pracuje s následujícími klíčovými datovými strukturami:

### AnalysisType
Enum (Literal) definující podporované typy analýz:
- `"risk_comparison"` - analýza a porovnání rizik
- `"common_suppliers"` - analýza dodavatelsko-odběratelských vztahů
- `"general"` - obecné informace a dotazy

### AnalysisResult
TypedDict reprezentující výsledek analýzy uživatelského dotazu:
```python
{
    "companies": List[str],           # Seznam identifikovaných společností
    "company": str,                   # Primární společnost (první v seznamu)
    "analysis_type": AnalysisType,    # Typ požadované analýzy
    "query": str,                     # Původní dotaz uživatele
    "is_company_analysis": bool,      # Zda jde o analýzu konkrétní společnosti
    "confidence": float               # Úroveň jistoty analýzy (0.0 - 1.0)
}
```

### CompanyAnalysisRequest
Pydantic BaseModel definující schéma požadavku na analýzu společnosti:
- `companies`: Seznam identifikovaných společností
- `analysis_type`: Typ požadované analýzy 
- `is_company_analysis`: Indikátor, zda se jedná o analýzu společnosti
- `confidence`: Úroveň jistoty analýzy (validovaná na rozmezí 0.0 - 1.0)

## Tok dat

Proces analýzy v komponentě Analyzer probíhá v následujících krocích:

1. **Vstup dotazu** - Uživatelský dotaz v přirozeném jazyce je přijat metodou `analyze_query`
2. **Inicializace LLM modelu** - Je inicializován jazykový model podle specifikované konfigurace
3. **Sestavení LCEL řetězce** - Je vytvořen řetězec `prompt | llm | StrOutputParser` pro zpracování dotazu
4. **Asynchronní zpracování** - Dotaz je asynchronně předán do LLM modelu
5. **Parsování odpovědi** - Výstup z LLM je zpracován pomocí `parse_response` funkce
6. **Strukturovaný výsledek** - Je vytvořena výsledná struktura `AnalysisResult`
7. **Ošetření chyb** - V případě chyby je vrácen výchozí výsledek

Tok dat je optimalizován pro asynchronní zpracování, což umožňuje efektivní paralelizaci při větším množství dotazů.

## Seznam metod komponenty

Komponenta Analyzer obsahuje následující klíčové metody:

- [**analyze_query**](/docs/components/analyzer/analyze_query_analyzer.md) - Hlavní metoda pro analýzu uživatelského vstupu
- [**parse_response**](/docs/components/analyzer/parse_response_analyzer.md) - Metoda pro parsování odpovědi z LLM do strukturované podoby

## Interakce metod

Interakce mezi metodami komponenty Analyzer:

1. **analyze_query** je primárním vstupním bodem komponenty
   - Přijímá uživatelský vstup a volitelnou konfiguraci
   - Inicializuje LLM model a vytváří LCEL řetězec
   - Asynchronně volá LLM pro analýzu dotazu
   - Volá `parse_response` pro zpracování odpovědi z LLM
   - Vrací strukturovaný výsledek nebo výchozí hodnoty při chybě

2. **parse_response** zpracovává výstup z LLM
   - Přijímá textovou odpověď z LLM a původní uživatelský dotaz
   - Parsuje formátovanou odpověď ve tvaru "Company name; analysis_type"
   - Identifikuje seznam společností, typ analýzy a nastavuje úroveň jistoty
   - Sestavuje a vrací kompletní `AnalysisResult` strukturu

Obě metody spolupracují na transformaci nestrukturovaného vstupu do strukturované podoby, kterou mohou další komponenty systému (jako Graph nebo Tools) dále zpracovávat.

## Testování komponenty

Testování komponenty Analyzer je rozděleno do několika úrovní:

### Jednotkové testy
- Testy v souboru `tests/unit_tests/test_analyzer.py`
- Zaměření na izolované testování jednotlivých metod
- Mock LLM odpovědí pro testování `parse_response`
- Validace správného formátování výstupu `AnalysisResult`

### Funkční testy
- Testy v souborech `test_analyzer_simple.py` a `test_analyzer.py`
- Testování end-to-end funkcionality s různými typy dotazů
- Ověření správné identifikace společností a typů analýz

### Integrační testy
- Testy interakce s ostatními komponentami systému
- Validace správného předávání dat mezi komponentami

### Přístup k testování
Při testování této komponenty je klíčové:
1. Testovat různé formáty uživatelských vstupů
2. Ověřit správnou extrakci společností a typů analýz
3. Testovat odolnost vůči nejednoznačným nebo neúplným dotazům
4. Validovat správné chování při chybových stavech
5. Měřit přesnost a konzistentnost analýzy při různých formulacích dotazů

Důležitou součástí testování je použití předem definovaných testovacích případů s očekávanými výstupy pro ověření stability a přesnosti analýzy.
