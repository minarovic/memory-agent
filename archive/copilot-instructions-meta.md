# Dočasné instrukce pro GitHub Copilot - Vytváření dokumentace metod

## Kontext
Vytváříš dokumentační šablony pro metody jednotlivých komponent Memory Agent projektu. Tyto šablony budou později použity pro samotnou implementaci kódu.

## Úkol
Tvým úkolem je POUZE vytvářet dokumentační soubory podle definované struktury. NEIMPLEMENTUJ žádný kód.

## Struktura dokumentace
### Hlavní soubor komponenty (např. `component_name.md` - kde component_name je název komponenty jako analyzer, tools, graph, atd.):
- Přehled komponenty
- Datové struktury
- Tok dat
- Seznam metod s odkazy na jejich dokumentační soubory
- Interakce metod
- Testování

### Soubor metody (např. `metoda_component_name.md` - kde metoda je název metody a component_name je název komponenty):
- Účel a kontext metody
- Implementační šablona
- Omezení a hranice
- Postup implementace
- Místo pro výslednou implementaci
- Instrukce pro dokumentaci
- Místo pro dokumentaci implementace

## Příklad pro konkrétní komponenty
- /docs/components/analyzer/analyzer.md (hlavní soubor)
- /docs/components/analyzer/parse_response_analyzer.md (metoda parse_response)
- /docs/components/tools/tools.md (hlavní soubor)
- /docs/components/tools/upsert_memory_tools.md (metoda upsert_memory)

## Instrukce
1. Analyzuj zdrojové soubory projektu a identifikuj komponenty a jejich metody
2. Pro každou metodu vytvoř dokumentační soubor dle výše uvedené struktury
3. Vyplň všechny sekce s relevantními informacemi
4. Ponech sekce "Výsledná implementace" a "Dokumentace implementace" prázdné
5. NEIMPLEMENTUJ žádný kód - vytváříš POUZE dokumentaci

## Poznámky
- Zaměř se na přesnost a úplnost dokumentace
- Zohledni existující architekturu a design projektu
- Dokumentuj metody v češtině, ale ponechej technické termíny v angličtině