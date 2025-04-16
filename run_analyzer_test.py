#!/usr/bin/env python
"""
Jednoduchý skript pro spuštění testů analyzátoru a zobrazení výsledků.
"""

import os
import sys
import subprocess
import datetime

# Nastavení cesty k testům
TEST_PATH = "tests/unit_tests/test_analyzer.py"
RESULTS_FILE = "analyzer_test_results.log"

def run_test():
    """Spustí testy analyzátoru a zapíše výsledky do souboru."""
    print(f"Spouštím testy: {TEST_PATH}")
    
    # Vytvoření časového razítka pro log
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Spuštění pytest s parametrem -v (verbose)
    result = subprocess.run(
        ["python", "-m", "pytest", TEST_PATH, "-v"],
        capture_output=True,
        text=True
    )
    
    # Výpis výsledků do konzole
    print("\n----- VÝSLEDEK TESTŮ -----")
    print(f"Návratový kód: {result.returncode} (0 = úspěch, jinak selhání)")
    print("\n----- VÝSTUP TESTŮ -----")
    print(result.stdout)
    
    if result.stderr:
        print("\n----- CHYBY -----")
        print(result.stderr)
    
    # Zápis výsledků do souboru
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write(f"=== Test {TEST_PATH} - {timestamp} ===\n\n")
        f.write(f"Návratový kód: {result.returncode}\n\n")
        f.write(result.stdout)
        if result.stderr:
            f.write("\n----- CHYBY -----\n")
            f.write(result.stderr)
    
    print(f"\nVýsledky byly zapsány do souboru: {RESULTS_FILE}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(run_test())
