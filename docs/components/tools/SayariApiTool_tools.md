# SayariApiTool

## Účel a kontext

`SayariApiTool` je nástroj pro komunikaci s Sayari API, který umožňuje získávat informace o společnostech a jejich rizikovém profilu. Tento nástroj je klíčovou součástí komponenty `tools.py` v projektu Memory Agent a slouží jako most mezi agentem a externím zdrojem dat o společnostech.

### Role v celkovém workflow

V rámci Memory Agent systému plní `SayariApiTool` následující role:

1. **Získávání externích dat o společnostech** - nástroj umožňuje dotazovat Sayari API pro vyhledávání společností a získávání detailních informací o jejich profilu
2. **Extrakce rizikových indikátorů** - zpracovává surová data z API a strukturuje rizikové indikátory do standardizovaného formátu
3. **Identifikace entit** - získává jedinečné identifikátory entit, které mohou být následně použity pro dotazování na vztahy mezi entitami
4. **Datový vstup pro analýzu** - poskytuje strukturovaná data, která jsou dále analyzována komponenty jako `analyzer.py`

Nástroj je běžně volán v první fázi workflow, kdy agent potřebuje získat základní informace o společnosti, které jsou následně použity pro hlubší analýzu rizik nebo vztahů.

## Implementační šablona

```python
class SayariApiTool(BaseTool):
    """Nástroj pro volání Sayari API a získání informací o společnosti."""
    
    # Základní konfigurace nástroje
    name: str = "sayari_api_tool"
    description: str = "Získává informace o společnosti z Sayari API"
    
    # URL endpoint pro API volání
    base_url: ClassVar[str] = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/sayari-simulator"
    
    async def _arun(self, company_name: str) -> Dict[str, Any]:
        """Asynchronní volání Sayari API.
        
        Args:
            company_name: Název společnosti, kterou chceme vyhledat
            
        Returns:
            Strukturovaný slovník obsahující data o společnosti, entitách, entity_id a rizikové analýze
            
        Raises:
            ToolException: Při chybě komunikace s API nebo zpracování odpovědi
        """
        # Logging volání API
        logger.info(f"Volání Sayari API pro společnost: {company_name}")
        
        try:
            # Sestavení URL pro vyhledávání entity
            search_url = f"{self.base_url}/search/entity?q={company_name}"
            
            # Vytvoření HTTP klienta a odeslání požadavku
            async with httpx.AsyncClient() as client:
                logger.debug(f"Odesílání GET požadavku na URL: {search_url}")
                response = await client.get(search_url)
                response.raise_for_status()  # Vyvolá výjimku při chybě
                data = response.json()
                
            logger.debug(f"Obdržena odpověď z API: {json.dumps(data)[:200]}...")
            
            # Zpracování odpovědi do standardního formátu
            return {
                "company": company_name,
                "external_data": {
                    "has_results": bool(data.get("data")),
                    "entities": self._extract_entities(data)
                },
                "entity_id": self._extract_entity_id(data),
                "risk_analysis": self._extract_risk_data(data)
            }
        except httpx.HTTPStatusError as e:
            # Zachycení HTTP chyb (404, 500 atd.)
            error_msg = f"HTTP chyba při volání Sayari API: {e.response.status_code}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except httpx.RequestError as e:
            # Zachycení chyb při komunikaci (timeout, connection error atd.)
            error_msg = f"Chyba při komunikaci se Sayari API: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except Exception as e:
            # Zachycení všech ostatních chyb
            error_msg = f"Neočekávaná chyba při volání Sayari API: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise ToolException(error_msg)
            
    def _extract_entities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrahuje entity z odpovědi API.
        
        Args:
            data: Odpověď z API
            
        Returns:
            Seznam extrahovaných entit
        """
        # Implementace extrakce entit z API odpovědi
        pass
    
    def _extract_entity_id(self, data: Dict[str, Any]) -> Optional[str]:
        """Extrahuje ID entity z odpovědi API.
        
        Args:
            data: Odpověď z API
            
        Returns:
            ID entity nebo None pokud není nalezeno
        """
        # Implementace extrakce ID entity
        pass
    
    def _extract_risk_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahuje data o riziku z odpovědi API.
        
        Args:
            data: Odpověď z API
            
        Returns:
            Slovník s daty o riziku
        """
        # Implementace extrakce rizikových dat
        pass
    
    def _parse_company_data(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Zpracuje odpověď z API a extrahuje relevantní data o společnosti.
        
        Args:
            api_response: Surová odpověď z API
            
        Returns:
            Strukturovaná data o společnosti
        """
        # Implementace zpracování dat o společnosti
        pass
```

## Omezení a hranice

