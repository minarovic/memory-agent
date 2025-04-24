# SayariRelationshipsTool

## Účel a kontext

`SayariRelationshipsTool` je specializovaný nástroj určený k získávání a vizualizaci vztahů mezi entitami (společnostmi, osobami, organizacemi) z Sayari API. Tento nástroj rozšiřuje základní funkčnost `SayariApiTool` o schopnost analyzovat síť vztahů kolem dané entity, což poskytuje klíčové informace o obchodních vazbách, vlastnické struktuře a dalších relevantních spojeních.

### Role v celkovém workflow

V rámci Memory Agent systému plní `SayariRelationshipsTool` následující role:

1. **Mapování vztahové sítě** - po identifikaci hlavní entity pomocí `SayariApiTool` získává tento nástroj kompletní síť vztahů
2. **Kategorizace vztahů** - třídí získané vztahy do logických kategorií (dodavatelé, zákazníci, vlastnictví, klíčové vztahy)
3. **Příprava dat pro vizualizaci** - transformuje surová data z API do struktury vhodné pro grafovou vizualizaci
4. **Hodnocení rizik v dodavatelském řetězci** - identifikuje potenciálně rizikové vztahy v síti dodavatelů a zákazníků

Nástroj je typicky volán po úspěšné identifikaci entity pomocí `SayariApiTool`, kdy využívá získané `entity_id` k dalšímu dotazování API. Výstupy tohoto nástroje jsou následně analyzovány v rámci hodnocení rizik a mohou být vizualizovány v uživatelském rozhraní pro lepší pochopení vztahového kontextu.

## Implementační šablona

