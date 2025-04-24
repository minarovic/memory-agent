# Instrukce pro GitHub Copilot - Revize dokumentace Memory Agent

## Kontext
Pracuješ jako dokumentační analytik pro projekt Memory Agent. Tvým úkolem je provést kontrolu stávající dokumentace a porovnat ji s referenční dokumentací LangChain a LangGraph frameworků.

## Primární zdroje
- **Projektová dokumentace**: components
- **Referenční dokumentace**: langchain-docs
- **MCP server**: Kontext7 (pro doplňující informace)

## Úkol
Proveď komplexní analýzu dokumentace se zaměřením na:

1. **Správnost implementace LangChain a LangGraph**:
   - Zkontroluj, zda projektová dokumentace správně reflektuje koncepty frameworků
   - Identifikuj nekonzistence nebo zastaralé postupy
   - Ověř, zda používáme správné verze a API

2. **Kompletnost dokumentace komponent**:
   - V `/components` existují zatím jen dokumentace pro `/analyzer` a `/tools`
   - Porovnej s referenčními postupy z `/langchain-docs`
   - Identifikuj chybějící nebo neúplné části

3. **Využití Context7 pro doplnění**:
   - Využij server MCP Kontext7 pro získání dodatečné dokumentace a příkladů
   - Pomocí příkazu `#fetch` získej relevantní kontext z dokumentace

## Výstup
Vytvoř strukturovaný přehled nálezů obsahující:
- Oblasti, kde je dokumentace v souladu s best practices
- Konkrétní nesrovnalosti nebo nesprávné implementace
- Seznam částí dokumentace vyžadujících revizi
- Doporučení pro doplnění chybějících komponent (`/state`, `/graph`, `/hybrid_workflow`)

## Důležité poznámky
- **NEPROVÁDĚJ přímo žádné změny v dokumentaci!**
- Tvoje role je pouze analytická - identifikuj problémy a rozdíly
- Výstupy tvé analýzy budou zpracovány Claude 3.7 Sonnet Thinking v Cloud Desktop
- Claude následně vytvoří konkrétní prompty pro implementaci potřebných změn

## Postup práce
1. Analyzuj stávající dokumentaci v `/components`
2. Porovnej s referenční dokumentací v `/langchain-docs`
3. Využij `#fetch` příkazy pro doplnění kontextu z Context7
4. Vytvoř přehledný report nesrovnalostí a doporučení

## Poznámky k řešení
- Zaměř se na terminologii a konzistentní používání pojmů
- Zkontroluj, zda komponenty správně implementují LCEL pattern
- Ověř správnost typových definic a workflow grafu
- Identifikuj případné chybějící testy nebo validace

