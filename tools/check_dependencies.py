#!/usr/bin/env python3
"""
ONEX Dependency Checker
Utility per verificare lo stato delle dipendenze e risolvere problemi comuni
"""

import os
import sys
import importlib
import subprocess
from pathlib import Path

def check_venv():
    """Verifica se è in uso un ambiente virtuale."""
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print(f"✅ Ambiente virtuale attivo: {sys.prefix}")
        return True
    else:
        print("❌ Nessun ambiente virtuale attivo")
        return False

def get_package_info(package_name):
    """Ottiene informazioni dettagliate su un pacchetto."""
    try:
        if package_name == "PIL":
            # Caso speciale per PIL/Pillow
            import PIL
            print(f"✅ PIL (Pillow) versione: {PIL.__version__}")
            print(f"   Percorso: {PIL.__file__}")
            return True
        else:
            module = importlib.import_module(package_name)
            version = getattr(module, "__version__", "sconosciuta")
            print(f"✅ {package_name} versione: {version}")
            print(f"   Percorso: {module.__file__}")
            return True
    except ImportError:
        print(f"❌ {package_name}: non installato o non importabile")
        return False
    except Exception as e:
        print(f"⚠️ Errore nell'ottenere informazioni su {package_name}: {e}")
        return False

def check_import_paths():
    """Controlla i percorsi di importazione Python."""
    print("\n📁 Percorsi di importazione Python:")
    for i, path in enumerate(sys.path):
        print(f"{i}: {path}")

def check_dependencies():
    """Verifica le dipendenze principali del progetto ONEX."""
    # Lista delle dipendenze da verificare
    dependencies = [
        "curses", 
        "pyfiglet", 
        "psutil", 
        "questionary", 
        "colorama", 
        "PIL",  # PIL/Pillow
        "tqdm"
    ]
    
    print("\n📦 Verifica delle dipendenze ONEX:")
    all_ok = True
    for dep in dependencies:
        if not get_package_info(dep):
            all_ok = False
            
    return all_ok

def fix_dependencies():
    """Tenta di risolvere i problemi con le dipendenze."""
    base_dir = Path(__file__).parent.parent.absolute()
    venv_dir = base_dir / ".venv"
    
    print("\n🔧 Tentativo di risoluzione dei problemi con le dipendenze...")
    
    # Controlla se esiste l'ambiente virtuale
    if not venv_dir.exists():
        print(f"❌ Ambiente virtuale non trovato in {venv_dir}")
        print("   Esegui il bootloader per creare l'ambiente virtuale")
        return False
    
    # Determina il pip da usare
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip"
    else:
        pip_path = venv_dir / "bin" / "pip"
    
    if not pip_path.exists():
        print(f"❌ pip non trovato in {pip_path}")
        return False
    
    # Reinstalla le dipendenze
    packages = ["pyfiglet", "psutil", "questionary", "colorama", "pillow", "tqdm"]
    print(f"📦 Reinstallazione dei pacchetti: {', '.join(packages)}")
    
    try:
        subprocess.run([str(pip_path), "install", "--upgrade"] + packages, check=True)
        print("✅ Reinstallazione completata")
        
        # Attiva l'ambiente virtuale
        site_packages = None
        if sys.platform == "win32":
            site_packages = venv_dir / "Lib" / "site-packages"
        else:
            python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
            site_packages = venv_dir / "lib" / python_version / "site-packages"
        
        if site_packages and site_packages.exists():
            if str(site_packages) not in sys.path:
                sys.path.insert(0, str(site_packages))
                print(f"✅ Aggiunto al path: {site_packages}")
        
        return True
    except Exception as e:
        print(f"❌ Errore durante la reinstallazione: {e}")
        return False

def main():
    """Funzione principale."""
    print("=== ONEX Dependency Checker ===\n")
    
    # Verifica ambiente virtuale
    check_venv()
    
    # Verifica percorsi di importazione
    check_import_paths()
    
    # Verifica dipendenze
    all_ok = check_dependencies()
    
    if not all_ok:
        print("\n⚠️ Alcune dipendenze presentano problemi")
        choice = input("\nProvare a risolvere i problemi? (s/n): ")
        if choice.lower() == 's':
            if fix_dependencies():
                print("\n🔍 Verifica delle dipendenze dopo la riparazione:")
                check_dependencies()
            else:
                print("\n❌ Impossibile risolvere automaticamente tutti i problemi")
                print("   Prova a eseguire manualmente: pip install -r requirements.txt")
    else:
        print("\n✅ Tutte le dipendenze sono correttamente installate e importabili")

if __name__ == "__main__":
    main()