```python
class SayariRelationshipsTool(BaseTool):
    """Nástroj pro získání vztahů entity z Sayari API."""
    
    # Základní konfigurace nástroje
    name: str = "sayari_relationships_tool"
    description: str = "Získává vztahy entity (společnosti) z Sayari API"
    
    # URL endpoint pro API volání
    base_url: ClassVar[str] = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/sayari-simulator"
    
    async def _arun(self, entity_id: str) -> Dict[str, Any]:
        """Asynchronní volání Sayari API pro získání vztahů.
        
        Metoda zpracovává dotaz na API pro získání vztahů entity a transformuje
        odpověď do strukturovaného formátu včetně vizualizačních dat.
        
        Args:
            entity_id: Identifikátor entity, pro kterou chceme získat vztahy
            
        Returns:
            Slovník obsahující vztahy entity kategorizované podle typu
            a data pro vizualizaci ve formátu grafu
            
        Raises:
            ToolException: Při chybě komunikace s API nebo zpracování odpovědi
        """
        # Logging operace
        logger.info(f"Získávání vztahů pro entitu s ID: {entity_id}")
        
        # Ověření vstupního parametru
        if not entity_id:
            logger.warning("Nelze získat vztahy - chybí ID entity")
            return {
                "has_relationships": False,
                "relationships": {"suppliers": [], "customers": [], "ownership": [], "key_relationships": []},
                "visualization": {"nodes": [], "links": []}
            }
            
        try:
            # Sestavení URL pro získání vztahů entity
            relationship_url = f"{self.base_url}/entity/{entity_id}/relationships"
            
            # Vytvoření HTTP klienta a odeslání požadavku
            async with httpx.AsyncClient() as client:
                logger.debug(f"Odesílání GET požadavku na URL: {relationship_url}")
                response = await client.get(relationship_url)
                response.raise_for_status()  # Vyvolá výjimku při chybě
                data = response.json()
                
            logger.debug(f"Obdržena odpověď z API: {json.dumps(data)[:200]}...")
            
            # Extrakce a formátování vztahů pomocí pomocných metod
            relationships = self._process_relationships(data)
            visualization = self._create_visualization(data)
                
            # Sestavení výsledné odpovědi
            return {
                "has_relationships": bool(relationships),
                "relationships": relationships,
                "visualization": visualization
            }
        except httpx.HTTPStatusError as e:
            # Zachycení HTTP chyb (404, 500 atd.)
            error_msg = f"HTTP chyba při získávání vztahů: {e.response.status_code}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except httpx.RequestError as e:
            # Zachycení chyb při komunikaci (timeout, connection error atd.)
            error_msg = f"Chyba při komunikaci s API: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except Exception as e:
            # Zachycení všech ostatních chyb
            error_msg = f"Neočekávaná chyba při získávání vztahů: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise ToolException(error_msg)
    
    def _process_relationships(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Zpracovává vztahy z odpovědi API.
        
        Metoda kategorizuje vztahy entity podle jejich typu do čtyř hlavních kategorií:
        dodavatelé, zákazníci, vlastnické vztahy a ostatní klíčové vztahy.
        
        Args:
            data: Odpověď z API obsahující vztahy entity
            
        Returns:
            Slovník kategorizovaných vztahů rozdělených do seznamů
        """
        # Ověření struktury vstupních dat
        if not data or not isinstance(data, dict):
            return {"suppliers": [], "customers": [], "ownership": [], "key_relationships": []}
        
        # Získání seznamu vztahů s ověřením datového typu
        relationships = data.get("relationships", [])
        if not isinstance(relationships, list):
            relationships = []
        
        # Kategorizace vztahů podle typu
        suppliers = []  # Seznam dodavatelů
        customers = []  # Seznam zákazníků
        ownership = []  # Seznam vlastnických vztahů
        key_relationships = []  # Seznam ostatních důležitých vztahů
        
        # Iterace přes všechny vztahy a jejich kategorizace
        for rel in relationships:
            rel_type = rel.get("type", "")
            source_label = rel.get("source", {}).get("label", "")
            target_label = rel.get("target", {}).get("label", "")
            
            # Rozdělení podle typu vztahu
            if rel_type in ["has_supplier", "supplies_to"]:
                # Dodavatelsko-odběratelské vztahy
                if source_label:
                    suppliers.append(source_label)
                if target_label:
                    customers.append(target_label)
            elif rel_type in ["has_subsidiary", "subsidiary_of", "has_shareholder", "shareholder_of"]:
                # Vlastnické vztahy
                if source_label and target_label:
                    ownership.append(f"{source_label} -> {target_label} ({rel_type})")
            elif source_label and target_label:
                # Ostatní důležité vztahy
                key_relationships.append(f"{source_label} -> {target_label} ({rel_type})")
        
        # Sestavení výsledné struktury a odstranění duplicit ze seznamů
        return {
            "suppliers": list(set(suppliers)),
            "customers": list(set(customers)),
            "ownership": ownership,
            "key_relationships": key_relationships
        }
    
    def _create_visualization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Vytváří vizualizační data pro vztahy.
        
        Transformuje surová data z API do formátu vhodného pro grafovou
        vizualizaci vztahů. Generuje uzly reprezentující entity a hrany
        reprezentující vztahy mezi nimi.
        
        Args:
            data: Odpověď z API obsahující vztahy entity
            
        Returns:
            Slovník obsahující seznamy uzlů a hran pro vizualizaci
        """
        # Ověření struktury vstupních dat
        if not data or not isinstance(data, dict):
            return {"nodes": [], "links": []}
        
        # Získání seznamu vztahů s ověřením datového typu
        relationships = data.get("relationships", [])
        if not isinstance(relationships, list):
            relationships = []
        
        # Mapa pro ukládání jedinečných uzlů (zabránění duplicitám)
        nodes_map = {}
        links = []
        
        # Iterace přes všechny vztahy a vytvoření uzlů a hran
        for rel in relationships:
            rel_type = rel.get("type", "")
            
            # Zpracování zdrojového uzlu
            source = rel.get("source", {})
            source_id = source.get("id", "")
            source_label = source.get("label", "")
            source_type = source.get("type", "company")
            
            # Přidání zdrojového uzlu do mapy, pokud ještě neexistuje
            if source_id and source_label and source_id not in nodes_map:
                nodes_map[source_id] = {
                    "id": source_id,
                    "label": source_label,
                    "data": {
                        "type": source_type,
                        "shape": "circle",
                        "color": self._get_node_color(source_type)
                    }
                }
            
            # Zpracování cílového uzlu
            target = rel.get("target", {})
            target_id = target.get("id", "")
            target_label = target.get("label", "")
            target_type = target.get("type", "company")
            
            # Přidání cílového uzlu do mapy, pokud ještě neexistuje
            if target_id and target_label and target_id not in nodes_map:
                nodes_map[target_id] = {
                    "id": target_id,
                    "label": target_label,
                    "data": {
                        "type": target_type,
                        "shape": "circle",
                        "color": self._get_node_color(target_type)
                    }
                }
            
            # Vytvoření hrany mezi uzly
            if source_id and target_id:
                links.append({
                    "id": rel.get("id", f"edge_{source_id}_{target_id}"),
                    "source": source_id,
                    "target": target_id,
                    "label": rel_type,
                    "data": {
                        "type": rel_type,
                        "color": self._get_edge_color(rel_type)
                    }
                })
        
        # Sestavení výsledné struktury
        return {
            "nodes": list(nodes_map.values()),  # Převod hodnot ze slovníku na seznam
            "links": links
        }
    
    def _get_node_color(self, node_type: str) -> str:
        """Vrací barvu uzlu podle typu.
        
        Přiřazuje konzistentní barvy k různým typům entit pro vizualizaci.
        
        Args:
            node_type: Typ entity (company, person, organization)
            
        Returns:
            Hexadecimální kód barvy pro daný typ uzlu
        """
        # Mapa barev pro různé typy entit
        type_colors = {
            "company": "#3366CC",  # Modrá pro společnosti
            "person": "#33AA33",   # Zelená pro osoby
            "organization": "#CC6633"  # Oranžová pro organizace
        }
        # Vrátí barvu podle typu nebo výchozí šedou barvu
        return type_colors.get(node_type.lower(), "#AAAAAA")
    
    def _get_edge_color(self, edge_type: str) -> str:
        """Vrací barvu hrany podle typu vztahu.
        
        Přiřazuje konzistentní barvy k různým typům vztahů pro vizualizaci.
        
        Args:
            edge_type: Typ vztahu mezi entitami
            
        Returns:
            Hexadecimální kód barvy pro daný typ hrany
        """
        # Mapa barev pro různé typy vztahů
        type_colors = {
            "has_subsidiary": "#3366CC",  # Modrá pro vlastnické vztahy
            "subsidiary_of": "#3366CC",
            "has_officer": "#33AA33",     # Zelená pro vztahy s vedoucími osobami
            "officer_of": "#33AA33",
            "has_shareholder": "#CC6633", # Oranžová pro akcionářské vztahy
            "shareholder_of": "#CC6633",
            "has_supplier": "#9900CC",    # Fialová pro dodavatelské vztahy
            "supplies_to": "#9900CC",
            "supplies": "#9900CC"
        }
        # Vrátí barvu podle typu nebo výchozí šedou barvu
        return type_colors.get(edge_type.lower(), "#AAAAAA")
```

