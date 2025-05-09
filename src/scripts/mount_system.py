#!/usr/bin/env python3
"""
ONEX Mount System Script
Configura il mount point per il filesystem reale nel filesystem virtuale
"""

import os
import sys
import stat
from pathlib import Path

def setup_mount_point(fs_root: Path) -> bool:
    """
    Configura il mount point per il filesystem reale.
    
    Args:
        fs_root: Percorso root del filesystem virtuale
        
    Returns:
        bool: True se la configurazione è riuscita
    """
    mount_point = fs_root / "mnt" / "system"
    
    print(f"Configurazione del mount point: {mount_point}")
    
    try:
        # Crea il mount point se non esiste
        mount_point.mkdir(parents=True, exist_ok=True)
        
        # Imposta i permessi
        os.chmod(mount_point, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
        
        print(f"Mount point configurato con successo: {mount_point}")
        print("Il filesystem reale sarà accessibile in: /mnt/system")
        
        return True
    except Exception as e:
        print(f"Errore durante la configurazione del mount point: {e}")
        return False

def main():
    """Funzione principale."""
    if len(sys.argv) > 1:
        fs_root = Path(sys.argv[1])
    else:
        base_dir = Path(__file__).parent.parent.parent.absolute()
        fs_root = base_dir / "userland_fs"
    
    if not fs_root.exists():
        print(f"Il filesystem virtuale non esiste: {fs_root}")
        print("Creazione del filesystem virtuale...")
        fs_root.mkdir(parents=True, exist_ok=True)
    
    success = setup_mount_point(fs_root)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
