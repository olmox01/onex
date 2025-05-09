#!/usr/bin/env python3
"""
ONEX Configuration
Impostazioni generali del sistema ONEX
"""

import os
from pathlib import Path

# Percorso base dell'applicazione
BASE_DIR = Path(__file__).parent.parent.absolute()

# Configurazione Filesystem
FS_ROOT = BASE_DIR / "userland_fs"  # Root del filesystem virtuale
DEFAULT_SYSTEM_MOUNT = FS_ROOT / "mnt" / "system"  # Mount point per filesystem reale

# Utenti
DEFAULT_USER = os.environ.get('USER', 'onex')  # Utente di default
ADMIN_USERS = ['root', 'admin']  # Utenti con privilegi amministrativi
ENABLE_SUDO = True  # Se True, richiede privilegi sudo per alcune operazioni

# UI
TERMINAL_COLORS = True  # Abilita/disabilita i colori nel terminale
DEFAULT_UI_MODE = 'standard'  # 'standard', 'split', o 'fullscreen'
ENABLE_MOUSE = True  # Supporto mouse nell'interfaccia
SHOW_LOGO_ON_STARTUP = True  # Mostra il logo ONEX all'avvio
SHOW_LOGO_IN_PROMPT = False  # Usa il mini-logo nel prompt
LOGO_STYLE = 'default'  # 'default', 'mini', 'boot'

# Sistema
REQUIRED_PACKAGES = [
    "curses",
    "pyfiglet",
    "psutil", 
    "questionary",
    "colorama",
    "pillow",
    "tqdm"
]  # Pacchetti Python richiesti

LOG_LEVEL = "INFO"  # Livello di logging: DEBUG, INFO, WARNING, ERROR, CRITICAL
CACHE_DIR = BASE_DIR / "cache"  # Directory per la cache
LOG_DIR = BASE_DIR / "logs"  # Directory per i log
CONFIG_DIR = BASE_DIR / "config"  # Directory per le configurazioni

# Funzionalità
ENABLE_NETWORK = False  # Abilita funzionalità di rete simulate
ENABLE_PROCESSES = True  # Abilita gestione processi simulati
ENABLE_FILE_PREVIEW = True  # Abilita anteprima file nel file manager

# Performance
MAX_HISTORY_SIZE = 1000  # Dimensione massima della cronologia comandi
CACHE_TIMEOUT = 3600  # Timeout cache in secondi
