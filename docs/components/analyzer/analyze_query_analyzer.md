# Metoda analyze_query komponenty analyzer

## Účel a kontext metody

Metoda `analyze_query` je klíčovou součástí komponenty `analyzer`, která zpracovává uživatelské dotazy a identifikuje v nich důležité entity a záměry. Hlavním účelem této metody je analyzovat vstupní text od uživatele a extrahovat z něj:

1. Názvy společností/firem zmíněných v dotazu
2. Typ analýzy, kterou uživatel požaduje
3. Určit, zda se jedná o analýzu konkrétní společnosti

Tato metoda tvoří vstupní bod analytického procesu celého Memory Agent systému, protože správné pochopení uživatelského dotazu je zásadní pro následné zpracování a vyhledávání relevantních informací v grafové databázi nebo externích zdrojích.

Metoda využívá jazykový model (LLM) pro pokročilou sémantickou analýzu textu a strukturuje získané informace do standardizovaného formátu `AnalysisResult`, který je dále zpracováván ostatními komponentami systému.

## Implementační šablona

```python
async def analyze_query(
    user_input: str, 
    config: Optional[RunnableConfig] = None,
    model: Optional[str] = "claude-3-7-sonnet-latest"
) -> AnalysisResult:
    """
    Analyzuje uživatelský vstup a identifikuje společnosti a typy analýz.
    
    Implementační detaily:
    1. Inicializuje LLM model podle zadaného parametru
    2. Vytvoří LCEL řetězec s promptem pro analýzu
    3. Spustí řetězec s uživatelským vstupem
    4. Zpracuje odpověď pomocí parse_response funkce
    5. Vrátí strukturovaný výsledek nebo výchozí hodnotu v případě chyby
    
    Args:
        user_input: Dotaz od uživatele
        config: Runtime konfigurace (volitelné)
        model: Model, který se má použít pro analýzu (výchozí je claude-3-7-sonnet-latest)
        
    Returns:
        AnalysisResult obsahující extrahované informace
    """
    # Logging zpráva o začátku analýzy
    
    # Inicializace výchozího výsledku pro případ chyby
    
    try:
        # Inicializace chat modelu
        
        # Vytvoření LCEL řetězce: prompt | llm | StrOutputParser
        
        # Asynchronní volání řetězce
        
        # Parsování odpovědi a vrácení strukturovaného výsledku
        
    except Exception as e:
        # Logování chyby
        # Vrácení výchozího výsledku
```

## Omezení a hranice

1. **Závislost na LLM modelu**:
   - Metoda je závislá na dostupnosti a kvalitě specifikovaného LLM modelu
   - Různé modely mohou poskytovat různou kvalitu analýzy
   - Je důležité zajistit kompatibilitu s použitým promptem

2. **Práce s nejistotou**:
   - Při extrakci entit a záměrů z přirozeného jazyka vždy existuje určitá míra nejistoty
   - Systém by měl obsahovat mechanismy pro zpracování nejasných nebo víceznačných dotazů

3. **Výkonnostní omezení**:
   - Asynchronní volání LLM modelu může představovat výkonnostní úzké hrdlo
   - Je třeba zohlednit latenci API volání externího LLM
   - Pro produkční nasazení zvážit caching často kladených dotazů

4. **Chybové stavy**:
   - Metoda musí být robustní vůči různým formátům a kvalitám uživatelských vstupů
   - Je nutné správně ošetřit všechny případy selhání LLM nebo parsování odpovědi

## Postup implementace

1. **Příprava logovacího systému**:
   - Zajistit správnou konfiguraci loggeru pro trackování průběhu analýzy
   - Implementovat informativní zprávy o průběhu analýzy

2. **Definice výchozí struktury výsledku**:
   - Vytvořit výchozí `AnalysisResult` s prázdnými hodnotami
   - Nastavit výchozí hodnoty pro všechny povinné položky

3. **Inicializace LLM modelu**:
   - Použít helper funkci `init_chat_model` s parametrem model
   - Zajistit správné nastavení parametrů modelu (teplota, max_tokens, atd.)

4. **Sestavení LCEL řetězce**:
   - Připravit analyzační prompt (předpokládá se globální definice `prompt`)
   - Sestavit řetězec ve formátu `prompt | llm | StrOutputParser()`

5. **Implementace asynchronního volání**:
   - Použít `ainvoke` metodu s předáním uživatelského vstupu a konfigurace
   - Zpracovat výsledek volání pro další analýzu

6. **Zpracování odpovědi**:
   - Předat výstup z LLM do funkce `parse_response`
   - Vrátit výsledek parsování jako návratovou hodnotu funkce

7. **Implementace ošetření chyb**:
   - Zachytit všechny potenciální výjimky v try-except bloku
   - Logovat detaily chyby včetně stacktrace
   - V případě chyby vrátit výchozí výsledek

## Výsledná implementace

_Místo pro finální verzi implementace po dokončení vývoje._

## Instrukce pro dokumentaci

Při dokumentování implementace této metody je potřeba:

1. Popsat hlavní účel metody v kontextu celého systému
2. Vysvětlit strukturu návratové hodnoty `AnalysisResult`
3. Dokumentovat všechny parametry včetně jejich typů a výchozích hodnot
4. Popsat chování metody v případě chybových stavů
5. Uvést příklady možných uživatelských dotazů a výsledků analýzy
6. Vysvětlit interakci s metodou `parse_response` a její očekávané vstupy/výstupy

## Dokumentace implementace

_Místo pro finální dokumentaci po dokončení implementace._
