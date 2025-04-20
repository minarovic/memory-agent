# Metoda parse_response komponenty analyzer

## Účel a kontext metody

Metoda `parse_response` je klíčovou součástí komponenty `analyzer`, která zpracovává odpovědi získané z jazykového modelu (LLM) a převádí je do strukturovaného formátu `AnalysisResult`. Tato metoda úzce spolupracuje s metodou `analyze_query`, která je zodpovědná za získávání surových odpovědí z LLM.

Hlavním účelem této metody je:
1. Parsovat formátovanou odpověď z LLM ve formátu "Company name; analysis_type"
2. Identifikovat seznam zmíněných společností z první části odpovědi
3. Určit typ požadované analýzy z druhé části odpovědi
4. Stanovit úroveň jistoty (confidence) analýzy na základě identifikovaných informací
5. Sestavit výsledný strukturovaný objekt `AnalysisResult`

Metoda `parse_response` představuje druhý krok v procesu analýzy uživatelských dotazů. Zatímco `analyze_query` zajišťuje komunikaci s LLM a získání strukturované odpovědi pomocí prompta, `parse_response` je zodpovědná za správnou interpretaci této odpovědi a její převod do datové struktury, se kterou mohou pracovat ostatní komponenty systému.

Spolupráce mezi těmito metodami je klíčová pro přesnou analýzu uživatelských dotazů a extrakci relevantních entit a záměrů, které jsou dále využívány v rámci Memory Agent systému pro vyhledávání informací a generování odpovědí.

## Implementační šablona

```python
def parse_response(response: str, original_query: str) -> AnalysisResult:
    """
    Parsuje odpověď z jazykového modelu a vytváří strukturovaný výsledek.
    
    Implementační detaily:
    1. Odstranění přebytečných mezer z odpovědi
    2. Rozdělení odpovědi podle ";" na části (Company name; analysis_type)
    3. Extrakce seznamu společností z první části (rozdělení podle čárek)
    4. Extrakce a validace typu analýzy z druhé části
    5. Stanovení úrovně jistoty (confidence) na základě identifikovaných informací
    6. Sestavení výsledného objektu AnalysisResult
    
    Args:
        response: Odpověď z LLM ve formátu "Company name; analysis_type"
        original_query: Původní dotaz uživatele
        
    Returns:
        AnalysisResult obsahující strukturované informace z odpovědi
    """
    # Odstranění přebytečných mezer
    
    # Rozdělení odpovědi podle ";" na části
    
    # Inicializace výchozích hodnot
    
    # Zpracování první části - identifikace společností
    
    # Zpracování druhé části - identifikace typu analýzy
    
    # Sestavení a vrácení výsledné struktury
```

## Omezení a hranice

1. **Závislost na formátu odpovědi**:
   - Metoda očekává odpověď v přesně definovaném formátu "Company name; analysis_type"
   - Jakákoliv odchylka od tohoto formátu může vést k nesprávné interpretaci odpovědi
   - LLM ne vždy vrací odpovědi v očekávaném formátu, zejména při změně parametrů modelu

2. **Validace typů analýz**:
   - Metoda podporuje pouze předdefinované typy analýz: "risk_comparison", "common_suppliers", "general"
   - Jiné typy analýz budou nahrazeny výchozí hodnotou "general"
   - Rozšíření podporovaných typů analýz vyžaduje úpravu validačního seznamu

3. **Úroveň jistoty (confidence)**:
   - Stanovení úrovně jistoty je založeno na heuristikách, nikoliv na skutečné pravděpodobnosti
   - Hodnoty (0.8 pro identifikované společnosti, 0.9 pro specifický typ analýzy) jsou pevně dané
   - Absence sofistikovanějšího mechanismu pro určení skutečné jistoty

4. **Zpracování vícenásobných entit**:
   - Metoda podporuje více společností oddělených čárkami, ale předpokládá je pouze v první části odpovědi
   - První společnost v seznamu je automaticky považována za primární (pole "company")
   - Neexistuje mechanismus pro určení relativní důležitosti jednotlivých společností

