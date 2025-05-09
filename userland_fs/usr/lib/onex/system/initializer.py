#!/usr/bin/env python3
"""
ONEX System Initializer
Gestisce l'inizializzazione coordinata dei vari sottosistemi
"""

import os
import sys
import importlib
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

# Se possibile importa il logger, altrimenti usa funzioni di fallback
try:
    from src.system.logger import get_logger
    logger = get_logger()
except ImportError:
    # Logger di fallback
    class SimpleLogger:
        def debug(self, msg): print(f"DEBUG: {msg}")
        def info(self, msg): print(f"INFO: {msg}")
        def warning(self, msg): print(f"WARNING: {msg}")
        def error(self, msg): print(f"ERROR: {msg}")
        def critical(self, msg): print(f"CRITICAL: {msg}")
    logger = SimpleLogger()

class SystemInitializer:
    """
    Gestisce l'inizializzazione ordinata dei sottosistemi di ONEX.
    Fornisce un meccanismo di dependency injection e hook per
    personalizzare il comportamento durante l'avvio.
    """
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.parent.absolute()
        self.components = {}
        self.initialized = set()
        self.dependencies = {}
        self.initialization_hooks = {}
        self.system_info = {}
        self.user_info = {}
        
    def register_component(self, name: str, 
                         initializer_func: Callable, 
                         dependencies: List[str] = None) -> None:
        """
        Registra un componente del sistema.
        
        Args:
            name: Nome del componente
            initializer_func: Funzione di inizializzazione del componente
            dependencies: Lista di nomi dei componenti da cui questo dipende
        """
        if dependencies is None:
            dependencies = []
            
        self.components[name] = initializer_func
        self.dependencies[name] = dependencies
        logger.debug(f"Componente registrato: {name}")
    
    def register_hook(self, point: str, hook_func: Callable) -> None:
        """
        Registra una hook function che verrà chiamata durante
        specifici punti dell'inizializzazione.
        
        Args:
            point: Punto di hook ('pre_init', 'post_init', etc.)
            hook_func: Funzione da chiamare
        """
        if point not in self.initialization_hooks:
            self.initialization_hooks[point] = []
            
        self.initialization_hooks[point].append(hook_func)
        logger.debug(f"Hook registrato per {point}")
    
    def initialize(self, system_info: Dict = None, user_info: Dict = None) -> bool:
        """
        Inizializza tutti i componenti registrati rispettando le dipendenze.
        
        Args:
            system_info: Informazioni di sistema da passare ai componenti
            user_info: Informazioni utente da passare ai componenti
            
        Returns:
            bool: True se l'inizializzazione è riuscita, False altrimenti
        """
        self.system_info = system_info or {}
        self.user_info = user_info or {}
        
        logger.info("Avvio dell'inizializzazione del sistema")
        
        # Esegui i pre-hook
        self._execute_hooks('pre_init')
        
        # Topological sort per rispettare le dipendenze
        init_order = self._sort_dependencies()
        
        if init_order is None:
            logger.error("Dipendenze circolari rilevate, impossibile inizializzare")
            return False
        
        # Inizializza i componenti nell'ordine corretto
        for component_name in init_order:
            if component_name in self.initialized:
                continue
                
            if not self._initialize_component(component_name):
                logger.error(f"Inizializzazione fallita per il componente {component_name}")
                return False
        
        # Esegui i post-hook
        self._execute_hooks('post_init')
        
        logger.info("Inizializzazione del sistema completata con successo")
        return True
    
    def _initialize_component(self, name: str) -> bool:
        """
        Inizializza un singolo componente.
        
        Args:
            name: Nome del componente
            
        Returns:
            bool: True se l'inizializzazione è riuscita, False altrimenti
        """
        if name in self.initialized:
            return True
            
        logger.debug(f"Inizializzazione del componente: {name}")
        
        try:
            # Controlla che tutte le dipendenze siano già inizializzate
            for dep in self.dependencies.get(name, []):
                if dep not in self.initialized:
                    logger.error(f"Dipendenza {dep} non inizializzata per {name}")
                    return False
            
            # Inizializza il componente passando le informazioni di sistema
            init_func = self.components[name]
            result = init_func(
                system_info=self.system_info,
                user_info=self.user_info
            )
            
            if result:
                self.initialized.add(name)
                logger.debug(f"Componente {name} inizializzato con successo")
                return True
            else:
                logger.error(f"Inizializzazione fallita per {name}")
                return False
                
        except Exception as e:
            logger.error(f"Errore durante l'inizializzazione di {name}: {str(e)}")
            logger.debug(f"Dettaglio errore:", exc_info=True)
            return False
    
    def _sort_dependencies(self) -> Optional[List[str]]:
        """
        Esegue un ordinamento topologico dei componenti in base alle dipendenze.
        
        Returns:
            Optional[List[str]]: Lista ordinata dei componenti o None se ci sono dipendenze circolari
        """
        result = []
        visited = set()
        temp_visited = set()
        
        def visit(node):
            if node in temp_visited:
                # Dipendenza circolare
                return False
                
            if node in visited:
                return True
                
            temp_visited.add(node)
            
            # Visita le dipendenze
            for dep in self.dependencies.get(node, []):
                if dep not in self.components:
                    logger.warning(f"Dipendenza {dep} non trovata per {node}")
                    continue
                    
                if not visit(dep):
                    return False
            
            temp_visited.remove(node)
            visited.add(node)
            result.append(node)
            return True
        
        # Visita tutti i nodi
        for node in self.components:
            if node not in visited:
                if not visit(node):
                    return None
        
        # Inverti l'ordine (l'algoritmo produce l'ordine inverso)
        return list(reversed(result))
    
    def _execute_hooks(self, point: str) -> None:
        """
        Esegue gli hook registrati per un punto specifico.
        
        Args:
            point: Punto di hook
        """
        for hook in self.initialization_hooks.get(point, []):
            try:
                hook(system_info=self.system_info, user_info=self.user_info)
            except Exception as e:
                logger.warning(f"Errore nell'esecuzione dell'hook {point}: {str(e)}")
    
    def get_component_status(self) -> Dict[str, bool]:
        """
        Restituisce lo stato di inizializzazione di tutti i componenti.
        
        Returns:
            Dict[str, bool]: Dizionario con lo stato dei componenti
        """
        return {comp: comp in self.initialized for comp in self.components}

