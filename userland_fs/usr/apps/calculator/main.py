#!/usr/bin/env python3
"""
ONEX Calculator App
Semplice calcolatrice a riga di comando
"""

__title__ = "calculator"
__description__ = "Semplice calcolatrice a riga di comando"
__version__ = "1.0.0"
__author__ = "ONEX Team"

import sys

def calculate(expression):
    """Valuta un'espressione matematica semplice."""
    try:
        # Valutazione sicura (limitata a operazioni aritmetiche)
        # Usa eval() solo per questo esempio semplice
        allowed_chars = "0123456789+-*/() ."
        if any(c not in allowed_chars for c in expression):
            return "Errore: caratteri non consentiti"
        
        result = eval(expression)
        return f"Risultato: {result}"
    except Exception as e:
        return f"Errore: {e}"

def main():
    """Funzione principale."""
    print("=== ONEX Calculator ===")
    print("Digita 'exit' per uscire")
    
    if len(sys.argv) > 1:
        # Se passato come argomento, valuta l'espressione direttamente
        expression = " ".join(sys.argv[1:])
        print(calculate(expression))
        return
    
    # Modalità interattiva
    while True:
        try:
            expression = input("\nEspressione > ").strip()
            
            if expression.lower() in ['exit', 'quit', 'q']:
                break
                
            if not expression:
                continue
                
            print(calculate(expression))
                
        except KeyboardInterrupt:
            print("\nUscita...")
            break
        except Exception as e:
            print(f"Errore: {e}")

if __name__ == "__main__":
    main()
