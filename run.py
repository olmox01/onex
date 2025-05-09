#!/usr/bin/env python3
import os
import sys
import traceback
from pathlib import Path

def check_venv():
    """
    Controlla se è presente un ambiente virtuale e lo attiva se necessario.
    """
    base_path = Path(__file__).parent.absolute()
    venv_dir = base_path / ".venv"
    
    if venv_dir.exists():
        # Determina il percorso del site-packages nell'ambiente virtuale
        site_packages = None
        
        if sys.platform == "win32":
            site_packages = venv_dir / "Lib" / "site-packages"
        else:
            # Per sistemi Unix-like
            python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
            site_packages = venv_dir / "lib" / python_version / "site-packages"
            
            # Se non esiste, cerca in altre directory Python
            if not site_packages.exists():
                for item in (venv_dir / "lib").glob("python*"):
                    if item.is_dir() and (item / "site-packages").exists():
                        site_packages = item / "site-packages"
                        break
            
        # Aggiungi il site-packages al path di Python se esiste
        if site_packages and site_packages.exists() and str(site_packages) not in sys.path:
            sys.path.insert(0, str(site_packages))
            print(f"🔄 Ambiente virtuale attivato: {site_packages}")
            return True
    
    return False

def main():
    """
    Punto di ingresso principale che avvia il bootloader e poi esegue main.py
    """
    print("=== ONEX USERLAND SYSTEM STARTUP ===")
    
    # Verifica se esiste un ambiente virtuale
    check_venv()
    
    # Aggiungi il percorso base al PATH di Python
    base_path = Path(__file__).parent.absolute()
    sys.path.insert(0, str(base_path))
    
    try:
        # Importa e avvia il bootloader
        print("\nAvvio del bootloader...")
        from bootloader.boot import Bootloader
        
        bootloader = Bootloader()
        boot_success = bootloader.boot()
        
        if not boot_success:
            print("\nErrore: Il bootloader non è stato completato con successo.")
            sys.exit(1)
        
        # Se il bootloader è riuscito, avvia il programma principale
        print("\nAvvio del programma principale...")
        from src.main import main as start_main
        
        # Esegui il programma principale
        exit_code = start_main()
        sys.exit(exit_code)
        
    except ImportError as e:
        print(f"\nErrore di importazione: {e}")
        print("Verifica che tutti i file necessari esistano e siano accessibili.")
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\nErrore imprevisto: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
