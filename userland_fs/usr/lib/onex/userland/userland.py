#!/usr/bin/env python3
"""
ONEX UserLand - Ambiente utente simulato
Fornisce un ambiente a riga di comando con file system virtualizzato
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Aggiungi il percorso base al PATH
base_path = Path(__file__).parent.parent.parent.absolute()
if str(base_path) not in sys.path:
    sys.path.insert(0, str(base_path))

# Importa il modulo dei loghi
try:
    from src.graphics.logos import ONEX_MINI_LOGO
except ImportError:
    ONEX_MINI_LOGO = "ONEX>"

class UserLandSystem:
    """
    Implementa l'ambiente utente virtualizzato con:
    - File manager
    - Shell interattiva
    - Filesystem simulato
    - Esecuzione programmi
    """
    def __init__(self, system_info: Dict, user_info: Dict, 
                 current_user: str, fs_root: Path):
        self.system_info = system_info
        self.user_info = user_info
        self.current_user = current_user
        self.fs_root = fs_root
        self.current_dir = f"/home/{current_user}"
        self.real_current_dir = fs_root / "home" / current_user
        self.app_manager = None
        
        # Importa i moduli necessari
        try:
            from src.system.shell_compatibility import ShellManager
            from src.system.input import InputHandler
            from src.graphics.ui import UserInterface
            from src.system.app_manager import AppManager
            
            self.shell_manager = ShellManager(system_info)
            self.input_handler = InputHandler()
            self.ui = UserInterface()
            self.app_manager = AppManager(base_path, fs_root)
            self.app_manager.scan_apps()
            
        except ImportError as e:
            print(f"❌ Errore durante l'importazione dei moduli richiesti: {e}")
            raise
    
    def start(self) -> None:
        """Avvia l'ambiente userland."""
        self._welcome()
        self._main_loop()
    
    def _welcome(self) -> None:
        """Mostra il messaggio di benvenuto."""
        try:
            from src.graphics.logos import print_logo
            print_logo()  # Usa il logo principale
        except ImportError:
            try:
                import pyfiglet
                header = pyfiglet.figlet_format("ONEX UserLand", font="slant")
                print(header)
            except ImportError:
                header = """
                ############################
                #     ONEX UserLand        #
                ############################
                """
                print(header)
        
        print(f"Benvenuto, {self.current_user}!")
        print(f"Sistema: {self.system_info.get('distribution', 'Unknown')} {self.system_info.get('os', 'Unknown')}")
        print("Digita 'help' per la lista dei comandi disponibili")
        print("=================================================")
    
    def _main_loop(self) -> None:
        """Loop principale dell'ambiente userland."""
        running = True
        while running:
            try:
                # Mostra il prompt
                prompt = f"{self.current_user}@onex:{self.current_dir}$ "
                cmd = input(prompt).strip()
                
                if not cmd:
                    continue
                
                # Dividi il comando per gestire argomenti con spazi
                cmd_parts = []
                current_part = ""
                in_quotes = False
                quote_char = None
                
                for char in cmd:
                    if char in ['"', "'"]:
                        if not in_quotes:
                            in_quotes = True
                            quote_char = char
                        elif char == quote_char:
                            in_quotes = False
                            quote_char = None
                        else:
                            current_part += char
                    elif char.isspace() and not in_quotes:
                        if current_part:
                            cmd_parts.append(current_part)
                            current_part = ""
                    else:
                        current_part += char
                
                if current_part:
                    cmd_parts.append(current_part)
                
                # Controlla se è rimasta una citazione non chiusa
                if in_quotes:
                    print("Errore: citazione non chiusa nel comando")
                    continue
                
                # Se non ci sono parti del comando, continua
                if not cmd_parts:
                    continue
                
                # Ottieni il comando base e gli argomenti
                cmd_base = cmd_parts[0]
                cmd_args = cmd_parts[1:] if len(cmd_parts) > 1 else []
                
                # Elabora il comando
                if cmd_base == "exit":
                    running = False
                elif cmd_base == "help":
                    self._show_help()
                elif cmd_base == "cd":
                    path = cmd_args[0] if cmd_args else ""
                    self._change_directory(path)
                elif cmd_base == "ls":
                    path = cmd_args[0] if cmd_args else ""
                    self._list_directory(path)
                elif cmd_base == "cat":
                    if not cmd_args:
                        print("cat: manca l'operando che specifica il file")
                    else:
                        self._cat_file(cmd_args[0])
                elif cmd_base == "pwd":
                    print(self.current_dir)
                elif cmd_base == "whoami":
                    print(self.current_user)
                elif cmd_base == "clear":
                    os.system('clear' if os.name != 'nt' else 'cls')
                elif cmd_base == "apps":
                    self._list_apps(cmd_args)
                elif cmd_base == "run":
                    if not cmd_args:
                        print("run: manca il nome dell'applicazione da eseguire")
                    else:
                        self._run_app(cmd_args[0], cmd_args[1:])
                elif cmd_base == "mkdir":
                    if not cmd_args:
                        print("mkdir: manca l'operando")
                    else:
                        self._make_directory(cmd_args[0])
                elif cmd_base == "touch":
                    if not cmd_args:
                        print("touch: manca l'operando")
                    else:
                        self._touch_file(cmd_args[0])
                elif cmd_base == "rm":
                    if not cmd_args:
                        print("rm: manca l'operando")
                    else:
                        self._remove_file(cmd_args[0])
                elif cmd_base == "echo":
                    print(" ".join(cmd_args))
                else:
                    # Prova ad eseguire come applicazione
                    if self.app_manager and cmd_base in self.app_manager.apps or cmd_base in self.app_manager.system_apps:
                        self._run_app(cmd_base, cmd_args)
                    else:
                        # Prova ad eseguire come comando di sistema
                        result = self._execute_command(cmd)
                        if not result:
                            print(f"Comando non riconosciuto: {cmd_base}")
                    
            except KeyboardInterrupt:
                print("\nUsa 'exit' per uscire")
            except Exception as e:
                print(f"Errore: {e}")
    
    def _show_help(self) -> None:
        """Mostra l'elenco dei comandi disponibili."""
        commands = [
            ("help", "Mostra questo messaggio di aiuto"),
            ("exit", "Esci dall'ambiente userland"),
            ("cd [dir]", "Cambia directory"),
            ("ls [dir]", "Elenca i file nella directory"),
            ("cat [file]", "Visualizza il contenuto di un file"),
            ("pwd", "Mostra la directory corrente"),
            ("whoami", "Mostra l'utente corrente"),
            ("clear", "Pulisce lo schermo"),
            ("apps [--all]", "Elenca le applicazioni disponibili"),
            ("run <app> [args]", "Esegue un'applicazione"),
            ("mkdir <dir>", "Crea una directory"),
            ("touch ", "Crea un file vuoto"),
            ("rm <file/dir>", "Rimuove un file o directory"),
            ("echo [testo]", "Visualizza un testo sullo schermo")
        ]
        
        print("\nComandi disponibili:")
        for cmd, desc in commands:
            print(f"  {cmd:<15} - {desc}")
        
        # Mostra le app di sistema disponibili
        if self.app_manager:
            system_apps = self.app_manager.get_app_list(include_system=True)
            if system_apps:
                print("\nApplicazioni disponibili:")
                for app in system_apps:
                    if app.system_app:
                        print(f"  {app.name:<15} - {app.description}")
        
        print("\nInoltre, puoi eseguire comandi di sistema con la sintassi standard.\n")
    
    def _change_directory(self, path: str) -> None:
        """Cambia la directory corrente."""
        # Risolvi il percorso virtuale
        if path.startswith("/"):
            new_path = path  # Percorso assoluto
        elif path == "..":
            # Vai alla directory superiore
            if self.current_dir == "/":
                return
            new_path = str(Path(self.current_dir).parent)
            if not new_path:
                new_path = "/"
        else:
            # Percorso relativo
            if self.current_dir.endswith("/"):
                new_path = f"{self.current_dir}{path}"
            else:
                new_path = f"{self.current_dir}/{path}"
        
        # Converti in path reale nel filesystem
        real_path = self._virtual_to_real_path(new_path)
        
        # Controlla se esiste e se è una directory
        if not real_path.exists():
            print(f"cd: {path}: No such file or directory")
            return
        
        if not real_path.is_dir():
            print(f"cd: {path}: Not a directory")
            return
        
        # Aggiorna il percorso corrente
        self.current_dir = new_path
        self.real_current_dir = real_path
    
    def _list_directory(self, path: str) -> None:
        """Elenca i contenuti di una directory."""
        # Se il percorso è vuoto, usa la directory corrente
        if not path:
            target_path = self.real_current_dir
        else:
            # Risolvi il percorso
            if path.startswith("/"):
                target_path = self._virtual_to_real_path(path)
            else:
                if self.current_dir.endswith("/"):
                    virtual_path = f"{self.current_dir}{path}"
                else:
                    virtual_path = f"{self.current_dir}/{path}"
                target_path = self._virtual_to_real_path(virtual_path)
        
        # Controlla se esiste e se è una directory
        if not target_path.exists():
            print(f"ls: cannot access '{path}': No such file or directory")
            return
        
        if not target_path.is_dir():
            print(f"{path}")
            return
        
        # Elenca i file
        try:
            files = list(target_path.iterdir())
            for file in sorted(files):
                # Mostra tipo e nome
                if file.is_dir():
                    print(f"\033[1;34m{file.name}/\033[0m")  # Blu per le directory
                elif os.access(file, os.X_OK):
                    print(f"\033[1;32m{file.name}*\\033[0m")  # Verde per gli eseguibili
                else:
                    print(f"{file.name}")
        except PermissionError:
            print(f"ls: cannot open directory '{path}': Permission denied")
    
    def _cat_file(self, path: str) -> None:
        """Visualizza il contenuto di un file."""
        # Risolvi il percorso del file
        if path.startswith("/"):
            real_path = self._virtual_to_real_path(path)
        else:
            if self.current_dir.endswith("/"):
                virtual_path = f"{self.current_dir}{path}"
            else:
                virtual_path = f"{self.current_dir}/{path}"
            real_path = self._virtual_to_real_path(virtual_path)
        
        # Controlla se il file esiste
        if not real_path.exists():
            print(f"cat: {path}: No such file or directory")
            return
        
        # Controlla se è un file
        if not real_path.is_file():
            print(f"cat: {path}: Is a directory")
            return
        
        # Leggi e mostra il contenuto
        try:
            with open(real_path, 'r') as f:
                print(f.read())
        except Exception as e:
            print(f"cat: {path}: {e}")
    
    def _execute_command(self, cmd: str) -> bool:
        """Esegue un comando di sistema."""
        try:
            result = self.shell_manager.execute_command(cmd)
            return True
        except Exception as e:
            print(f"Errore durante l'esecuzione del comando: {e}")
            return False
    
    def _virtual_to_real_path(self, virtual_path: str) -> Path:
        """
        Converte un percorso virtuale nel filesystem simulato
        in un percorso reale nel filesystem effettivo.
        """
        # Normalizza il percorso
        if not virtual_path:
            virtual_path = "/"
        
        # Gestione speciale per /mnt/system che deve puntare al filesystem reale
        if virtual_path.startswith("/mnt/system"):
            # Rimuovi "/mnt/system" e ottieni il percorso relativo al root reale
            rel_path = virtual_path[11:]  # Lunghezza di "/mnt/system"
            if not rel_path:
                return Path("/")  # Root del filesystem reale
            return Path(rel_path)
        
        # Rimuovi eventuali '..' e '.'
        parts = []
        for part in virtual_path.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part and part != ".":
                parts.append(part)
        
        # Ricostruisci il percorso virtuale normalizzato
        if not parts:
            norm_virtual_path = "/"
        else:
            norm_virtual_path = "/" + "/".join(parts)
        
        # Costruisci il percorso reale
        if norm_virtual_path == "/":
            return self.fs_root
        
        # Rimuovi la prima barra e unisci con la root del filesystem simulato
        path_without_leading_slash = norm_virtual_path[1:]
        return self.fs_root / path_without_leading_slash
    
    def _list_apps(self, args: List[str]) -> None:
        """Elenca le applicazioni disponibili."""
        if not self.app_manager:
            print("Sistema di gestione applicazioni non disponibile")
            return
            
        show_all = "--all" in args or "-a" in args
        
        apps = self.app_manager.get_app_list(include_system=show_all)
        
        if not apps:
            print("Nessuna applicazione trovata")
            return
        
        print("=== Applicazioni Disponibili ===\n")
        
        # Formatta l'output
        name_width = max(len(app.name) for app in apps) + 2
        version_width = max(len(app.version) for app in apps) + 2
        
        # Intestazione
        print(f"{'Nome':<{name_width}}{'Versione':<{version_width}}Descrizione")
        print("-" * (name_width + version_width + 40))
        
        for app in apps:
            print(f"{app.name:<{name_width}}{app.version:<{version_width}}{app.description}")
    
    def _run_app(self, app_name: str, args: List[str] = None) -> None:
        """Esegue un'applicazione."""
        if not self.app_manager:
            print("Sistema di gestione applicazioni non disponibile")
            return
            
        success, message = self.app_manager.run_app(app_name, args)
        
        if not success:
            print(message)
    
    def _make_directory(self, path: str) -> None:
        """Crea una directory."""
        if path.startswith("/"):
            real_path = self._virtual_to_real_path(path)
        else:
            if self.current_dir.endswith("/"):
                virtual_path = f"{self.current_dir}{path}"
            else:
                virtual_path = f"{self.current_dir}/{path}"
            real_path = self._virtual_to_real_path(virtual_path)
        
        try:
            real_path.mkdir(parents=True)
        except Exception as e:
            print(f"mkdir: impossibile creare la directory '{path}': {e}")
    
    def _touch_file(self, path: str) -> None:
        """Crea un file vuoto."""
        if path.startswith("/"):
            real_path = self._virtual_to_real_path(path)
        else:
            if self.current_dir.endswith("/"):
                virtual_path = f"{self.current_dir}{path}"
            else:
                virtual_path = f"{self.current_dir}/{path}"
            real_path = self._virtual_to_real_path(virtual_path)
        
        try:
            real_path.parent.mkdir(parents=True, exist_ok=True)
            real_path.touch()
        except Exception as e:
            print(f"touch: impossibile creare il file '{path}': {e}")
    
    def _remove_file(self, path: str) -> None:
        """Rimuove un file o una directory."""
        if path.startswith("/"):
            real_path = self._virtual_to_real_path(path)
        else:
            if self.current_dir.endswith("/"):
                virtual_path = f"{self.current_dir}{path}"
            else:
                virtual_path = f"{self.current_dir}/{path}"
            real_path = self._virtual_to_real_path(virtual_path)
        
        try:
            if real_path.is_dir():
                shutil.rmtree(real_path)
            else:
                real_path.unlink()
        except Exception as e:
            print(f"rm: impossibile rimuovere '{path}': {e}")

# Classe per il FileManager che verrà implementata in futuro
class FileManager:
    """
    Implementa un file manager interattivo con interfaccia utente basata su curses.
    Permette di navigare nel filesystem, visualizzare file ed eseguire programmi.
    """
    def __init__(self, fs_root: Path, current_dir: str, 
                real_current_dir: Path, user: str):
        self.fs_root = fs_root
        self.current_dir = current_dir
        self.real_current_dir = real_current_dir
        self.user = user
    
    def start(self) -> None:
        """Avvia il file manager."""
        # TODO: Implementare l'interfaccia curses del file manager
        pass
