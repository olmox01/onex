#!/usr/bin/env python3
"""
ONEX Curses Fixer
Utility per verificare e riparare l'installazione di curses
"""

import os
import sys
import subprocess
from pathlib import Path

def check_curses():
    """Verifica se curses è disponibile nel sistema."""
    try:
        import curses
        print("✅ Il modulo curses è installato correttamente")
        return True
    except ImportError:
        print("❌ Il modulo curses non è disponibile")
        return False

def install_curses():
    """Tenta di installare curses."""
    print("📦 Tentativo di installazione del modulo curses...")
    
    if sys.platform == "win32":
        # Windows richiede windows-curses
        package = "windows-curses"
    else:
        # Su sistemi Linux, curses è generalmente parte di python3-dev
        if os.path.exists("/etc/debian_version"):
            print("📋 Sistema Debian/Ubuntu rilevato")
            print("🔧 Esecuzione: sudo apt install python3-dev libncurses-dev")
            try:
                subprocess.run(["sudo", "apt", "install", "-y", "python3-dev", "libncurses-dev"], check=True)
                return True
            except subprocess.CalledProcessError:
                print("❌ Impossibile installare python3-dev")
                return False
        elif os.path.exists("/etc/redhat-release"):
            print("📋 Sistema Red Hat/Fedora rilevato")
            print("🔧 Esecuzione: sudo dnf install python3-devel ncurses-devel")
            try:
                subprocess.run(["sudo", "dnf", "install", "-y", "python3-devel", "ncurses-devel"], check=True)
                return True
            except subprocess.CalledProcessError:
                print("❌ Impossibile installare python3-devel")
                return False
        elif os.path.exists("/etc/arch-release"):
            print("📋 Sistema Arch Linux rilevato")
            print("🔧 Esecuzione: sudo pacman -S python ncurses")
            try:
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm", "python", "ncurses"], check=True)
                return True
            except subprocess.CalledProcessError:
                print("❌ Impossibile installare ncurses")
                return False
        else:
            print("⚠️ Sistema operativo non riconosciuto")
            print("📝 Prova a installare manualmente i pacchetti per curses")
            print("   Su Debian/Ubuntu: sudo apt install python3-dev libncurses-dev")
            print("   Su Fedora/RHEL: sudo dnf install python3-devel ncurses-devel")
            print("   Su Arch Linux: sudo pacman -S python ncurses")
            return False
    
    return True

def setup_venv_with_curses():
    """Configura un ambiente virtuale con curses."""
    base_dir = Path(__file__).parent.parent.absolute()
    venv_dir = base_dir / ".venv"
    
    print(f"🔧 Creazione ambiente virtuale in {venv_dir}")
    
    # Crea l'ambiente virtuale
    try:
        import venv
        venv.create(venv_dir, with_pip=True)
    except Exception as e:
        print(f"❌ Errore nella creazione dell'ambiente virtuale: {e}")
        return False
    
    # Determina il percorso di pip
    if sys.platform == "win32":
        pip_path = venv_dir / "Scripts" / "pip"
    else:
        pip_path = venv_dir / "bin" / "pip"
    
    if not os.path.exists(pip_path):
        print(f"❌ Eseguibile pip non trovato in {pip_path}")
        return False
    
    # Installa i pacchetti necessari
    try:
        if sys.platform == "win32":
            subprocess.run([str(pip_path), "install", "windows-curses"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Impossibile installare i pacchetti necessari")
        return False

def main():
    """Funzione principale."""
    print("=== ONEX Curses Fixer ===\n")
    
    if check_curses():
        print("✅ Il sistema è configurato correttamente per usare curses")
        return 0
    
    print("\n❌ Il modulo curses non è disponibile")
    choice = input("\nProvare a risolvere il problema? (s/n): ")
    
    if choice.lower() != 's':
        print("❌ Operazione annullata dall'utente")
        return 1
    
    if install_curses():
        if check_curses():
            print("\n✅ Il modulo curses è stato installato con successo!")
            return 0
    
    print("\n⚠️ Impossibile installare curses nel sistema")
    print("📝 Tentativo di configurazione di un ambiente virtuale...")
    
    if setup_venv_with_curses():
        print("\n✅ Ambiente virtuale configurato con curses!")
        print("\n📋 Ora esegui:")
        print(f"   source {Path.cwd().parent / '.venv' / 'bin' / 'activate'}")
        print("   python run.py")
    else:
        print("\n❌ Impossibile configurare l'ambiente")
        print("\n📝 Prova a eseguire manualmente:")
        print("   python -m pip install --user --break-system-packages pyfiglet questionary pillow")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
