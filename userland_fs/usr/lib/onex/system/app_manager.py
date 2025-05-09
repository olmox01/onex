#!/usr/bin/env python3
"""
ONEX App Manager
Gestisce il caricamento e l'esecuzione delle applicazioni
"""

import os
import sys
import json
import importlib.util
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class AppInfo:
    """Informazioni su un'applicazione."""
    def __init__(self, name: str, path: Path, app_type: str, 
                description: str = "", version: str = "1.0.0",
                author: str = "", system_app: bool = False):
        self.name = name
        self.path = path
        self.app_type = app_type  # "py" o "sh"
        self.description = description
        self.version = version
        self.author = author
        self.system_app = system_app
        
    def to_dict(self) -> Dict:
        """Converte l'oggetto in un dizionario."""
        return {
            "name": self.name,
            "path": str(self.path),
            "app_type": self.app_type,
            "description": self.description,
            "version": self.version,
            "author": self.author,
            "system_app": self.system_app
        }
    
    @classmethod
    def from_dict(cls, data: Dict, base_path: Path) -> 'AppInfo':
        """Crea un oggetto AppInfo da un dizionario."""
        return cls(
            name=data.get("name", ""),
            path=Path(data.get("path", "")),
            app_type=data.get("app_type", "py"),
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            author=data.get("author", ""),
            system_app=data.get("system_app", False)
        )

