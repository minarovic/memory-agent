#!/usr/bin/env python
"""
Skript pro spuštění testů analyzer.py a zápis výsledků.
"""

import os
import sys
import datetime
import subprocess
import json

def run_analyzer_tests():
    """Spustí testy pro analyzer.py a zapíše výsledky."""
    # Vytvoření adresáře pro výsledky, pokud neexistuje
    results_dir = os.path.join(os.path.dirname(__file__), "test_results")
    os.makedirs(results_dir, exist_ok=True)
    
    # Současné datum a čas pro název souboru
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = os.path.join(results_dir, f"analyzer_tests_{timestamp}.log")
    
    # Definice příkazu pro pytest
    test_path = "tests/unit_tests/test_analyzer.py"
    cmd = ["python", "-m", "pytest", test_path, "-v"]
    
    print(f"Spouštím testy: {' '.join(cmd)}")
    
    # Spuštění testů a zachycení výstupu
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Zobrazení výstupu v terminálu
        print("\n--- Výstup testů ---")
        print(result.stdout)
        
        if result.stderr:
            print("\n--- Chyby ---")
            print(result.stderr)
        
        # Vytvoření struktury výsledků
        test_results = {
            "timestamp": timestamp,
            "test_file": test_path,
            "success": result.returncode == 0,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
        
        # Zápis výsledků do souboru
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"=== Test {test_path} - {timestamp} ===\n\n")
            f.write(f"Návratový kód: {result.returncode}\n")
            f.write(f"Úspěch: {'Ano' if result.returncode == 0 else 'Ne'}\n\n")
            f.write("--- Výstup ---\n")
            f.write(result.stdout)
            if result.stderr:
                f.write("\n--- Chyby ---\n")
                f.write(result.stderr)
        
        # Zápis strukturovaných výsledků do JSON souboru pro případné strojové zpracování
        json_output_file = os.path.join(results_dir, f"analyzer_tests_{timestamp}.json")
        with open(json_output_file, "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2)
        
        # Výsledek pro uživatele
        if result.returncode == 0:
            print(f"\n✅ Testy {test_path} ÚSPĚŠNĚ dokončeny!")
        else:
            print(f"\n❌ Testy {test_path} SELHALY s kódem {result.returncode}")
        
        print(f"Výsledky byly zapsány do:\n- {output_file}\n- {json_output_file}")
        
        return result.returncode
        
    except Exception as e:
        error_message = f"Chyba při spouštění testů: {str(e)}"
        print(f"\n❌ {error_message}")
        
        # Zápis chyby do souboru
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(f"=== Test {test_path} - {timestamp} ===\n\n")
            f.write(f"CHYBA: {error_message}\n")
        
        return 1

if __name__ == "__main__":
    sys.exit(run_analyzer_tests())
