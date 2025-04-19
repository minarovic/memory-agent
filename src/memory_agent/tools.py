"""Define the agent's tools."""

import logging
import traceback
import uuid
import httpx
import json
from typing import Annotated, Dict, Any, Optional, List, ClassVar

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg, BaseTool, ToolException
from langgraph.store.base import BaseStore

from memory_agent.configuration import Configuration

logger = logging.getLogger(__name__)

# V PROCESU(A4): Implementace funkce upsert_memory pro ukládání paměti - čeká na dokončení testů
async def upsert_memory(
    content: str,
    context: str,
    *,
    memory_id: Optional[uuid.UUID] = None,
    # Hide these arguments from the model.
    config: Annotated[RunnableConfig, InjectedToolArg],
    store: Annotated[BaseStore, InjectedToolArg],
):
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
    """
    try:
        logger.info(f"Upserting memory: content='{content[:50]}...'")
        
        # Generate or use provided memory ID
        mem_id = memory_id or uuid.uuid4()
        logger.debug(f"Memory ID: {mem_id}")
        
        # Extract user ID from configuration
        try:
            user_id = Configuration.from_runnable_config(config).user_id
            logger.debug(f"User ID: {user_id}")
        except Exception as e:
            logger.error(f"Error extracting user_id from config: {str(e)}")
            logger.error(traceback.format_exc())
            raise ValueError(f"Failed to get user_id from configuration: {str(e)}")
        
        # Prepare memory data
        memory_data = {"content": content, "context": context}
        logger.debug(f"Memory data: {memory_data}")
        
        # Store memory in database
        try:
            logger.info(f"Storing memory {mem_id} for user {user_id}")
            await store.aput(
                ("memories", user_id),
                key=str(mem_id),
                value=memory_data,
            )
            logger.info(f"Successfully stored memory {mem_id}")
        except Exception as e:
            logger.error(f"Database error storing memory: {str(e)}")
            logger.error(traceback.format_exc())
            raise RuntimeError(f"Failed to store memory in database: {str(e)}")
        
        return f"Stored memory {mem_id}"
    except Exception as e:
        error_msg = f"Error in upsert_memory: {str(e)}"
        logger.error(error_msg)
        logger.error(traceback.format_exc())
        return f"Failed to store memory: {str(e)}"


# V PROCESU: Implementace nástroje pro získávání dat ze Sayari API
class SayariApiTool(BaseTool):
    """Nástroj pro volání Sayari API a získání informací o společnosti."""
    
    name: str = "sayari_api_tool"
    description: str = "Získává informace o společnosti z Sayari API"
    
    base_url: ClassVar[str] = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/sayari-simulator"
    
    async def _arun(self, company_name: str) -> Dict[str, Any]:
        """Asynchronní volání Sayari API."""
        logger.info(f"Volání Sayari API pro společnost: {company_name}")
        
        try:
            search_url = f"{self.base_url}/search/entity?q={company_name}"
            
            async with httpx.AsyncClient() as client:
                logger.debug(f"Odesílání GET požadavku na URL: {search_url}")
                response = await client.get(search_url)
                response.raise_for_status()  # Vyvolá výjimku při chybě
                data = response.json()
                
            logger.debug(f"Obdržena odpověď z API: {json.dumps(data)[:200]}...")
            
            # Zpracování odpovědi
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
            error_msg = f"HTTP chyba při volání Sayari API: {e.response.status_code}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Chyba při komunikaci se Sayari API: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except Exception as e:
            error_msg = f"Neočekávaná chyba při volání Sayari API: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise ToolException(error_msg)
    
    def _parse_company_data(self, api_response: Dict[str, Any]) -> Dict[str, Any]:
        """Zpracuje odpověď z API a extrahuje relevantní data o společnosti.
        
        Args:
            api_response: Surová odpověď z API
            
        Returns:
            Strukturovaná data o společnosti
        """
        try:
            # Implementace
            result = {
                "name": "",
                "risk_score": 0,
                "industry": "",
                "founded": None
            }
            
            # Extrahuj data z api_response
            if not api_response or not api_response.get("data"):
                logger.warning("Prázdná nebo neplatná odpověď z API")
                return result
            
            entity_data = api_response.get("data", {})
            
            # Extrahuj základní informace
            result["name"] = entity_data.get("label", "")
            
            # Konverze risk_score na číslo (integer)
            try:
                risk_score = entity_data.get("risk_score", "0")
                result["risk_score"] = int(risk_score) if risk_score else 0
            except (ValueError, TypeError):
                logger.warning(f"Nelze převést risk_score na číslo: {entity_data.get('risk_score')}")
                result["risk_score"] = 0
            
            # Extrahuj informace o průmyslu a datumu založení
            metadata = entity_data.get("metadata", {})
            result["industry"] = metadata.get("industry", "")
            
            # Zpracování datumu založení (pokud existuje)
            if "founded" in metadata and metadata["founded"]:
                result["founded"] = metadata["founded"]
            
            return result
        except Exception as e:
            logger.error(f"Chyba při zpracování dat společnosti: {str(e)}")
            return {"error": str(e)}
    
    def _extract_entities(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extrahuje entity z odpovědi API."""
        if not data or not data.get("data"):
            return []
                
        entity_data = data.get("data", {})
        return [{
            "id": entity_data.get("id", ""),
            "name": entity_data.get("label", ""),
            "type": entity_data.get("type", "Company"),
            "risk_score": entity_data.get("risk_score", "0")
        }]
    
    def _extract_entity_id(self, data: Dict[str, Any]) -> Optional[str]:
        """Extrahuje ID entity z odpovědi API."""
        if not data or not data.get("data"):
            return None
                
        return data.get("data", {}).get("id")
    
    def _extract_risk_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrahuje data o riziku z odpovědi API."""
        if not data or not data.get("data"):
            return {
                "sanctions_status": "Žádné aktivní sankce nenalezeny",
                "pep_connections": [],
                "compliance_issues": [],
                "risk_score": "0",
                "risk_factors": []
            }
            
        entity_data = data.get("data", {})
        return {
            "sanctions_status": entity_data.get("sanctions_status", "Žádné aktivní sankce nenalezeny"),
            "pep_connections": entity_data.get("pep_connections", []),
            "compliance_issues": entity_data.get("compliance_issues", []),
            "risk_score": entity_data.get("risk_score", "0"),
            "risk_factors": list(entity_data.get("risk_factors", {}).keys()) if isinstance(entity_data.get("risk_factors"), dict) else []
        }


# V PROCESU: Implementace nástroje pro získávání interních dat ze Supabase
class SupabaseInternalDataTool(BaseTool):
    """Nástroj pro získání interních dat o společnosti ze Supabase."""
    
    name: str = "supabase_internal_data_tool"
    description: str = "Získává interní data o společnosti včetně tier klasifikace a HS kódů"
    
    base_url: ClassVar[str] = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/get-supplier-data"
    
    async def _arun(self, company_name: str) -> Dict[str, Any]:
        """Asynchronní volání Supabase API pro získání interních dat."""
        logger.info(f"Získávání interních dat pro společnost: {company_name}")
        
        try:
            # Vytvoření URL s parametrem pro název společnosti
            request_url = f"{self.base_url}?name={company_name}"
            
            async with httpx.AsyncClient() as client:
                logger.debug(f"Odesílání GET požadavku na URL: {request_url}")
                response = await client.get(request_url)
                response.raise_for_status()
                data = response.json()
                
            logger.debug(f"Obdržena odpověď z API: {json.dumps(data)[:200]}...")
            
            # Zpracování odpovědi
            return self._process_internal_data(data, company_name)
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP chyba při získávání interních dat: {e.response.status_code}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Chyba při komunikaci s API: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except Exception as e:
            error_msg = f"Neočekávaná chyba při získávání interních dat: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise ToolException(error_msg)
    
    def _process_internal_data(self, data: Dict[str, Any], company_name: str) -> Dict[str, Any]:
        """Zpracovává interní data o společnosti."""
        # Extrakce dat z supplier_info
        supplier_info = data.get("supplier_info", {})
        
        # Extrakce tier klasifikace
        tier_classification = supplier_info.get("primary_tier", "Neurčeno")
        
        # Extrakce HS kódů
        hs_codes = []
        if "hs_code_matches" in supplier_info and isinstance(supplier_info["hs_code_matches"], list):
            hs_codes = [match.get("hsCode", "") for match in supplier_info["hs_code_matches"] if match.get("hsCode")]
        
        # Extrakce obchodních aktivit
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
                "geographic_presence": []
            }
        }


# V PROCESU(A4): Implementace nástroje pro získávání vztahů entit ze Sayari API - chybí testy pro úspěšnou odpověď a prázdné ID
class SayariRelationshipsTool(BaseTool):
    """Nástroj pro získání vztahů entity z Sayari API."""
    
    name: str = "sayari_relationships_tool"
    description: str = "Získává vztahy entity (společnosti) z Sayari API"
    
    base_url: ClassVar[str] = "https://zyjgjpdwpdgfrpilxvvg.supabase.co/functions/v1/sayari-simulator"
    
    async def _arun(self, entity_id: str) -> Dict[str, Any]:
        """Asynchronní volání Sayari API pro získání vztahů."""
        logger.info(f"Získávání vztahů pro entitu s ID: {entity_id}")
        
        if not entity_id:
            logger.warning("Nelze získat vztahy - chybí ID entity")
            return {
                "has_relationships": False,
                "relationships": [],
                "visualization": {"nodes": [], "links": []}
            }
            
        try:
            relationship_url = f"{self.base_url}/entity/{entity_id}/relationships"
            
            async with httpx.AsyncClient() as client:
                logger.debug(f"Odesílání GET požadavku na URL: {relationship_url}")
                response = await client.get(relationship_url)
                response.raise_for_status()
                data = response.json()
                
            logger.debug(f"Obdržena odpověď z API: {json.dumps(data)[:200]}...")
            
            # Extrakce a formátování vztahů
            relationships = self._process_relationships(data)
            visualization = self._create_visualization(data)
                
            return {
                "has_relationships": bool(relationships),
                "relationships": relationships,
                "visualization": visualization
            }
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP chyba při získávání vztahů: {e.response.status_code}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except httpx.RequestError as e:
            error_msg = f"Chyba při komunikaci s API: {str(e)}"
            logger.error(error_msg)
            raise ToolException(error_msg)
        except Exception as e:
            error_msg = f"Neočekávaná chyba při získávání vztahů: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            raise ToolException(error_msg)
    
    def _process_relationships(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Zpracovává vztahy z odpovědi API."""
        if not data or not isinstance(data, dict):
            return {"suppliers": [], "customers": [], "ownership": [], "key_relationships": []}
        
        relationships = data.get("relationships", [])
        if not isinstance(relationships, list):
            relationships = []
        
        # Kategorizace vztahů podle typu
        suppliers = []
        customers = []
        ownership = []
        key_relationships = []
        
        for rel in relationships:
            rel_type = rel.get("type", "")
            source_label = rel.get("source", {}).get("label", "")
            target_label = rel.get("target", {}).get("label", "")
            
            if rel_type in ["has_supplier", "supplies_to"]:
                if source_label:
                    suppliers.append(source_label)
                if target_label:
                    customers.append(target_label)
            elif rel_type in ["has_subsidiary", "subsidiary_of", "has_shareholder", "shareholder_of"]:
                if source_label and target_label:
                    ownership.append(f"{source_label} -> {target_label} ({rel_type})")
            elif source_label and target_label:
                key_relationships.append(f"{source_label} -> {target_label} ({rel_type})")
        
        return {
            "suppliers": list(set(suppliers)),
            "customers": list(set(customers)),
            "ownership": ownership,
            "key_relationships": key_relationships
        }
    
    def _create_visualization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Vytváří vizualizační data pro vztahy."""
        if not data or not isinstance(data, dict):
            return {"nodes": [], "links": []}
        
        relationships = data.get("relationships", [])
        if not isinstance(relationships, list):
            relationships = []
        
        # Mapa pro ukládání jedinečných uzlů
        nodes_map = {}
        links = []
        
        # Vytvoření uzlů a hran
        for rel in relationships:
            rel_type = rel.get("type", "")
            
            # Zpracování zdrojového uzlu
            source = rel.get("source", {})
            source_id = source.get("id", "")
            source_label = source.get("label", "")
            source_type = source.get("type", "company")
            
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
            
            # Vytvoření hrany
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
        
        return {
            "nodes": list(nodes_map.values()),
            "links": links
        }
    
    def _get_node_color(self, node_type: str) -> str:
        """Vrací barvu uzlu podle typu."""
        type_colors = {
            "company": "#3366CC",
            "person": "#33AA33",
            "organization": "#CC6633"
        }
        return type_colors.get(node_type.lower(), "#AAAAAA")
    
    def _get_edge_color(self, edge_type: str) -> str:
        """Vrací barvu hrany podle typu vztahu."""
        type_colors = {
            "has_subsidiary": "#3366CC",
            "subsidiary_of": "#3366CC",
            "has_officer": "#33AA33",
            "officer_of": "#33AA33",
            "has_shareholder": "#CC6633",
            "shareholder_of": "#CC6633",
            "has_supplier": "#9900CC",
            "supplies_to": "#9900CC",
            "supplies": "#9900CC"
        }
        return type_colors.get(edge_type.lower(), "#AAAAAA")
