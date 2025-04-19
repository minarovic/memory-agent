# Copilot Instructions for Memory Agent Project

Tato příručka poskytuje základní pokyny pro AI asistenty pracující s kódem Memory Agent projektu.

## 1. Základní principy analýzy kódu

- **Architektura projektu:** Při analýze vždy zohledni hybridní architekturu projektu (LangGraph workflow + React Agents + LCEL chains)
- **Workflow komponenty:** Identifikuj, zda analyzovaný kód patří do workflow orchestrace (LangGraph), nástrojů (Tools) nebo řetězců (Chains)
- **Dodržování standardů:** Kontroluj, zda kód využívá správně LangChain a LangGraph komponenty podle aktuálních verzí (≥0.3.x)
- **Asynchronní operace:** Ověř, že kód správně implementuje asynchronní volání pomocí `async/await` a ne synchronní volání
- **State management:** Při analýze workflow komponent věnuj pozornost správě stavu pomocí `State` objektu v LangGraph

## 2. Jak pracovat s dokumentací komponent

- **Umístění dokumentace:** Veškerá dokumentace komponent se nachází v adresáři `docs/components/`
- **Struktura dokumentace:** Každá komponenta by měla obsahovat:
  - Účel a základní popis
  - Vstupní a výstupní datové struktury
  - Závislosti na jiných komponentách
  - Příklady použití
- **Aktualizace dokumentace:** Při změnách v implementaci je nutné aktualizovat i příslušnou dokumentaci
- **Reference na API:** Při práci s externími API (Sayari, Supabase) vždy odkazuj na aktuální dokumentaci v `docs/`

## 3. Jak ověřovat implementaci

- **Unit testy:** Každá nová funkce musí mít odpovídající unit testy v adresáři `tests/unit_tests/`
- **Integrační testy:** Složitější workflow musí mít integrační testy v `tests/integration_tests/`
- **Typové kontroly:** Používej typové anotace a ověř správnost pomocí `mypy`
- **Kontrolní body:**
  - Jsou použity správné LangChain/LangGraph komponenty?
  - Jsou všechny operace asynchronní kde je to vhodné?
  - Jsou stavy grafu správně aktualizovány?
  - Je zachována kompatibilita s existujícím workflow?
  - Jsou správně ošetřeny chybové stavy a výjimky?

## 4. Status úkolů

### V PROCESU
- Implementace analýzy vztahů mezi společnostmi
- Vylepšení ukládání a načítání paměti
- Optimalizace promptů pro analýzu

### DOKONČENO
- Základní struktura LangGraph workflow
- Integrace Sayari API pro získání dat o společnostech
- Implementace Supabase pro ukládání interních dat
- Analýza vstupu uživatele pro extrakci společností a typu analýzy
- Generování odpovědí na základě sesbíraných dat
