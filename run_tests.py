#!/usr/bin/env python
"""
Test runner for Memory Agent - spouští testy a zapisuje výsledky do souboru.
"""

import os
import sys
import datetime
import subprocess
import argparse

def run_tests(test_path, output_file=None):
    """
    Spustí testy na zadané cestě a zapíše výsledky do souboru.
    
    Args:
        test_path: Cesta k testům, které mají být spuštěny
        output_file: Soubor pro zápis výsledků (volitelný)
    
    Returns:
        Kód výsledku (0 při úspěchu)
    """
    # Vytvoření časového razítka
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Příprava příkazu pro pytest
    cmd = ["python", "-m", "pytest", test_path, "-v"]
    
    print(f"Spouštím testy: {' '.join(cmd)}")
    
    # Spuštění testů a zachycení výstupu
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Zobrazení výstupu v terminálu
    print("\n--- Výstup testů ---")
    print(result.stdout)
    
    if result.stderr:
        print("\n--- Chyby ---")
        print(result.stderr)
    
    # Zápis výsledků do souboru, pokud je zadán
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"\n\n=== Test {test_path} - {timestamp} ===\n")
            f.write(f"Návratový kód: {result.returncode}\n\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\n--- Chyby ---\n")
                f.write(result.stderr)
            f.write("\n" + "="*50 + "\n")
    
    return result.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test runner pro Memory Agent")
    parser.add_argument("--test-path", default="tests/unit_tests/test_analyzer.py",
                      help="Cesta k testům, které mají být spuštěny")
    parser.add_argument("--output", default="test_results.log",
                      help="Soubor pro zápis výsledků")
    
    args = parser.parse_args()
    
    # Vytvoření adresáře pro výstupní soubor, pokud neexistuje
    os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else ".", exist_ok=True)
    
    # Spuštění testů
    result = run_tests(args.test_path, args.output)
    
    # Výpis výsledku
    if result == 0:
        print(f"\nTesty {args.test_path} ÚSPĚŠNĚ dokončeny!")
        print(f"Výsledky byly zapsány do {args.output}")
    else:
        print(f"\nTesty {args.test_path} SELHALY s kódem {result}")
        print(f"Podrobnosti najdete v {args.output}")
    
    sys.exit(result)