### Technická omezení

1. **Závislost na externím API** - nástroj je závislý na dostupnosti a správném fungování Sayari API
2. **Omezení struktury dat** - nástroj očekává specifickou strukturu odpovědi z API, změny v API mohou vyžadovat úpravy
3. **Asynchronní zpracování** - nástroj je implementován jako asynchronní, což vyžaduje odpovídající kontext pro volání
4. **Chybové stavy** - je nutné počítat s různými chybovými stavy API a ošetřit je

### Designová omezení

1. **Jednotný formát odpovědi** - nástroj by měl vždy vracet konzistentní strukturu dat i při různých scénářích API odpovědí
2. **Oddělení zpracování dat** - extrakce a transformace dat by měla být implementována v pomocných metodách pro lepší testovatelnost
3. **Robustní zpracování chyb** - nástroj by měl zachytit všechny očekávatelné chyby a transformovat je na ToolException
4. **Minimální zpracování dat** - složitá transformace a interpretace dat by měla být ponechána na analyzátoru

## Postup implementace

### Příprava implementace

1. **Import potřebných knihoven**:
   - Ujistit se, že jsou dostupné závislosti `httpx` pro HTTP volání
   - Importovat potřebné typy z `typing` modulů
   - Importovat `BaseTool` a `ToolException` z LangChain

2. **Definice základních atributů**:
   - Nastavit `name` a `description` pro identifikaci nástroje v LangChain
   - Definovat `base_url` jako třídní proměnnou

### Implementace _arun metody

1. **Validace vstupu**:
   - Zajistit, že `company_name` je platný vstup pro API volání
   - Připravit URL s parametrem pro vyhledávání

2. **Provedení HTTP volání**:
   - Vytvořit asynchronní HTTP klienta
   - Odeslat GET požadavek na sestavené URL
   - Zkontrolovat odpověď pomocí `raise_for_status()`
   - Deserializovat JSON odpověď

3. **Zpracování odpovědi**:
   - Extrahovat relevantní data pomocí pomocných metod
   - Strukturovat data do konzistentního formátu
   - Vrátit strukturovaný výsledek

4. **Ošetření výjimek**:
   - Zachytit specifické HTTP výjimky a transformovat je na ToolException
   - Zachytit obecné výjimky a poskytnout užitečné chybové hlášení

### Implementace pomocných metod

1. **_extract_entities**: Zpracování entitních záznamů z API odpovědi
2. **_extract_entity_id**: Získání ID entity pro pozdější volání API
3. **_extract_risk_data**: Extrakce dat týkajících se rizikového profilu společnosti
4. **_parse_company_data**: Komplexní zpracování dat o společnosti

### Testování implementace

1. **Unit testy**:
   - Test úspěšného volání API s mockem odpovědi
   - Test chybových stavů API (404, 500)
   - Test zpracování prázdných dat

2. **Integrační testy**:
   - Test komunikace se simulovaným API endpointem
   - Test integrace s ostatními nástroji v workflow

## Struktura návratové hodnoty

Nástroj vrací strukturovaný slovník s následujícím schématem:

```python
{
    "company": str,  # Název hledané společnosti
    "external_data": {
        "has_results": bool,  # Indikátor, zda API vrátilo nějaké výsledky
        "entities": [
            {
                "id": str,  # ID entity v Sayari systému
                "name": str,  # Název entity
                "type": str,  # Typ entity (obvykle "Company")
                "risk_score": str  # Skóre rizika jako řetězec
            }
        ]
    },
    "entity_id": Optional[str],  # ID hlavní entity nebo None
    "risk_analysis": {
        "sanctions_status": str,  # Status sankcí jako textový popis
        "pep_connections": List[str],  # Seznam spojení s politicky exponovanými osobami
        "compliance_issues": List[str],  # Seznam problémů s dodržováním předpisů
        "risk_score": str,  # Číselné hodnocení rizika
        "risk_factors": List[str]  # Seznam identifikovaných rizikových faktorů
    }
}
```

## Výsledná implementace

_Toto místo je vyhrazeno pro finální implementaci po schválení a kódové revizi._

## Instrukce pro dokumentaci

1. Dokumentace by měla obsahovat příklady volání nástroje
2. Detailně popsat strukturu návratové hodnoty včetně typů a možných hodnot
3. Vysvětlit význam rizikových indikátorů a jak je interpretovat
4. Popsat možné chybové stavy a jak je řešit
5. Uvést informace o limitech API (rate limiting, timeout atd.)
6. Popsat integrační body s ostatními komponenty systému

## Dokumentace implementace

_Toto místo je vyhrazeno pro dokumentaci finální implementace po jejím dokončení._