## Omezení a hranice

### Technická omezení

1. **Závislost na ID entity** - nástroj vyžaduje platné ID entity z předchozího volání `SayariApiTool`
2. **Omezený počet vztahů** - API může omezit počet vrácených vztahů, což může vést k neúplnému obrazu sítě
3. **Závislost na dostupnosti API** - nástroj je závislý na funkčnosti a dostupnosti Sayari API
4. **Složité vztahy** - některé komplexní vztahové struktury mohou být zjednodušeny pro potřeby vizualizace
5. **Omezení vizualizace** - generovaná vizualizační data jsou závislá na schopnostech zobrazovacího enginu

### Designová omezení

1. **Kategorizace vztahů** - vztahy jsou kategorizovány do pevně daných skupin, což může zjednodušovat komplexní realitu
2. **Barevné kódování** - barevné schéma je pevně definované a nemusí být optimální pro všechny typy vizualizací
3. **Formát výstupu** - struktura výstupu je navržena pro konkrétní typ vizualizační komponenty
4. **Omezené atributy** - u uzlů a hran jsou uchovávány pouze základní atributy, detailnější informace mohou chybět

## Postup implementace

### Příprava implementace

1. **Import potřebných knihoven**:
   - Importovat `httpx` pro HTTP komunikaci
   - Importovat `BaseTool` a `ToolException` z LangChain
   - Zajistit dostupnost typových anotací z `typing`

2. **Definice základní konfigurace**:
   - Nastavit jméno a popis nástroje
   - Definovat URL endpoint pro Sayari API

### Implementace hlavní metody _arun

1. **Validace vstupního parametru**:
   - Ověření, že `entity_id` není prázdné
   - Vrácení prázdné odpovědi, pokud ID chybí

2. **Volání API**:
   - Sestavení URL pro získání vztahů
   - Vytvoření asynchronního HTTP klienta
   - Odeslání GET požadavku
   - Zpracování a deserializace odpovědi

3. **Zpracování dat**:
   - Volání pomocných metod pro kategorizaci vztahů
   - Vytvoření vizualizačních dat
   - Sestavení výsledné struktury odpovědi

4. **Ošetření výjimek**:
   - Zachycení a logování specifických HTTP výjimek
   - Zachycení chyb při komunikaci s API
   - Zachycení a logování ostatních neočekávaných chyb

### Implementace pomocných metod

1. **_process_relationships**:
   - Validace vstupních dat
   - Extrakce seznamu vztahů
   - Kategorizace vztahů podle typu
   - Odstranění duplicit a sestavení výsledné struktury

