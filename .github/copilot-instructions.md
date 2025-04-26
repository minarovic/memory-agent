# GitHub Copilot - Pokyny pro modernizaci state.py
# Tento dokument slouží jako pokyn pro GitHub Copilot k modernizaci souboru state.py v projektu Memory Agent.
# Zaměřuje se na implementaci moderního state managementu s využitím @dataclass a speciálních anotací LangGraph.




```markdown
# Modernizace komponenty State v projektu Memory Agent

## Úkol
Analyzuj a modernizuj state.py z projektu Memory Agent. Zaměř se na implementaci state management s využitím @dataclass a speciálních anotací LangGraph.

## Současný kód
Aktuální implementace již používá @dataclass, ale potřebuje rozšíření a vylepšení:

```python
"""Define the shared values."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated

from memory_agent.analyzer import AnalysisResult

# BLOKOVÁNO(B1): Implementace stavového grafu čeká na dokončení unit testů pro tools.py (A4)
@dataclass(kw_only=True)
class State:
    """Main graph state."""

    messages: Annotated[list[AnyMessage], add_messages]
    """The messages in the conversation."""
    
    company_analysis: Optional[AnalysisResult] = None
    """Výsledek analýzy společností z uživatelského dotazu."""


__all__ = [
    "State",
]
```

## Požadované vylepšení
1. Zkontroluj, zda implementace plně využívá moderních funkcí LangGraph
2. Rozšiř State třídu o další standardní atributy používané v moderních LangGraph workflow:
   - Přidej pole pro ukládání dat o společnostech (`company_data`, `internal_data`, `relationships_data`)
   - Přidej pole pro chybové stavy a výstup
   - Zachovej kompatibilitu s existujícím kódem

3. Doplň podrobné docstringy vysvětlující:
   - Účel každého atributu ve workflow
   - Jak funguje anotace `add_messages`
   - Jak State interaguje s ostatními komponentami

4. Využij dokumentaci z Context7 serveru k implementaci nejlepších praktik

## Použití Context7 MCP serveru
Nejprve získej aktuální dokumentaci k state management v LangGraph:

```
resolve-library-id --libraryName="langgraph"
get-library-docs --context7CompatibleLibraryID="langgraph-ai/langgraph" --topic="state"
```

## Očekávaný výstup
Kompletní modernizovaný soubor state.py s:
- Rozšířenou definicí State třídy
- Podrobnými komentáři a docstringy
- Implementací moderních přístupů LangGraph k správě stavu
```

