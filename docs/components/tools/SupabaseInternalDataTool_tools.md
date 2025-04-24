# SupabaseInternalDataTool

## Účel a kontext

`SupabaseInternalDataTool` je nástroj určený pro získávání interních dat o společnostech z databáze Supabase. Tento nástroj poskytuje přístup k proprietárním informacím o dodavatelích, které nejsou dostupné z veřejných zdrojů, ale jsou klíčové pro komplexní analýzu společností.

### Role v celkovém workflow

V rámci Memory Agent systému plní `SupabaseInternalDataTool` následující role:

1. **Získávání interních kategorizačních dat** - nástroj slouží k získání interních klasifikací společností, jako je jejich tier úroveň (strategic, preferred, standard)
2. **Přístup k HS kódům** - poskytuje informace o Harmonized System (HS) kódech spojených s produkty a službami dodavatele
3. **Identifikace obchodních aktivit** - extrahuje zaznamenané obchodní aktivity společnosti z interní databáze
4. **Doplnění externích dat** - slouží jako doplněk k externím datům získaným pomocí nástrojů jako `SayariApiTool`

Nástroj je obvykle volán v průběhu analýzy společnosti po získání základních veřejných informací. Interní data poskytují dodatečný kontext pro hodnocení rizik a vztahů, zejména v případech, kdy má organizace s danou společností předchozí zkušenosti.

## Implementační šablona

```python
class SupabaseInternalDataTool(BaseTool):
    """Nástroj pro získání interních dat o společnosti ze Supabase."""
    
    # Základní konfigurace nástroje
    name: str = "supabase_internal_data_tool"
    description: str = "Získává interní data o společnosti včetně tier klasifikace a HS kódů"
    
    # Endpoint pro API volání do Supabase Functions
    base_url: ClassVar[str] = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/get-supplier-data"
    
    async def _arun(self, company_name: str) -> Dict[str, Any]:
        """Asynchronní volání Supabase API pro získání interních dat.
        
        Args:
            company_name: Název společnosti, pro kterou chceme získat interní data
            
        Returns:
            Strukturovaný slovník obsahující profil společnosti s tier klasifikací, HS kódy a obchodními aktivitami
            
        Raises:
            ToolException: Při chybě komunikace s API nebo zpracování odpovědi
        """
        # Logging operace
        logger.info(f"Získávání interních dat pro společnost: {company_name}")
        
        try:
            # Vytvoření URL s parametrem pro název společnosti
            request_url = f"{self.base_url}?name={company_name}"
            
            # Vytvoření HTTP klienta a odeslání požadavku
            async with httpx.AsyncClient() as client:
                logger.debug(f"Odesílání GET požadavku na URL: {request_url}")
                response = await client.get(request_url)
                response.raise_for_status()  # Vyvolá výjimku při chybovém HTTP statusu
                data = response.json()
                
            logger.debug(f"Obdržena odpověď z API: {json.dumps(data)[:200]}...")
            
            # Zpracování odpovědi pomocí pomocné metody
            return self._process_internal_data(data, company_name)
        except httpx.HTTPStatusError as e:
            # Zachycení HTTP chyb (404, 500 atd.)
            error_msg = f"HTTP chyba při získávání interních dat: {e.response.status_code}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except httpx.RequestError as e:
            # Zachycení chyb při komunikaci (timeout, connection error atd.)
            error_msg = f"Chyba při komunikaci s API: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except Exception as e:
            # Zachycení všech ostatních chyb
            error_msg = f"Neočekávaná chyba při získávání interních dat: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise ToolException(error_msg)
    
    def _process_internal_data(self, data: Dict[str, Any], company_name: str) -> Dict[str, Any]:
        """Zpracovává interní data o společnosti.
        
        Args:
            data: Surová odpověď z API
            company_name: Název společnosti pro doplnění do výsledku
            
        Returns:
            Strukturovaný profil společnosti
        """
        # Extrakce dat z supplier_info
        supplier_info = data.get("supplier_info", {})
        
        # Extrakce tier klasifikace s výchozí hodnotou pro případ chybějících dat
        tier_classification = supplier_info.get("primary_tier", "Neurčeno")
        
        # Extrakce HS kódů s ověřením struktury dat
        hs_codes = []
        if "hs_code_matches" in supplier_info and isinstance(supplier_info["hs_code_matches"], list):
            hs_codes = [match.get("hsCode", "") for match in supplier_info["hs_code_matches"] if match.get("hsCode")]
        
        # Extrakce obchodních aktivit s ověřením struktury dat
        business_activities = []
        if "identified_activities" in supplier_info and isinstance(supplier_info["identified_activities"], list):
            business_activities = [activity.get("activity", "") for activity in supplier_info["identified_activities"] if activity.get("activity")]
        
        # Vytvoření výsledné struktury
        return {
            "company": company_name,
            "company_profile": {
                "tier_classification": tier_classification,
                "hs_codes": hs_codes,
                "business_activities": business_activities,
                "geographic_presence": []  # Toto pole se připravuje pro budoucí rozšíření
            }
        }
```

## Omezení a hranice

