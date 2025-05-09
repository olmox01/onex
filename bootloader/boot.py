#!/usr/bin/env python3
import os
import sys
import json
import platform
import shutil
import subprocess
import importlib
import pkg_resources
import time  # Aggiunta l'importazione corretta del modulo time
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

class Bootloader:
    """
    Gestisce il processo di avvio del sistema ONEX.
    Responsabilità:
    - Verificare l'ambiente di sistema
    - Gestire le dipendenze
    - Inizializzare il filesystem virtuale
    - Gestire l'autenticazione utente
    """
    def __init__(self):
        self.base_path = Path(__file__).parent.parent.absolute()
        self.system_info = {}
        self.user_info = {}
        self.required_packages = [
            "curses", 
            "pyfiglet", 
            "psutil", 
            "questionary", 
            "colorama", 
            "PIL",  # Cambiato da "pillow" a "PIL" per l'importazione corretta
            "tqdm"
        ]
        self.fs_root = self.base_path / "userland_fs"
        
    def boot(self) -> bool:
        """
        Avvia il processo di bootstrap del sistema
        
        Returns:
            bool: True se il boot è completato con successo, False altrimenti
        """
        try:
            # Importa e mostra il logo ONEX
            try:
                sys.path.insert(0, str(self.base_path))
                from src.graphics.logos import print_logo
                print_logo()
            except ImportError:
                # Se non riusciamo a importare il logo, continuiamo senza
                print("🚀 ONEX Bootloader v1.0")
            
            print("🔍 Analisi del sistema in corso...")
            
            # Controllo permessi sudo
            if not self._check_sudo():
                print("⚠️  Attenzione: privilegi sudo non rilevati.")
                response = input("Continuare senza privilegi elevati? (s/n): ").lower()
                if response != 's':
                    print("🛑 Avvio interrotto: privilegi insufficienti.")
                    return False
            
            # Raccolta informazioni di sistema
            self._collect_system_info()
            self._collect_user_info()
            
            # Salvataggio informazioni raccolte
            self._save_system_table()
            
            # Controllo e installazione librerie necessarie
            if not self._check_and_install_dependencies():
                print("🛑 Errore: impossibile installare le dipendenze necessarie.")
                return False
            
            # Inizializzazione del filesystem userland
            if not self._init_userland_filesystem():
                print("🛑 Errore: impossibile inizializzare il filesystem userland.")
                return False
            
            # Carica e installa le applicazioni
            if not self._load_and_install_apps():
                print("⚠️  Attenzione: Problemi nel caricamento delle applicazioni.")
                # Non fallire il boot per questo, è un avviso
            
            # Autenticazione utente
            user = self._authenticate_user()
            if not user:
                print("🛑 Errore: autenticazione fallita.")
                return False
            
            print("✅ Bootloader completato con successo!")
            return True
            
        except Exception as e:
            print(f"🛑 Errore durante il boot: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _check_sudo(self) -> bool:
        """Verifica se lo script è stato eseguito con privilegi sudo."""
        return os.geteuid() == 0 if hasattr(os, "geteuid") else False
    
    def _collect_system_info(self) -> None:
        """Raccoglie informazioni sul sistema operativo."""
        print("📊 Raccolta informazioni di sistema...")
        
        self.system_info = {
            "os": platform.system(),
            "distribution": self._get_linux_distribution(),
            "kernel": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "cpu_count": os.cpu_count(),
            "terminal": os.environ.get('TERM', 'unknown'),
            "shell": os.environ.get('SHELL', 'unknown'),
            "path": os.environ.get('PATH', ''),
        }
        
        print(f"📌 Sistema rilevato: {self.system_info['distribution']} "
              f"{self.system_info['os']} {self.system_info['kernel']}")
    
    def _get_linux_distribution(self) -> str:
        """Rileva la distribuzione Linux in uso."""
        try:
            if os.path.exists('/etc/os-release'):
                with open('/etc/os-release', 'r') as f:
                    lines = f.readlines()
                    for line in lines:
                        if line.startswith('ID='):
                            return line.strip().split('=')[1].strip('"\'')
        except:
            pass
        return "Unknown"
    
    def _collect_user_info(self) -> None:
        """Raccoglie informazioni sugli utenti e le directory."""
        print("👤 Raccolta informazioni utente...")
        
        current_user = os.environ.get('USER') or os.environ.get('USERNAME') or 'unknown'
        home_dir = str(Path.home())
        
        self.user_info = {
            "current_user": current_user,
            "home_dir": home_dir,
            "sudo_access": self._check_sudo(),
            "user_groups": self._get_user_groups(current_user),
            "all_users": self._get_all_users()
        }
        
        print(f"👤 Utente attuale: {current_user} (Sudo: {'Sì' if self.user_info['sudo_access'] else 'No'})")
    
    def _get_user_groups(self, username: str) -> List[str]:
        """Ottiene i gruppi a cui appartiene l'utente."""
        try:
            result = subprocess.run(['groups', username], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip().split(':')[1].strip().split()
        except:
            pass
        return []
    
    def _get_all_users(self) -> List[Dict]:
        """Ottiene la lista di tutti gli utenti del sistema."""
        users = []
        try:
            with open('/etc/passwd', 'r') as f:
                for line in f:
                    fields = line.strip().split(':')
                    if len(fields) >= 6 and int(fields[2]) >= 1000 and int(fields[2]) < 65534:
                        users.append({
                            "username": fields[0],
                            "uid": fields[2],
                            "home": fields[5],
                            "shell": fields[6] if len(fields) > 6 else ""
                        })
        except:
            pass
        return users
    
    def _save_system_table(self) -> None:
        """Salva le informazioni di sistema in un file JSON."""
        data = {
            "system": self.system_info,
            "user": self.user_info,
            "timestamp": time.time()  # Corretto l'errore qui
        }
        
        system_info_path = self.base_path / "system_info.json"
        try:
            with open(system_info_path, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"💾 Informazioni di sistema salvate in {system_info_path}")
        except Exception as e:
            print(f"⚠️  Impossibile salvare le informazioni di sistema: {e}")
    
    def _check_and_install_dependencies(self) -> bool:
        """Verifica e installa le dipendenze necessarie."""
        print("📦 Controllo dipendenze...")
        
        # Mappa dei nomi dei pacchetti reali per l'installazione
        package_map = {
            "PIL": "pillow",  # PIL è il nome del modulo, pillow è il pacchetto da installare
            "curses": "windows-curses" if sys.platform == "win32" else "curses"
        }
        
        to_install = []
        for package in self.required_packages:
            try:
                if package == "PIL":
                    # Verifica specifica per PIL/Pillow
                    from PIL import Image
                    print(f"✅ {package}: già installato")
                else:
                    importlib.import_module(package)
                    print(f"✅ {package}: già installato")
            except ImportError:
                # Usa il nome del pacchetto corretto per l'installazione
                install_name = package_map.get(package, package)
                if install_name not in to_install:
                    to_install.append(install_name)
                print(f"❌ {package}: non installato")
        
        if to_install:
            print(f"\n🔧 Installazione di {len(to_install)} pacchetti mancanti...")
            
            # In un ambiente gestito esternamente, utilizziamo un ambiente virtuale
            if self._is_externally_managed():
                print("🔍 Rilevato ambiente gestito esternamente, utilizzo ambiente virtuale...")
                success = self._setup_and_use_venv(to_install)
            else:
                # Tentiamo l'installazione diretta
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install"] + to_install)
                    success = True
                    print("✅ Dipendenze installate con successo")
                except subprocess.CalledProcessError as e:
                    print(f"❌ Errore durante l'installazione: {e}")
                    print("🔄 Tentativo di utilizzo ambiente virtuale...")
                    success = self._setup_and_use_venv(to_install)
            
            if not success:
                print("🛑 Impossibile installare le dipendenze necessarie.")
                return False
        
        # Verifica finale delle importazioni
        for package in self.required_packages:
            try:
                if package == "PIL":
                    # Verifica specifica per PIL/Pillow
                    from PIL import Image
                else:
                    importlib.import_module(package)
            except ImportError:
                print(f"❌ Impossibile importare {package} anche dopo l'installazione")
                return False
        
        return True
    
    def _is_externally_managed(self) -> bool:
        """
        Verifica se l'ambiente Python è gestito esternamente.
        """
        try:
            # Verifica il file externally-managed
            import sysconfig
            ext_path = os.path.join(sysconfig.get_path('stdlib'), "EXTERNALLY-MANAGED")
            if os.path.exists(ext_path):
                return True
                
            # Tenta una piccola installazione per vedere se fallisce
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", "--dry-run", "wheel"],
                    capture_output=True,
                    text=True
                )
                if "externally-managed-environment" in result.stderr:
                    return True
            except:
                pass
                
            return False
        except Exception:
            return False
    
    def _setup_and_use_venv(self, packages: List[str]) -> bool:
        """
        Crea un ambiente virtuale e installa i pacchetti.
        
        Args:
            packages: Lista dei pacchetti da installare
            
        Returns:
            bool: True se l'installazione è riuscita
        """
        venv_dir = self.base_path / ".venv"
        print(f"📦 Creazione ambiente virtuale in {venv_dir}...")
        
        try:
            # Controlla se il modulo venv è disponibile
            try:
                import venv
            except ImportError:
                print("❌ Modulo 'venv' non disponibile. Tentativo di installazione...")
                result = subprocess.run(["apt", "install", "-y", "python3-venv"], check=False)
                if result.returncode != 0:
                    print("❌ Impossibile installare python3-venv")
                    return False
                
                # Riprova l'importazione
                try:
                    import venv
                except ImportError:
                    print("❌ Impossibile importare il modulo 'venv' anche dopo l'installazione")
                    return False
            
            # Rimuovi l'ambiente virtuale se già esiste
            if venv_dir.exists():
                import shutil
                shutil.rmtree(venv_dir)
            
            # Crea l'ambiente virtuale
            venv.create(venv_dir, with_pip=True)
            
            # Determina il percorso dell'eseguibile pip nell'ambiente virtuale
            if sys.platform == "win32":
                pip_exe = venv_dir / "Scripts" / "pip"
            else:
                pip_exe = venv_dir / "bin" / "pip"
            
            # Verifica che l'eseguibile pip esista
            if not os.path.exists(pip_exe):
                print(f"❌ Eseguibile pip non trovato in {pip_exe}")
                return False
            
            # Aggiorna pip e setuptools
            print("📦 Aggiornamento di pip e setuptools...")
            subprocess.run([str(pip_exe), "install", "--upgrade", "pip", "setuptools"], check=True)
            
            # Installa i pacchetti
            print(f"📦 Installazione di {len(packages)} pacchetti nell'ambiente virtuale...")
            subprocess.run([str(pip_exe), "install"] + packages, check=True)
            
            # Aggiungi l'ambiente virtuale al path di Python
            site_packages = self._get_venv_site_packages(venv_dir)
            if site_packages and site_packages.exists():
                sys.path.insert(0, str(site_packages))
                print(f"✅ Ambiente virtuale configurato: {site_packages}")
                return True
            else:
                print("❌ Impossibile trovare il percorso site-packages nell'ambiente virtuale")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Errore durante l'esecuzione del comando: {e}")
            return False
        except Exception as e:
            print(f"❌ Errore durante la creazione dell'ambiente virtuale: {e}")
            return False
    
    def _get_venv_site_packages(self, venv_dir: Path) -> Optional[Path]:
        """
        Trova il percorso site-packages nell'ambiente virtuale.
        
        Args:
            venv_dir: Percorso dell'ambiente virtuale
            
        Returns:
            Optional[Path]: Percorso del site-packages o None se non trovato
        """
        if sys.platform == "win32":
            site_packages = venv_dir / "Lib" / "site-packages"
        else:
            # Per sistemi Unix-like, cerca in diverse posizioni possibili
            python_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
            site_packages = venv_dir / "lib" / python_version / "site-packages"
            
            if not site_packages.exists():
                # Prova con altro formato di versione Python
                for item in (venv_dir / "lib").glob("python*"):
                    if item.is_dir() and (item / "site-packages").exists():
                        site_packages = item / "site-packages"
                        break
        
        return site_packages if site_packages.exists() else None
    
    def _init_userland_filesystem(self) -> bool:
        """Inizializza il filesystem virtuale per l'userland."""
        print("🗄️  Inizializzazione filesystem userland...")
        
        try:
            # Crea la directory principale se non esiste
            if not self.fs_root.exists():
                self.fs_root.mkdir(parents=True)
                print(f"📁 Creata directory root: {self.fs_root}")
            
            # Struttura base del filesystem (stile UNIX)
            dirs = ["bin", "etc", "home", "usr", "var", "tmp", "opt", "mnt"]
            
            for d in dirs:
                dir_path = self.fs_root / d
                if not dir_path.exists():
                    dir_path.mkdir(parents=True)
                    print(f"📁 Creata directory: {d}")
            
            # Crea la home directory per ciascun utente
            for user in self.user_info["all_users"]:
                user_home = self.fs_root / "home" / user["username"]
                if not user_home.exists():
                    user_home.mkdir(parents=True)
                    print(f"📁 Creata home per l'utente: {user['username']}")
            
            # Mount point per il filesystem reale
            real_fs_mount = self.fs_root / "mnt" / "system"
            if not real_fs_mount.exists():
                real_fs_mount.mkdir(parents=True)
                print(f"📁 Creato mount point per il filesystem reale: {real_fs_mount}")
                
                # Imposta permessi adeguati
                import stat
                os.chmod(real_fs_mount, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                print("🔒 Impostati permessi per il mount point")
            
            # Creazione delle directory per le applicazioni
            app_dirs = ["usr/apps", "usr/lib", "usr/bin"]
            for d in app_dirs:
                dir_path = self.fs_root / d
                if not dir_path.exists():
                    dir_path.mkdir(parents=True)
                    print(f"📁 Creata directory: {d}")
            
            # Copia le librerie di sistema nel filesystem virtuale
            self._copy_system_libs()
            
            print("✅ Filesystem inizializzato con successo")
            return True
            
        except Exception as e:
            print(f"❌ Errore durante l'inizializzazione del filesystem: {e}")
            return False
    
    def _copy_system_libs(self) -> None:
        """Copia le librerie di sistema nel filesystem virtuale."""
        lib_dir = self.fs_root / "usr" / "lib" / "onex"
        lib_dir.mkdir(parents=True, exist_ok=True)
        
        # Crea un file __init__.py vuoto
        with open(lib_dir / "__init__.py", "w") as f:
            f.write("# ONEX System Libraries")
        
        # Copia i moduli del sistema
        system_modules = [
            ("src/system", "system"),
            ("src/graphics", "graphics"),
            ("src/userland", "userland")
        ]
        
        for src_path, dest_name in system_modules:
            src_dir = self.base_path / src_path
            dest_dir = lib_dir / dest_name
            
            # Crea la directory di destinazione
            dest_dir.mkdir(exist_ok=True)
            
            # Crea un file __init__.py vuoto
            with open(dest_dir / "__init__.py", "w") as f:
                f.write(f"# ONEX {dest_name.capitalize()} Module")
            
            # Copia i file Python
            for py_file in src_dir.glob("*.py"):
                if py_file.name != "__init__.py":
                    with open(py_file, "r") as src_f:
                        with open(dest_dir / py_file.name, "w") as dest_f:
                            dest_f.write(src_f.read())
    
    def _load_and_install_apps(self) -> bool:
        """Carica e installa le app nel filesystem virtuale."""
        try:
            print("📱 Caricamento delle applicazioni...")
            
            # Importa l'AppManager
            sys.path.insert(0, str(self.base_path))
            from src.system.app_manager import AppManager
            
            # Inizializza l'AppManager
            app_manager = AppManager(self.base_path, self.fs_root)
            
            # Scansiona le app
            app_manager.scan_apps()
            
            # Installa le app nel filesystem virtuale
            if app_manager.install_app_to_virtual_fs():
                print("✅ App installate con successo nel filesystem virtuale")
            else:
                print("⚠️ Problemi durante l'installazione delle app nel filesystem virtuale")
            
            # Crea script di avvio per il filemanager
            self._create_filemanager_launcher()
            
            return True
        except ImportError as e:
            print(f"⚠️  Impossibile importare AppManager: {e}")
            return False
        except Exception as e:
            print(f"⚠️  Errore nel caricamento delle applicazioni: {e}")
            return False

    def _create_filemanager_launcher(self) -> None:
        """
        Crea uno script di avvio per il filemanager nel bin di sistema.
        Questo garantisce che il terminale venga correttamente ripristinato
        dopo l'esecuzione del filemanager.
        """
        try:
            # Percorso dello script di lancio
            bin_dir = self.fs_root / "bin"
            launcher_path = bin_dir / "filemanager"
            
            # Crea la directory bin se non esiste
            bin_dir.mkdir(parents=True, exist_ok=True)
            
            # Contenuto dello script launcher
            launcher_content = """#!/bin/sh
# File Manager Launcher
# Avvia il file manager preservando lo stato del terminale

# Salva lo stato del terminale
stty_save=$(stty -g 2>/dev/null)

# Avvia il file manager
{python} {app_path}/main.py "$@"
EXIT_CODE=$?

# Ripristina lo stato del terminale
stty $stty_save 2>/dev/null || true
clear

# Migliora l'aspetto del prompt
echo ""

exit $EXIT_CODE
""".format(python=sys.executable, app_path=self.base_path / "apps" / "filemanager")

            # Scrivi lo script
            with open(launcher_path, 'w') as f:
                f.write(launcher_content)
            
            # Rendi lo script eseguibile
            os.chmod(launcher_path, 0o755)
            
            print("✅ Creato script di lancio per il file manager")
            
        except Exception as e:
            print(f"⚠️ Impossibile creare lo script di lancio per il file manager: {e}")
    
    def _authenticate_user(self) -> Optional[str]:
        """Autenticazione dell'utente."""
        print("\n🔐 Autenticazione utente...")
        
        current_user = self.user_info["current_user"]
        print(f"👤 Utente di sistema corrente: {current_user}")
        
        # In una versione reale si potrebbe implementare un vero sistema di autenticazione
        # Per ora ritorniamo semplicemente l'utente corrente
        return current_user
    
    def get_system_info(self) -> Dict:
        """Restituisce le informazioni di sistema raccolte."""
        return self.system_info
    
    def get_user_info(self) -> Dict:
        """Restituisce le informazioni utente raccolte."""
        return self.user_info

# Fix importazione mancante (aggiunto dopo l'implementazione)
import time
