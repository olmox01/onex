#!/usr/bin/env python3
"""
ONEX Shell Compatibility
Gestisce la compatibilità con diverse shell di sistema
"""

import os
import sys
import subprocess
import shlex
from typing import Dict, List, Any, Tuple, Optional

class ShellManager:
    """
    Gestisce l'interazione con le shell di sistema,
    adattandosi alle differenze tra le varie distribuzioni Linux.
    """
    def __init__(self, system_info: Dict):
        self.system_info = system_info
        self.shell_type = self._detect_shell()
        self.env = os.environ.copy()
    
    def _detect_shell(self) -> str:
        """
        Rileva il tipo di shell in uso nel sistema.
        
        Returns:
            str: Il tipo di shell (bash, zsh, fish, ecc.)
        """
        shell_path = os.environ.get('SHELL', '')
        if 'bash' in shell_path:
            return 'bash'
        elif 'zsh' in shell_path:
            return 'zsh'
        elif 'fish' in shell_path:
            return 'fish'
        elif 'dash' in shell_path:
            return 'dash'
        elif 'sh' in shell_path:
            return 'sh'
        else:
            return 'unknown'
    
    def execute_command(self, command: str) -> Tuple[str, str, int]:
        """
        Esegue un comando nella shell di sistema.
        
        Args:
            command: Il comando da eseguire
            
        Returns:
            Tuple[str, str, int]: Output standard, output errore e codice di ritorno
        """
        try:
            # Parsing sicuro del comando
            args = shlex.split(command)
            if not args:
                return "", "", 0
            
            # Esecuzione del comando
            proc = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self.env
            )
            
            # Cattura l'output
            stdout, stderr = proc.communicate()
            
            # Stampa l'output
            if stdout:
                print(stdout, end='')
            if stderr:
                print(stderr, file=sys.stderr, end='')
            
            return stdout, stderr, proc.returncode
            
        except FileNotFoundError:
            error_msg = f"Comando non trovato: {command.split()[0]}"
            print(error_msg, file=sys.stderr)
            return "", error_msg, 127
        except Exception as e:
            error_msg = f"Errore durante l'esecuzione del comando: {e}"
            print(error_msg, file=sys.stderr)
            return "", str(e), 1
    
    def execute_script(self, script_path: str, args: List[str] = None) -> Tuple[str, str, int]:
        """
        Esegue uno script shell.
        
        Args:
            script_path: Percorso allo script da eseguire
            args: Argomenti da passare allo script
            
        Returns:
            Tuple[str, str, int]: Output standard, output errore e codice di ritorno
        """
        if args is None:
            args = []
        
        # Verifica che lo script esista
        if not os.path.exists(script_path):
            error_msg = f"Script non trovato: {script_path}"
            print(error_msg, file=sys.stderr)
            return "", error_msg, 1
        
        # Determina l'interprete da usare
        interpreter = self._get_script_interpreter(script_path)
        
        # Esegui lo script
        try:
            cmd = [interpreter, script_path] + args
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=self.env
            )
            
            stdout, stderr = proc.communicate()
            
            if stdout:
                print(stdout, end='')
            if stderr:
                print(stderr, file=sys.stderr, end='')
                
            return stdout, stderr, proc.returncode
            
        except Exception as e:
            error_msg = f"Errore durante l'esecuzione dello script: {e}"
            print(error_msg, file=sys.stderr)
            return "", str(e), 1
    
    def _get_script_interpreter(self, script_path: str) -> str:
        """
        Determina l'interprete appropriato per uno script.
        Controlla lo shebang o usa l'estensione del file.
        
        Args:
            script_path: Percorso allo script
            
        Returns:
            str: Il percorso all'interprete da usare
        """
        try:
            # Controlla se c'è uno shebang
            with open(script_path, 'r') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!'):
                    interpreter = first_line[2:].split()[0]
                    if os.path.exists(interpreter):
                        return interpreter
        except:
            pass
        
        # Usa l'estensione del file
        if script_path.endswith('.sh'):
            return '/bin/sh'
        elif script_path.endswith('.bash'):
            return '/bin/bash'
        elif script_path.endswith('.py'):
            return sys.executable
        elif script_path.endswith('.rb'):
            return '/usr/bin/ruby'
        elif script_path.endswith('.pl'):
            return '/usr/bin/perl'
        
        # Default a sh
        return '/bin/sh'
    
    def set_environment_variable(self, name: str, value: str) -> None:
        """
        Imposta una variabile d'ambiente.
        
        Args:
            name: Nome della variabile
            value: Valore da assegnare
        """
        self.env[name] = value
        os.environ[name] = value
    
    def get_environment_variable(self, name: str) -> Optional[str]:
        """
        Ottiene il valore di una variabile d'ambiente.
        
        Args:
            name: Nome della variabile
            
        Returns:
            Optional[str]: Valore della variabile o None se non esiste
        """
        return self.env.get(name)
