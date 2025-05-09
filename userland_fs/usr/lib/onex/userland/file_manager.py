#!/usr/bin/env python3
"""
ONEX File Manager
Implementazione del file manager interattivo basato su curses
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from enum import Enum, auto
from typing import List, Dict, Tuple, Optional, Any, Callable

# Importa curses in modo sicuro
try:
    import curses
except ImportError:
    # Se siamo su Windows e curses non è disponibile, prova ad usare windows-curses
    if sys.platform == "win32":
        try:
            import pip
            pip.main(['install', 'windows-curses'])
            import curses
        except:
            print("Errore: impossibile importare il modulo curses.")
            print("Installa il pacchetto 'windows-curses' se sei su Windows.")
            print("Su Linux, assicurati che il pacchetto 'python3-curses' sia installato.")
            sys.exit(1)
    else:
        print("Errore: impossibile importare il modulo curses.")
        print("Su Linux, assicurati che il pacchetto 'python3-curses' sia installato.")
        sys.exit(1)

class FileType(Enum):
    """Enumerazione dei tipi di file."""
    DIRECTORY = auto()
    TEXT = auto()
    BINARY = auto()
    EXECUTABLE = auto()
    IMAGE = auto()
    AUDIO = auto()
    VIDEO = auto()
    ARCHIVE = auto()
    LINK = auto()
    OTHER = auto()

class FileItem:
    """Rappresenta un file nel file manager."""
    def __init__(self, path: Path, virtual_path: str):
        self.path = path
        self.virtual_path = virtual_path
        self.name = path.name
        self.size = self._get_size()
        self.type = self._get_type()
        self.is_dir = path.is_dir()
        self.is_executable = os.access(path, os.X_OK) if path.is_file() else False
    
    def _get_size(self) -> int:
        """Ottiene la dimensione del file."""
        try:
            if self.path.is_dir():
                return 0  # Le directory non hanno una dimensione diretta
            return self.path.stat().st_size
        except:
            return 0
    
    def _get_type(self) -> FileType:
        """Determina il tipo di file basato sull'estensione o le proprietà."""
        if self.path.is_dir():
            return FileType.DIRECTORY
        elif self.path.is_symlink():
            return FileType.LINK
        
        # Controllo per eseguibili
        if os.access(self.path, os.X_OK):
            return FileType.EXECUTABLE
        
        # Controllo basato sull'estensione
        suffix = self.path.suffix.lower()
        
        # File di testo
        if suffix in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', 
                      '.sh', '.c', '.cpp', '.h', '.java', '.log', '.conf']:
            return FileType.TEXT
        
        # Immagini
        elif suffix in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
            return FileType.IMAGE
            
        # Audio
        elif suffix in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
            return FileType.AUDIO
            
        # Video
        elif suffix in ['.mp4', '.mkv', '.avi', '.mov', '.webm']:
            return FileType.VIDEO
            
        # Archivi
        elif suffix in ['.zip', '.tar', '.gz', '.bz2', '.xz', '.rar', '.7z']:
            return FileType.ARCHIVE
            
        # Binari
        elif suffix in ['.exe', '.dll', '.so', '.bin']:
            return FileType.BINARY
            
        return FileType.OTHER
    
    def get_formatted_size(self) -> str:
        """Restituisce una dimensione formattata in maniera leggibile."""
        if self.is_dir:
            return "<DIR>"
            
        size = self.size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def get_color(self) -> int:
        """Restituisce l'indice del colore da usare per questo file."""
        if self.is_dir:
            return 1  # Blu
        elif self.is_executable:
            return 2  # Verde
        elif self.type == FileType.TEXT:
            return 0  # Bianco
        elif self.type == FileType.IMAGE:
            return 3  # Magenta
        elif self.type == FileType.AUDIO or self.type == FileType.VIDEO:
            return 4  # Ciano
        elif self.type == FileType.ARCHIVE:
            return 5  # Giallo
        elif self.type == FileType.LINK:
            return 6  # Viola chiaro
        else:
            return 0  # Bianco