# Singleton per l'inizializzatore di sistema
_SYSTEM_INITIALIZER = None

def get_initializer() -> SystemInitializer:
    """
    Ottiene l'istanza singleton dell'inizializzatore di sistema.
    
    Returns:
        SystemInitializer: Istanza dell'inizializzatore
    """
    global _SYSTEM_INITIALIZER
    
    if _SYSTEM_INITIALIZER is None:
        _SYSTEM_INITIALIZER = SystemInitializer()
        
    return _SYSTEM_INITIALIZER

# Funzioni di inizializzazione per i vari sottosistemi
def initialize_filesystem(system_info: Dict, user_info: Dict) -> bool:
    """Inizializza il filesystem."""
    try:
        fs_root = Path(system_info.get('fs_root', Path(__file__).parent.parent.parent / 'userland_fs'))
        
        # Verifica se il filesystem esiste già
        if fs_root.exists():
            logger.debug(f"Filesystem già esistente in {fs_root}")
            return True
            
        # Crea la struttura base
        logger.info(f"Inizializzazione del filesystem virtuale in {fs_root}")
        
        # Crea le directory di base
        dirs = ["bin", "etc", "home", "usr", "var", "tmp", "opt", "mnt", "dev", "proc", "sys"]
        for d in dirs:
            (fs_root / d).mkdir(parents=True, exist_ok=True)
            
        # Crea il mount point per il filesystem reale
        real_mount = fs_root / "mnt" / "system"
        real_mount.mkdir(parents=True, exist_ok=True)
        
        # Crea la home per l'utente corrente
        if user_info and 'current_user' in user_info:
            user_home = fs_root / "home" / user_info['current_user']
            user_home.mkdir(parents=True, exist_ok=True)
            
            # Crea alcune sottodirectory nella home
            for subdir in ['Documents', 'Downloads', 'Pictures']:
                (user_home / subdir).mkdir(exist_ok=True)
                
        logger.info("Filesystem virtuale inizializzato con successo")
        return True
        
    except Exception as e:
        logger.error(f"Errore nell'inizializzazione del filesystem: {str(e)}")
        return False

def initialize_graphics(system_info: Dict, user_info: Dict) -> bool:
    """Inizializza il sistema grafico."""
    try:
        # Importa i moduli grafici
        from src.graphics import ui, graphics
        
        # Verifica che il terminale supporti i colori
        if 'TERM' in os.environ and 'color' in os.environ['TERM']:
            logger.info("Terminale con supporto colori rilevato")
        else:
            logger.warning("Terminale potrebbe non supportare i colori")
            
        logger.info("Sistema grafico inizializzato con successo")
        return True
        
    except ImportError as e:
        logger.error(f"Errore nell'importazione dei moduli grafici: {str(e)}")
        return False

def initialize_shell(system_info: Dict, user_info: Dict) -> bool:
    """Inizializza la shell compatibility."""
    try:
        from src.system.shell_compatibility import ShellManager
        
        shell_type = os.environ.get('SHELL', '').split('/')[-1]
        if not shell_type:
            shell_type = 'unknown'
            
        logger.info(f"Shell rilevata: {shell_type}")
        logger.info("Sistema shell inizializzato con successo")
        return True
        
    except ImportError as e:
        logger.error(f"Errore nell'inizializzazione della shell: {str(e)}")
        return False

# Registrazione dei componenti di sistema
def register_default_components():
    """Registra i componenti predefiniti del sistema."""
    initializer = get_initializer()
    
    # Registra i componenti in ordine di dipendenza
    initializer.register_component('filesystem', initialize_filesystem, [])
    initializer.register_component('shell', initialize_shell, [])
    initializer.register_component('graphics', initialize_graphics, ['shell'])

# Pre-registra i componenti predefiniti
register_default_components()
