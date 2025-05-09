#!/usr/bin/env python3
"""
ONEX Logger
Sistema di logging per il tracciamento delle attività e degli errori
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional

class Logger:
    """
    Logger centralizzato per il sistema ONEX.
    Gestisce il logging di eventi, errori e debug info su file e console.
    """
    def __init__(self, log_dir: Path = None, log_level: str = "INFO", 
                 app_name: str = "onex", console_output: bool = True):
        # Configura directory
        if log_dir is None:
            base_dir = Path(__file__).parent.parent.parent.absolute()
            log_dir = base_dir / "logs"
        
        self.log_dir = log_dir
        self.app_name = app_name
        self.log_level = self._get_log_level(log_level)
        
        # Crea directory dei log se non esiste
        self._ensure_log_dir()
        
        # Inizializza il logger
        self.logger = logging.getLogger(app_name)
        self.logger.setLevel(self.log_level)
        self.logger.handlers = []  # Rimuovi handler esistenti
        
        # Crea il file di log con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"{app_name}_{timestamp}.log"
        
        # Handler per il file
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(self.log_level)
        
        # Handler per la console (se richiesto)
        if console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            self.logger.addHandler(console_handler)
        
        # Formato dei log
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        
        # Aggiungi l'handler al logger
        self.logger.addHandler(file_handler)
        
        # Log di avvio
        self.info(f"Logger inizializzato. Livello: {log_level}")
    
    def _ensure_log_dir(self) -> None:
        """Assicura che la directory dei log esista."""
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Errore nella creazione della directory dei log: {e}")
            self.log_dir = Path.cwd()
    
    def _get_log_level(self, level_name: str) -> int:
        """Converte il nome del livello di log in costante logging."""
        levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        return levels.get(level_name.upper(), logging.INFO)
    
    def debug(self, message: str) -> None:
        """Log di un messaggio di debug."""
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log di un messaggio informativo."""
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log di un avviso."""
        self.logger.warning(message)
    
    def error(self, message: str, exc_info: bool = False) -> None:
        """Log di un errore."""
        if exc_info:
            self.logger.error(message, exc_info=True)
        else:
            self.logger.error(message)
    
    def critical(self, message: str, exc_info: bool = True) -> None:
        """Log di un errore critico."""
        self.logger.critical(message, exc_info=exc_info)
    
    def exception(self, message: str) -> None:
        """Log di un'eccezione con traceback."""
        self.logger.exception(message)
    
    def log_exception(self, e: Exception, message: Optional[str] = None) -> None:
        """
        Log di un'eccezione con un messaggio personalizzato.
        
        Args:
            e: L'eccezione catturata
            message: Messaggio opzionale da aggiungere
        """
        if message:
            full_message = f"{message}: {str(e)}"
        else:
            full_message = str(e)
            
        self.error(full_message)
        self.debug(f"Traceback: {traceback.format_exc()}")

# Singleton logger per tutto il sistema
_SYSTEM_LOGGER = None

def get_logger(log_dir: Path = None, log_level: str = "INFO", 
              app_name: str = "onex", console_output: bool = True) -> Logger:
    """
    Ottiene l'istanza singleton del logger.
    
    Args:
        log_dir: Directory per i file di log
        log_level: Livello di logging
        app_name: Nome dell'applicazione per il logging
        console_output: Se True, mostra anche output sulla console
        
    Returns:
        Logger: Istanza del logger
    """
    global _SYSTEM_LOGGER
    
    if _SYSTEM_LOGGER is None:
        _SYSTEM_LOGGER = Logger(log_dir, log_level, app_name, console_output)
        
    return _SYSTEM_LOGGER