class FileManager:
    """
    File manager interattivo con interfaccia curses.
    Permette di navigare nei file, visualizzare contenuti ed eseguire programmi.
    """
    def __init__(self, fs_root: Path, current_virtual_dir: str = "/"):
        self.fs_root = fs_root
        self.current_virtual_dir = current_virtual_dir
        self.current_real_dir = self._virtual_to_real_path(current_virtual_dir)
        
        self.items = []
        self.selection = 0
        self.offset = 0
        self.header_lines = 3
        self.footer_lines = 2
        self.screen_height = 0
        self.screen_width = 0
        self.list_height = 0
        
        self.stdscr = None
        self._is_running = False
    
    def start(self) -> None:
        """Avvia il file manager in modalità curses."""
        # Salva lo stato originale del terminale
        original_terminal_state = None
        try:
            # Assicurati che il terminale sia in modalità normale prima di iniziare
            if 'curses' in sys.modules:
                try:
                    curses.endwin()
                except:
                    pass
            
            # Inizia curses in modo controllato
            original_terminal_state = os.system('')  # Trick per salvare lo stato del terminale
            curses.wrapper(self._main_loop)
        except Exception as e:
            print(f"Errore durante l'esecuzione del file manager: {e}")
        finally:
            # Ripristina lo stato del terminale
            try:
                curses.endwin()
                sys.stdout.write("\033c")  # Reset del terminale
                sys.stdout.flush()
            except:
                pass
    
    def _main_loop(self, stdscr) -> None:
        """Loop principale del file manager."""
        self.stdscr = stdscr
        self._is_running = True
        
        # Inizializzazione
        curses.curs_set(0)  # Nasconde il cursore
        curses.start_color()
        curses.use_default_colors()
        
        # Definizione delle coppie di colori
        curses.init_pair(1, curses.COLOR_BLUE, -1)     # Directory
        curses.init_pair(2, curses.COLOR_GREEN, -1)    # Eseguibile
        curses.init_pair(3, curses.COLOR_MAGENTA, -1)  # Immagine
        curses.init_pair(4, curses.COLOR_CYAN, -1)     # Audio/Video
        curses.init_pair(5, curses.COLOR_YELLOW, -1)   # Archivio
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)  # Link
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selezione
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLUE)   # Header
        curses.init_pair(9, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Footer
        
        # Carica la directory iniziale
        self._load_directory()
        
        # Loop principale
        while self._is_running:
            self.screen_height, self.screen_width = self.stdscr.getmaxyx()
            self.list_height = self.screen_height - self.header_lines - self.footer_lines
            
            self._draw_interface()
            self._handle_input()
    
    def _load_directory(self) -> None:
        """Carica i file nella directory corrente."""
        self.items = []
        self.selection = 0
        self.offset = 0
        
        try:
            # Verifica se stiamo accedendo al filesystem reale
            is_real_fs = self.current_virtual_dir.startswith("/mnt/system")
            
            # Aggiungi '..' per tornare alla directory superiore
            if self.current_virtual_dir != "/":
                parent_path = self.current_real_dir.parent
                parent_virtual = str(Path(self.current_virtual_dir).parent)
                self.items.append(FileItem(parent_path, parent_virtual))
                self.items[0].name = ".."  # Override del nome per chiarezza
            
            # Gestione speciale per i permessi quando si accede al filesystem reale
            if is_real_fs:
                try:
                    # Carica tutti i file e le directory con controllo permessi
                    for item in self.current_real_dir.iterdir():
                        try:
                            # Converti il percorso reale in percorso virtuale
                            rel_path = str(item.relative_to('/') if str(item).startswith('/') else item)
                            virtual_path = os.path.join("/mnt/system", rel_path)
                            virtual_path = virtual_path.replace("\\", "/")  # Normalizza separatori
                            self.items.append(FileItem(item, virtual_path))
                        except (PermissionError, OSError):
                            # Ignora file a cui non abbiamo accesso
                            pass
                except (PermissionError, OSError) as e:
                    # Mostra errore se non possiamo accedere alla directory
                    self._show_error(f"Accesso negato a {self.current_real_dir}: {e}")
                    # Torna alla directory precedente se possibile
                    if self.current_virtual_dir != "/mnt/system":
                        self._action_go_parent()
            else:
                # Normali operazioni per il filesystem virtuale
                for item in self.current_real_dir.iterdir():
                    try:
                        virtual_path = os.path.join(self.current_virtual_dir, item.name)
                        virtual_path = virtual_path.replace("\\", "/")  # Normalizza separatori
                        self.items.append(FileItem(item, virtual_path))
                    except PermissionError:
                        # Salta i file a cui non abbiamo accesso
                        pass
            
            # Ordina: prima le directory, poi i file, in ordine alfabetico
            self.items.sort(key=lambda x: (0 if x.name == ".." else 
                                         (1 if not x.is_dir else 0), x.name.lower()))
        except Exception as e:
            self._show_error(f"Errore nel caricamento della directory: {e}")
    
    def _draw_interface(self) -> None:
        """Disegna l'interfaccia del file manager."""
        self.stdscr.clear()
        
        # Disegna l'header
        header = f" ONEX File Manager - {self.current_virtual_dir} "
        self.stdscr.attron(curses.color_pair(8) | curses.A_BOLD)
        self.stdscr.addstr(0, 0, " " * self.screen_width)  # Sfondo blu per tutta la riga
        self.stdscr.addstr(0, (self.screen_width - len(header)) // 2, header[:self.screen_width])
        self.stdscr.attroff(curses.color_pair(8) | curses.A_BOLD)
        
        # Disegna la guida dei tasti
        key_guide = " Enter: Apri | F1: Aiuto | F5: Aggiorna | F10/Q: Esci "
        self.stdscr.addstr(1, 0, key_guide[:self.screen_width])
        
        # Linea separatrice
        self.stdscr.addstr(2, 0, "─" * self.screen_width)
        
        # Disegna la lista dei file
        self._draw_file_list()
        
        # Disegna il footer
        footer_y = self.screen_height - self.footer_lines
        self.stdscr.attron(curses.color_pair(9))
        self.stdscr.addstr(footer_y, 0, " " * self.screen_width)
        
        if self.selection < len(self.items):
            item = self.items[self.selection]
            footer_text = f" {item.name} - {item.get_formatted_size()} "
            self.stdscr.addstr(footer_y, 0, footer_text[:self.screen_width])
        
        help_text = " F1=Aiuto Esc=Indietro "
        if len(help_text) < self.screen_width:
            self.stdscr.addstr(footer_y, self.screen_width - len(help_text), help_text)
        self.stdscr.attroff(curses.color_pair(9))
        
        # Linea separatrice
        self.stdscr.addstr(footer_y - 1, 0, "─" * self.screen_width)
        
        self.stdscr.refresh()
    
    def _draw_file_list(self) -> None:
        """Disegna la lista dei file."""
        if not self.items:
            self.stdscr.addstr(self.header_lines + 1, 0, " Directory vuota")
            return
        
        # Assicurati che la selezione sia visibile
        if self.selection < self.offset:
            self.offset = self.selection
        if self.selection >= self.offset + self.list_height:
            self.offset = self.selection - self.list_height + 1
        
        # Limita l'offset
        max_offset = max(0, len(self.items) - self.list_height)
        self.offset = min(self.offset, max_offset)
        
        # Disegna gli elementi visibili
        for i in range(self.list_height):
            idx = i + self.offset
            if idx >= len(self.items):
                break
                
            item = self.items[idx]
            
            # Determina lo stile
            if idx == self.selection:
                attr = curses.color_pair(7)  # Selezione
            else:
                attr = curses.color_pair(item.get_color())
            
            # Prepara la stringa da visualizzare
            prefix = "📁 " if item.is_dir else "📄 "
            if item.is_executable:
                prefix = "🔧 "
            elif item.type == FileType.IMAGE:
                prefix = "🖼️  "
            elif item.type == FileType.AUDIO:
                prefix = "🎵 "
            elif item.type == FileType.VIDEO:
                prefix = "🎬 "
            elif item.type == FileType.ARCHIVE:
                prefix = "📦 "
            elif item.type == FileType.LINK:
                prefix = "🔗 "
            
            name = item.name
            size = item.get_formatted_size().rjust(10)
            
            # Calcola la lunghezza massima per il nome
            max_name_len = self.screen_width - len(prefix) - len(size) - 3
            if len(name) > max_name_len:
                name = name[:max_name_len-3] + "..."
            
            # Formatta la riga
            text = f"{prefix}{name} {size}"
            padding = " " * max(0, self.screen_width - len(text))
            text += padding
            
            # Disegna la riga
            try:
                y = i + self.header_lines
                self.stdscr.addstr(y, 0, text[:self.screen_width], attr)
            except:
                break
    
    def _handle_input(self) -> None:
        """Gestisce l'input dell'utente."""
        key = self.stdscr.getch()
        
        if key == curses.KEY_UP:
            self._move_selection(-1)
        elif key == curses.KEY_DOWN:
            self._move_selection(1)
        elif key == curses.KEY_PPAGE:  # Page Up
            self._move_selection(-self.list_height)
        elif key == curses.KEY_NPAGE:  # Page Down
            self._move_selection(self.list_height)
        elif key == curses.KEY_HOME:
            self._move_selection(-len(self.items))  # Vai all'inizio
        elif key == curses.KEY_END:
            self._move_selection(len(self.items))  # Vai alla fine
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            self._action_open_item()
        elif key == curses.KEY_BACKSPACE or key == 8 or key == 127 or key == 27:  # Esc/Backspace
            self._action_go_parent()
        elif key == curses.KEY_F5:
            self._load_directory()  # Ricarica la directory
        elif key == ord('q') or key == ord('Q') or key == curses.KEY_F10:
            self._is_running = False  # Esci
        elif key == curses.KEY_F1:
            self._show_help()
    
    def _move_selection(self, delta: int) -> None:
        """Muove la selezione di un numero di elementi."""
        self.selection += delta
        
        # Limita la selezione
        if self.selection < 0:
            self.selection = 0
        if self.selection >= len(self.items):
            self.selection = len(self.items) - 1
    
    def _action_open_item(self) -> None:
        """Apre l'elemento selezionato."""
        if self.selection >= len(self.items):
            return
        
        item = self.items[self.selection]
        
        if item.is_dir:
            # Cambia directory
            self.current_virtual_dir = item.virtual_path
            self.current_real_dir = item.path
            self._load_directory()
        elif item.is_executable:
            # Esegui file eseguibile
            self._execute_file(item)
        else:
            # Visualizza il contenuto del file
            self._view_file(item)
    
    def _action_go_parent(self) -> None:
        """Va alla directory genitore."""
        if self.current_virtual_dir == "/":
            return
        
        parent_virtual = str(Path(self.current_virtual_dir).parent)
        if not parent_virtual:
            parent_virtual = "/"
            
        parent_real = self.current_real_dir.parent
        
        self.current_virtual_dir = parent_virtual
        self.current_real_dir = parent_real
        self._load_directory()
    
    def _execute_file(self, item: FileItem) -> None:
        """Esegue un file."""
        # Salva lo stato del terminale
        curses.endwin()
        
        try:
            print(f"\nEsecuzione di {item.name}...")
            subprocess.run([item.path], check=False)
            print("\nEsecuzione completata. Premi un tasto per continuare...")
            input()
        except Exception as e:
            print(f"\nErrore durante l'esecuzione: {e}")
            print("Premi un tasto per continuare...")
            input()
        
        # Ripristina l'interfaccia curses
        self.stdscr.touchwin()
        self.stdscr.refresh()
    
    def _view_file(self, item: FileItem) -> None:
        """Visualizza il contenuto di un file."""
        if item.type == FileType.TEXT:
            self._view_text_file(item)
        elif item.type == FileType.IMAGE:
            self._show_message(f"Immagine: {item.name}\n\nUtilizza un visualizzatore esterno per vedere questo file.")
        elif item.type == FileType.AUDIO:
            self._show_message(f"File audio: {item.name}\n\nUtilizza un player esterno per ascoltare questo file.")
        elif item.type == FileType.VIDEO:
            self._show_message(f"File video: {item.name}\n\nUtilizza un player esterno per guardare questo video.")
        else:
            self._show_message(f"File binario: {item.name}\n\nDimensione: {item.get_formatted_size()}\n\nQuesto tipo di file non può essere visualizzato direttamente.")
    
    def _view_text_file(self, item: FileItem) -> None:
        """Visualizza un file di testo."""
        try:
            with open(item.path, 'r') as f:
                content = f.read()
            
            self._show_text_viewer(item.name, content)
        except UnicodeDecodeError:
            self._show_message(f"Il file {item.name} non è un file di testo o usa una codifica non supportata.")
        except Exception as e:
            self._show_message(f"Errore durante la lettura del file: {e}")
    
    def _show_text_viewer(self, title: str, content: str) -> None:
        """Mostra un visualizzatore di testo."""
        lines = content.splitlines()
        top_line = 0
        exit_viewer = False
        
        # Salva le dimensioni dello schermo
        height, width = self.stdscr.getmaxyx()
        
        while not exit_viewer:
            self.stdscr.clear()
            
            # Disegna l'header
            header = f" {title} "
            self.stdscr.attron(curses.color_pair(8) | curses.A_BOLD)
            self.stdscr.addstr(0, 0, " " * width)
            self.stdscr.addstr(0, (width - len(header)) // 2, header[:width])
            self.stdscr.attroff(curses.color_pair(8) | curses.A_BOLD)
            
            # Disegna il contenuto
            max_lines = height - 3  # Riserva righe per header e footer
            for i in range(min(max_lines, len(lines) - top_line)):
                line = lines[top_line + i]
                try:
                    self.stdscr.addstr(i + 1, 0, line[:width])
                except:
                    pass
            
            # Disegna il footer
            footer = f" Linee: {len(lines)} - Premi Q per uscire "
            self.stdscr.attron(curses.color_pair(9))
            self.stdscr.addstr(height - 1, 0, " " * width)
            self.stdscr.addstr(height - 1, 0, footer[:width])
            self.stdscr.attroff(curses.color_pair(9))
            
            # Aggiorna lo schermo
            self.stdscr.refresh()
            
            # Gestisci l'input
            key = self.stdscr.getch()
            
            if key == ord('q') or key == ord('Q') or key == 27:  # Esc
                exit_viewer = True
            elif key == curses.KEY_UP:
                top_line = max(0, top_line - 1)
            elif key == curses.KEY_DOWN:
                top_line = min(len(lines) - 1, top_line + 1)
            elif key == curses.KEY_PPAGE:  # Page Up
                top_line = max(0, top_line - max_lines)
            elif key == curses.KEY_NPAGE:  # Page Down
                top_line = min(len(lines) - 1, top_line + max_lines)
            elif key == curses.KEY_HOME:
                top_line = 0
            elif key == curses.KEY_END:
                top_line = max(0, len(lines) - max_lines)
    
    def _show_message(self, message: str) -> None:
        """Mostra un messaggio in una finestra popup."""
        lines = message.splitlines()
        
        # Calcola dimensioni della finestra
        max_line_len = max(len(line) for line in lines)
        height = len(lines) + 4
        width = max(max_line_len + 4, 20)
        
        # Posiziona la finestra al centro
        y = (self.screen_height - height) // 2
        x = (self.screen_width - width) // 2
        
        # Crea la finestra
        win = curses.newwin(height, width, y, x)
        win.box()
        
        # Mostra il messaggio
        for i, line in enumerate(lines):
            win.addstr(i + 2, 2, line)
        
        # Visualizza istruzioni
        win.addstr(height - 2, 2, "Premi un tasto per continuare...")
        
        win.refresh()
        win.getch()  # Attendi un tasto
    
    def _show_help(self) -> None:
        """Mostra la schermata di aiuto."""
        help_text = """
        ONEX File Manager - Aiuto
        
        Navigazione:
        ↑/↓      - Muovi selezione su/giù
        PgUp/PgDn - Scorri pagina su/giù
        Home/End  - Vai all'inizio/fine della lista
        
        Azioni:
        Enter     - Apri file/directory
        Esc/Backspc - Vai alla directory superiore
        F5        - Aggiorna directory
        
        Comandi generali:
        F1        - Mostra questo aiuto
        F10/Q     - Esci dal file manager
        """.strip()
        
        self._show_message(help_text)
    
    def _show_error(self, message: str) -> None:
        """Mostra un messaggio di errore."""
        self._show_message(f"ERRORE\n\n{message}")
    
    def _virtual_to_real_path(self, virtual_path: str) -> Path:
        """
        Converte un percorso virtuale in un percorso reale nel filesystem.
        """
        if not virtual_path:
            virtual_path = "/"
        
        # Gestione speciale per /mnt/system che deve puntare al filesystem reale
        if virtual_path.startswith("/mnt/system"):
            # Rimuovi "/mnt/system" e ottieni il percorso relativo al root reale
            rel_path = virtual_path[11:]  # Lunghezza di "/mnt/system"
            if not rel_path:
                return Path("/")  # Root del filesystem reale
            return Path(rel_path)
        
        # Normalizza il percorso
        parts = []
        for part in virtual_path.split("/"):
            if part == "..":
                if parts:
                    parts.pop()
            elif part and part != ".":
                parts.append(part)
        
        # Costruisci il percorso reale
        if not parts:
            return self.fs_root
        
        return self.fs_root.joinpath(*parts)

# Funzione per avviare il file manager direttamente
def start_file_manager(fs_root: Path, start_dir: str = "/") -> None:
    """
    Avvia il file manager.
    
    Args:
        fs_root: Directory radice del filesystem virtuale
        start_dir: Directory iniziale (percorso virtuale)
    """
    fm = FileManager(fs_root, start_dir)
    fm.start()

if __name__ == "__main__":
    # Test diretto del file manager
    if len(sys.argv) > 1:
        root_path = Path(sys.argv[1])
    else:
        root_path = Path.cwd()
    
    start_file_manager(root_path)