class AppManager:
    """
    Gestisce il caricamento, la registrazione e l'esecuzione delle applicazioni.
    """
    def __init__(self, base_path: Path, fs_root: Path):
        self.base_path = base_path
        self.fs_root = fs_root
        self.apps_dir = base_path / "apps"
        self.virtual_apps_dir = fs_root / "usr" / "apps"
        self.system_apps_dir = fs_root / "bin"
        self.apps: Dict[str, AppInfo] = {}
        self.system_apps: Dict[str, AppInfo] = {}
        
    def scan_apps(self) -> None:
        """Scansiona e registra tutte le applicazioni disponibili."""
        # Reset delle app
        self.apps = {}
        self.system_apps = {}
        
        # Scansiona le app nella directory apps/
        if self.apps_dir.exists():
            for app_dir in self.apps_dir.iterdir():
                if app_dir.is_dir():
                    app_info = self._load_app_info(app_dir)
                    if app_info and not app_info.system_app:
                        self.apps[app_info.name] = app_info
                    elif app_info and app_info.system_app:
                        self.system_apps[app_info.name] = app_info
        
        # Scansiona le app di sistema
        if self.system_apps_dir.exists():
            for item in self.system_apps_dir.iterdir():
                if (item.is_file() and 
                    (item.suffix == '.py' or item.suffix == '.sh') and 
                    os.access(item, os.X_OK)):
                    # Crea un AppInfo per l'app di sistema
                    app_name = item.stem
                    app_info = AppInfo(
                        name=app_name,
                        path=item,
                        app_type=item.suffix[1:],  # Rimuovi il punto
                        description=f"Applicazione di sistema: {app_name}",
                        system_app=True
                    )
                    self.system_apps[app_name] = app_info
        
        print(f"Caricate {len(self.apps)} applicazioni e {len(self.system_apps)} app di sistema")
    
    def _load_app_info(self, app_dir: Path) -> Optional[AppInfo]:
        """
        Carica le informazioni su un'applicazione.
        Cerca un file app.json o un file main.py/sh con metadati.
        """
        app_json = app_dir / "app.json"
        main_py = app_dir / "main.py"
        main_sh = app_dir / "main.sh"
        
        # Controlla se esiste app.json
        if app_json.exists():
            try:
                with open(app_json, 'r') as f:
                    data = json.load(f)
                
                app_type = "py"
                if main_sh.exists() and not main_py.exists():
                    app_type = "sh"
                
                # Utilizza i metadati dal JSON
                return AppInfo(
                    name=data.get("name", app_dir.name),
                    path=app_dir,
                    app_type=data.get("type", app_type),
                    description=data.get("description", ""),
                    version=data.get("version", "1.0.0"),
                    author=data.get("author", ""),
                    system_app=data.get("system_app", False)
                )
            except Exception as e:
                print(f"Errore nel caricamento del file app.json per {app_dir.name}: {e}")
                return None
        
        # Controlla se esiste main.py
        elif main_py.exists():
            try:
                # Estrai metadati dal docstring
                spec = importlib.util.spec_from_file_location("app_module", main_py)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Cerca metadati nel modulo
                name = getattr(module, "__title__", app_dir.name)
                description = getattr(module, "__description__", "")
                version = getattr(module, "__version__", "1.0.0")
                author = getattr(module, "__author__", "")
                system_app = getattr(module, "__system_app__", False)
                
                return AppInfo(
                    name=name,
                    path=app_dir,
                    app_type="py",
                    description=description,
                    version=version,
                    author=author,
                    system_app=system_app
                )
            except Exception:
                # Se non riesce a importare, crea un oggetto di base
                return AppInfo(
                    name=app_dir.name,
                    path=app_dir,
                    app_type="py",
                    description=f"Applicazione: {app_dir.name}"
                )
        
        # Controlla se esiste main.sh
        elif main_sh.exists():
            # Per gli script shell, estrai i metadati dai commenti se possibile
            try:
                with open(main_sh, 'r') as f:
                    content = f.readlines()
                
                # Cerca metadati nei commenti
                name = app_dir.name
                description = ""
                version = "1.0.0"
                author = ""
                system_app = False
                
                for line in content[:20]:  # Esamina solo le prime 20 righe
                    line = line.strip()
                    if line.startswith("# Name:"):
                        name = line[7:].strip()
                    elif line.startswith("# Description:"):
                        description = line[14:].strip()
                    elif line.startswith("# Version:"):
                        version = line[10:].strip()
                    elif line.startswith("# Author:"):
                        author = line[9:].strip()
                    elif line.startswith("# System:"):
                        system_app = line[9:].strip().lower() == "true"
                
                return AppInfo(
                    name=name,
                    path=app_dir,
                    app_type="sh",
                    description=description,
                    version=version,
                    author=author,
                    system_app=system_app
                )
            except Exception:
                # Se non riesce a leggere, crea un oggetto di base
                return AppInfo(
                    name=app_dir.name,
                    path=app_dir,
                    app_type="sh",
                    description=f"Applicazione: {app_dir.name}"
                )
        
        return None
    
    def run_app(self, app_name: str, args: List[str] = None) -> Tuple[bool, str]:
        """
        Esegue un'applicazione dato il nome.
        
        Args:
            app_name: Nome dell'applicazione
            args: Argomenti da passare all'applicazione
            
        Returns:
            Tuple[bool, str]: Status e output/errore
        """
        if args is None:
            args = []
            
        # Cerca prima tra le app di sistema
        app_info = self.system_apps.get(app_name)
        
        # Se non è un'app di sistema, cerca tra le app normali
        if not app_info:
            app_info = self.apps.get(app_name)
            
        if not app_info:
            return False, f"Applicazione '{app_name}' non trovata"
            
        try:
            # Salva lo stato del terminale prima dell'esecuzione
            terminal_state_saved = False
            try:
                import curses
                curses.endwin()
                terminal_state_saved = True
            except:
                pass
                
            if app_info.app_type == "py":
                # Per applicazioni Python
                if app_info.system_app and app_info.path.is_file():
                    # App di sistema direttamente eseguibile
                    result = subprocess.run(
                        [sys.executable, str(app_info.path)] + args,
                        capture_output=True,
                        text=True
                    )
                else:
                    # App normale in directory
                    main_py = app_info.path / "main.py"
                    if not main_py.exists():
                        return False, f"File main.py non trovato per l'app '{app_name}'"
                        
                    # Prepara l'ambiente per l'applicazione
                    env = os.environ.copy()
                    env["ONEX_APP_PATH"] = str(app_info.path)
                    env["ONEX_APP_NAME"] = app_info.name
                    env["ONEX_FS_ROOT"] = str(self.fs_root)
                    
                    # Se l'app è il file manager o un'altra app che usa curses, non catturiamo l'output
                    if app_name == "filemanager" or self._app_uses_curses(main_py):
                        # Esecuzione diretta con reindirizzamento dell'output
                        proc = subprocess.Popen([sys.executable, str(main_py)] + args, env=env)
                        proc.wait()
                        
                        # Ripristina il terminale
                        os.system('stty sane')
                        
                        # Stampa un prompt vuoto per migliorare l'aspetto dell'interfaccia
                        print()
                        
                        return True, "Applicazione eseguita con successo"
                    else:
                        # Esecuzione normale con cattura dell'output
                        result = subprocess.run(
                            [sys.executable, str(main_py)] + args,
                            capture_output=True,
                            text=True,
                            env=env
                        )
                
                if result and result.returncode != 0:
                    return False, f"Errore nell'esecuzione: {result.stderr}"
                    
                if result and result.stdout:
                    print(result.stdout)
                if result and result.stderr:
                    print(result.stderr, file=sys.stderr)
                    
                return True, "Applicazione eseguita con successo"
                
            elif app_info.app_type == "sh":
                # Per script shell
                if app_info.system_app and app_info.path.is_file():
                    # App di sistema direttamente eseguibile
                    script_path = app_info.path
                else:
                    # App normale in directory
                    script_path = app_info.path / "main.sh"
                    if not script_path.exists():
                        return False, f"File main.sh non trovato per l'app '{app_name}'"
                
                # Assicurati che lo script sia eseguibile
                os.chmod(script_path, 0o755)
                
                # Prepara l'ambiente per l'applicazione
                env = os.environ.copy()
                env["ONEX_APP_PATH"] = str(app_info.path)
                env["ONEX_APP_NAME"] = app_info.name
                env["ONEX_FS_ROOT"] = str(self.fs_root)
                
                result = subprocess.run(
                    ["/bin/bash", str(script_path)] + args,
                    capture_output=True,
                    text=True,
                    env=env
                )
                
                if result.returncode != 0:
                    return False, f"Errore nell'esecuzione: {result.stderr}"
                    
                if result.stdout:
                    print(result.stdout)
                if result.stderr:
                    print(result.stderr, file=sys.stderr)
                    
                return True, "Script eseguito con successo"
                
            else:
                return False, f"Tipo di applicazione non supportato: {app_info.app_type}"
                
        except Exception as e:
            return False, f"Errore durante l'esecuzione dell'applicazione: {e}"
        finally:
            # Ripristina il terminale se necessario
            if terminal_state_saved:
                try:
                    import curses
                    curses.initscr()
                except:
                    pass
    
    def _app_uses_curses(self, app_path: Path) -> bool:
        """
        Verifica se un'applicazione Python utilizza curses.
        
        Args:
            app_path: Percorso al file Python dell'app
            
        Returns:
            bool: True se l'app utilizza curses
        """
        try:
            with open(app_path, 'r') as f:
                content = f.read()
                # Verifica se importa curses o utilizza la funzione wrapper
                return 'import curses' in content or 'curses.wrapper' in content
        except:
            return False
    
    def _run_filemanager(self, app_info: AppInfo, args: List[str]) -> Tuple[bool, str]:
        """
        Gestione speciale per l'applicazione filemanager che richiede
        accesso alle librerie di sistema e ripristino del terminale.
        
        Args:
            app_info: Informazioni sull'app filemanager
            args: Argomenti da passare all'app
            
        Returns:
            Tuple[bool, str]: Status e output/errore
        """
        try:
            # Determina il percorso dell'app
            if app_info.system_app and app_info.path.is_file():
                main_py = app_info.path
            else:
                main_py = app_info.path / "main.py"
            
            if not main_py.exists():
                return False, "File main.py del filemanager non trovato"
            
            # Crea uno script shell dedicato per il filemanager
            temp_script = self.base_path / "tmp_run_filemanager.sh"
            with open(temp_script, "w") as f:
                f.write("#!/bin/bash\n\n")
                # Salva lo stato del terminale
                f.write("stty_settings=$(stty -g)\n\n")
                # Prepara l'ambiente per il filemanager
                f.write("# Reset del terminale prima dell'avvio\n")
                f.write("reset\n\n")
                # Esegui il filemanager
                f.write(f"# Esecuzione del filemanager\n")
                f.write(f"PYTHONPATH=\"{self.base_path}\" {sys.executable} {main_py}")
                # Aggiungi gli argomenti
                if args:
                    f.write(f" \"{' '.join(args)}\"")
                f.write("\n\n")
                # Salva il codice di uscita
                f.write("exit_code=$?\n\n")
                # Ripristina il terminale
                f.write("# Ripristino del terminale\n")
                f.write("stty $stty_settings\n")
                f.write("reset\n")
                f.write("stty sane\n")
                # Restituisci il codice di uscita
                f.write("exit $exit_code\n")
            
            # Rendi lo script eseguibile
            os.chmod(temp_script, 0o755)
            
            # Esegui lo script
            result = subprocess.run([str(temp_script)])
            
            # Rimuovi lo script temporaneo
            temp_script.unlink()
            
            return True, f"Filemanager eseguito con codice di uscita: {result.returncode}"
            
        except Exception as e:
            return False, f"Errore durante l'esecuzione del filemanager: {e}"
    
    def get_app_list(self, include_system: bool = False) -> List[AppInfo]:
        """
        Ottiene la lista di tutte le applicazioni disponibili.
        
        Args:
            include_system: Se True, include anche le app di sistema
            
        Returns:
            List[AppInfo]: Lista delle app
        """
        result = list(self.apps.values())
        
        if include_system:
            result.extend(list(self.system_apps.values()))
            
        return sorted(result, key=lambda app: app.name)
        
    def install_app_to_virtual_fs(self) -> bool:
        """
        Installa le applicazioni nel filesystem virtuale.
        Copia le app nella directory /usr/apps e crea link simbolici in /bin per le app di sistema.
        """
        try:
            # Assicurati che le directory esistano
            self.virtual_apps_dir.mkdir(parents=True, exist_ok=True)
            self.system_apps_dir.mkdir(parents=True, exist_ok=True)
            
            # Copia le app normali nel filesystem virtuale
            for app_name, app_info in self.apps.items():
                dest_dir = self.virtual_apps_dir / app_name
                
                # Crea la directory se non esiste
                dest_dir.mkdir(exist_ok=True)
                
                # Copia i file dell'applicazione
                for item in app_info.path.glob("*"):
                    if item.is_file():
                        # Copia il file
                        with open(item, "rb") as src_file:
                            with open(dest_dir / item.name, "wb") as dest_file:
                                dest_file.write(src_file.read())
                                
                        # Se è uno script o un eseguibile, mantieni i permessi
                        if os.access(item, os.X_OK):
                            os.chmod(dest_dir / item.name, 0o755)
            
            # Crea link simbolici in /bin per le app di sistema
            for app_name, app_info in self.system_apps.items():
                if not app_info.system_app:
                    continue
                    
                # Per le app di sistema, crea un link in /bin
                dest_file = self.system_apps_dir / app_name
                
                # Salta se il file già esiste
                if dest_file.exists():
                    continue
                    
                # Crea un file wrapper che esegue l'app
                if app_info.app_type == "py":
                    with open(dest_file, "w") as f:
                        f.write("#!/bin/sh\n")
                        f.write(f"exec {sys.executable} {app_info.path} \"$@\"\n")
                else:  # sh
                    with open(dest_file, "w") as f:
                        f.write("#!/bin/sh\n")
                        f.write(f"exec /bin/bash {app_info.path} \"$@\"\n")
                
                # Rendi il file eseguibile
                os.chmod(dest_file, 0o755)
            
            return True
            
        except Exception as e:
            print(f"Errore nell'installazione delle app nel filesystem virtuale: {e}")
            return False
