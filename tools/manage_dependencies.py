#!/usr/bin/env python3
"""
ONEX Dependency Manager
Utility per gestire le dipendenze del progetto ONEX
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def create_venv(base_dir):
    """Crea un ambiente virtuale."""
    venv_dir = base_dir / ".venv"
    
    # Rimuovi l'ambiente esistente se presente
    if venv_dir.exists():
        import shutil
        print(f"🗑️  Rimozione ambiente virtuale esistente: {venv_dir}")
        shutil.rmtree(venv_dir)
    
    print(f"🔨 Creazione nuovo ambiente virtuale: {venv_dir}")
    
    try:
        # Crea l'ambiente virtuale
        import venv
        venv.create(venv_dir, with_pip=True)
        
        # Determina il percorso del pip nell'ambiente
        if sys.platform == "win32":
            pip_path = venv_dir / "Scripts" / "pip"
        else:
            pip_path = venv_dir / "bin" / "pip"
        
        # Aggiorna pip e setuptools
        subprocess.run([str(pip_path), "install", "--upgrade", "pip", "setuptools"], check=True)
        print("✅ Ambiente virtuale creato con successo")
        return pip_path
        
    except Exception as e:
        print(f"❌ Errore durante la creazione dell'ambiente virtuale: {e}")
        return None

def install_dependencies(pip_path, packages):
    """Installa le dipendenze nell'ambiente virtuale."""
    print(f"📦 Installazione dipendenze: {', '.join(packages)}")
    
    try:
        subprocess.run([str(pip_path), "install"] + packages, check=True)
        print("✅ Dipendenze installate con successo")
        return True
    except Exception as e:
        print(f"❌ Errore durante l'installazione delle dipendenze: {e}")
        return False

def main():
    """Funzione principale."""
    parser = argparse.ArgumentParser(description="Gestore dipendenze per ONEX")
    parser.add_argument("--recreate", action="store_true", help="Ricrea l'ambiente virtuale")
    parser.add_argument("--install", action="store_true", help="Installa le dipendenze")
    parser.add_argument("--list", action="store_true", help="Elenca le dipendenze installate")
    args = parser.parse_args()
    
    base_dir = Path(__file__).parent.parent.absolute()
    venv_dir = base_dir / ".venv"
    
    # Elenca le dipendenze predefinite
    packages = [
        "curses", "pyfiglet", "psutil", "questionary", 
        "colorama", "pillow", "tqdm"
    ]
    
    if args.recreate or not venv_dir.exists():
        pip_path = create_venv(base_dir)
        if not pip_path:
            sys.exit(1)
        
        if args.recreate or args.install:
            success = install_dependencies(pip_path, packages)
            if not success:
                sys.exit(1)
    elif args.install:
        # Usa il pip esistente
        if sys.platform == "win32":
            pip_path = venv_dir / "Scripts" / "pip"
        else:
            pip_path = venv_dir / "bin" / "pip"
            
        if not pip_path.exists():
            print(f"❌ Pip non trovato nell'ambiente virtuale: {pip_path}")
            sys.exit(1)
            
        success = install_dependencies(pip_path, packages)
        if not success:
            sys.exit(1)
    
    if args.list:
        # Mostra i pacchetti installati
        if sys.platform == "win32":
            pip_path = venv_dir / "Scripts" / "pip"
        else:
            pip_path = venv_dir / "bin" / "pip"
            
        if pip_path.exists():
            print("📋 Pacchetti installati:")
            subprocess.run([str(pip_path), "list"], check=False)
        else:
            print("❌ Ambiente virtuale non trovato")
            sys.exit(1)
    
    # Se non sono stati specificati argomenti, mostra l'help
    if not (args.recreate or args.install or args.list):
        parser.print_help()

if __name__ == "__main__":
    main()