## Postup implementace

1. **Příprava a čištění vstupu**:
   - Odstranit přebytečné mezery z odpovědi pomocí metody `strip()`
   - Rozdělit odpověď podle středníku na části pomocí metody `split(";")`

2. **Inicializace výchozích hodnot**:
   - Vytvořit prázdný seznam pro společnosti
   - Nastavit výchozí typ analýzy na "general"
   - Inicializovat proměnnou `is_company_analysis` na `False`
   - Nastavit výchozí úroveň jistoty na 0.0

3. **Zpracování první části odpovědi (společnosti)**:
   - Ověřit, zda existuje první část a není prázdná
   - Rozdělit první část podle čárky pro identifikaci více společností
   - Odstranit přebytečné mezery z názvů společností
   - Filtrovat prázdné řetězce
   - Pokud byly identifikovány společnosti, nastavit `is_company_analysis` na `True`
   - Zvýšit úroveň jistoty na 0.8

4. **Zpracování druhé části odpovědi (typ analýzy)**:
   - Ověřit, zda existuje druhá část a není prázdná
   - Převést typ analýzy na malá písmena
   - Validovat typ analýzy proti seznamu povolených hodnot
   - Pokud je typ analýzy validní a není "general" a byly identifikovány společnosti, zvýšit úroveň jistoty na 0.9

5. **Sestavení výsledné struktury**:
   - Vytvořit slovník odpovídající struktuře `AnalysisResult`
   - Nastavit seznam identifikovaných společností
   - Nastavit primární společnost (první v seznamu nebo prázdný řetězec)
   - Nastavit identifikovaný typ analýzy
   - Přidat původní dotaz uživatele
   - Nastavit příznak, zda se jedná o analýzu společnosti
   - Nastavit vypočítanou úroveň jistoty
   - Vrátit sestavený výsledek

## Výsledná implementace

_Místo pro finální verzi implementace po dokončení vývoje._

## Instrukce pro dokumentaci

Při dokumentování implementace této metody je potřeba:

1. Popsat hlavní účel metody v kontextu procesu analýzy dotazů
2. Vysvětlit očekávaný formát vstupní odpovědi z LLM
3. Dokumentovat algoritmus pro extrakci společností a typů analýz
4. Vysvětlit heuristiky pro určení úrovně jistoty (confidence)
5. Popsat strukturu výsledného objektu `AnalysisResult`
6. Upozornit na potenciální edge cases a jejich řešení
7. Vysvětlit interakci s metodou `analyze_query`

## Potenciální edge cases a jejich řešení

### 1. Neočekávaný formát odpovědi
Pokud odpověď neobsahuje středník nebo má jinou strukturu než očekávanou, metoda zpracuje dostupné části a doplní výchozí hodnoty pro chybějící informace.

### 2. Prázdná odpověď
Pokud je odpověď prázdná, metoda vrátí výchozí hodnoty pro všechny pole `AnalysisResult`, což zajistí stabilitu systému.

### 3. Vícenásobné středníky
Metoda je navržena tak, aby zpracovala první dvě části oddělené středníkem. Další středníky v odpovědi budou ignorovány.

### 4. Neznámý typ analýzy
Pokud druhá část odpovědi obsahuje neznámý typ analýzy, bude ponechán výchozí typ "general".

### 5. Nevalidní názvy společností
Metoda nevaliduje názvy společností proti seznamu známých společností, což může vést k falešně pozitivním identifikacím.

### 6. Prázdná pole ve výstupu
Metoda zajišťuje, že každé pole ve výstupu má validní hodnotu (prázdný seznam, prázdný řetězec nebo výchozí hodnoty), což zabraňuje chybám při dalším zpracování.

## Dokumentace implementace

_Místo pro finální dokumentaci po dokončení implementace._
