#!/usr/bin/env python3
"""
ONEX - Sistema Userland
Modulo principale che coordina l'avvio del sistema e carica l'ambiente userland
"""

import os
import sys
import json
import curses
from pathlib import Path
from typing import Dict, Any, Optional

# Aggiungi il percorso base al PATH
base_path = Path(__file__).parent.parent.absolute()
if str(base_path) not in sys.path:
    sys.path.insert(0, str(base_path))

# Importa il modulo dei loghi
try:
    from src.graphics.logos import print_logo
except ImportError:
    # Funzione di fallback se non possiamo importare i loghi
    def print_logo(logo_type=None):
        print("=== ONEX SYSTEM ===")

class MainSystem:
    """
    Classe principale che gestisce l'avvio del sistema ONEX
    dopo la fase di bootstrap.
    """
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.absolute()
        self.system_info = {}
        self.user_info = {}
        self.current_user = None
        self.userland_fs_path = self.base_path / "userland_fs"
        
        # Inizializza i moduli di base
        self._init_base_modules()
    
    def _init_base_modules(self) -> bool:
        """Inizializza i moduli di base necessari per il sistema."""
        try:
            # Assicura che curses sia disponibile
            import curses
            
            # Inizializza i moduli grafici senza attivare l'interfaccia
            from src.graphics.ui import UserInterface
            from src.graphics.graphics import TerminalGraphics
            from src.system.input import InputHandler
            
            # Verifica che il modulo file_manager sia disponibile
            from src.userland.file_manager import FileManager
            
            print("✓ Moduli di base inizializzati")
            return True
        except ImportError as e:
            print(f"⚠️ Errore nell'inizializzazione dei moduli di base: {e}")
            print("  Alcune funzionalità potrebbero non essere disponibili")
            return False
    
    def load_system_info(self) -> bool:
        """Carica le informazioni di sistema dal file creato dal bootloader."""
        try:
            system_info_path = self.base_path / "system_info.json"
            if not system_info_path.exists():
                print("❌ File di informazioni di sistema non trovato!")
                return False
                
            with open(system_info_path, 'r') as f:
                data = json.load(f)
            
            self.system_info = data.get("system", {})
            self.user_info = data.get("user", {})
            self.current_user = self.user_info.get("current_user")
            
            print(f"✅ Informazioni di sistema caricate. Utente: {self.current_user}")
            return True
            
        except Exception as e:
            print(f"❌ Errore durante il caricamento delle informazioni di sistema: {e}")
            return False
    
    def verify_imports(self) -> bool:
        """
        Verifica che tutte le importazioni necessarie funzionino correttamente.
        Utilizzato dal bootloader per testare l'ambiente.
        """
        try:
            # Test importazione dei moduli di sistema
            from src.system import shell_compatibility, input
            print("✓ Moduli di sistema importati correttamente")
            
            # Test importazione dei moduli grafici
            from src.graphics import ui, graphics, logos  # Aggiungi logos
            print("✓ Moduli grafici importati correttamente")
            
            # Test importazione userland
            from src.userland import userland
            print("✓ Modulo userland importato correttamente")
            
            # Test file manager
            from src.userland import file_manager
            print("✓ Modulo file manager importato correttamente")
            
            return True
        except ImportError as e:
            print(f"❌ Errore di importazione: {e}")
            return False
    
    def start_userland(self) -> None:
        """Avvia l'ambiente userland."""
        try:
            from src.userland.userland import UserLandSystem
            
            # Passa le informazioni di sistema e utente all'userland
            userland_system = UserLandSystem(
                system_info=self.system_info,
                user_info=self.user_info,
                current_user=self.current_user,
                fs_root=self.userland_fs_path
            )
            
            # Avvia l'ambiente userland
            userland_system.start()
            
        except Exception as e:
            print(f"❌ Errore durante l'avvio dell'userland: {e}")
            import traceback
            traceback.print_exc()
    
    def shutdown(self) -> None:
        """Esegue le operazioni di chiusura del sistema."""
        print("\n🛑 Arresto del sistema ONEX in corso...")
        # Operazioni di pulizia se necessarie
        print("✅ Sistema arrestato correttamente.")

def main() -> int:
    """
    Funzione principale che gestisce l'avvio del sistema ONEX.
    Viene chiamata dal bootloader dopo la fase di inizializzazione.
    
    Returns:
        int: Codice di uscita (0 per successo, altri valori per errori)
    """
    try:
        # Mostra il logo di avvio
        print_logo("boot")
        
        print("\n🚀 Inizializzazione del sistema principale ONEX...")
        
        main_system = MainSystem()
        
        # Carica le informazioni di sistema
        if not main_system.load_system_info():
            print("❌ Impossibile caricare le informazioni di sistema. Uscita.")
            return 1
        
        # Avvia l'ambiente userland
        main_system.start_userland()
        
        # Chiusura ordinata
        main_system.shutdown()
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruzione da tastiera. Arresto del sistema.")
        return 130
    except Exception as e:
        print_logo("error")
        print(f"\n❌ Errore imprevisto: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