### Technická omezení

1. **Závislost na Supabase** - nástroj je závislý na dostupnosti a správném fungování Supabase Functions
2. **Omezený formát vstupu** - nástroj akceptuje pouze název společnosti, ne jiné identifikátory (IČO, DIČ)
3. **Omezení rozsahu dat** - interní databáze obsahuje pouze společnosti, se kterými organizace již měla nějaké interakce
4. **Asynchronní zpracování** - nástroj je implementován jako asynchronní, což vyžaduje odpovídající kontext pro volání

### Designová omezení

1. **Konzistentní návratový formát** - nástroj by měl zachovat stejnou strukturu výstupu i při chybějících datech
2. **Robustní zpracování chyb** - všechny chybové stavy musí být zachyceny a správně zpracovány
3. **Logování operací** - kritické operace a chyby musí být logovány pro pozdější analýzu
4. **Ochrana před prázdnými daty** - nástroj by měl elegantně zpracovávat situace, kdy API vrací prázdná nebo neúplná data

## Postup implementace

### Příprava implementace

1. **Import potřebných knihoven**:
   - Zajistit dostupnost `httpx` pro asynchronní HTTP volání
   - Importovat potřebné typy z `typing` pro anotace
   - Importovat `BaseTool` a `ToolException` z LangChain

2. **Definice základní konfigurace**:
   - Nastavit jméno a popis nástroje
   - Definovat URL endpoint pro Supabase Functions

### Implementace hlavní metody _arun

1. **Příprava požadavku**:
   - Sestavení URL s parametrem pro název společnosti
   - Vytvoření asynchronního HTTP klienta

2. **Odeslání požadavku**:
   - Vykonání GET volání na API endpoint
   - Kontrola HTTP statusu odpovědi
   - Deserializace JSON odpovědi

3. **Zpracování odpovědi**:
   - Předání dat pomocné metodě pro zpracování
   - Vrácení strukturovaného výsledku

4. **Ošetření výjimek**:
   - Zachycení a logování HTTP výjimek
   - Zachycení výjimek při komunikaci
   - Zachycení a logování ostatních výjimek
   - Transformace výjimek na ToolException

### Implementace pomocné metody _process_internal_data

1. **Extrakce základních informací**:
   - Získání supplier_info z odpovědi
   - Extrakce tier klasifikace s výchozí hodnotou

2. **Zpracování seznamových polí**:
   - Ověření existence a datového typu HS kódů
   - Extrakce relevantních hodnot z hs_code_matches
   - Ověření existence a datového typu obchodních aktivit
   - Extrakce relevantních hodnot z identified_activities

3. **Sestavení výsledného objektu**:
   - Vytvoření strukturovaného slovníku s profilem společnosti
   - Zahnutí všech zpracovaných informací

### Testování implementace

1. **Unit testy**:
   - Test úspěšného volání API s komplexní odpovědí
   - Test zpracování minimální odpovědi
   - Test zpracování prázdné odpovědi
   - Test ošetření chybových stavů API

2. **Integrační testy**:
   - Test komunikace se simulovaným Supabase API
   - Test integrace s ostatními nástroji workflow

## Struktura návratové hodnoty

Nástroj vrací strukturovaný slovník s následujícím schématem:

```python
{
    "company": str,  # Název společnosti poskytnutý jako vstup
    "company_profile": {
        "tier_classification": str,  # Interní klasifikace dodavatele ("Tier 1", "Tier 2", "Tier 3" nebo "Neurčeno")
        "hs_codes": List[str],  # Seznam HS kódů spojených s produkty dodavatele
        "business_activities": List[str],  # Seznam identifikovaných obchodních aktivit
        "geographic_presence": List[str]  # Seznam regionů působnosti (připraveno pro budoucí rozšíření)
    }
}
```

### Příklady návratových hodnot

**Úplná odpověď**:
```json
{
    "company": "Example Tech",
    "company_profile": {
        "tier_classification": "Tier 1",
        "hs_codes": ["8471.30", "8517.62", "8473.30"],
        "business_activities": ["IT Services", "Hardware Manufacturing", "Software Development"],
        "geographic_presence": []
    }
}
```

**Minimální odpověď**:
```json
{
    "company": "Unknown Company",
    "company_profile": {
        "tier_classification": "Neurčeno",
        "hs_codes": [],
        "business_activities": [],
        "geographic_presence": []
    }
}
```

## Výsledná implementace

_Toto místo je vyhrazeno pro finální implementaci po schválení a kódové revizi._

## Instrukce pro dokumentaci

1. Dokumentace by měla vysvětlovat význam tier klasifikace v kontextu dodavatelského řetězce
2. Zahrnout informace o formátu a významu HS kódů
3. Vysvětlit, jak jsou interní data používána v procesu hodnocení dodavatelů
4. Popsat zdroje dat a jejich aktualizaci v Supabase
5. Nastínit plánovaná rozšíření, zejména v oblasti geographic_presence
6. Uvést omezení a spolehlivost interních dat

## Dokumentace implementace

_Toto místo je vyhrazeno pro dokumentaci finální implementace po jejím dokončení._
