#!/usr/bin/env python3
"""
ONEX UI
Interfaccia utente per il sistema ONEX basata su curses
"""

import curses
import time
from typing import List, Dict, Any, Callable, Tuple, Optional

class UserInterface:
    """
    Fornisce un'interfaccia utente basata su curses per il sistema ONEX.
    Gestisce layout, menu, finestre e componenti dell'interfaccia.
    """
    def __init__(self):
        self.stdscr = None
        self.height = 0
        self.width = 0
        self.windows = {}
        self._is_initialized = False
    
    def initialize(self) -> None:
        """Inizializza l'interfaccia curses."""
        if self._is_initialized:
            return
            
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        
        # Nascondi il cursore
        try:
            curses.curs_set(0)
        except:
            pass
        
        # Abilita i colori
        try:
            curses.start_color()
            curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)  # Intestazione
            curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Barra di stato
            curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Testo evidenziato
            curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Avvisi
            curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)  # Errori
            curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Informazioni
        except:
            pass
        
        # Ottieni dimensioni del terminale
        self.height, self.width = self.stdscr.getmaxyx()
        self._is_initialized = True
    
    def cleanup(self) -> None:
        """Ripristina le impostazioni del terminale."""
        if not self._is_initialized:
            return
            
        self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        self._is_initialized = False
    
    def create_window(self, name: str, height: int, width: int, 
                     y: int, x: int, border: bool = True) -> bool:
        """
        Crea una finestra nell'interfaccia.
        
        Args:
            name: Nome identificativo della finestra
            height: Altezza della finestra
            width: Larghezza della finestra
            y: Posizione Y (riga) della finestra
            x: Posizione X (colonna) della finestra
            border: Se True, disegna un bordo attorno alla finestra
            
        Returns:
            bool: True se la creazione è riuscita, False altrimenti
        """
        if not self._is_initialized:
            self.initialize()
            
        try:
            # Verifica che le dimensioni siano valide
            if y + height > self.height or x + width > self.width:
                return False
                
            # Crea la finestra
            win = curses.newwin(height, width, y, x)
            
            if border:
                win.box()
            
            # Aggiunge la finestra al dizionario
            self.windows[name] = {
                'window': win,
                'height': height,
                'width': width,
                'y': y,
                'x': x,
                'border': border
            }
            
            win.refresh()
            return True
            
        except Exception as e:
            return False
    
    def write_to_window(self, name: str, text: str, y: int, x: int, 
                       color_pair: int = 0, bold: bool = False) -> bool:
        """
        Scrive testo in una finestra.
        
        Args:
            name: Nome della finestra
            text: Testo da scrivere
            y: Posizione Y relativa alla finestra
            x: Posizione X relativa alla finestra
            color_pair: Indice della coppia di colori da usare
            bold: Se True, il testo sarà in grassetto
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if name not in self.windows:
            return False
            
        try:
            win = self.windows[name]['window']
            attrs = curses.color_pair(color_pair)
            
            if bold:
                attrs |= curses.A_BOLD
                
            win.addstr(y, x, text, attrs)
            win.refresh()
            return True
            
        except:
            return False
    
    def clear_window(self, name: str) -> bool:
        """
        Pulisce una finestra.
        
        Args:
            name: Nome della finestra
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if name not in self.windows:
            return False
            
        try:
            win = self.windows[name]['window']
            win.clear()
            
            if self.windows[name]['border']:
                win.box()
                
            win.refresh()
            return True
            
        except:
            return False
    
    def delete_window(self, name: str) -> bool:
        """
        Elimina una finestra.
        
        Args:
            name: Nome della finestra
            
        Returns:
            bool: True se l'operazione è riuscita, False altrimenti
        """
        if name not in self.windows:
            return False
            
        try:
            self.windows[name]['window'].clear()
            self.windows[name]['window'].refresh()
            del self.windows[name]
            return True
            
        except:
            return False
    
    def create_layout(self, layout_type: str) -> Dict[str, Any]:
        """
        Crea un layout predefinito per l'interfaccia.
        
        Args:
            layout_type: Tipo di layout ('standard', 'split', 'fullscreen')
            
        Returns:
            Dict[str, Any]: Dizionario con le finestre create
        """
        if not self._is_initialized:
            self.initialize()
            
        # Elimina eventuali finestre esistenti
        for name in list(self.windows.keys()):
            self.delete_window(name)
            
        if layout_type == 'standard':
            # Layout standard: intestazione, area principale, barra di stato
            self.create_window('header', 3, self.width, 0, 0)
            self.create_window('main', self.height - 4, self.width, 3, 0)
            self.create_window('status', 1, self.width, self.height - 1, 0, False)
            
            # Scrivi nell'intestazione
            self.write_to_window('header', " ONEX System ", 1, 2, 1, True)
            self.write_to_window('status', " Pronto ", 0, 0, 2)
            
            return {
                'header': self.windows['header'],
                'main': self.windows['main'],
                'status': self.windows['status']
            }
            
        elif layout_type == 'split':
            # Layout diviso: intestazione, area sinistra, area destra, barra di stato
            half_width = self.width // 2
            
            self.create_window('header', 3, self.width, 0, 0)
            self.create_window('left', self.height - 4, half_width, 3, 0)
            self.create_window('right', self.height - 4, self.width - half_width, 3, half_width)
            self.create_window('status', 1, self.width, self.height - 1, 0, False)
            
            self.write_to_window('header', " ONEX System ", 1, 2, 1, True)
            self.write_to_window('status', " Modalità divisa ", 0, 0, 2)
            
            return {
                'header': self.windows['header'],
                'left': self.windows['left'],
                'right': self.windows['right'],
                'status': self.windows['status']
            }
            
        elif layout_type == 'fullscreen':
            # Layout a schermo intero: solo area principale
            self.create_window('main', self.height, self.width, 0, 0, False)
            return {
                'main': self.windows['main']
            }
            
        return {}
    
    def show_menu(self, items: List[str], title: str = "Menu") -> int:
        """
        Mostra un menu di selezione.
        
        Args:
            items: Elenco di voci del menu
            title: Titolo del menu
            
        Returns:
            int: Indice dell'elemento selezionato o -1 se annullato
        """
        if not self._is_initialized:
            self.initialize()
            
        if not items:
            return -1
            
        # Calcola dimensioni del menu
        height = len(items) + 4
        width = max(len(title) + 4, max(len(item) for item in items) + 4)
        
        # Centra il menu
        y = (self.height - height) // 2
        x = (self.width - width) // 2
        
        # Crea la finestra del menu
        menu_win = curses.newwin(height, width, y, x)
        menu_win.keypad(True)
        menu_win.box()
        
        # Mostra il titolo
        menu_win.addstr(1, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Gestione della selezione
        current_row = 0
        
        while True:
            # Mostra le voci del menu
            for i, item in enumerate(items):
                y_pos = i + 2
                x_pos = 2
                
                if i == current_row:
                    menu_win.addstr(y_pos, x_pos, item, curses.A_REVERSE)
                else:
                    menu_win.addstr(y_pos, x_pos, item)
            
            menu_win.refresh()
            
            # Gestione dell'input
            key = menu_win.getch()
            
            if key == curses.KEY_UP and current_row > 0:
                current_row -= 1
            elif key == curses.KEY_DOWN and current_row < len(items) - 1:
                current_row += 1
            elif key in [curses.KEY_ENTER, 10, 13]:  # Enter
                break
            elif key == 27:  # Escape
                current_row = -1
                break
                
        del menu_win
        self.stdscr.touchwin()
        self.stdscr.refresh()
        
        return current_row
    
    def show_message(self, message: str, title: str = "Messaggio", wait_key: bool = True) -> None:
        """
        Mostra un messaggio in una finestra popup.
        
        Args:
            message: Il messaggio da visualizzare
            title: Il titolo della finestra
            wait_key: Se True, attende la pressione di un tasto
        """
        if not self._is_initialized:
            self.initialize()
        
        # Divide il messaggio in righe
        lines = message.split('\n')
        
        # Calcola dimensioni della finestra
        height = len(lines) + 4
        width = max(len(title) + 4, max(len(line) for line in lines) + 4)
        
        # Centra la finestra
        y = (self.height - height) // 2
        x = (self.width - width) // 2
        
        # Crea la finestra
        msg_win = curses.newwin(height, width, y, x)
        msg_win.box()
        
        # Mostra il titolo
        msg_win.addstr(1, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Mostra il messaggio
        for i, line in enumerate(lines):
            msg_win.addstr(i + 2, 2, line)
        
        # Mostra istruzioni
        if wait_key:
            msg_win.addstr(height - 2, 2, "Premi un tasto per continuare...", curses.A_DIM)
        
        msg_win.refresh()
        
        # Attendi input
        if wait_key:
            msg_win.getch()
            
        del msg_win
        self.stdscr.touchwin()
        self.stdscr.refresh()
    
    def get_terminal_size(self) -> Tuple[int, int]:
        """
        Restituisce le dimensioni del terminale.
        
        Returns:
            Tuple[int, int]: Altezza e larghezza del terminale
        """
        if not self._is_initialized:
            self.initialize()
            
        return self.height, self.width

# Funzioni di supporto per l'utilizzo dell'interfaccia senza inizializzazione di curses
def simple_progress_bar(total: int, description: str = "") -> Callable[[int], None]:
    """
    Crea una barra di progresso semplice per console.
    
    Args:
        total: Numero totale di step
        description: Descrizione della barra
        
    Returns:
        Callable[[int], None]: Funzione per aggiornare la barra
    """
    def update(current: int) -> None:
        percent = int(current / total * 100)
        bar_length = 40
        filled_length = int(bar_length * current / total)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        print(f"\r{description} |{bar}| {percent}% ({current}/{total})", end="", flush=True)
        if current >= total:
            print()
    
    return update

def clear_screen() -> None:
    """Pulisce lo schermo del terminale."""
    print("\033c", end="")