2. **_create_visualization**:
   - Validace vstupních dat
   - Vytvoření mapy pro ukládání jedinečných uzlů
   - Zpracování zdrojových a cílových uzlů
   - Vytvoření hran mezi uzly
   - Sestavení výsledné struktury pro vizualizaci

3. **_get_node_color** a **_get_edge_color**:
   - Definice barevného schématu pro různé typy uzlů a hran
   - Přiřazení barev podle typu

### Testování implementace

1. **Unit testy**:
   - Test zpracování prázdného ID entity
   - Test zpracování odpovědi s různými typy vztahů
   - Test generování vizualizačních dat
   - Test ošetření chybových stavů API

2. **Integrační testy**:
   - Test spolupráce s `SayariApiTool`
   - Test integrace do workflow se zobrazením výsledků

## Struktura návratové hodnoty

Nástroj vrací strukturovaný slovník s následujícím schématem:

```python
{
    "has_relationships": bool,  # Indikátor existence vztahů
    "relationships": {
        "suppliers": List[str],  # Seznam jmen/názvů dodavatelů
        "customers": List[str],  # Seznam jmen/názvů zákazníků
        "ownership": List[str],  # Seznam vlastnických vztahů ve formátu "Entity A -> Entity B (typ_vztahu)"
        "key_relationships": List[str]  # Seznam ostatních klíčových vztahů ve stejném formátu
    },
    "visualization": {
        "nodes": [  # Seznam uzlů pro vizualizaci
            {
                "id": str,  # Jedinečný identifikátor uzlu
                "label": str,  # Zobrazovaný název entity
                "data": {
                    "type": str,  # Typ entity (company, person, organization)
                    "shape": str,  # Tvar uzlu pro vizualizaci
                    "color": str  # Hexadecimální kód barvy uzlu
                }
            },
            # další uzly...
        ],
        "links": [  # Seznam hran pro vizualizaci
            {
                "id": str,  # Jedinečný identifikátor hrany
                "source": str,  # ID zdrojového uzlu
                "target": str,  # ID cílového uzlu
                "label": str,  # Typ vztahu
                "data": {
                    "type": str,  # Typ vztahu
                    "color": str  # Hexadecimální kód barvy hrany
                }
            },
            # další hrany...
        ]
    }
}
```

### Příklady návratových hodnot

**Úplná odpověď s identifikovanými vztahy**:
```json
{
    "has_relationships": true,
    "relationships": {
        "suppliers": ["Supplier A", "Supplier B"],
        "customers": ["Customer X", "Customer Y"],
        "ownership": ["Acme Corp -> Subsidiary Ltd (has_subsidiary)"],
        "key_relationships": ["Person A -> Acme Corp (officer_of)"]
    },
    "visualization": {
        "nodes": [
            {
                "id": "entity-123",
                "label": "Acme Corp",
                "data": {
                    "type": "company",
                    "shape": "circle",
                    "color": "#3366CC"
                }
            },
            {
                "id": "entity-456",
                "label": "Subsidiary Ltd",
                "data": {
                    "type": "company",
                    "shape": "circle",
                    "color": "#3366CC"
                }
            }
        ],
        "links": [
            {
                "id": "rel-789",
                "source": "entity-123",
                "target": "entity-456",
                "label": "has_subsidiary",
                "data": {
                    "type": "has_subsidiary",
                    "color": "#3366CC"
                }
            }
        ]
    }
}
```

**Odpověď bez vztahů nebo při prázdném ID**:
```json
{
    "has_relationships": false,
    "relationships": {
        "suppliers": [],
        "customers": [],
        "ownership": [],
        "key_relationships": []
    },
    "visualization": {
        "nodes": [],
        "links": []
    }
}
```

## Výsledná implementace

_Toto místo je vyhrazeno pro finální implementaci po schválení a kódové revizi._

## Instrukce pro dokumentaci

1. Dokumentace by měla obsahovat detailní vysvětlení typů vztahů a jejich významu pro analýzu rizik
2. Popsat proces vizualizace vztahových dat ve front-endové části aplikace
3. Vysvětlit význam barevného kódování v kontextu analýzy vztahové sítě
4. Zahrnout příklady, jak interpretovat různé typy vztahových struktur
5. Popsat omezení při práci s rozsáhlými vztahovými sítěmi a možné optimalizace
6. Uvést návaznost na ostatní nástroje a komponenty systému
7. Popsat postup pro rozšíření o další typy vztahů nebo vizualizační atributy

## Dokumentace implementace

_Toto místo je vyhrazeno pro dokumentaci finální implementace po jejím dokončení._
