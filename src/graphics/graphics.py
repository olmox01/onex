import curses
from typing import Any, List

class Graphics:
    def __init__(self):
        self.stdscr = None
        self._is_initialized = False
        self.has_colors = False
        self.color_counter = 0
        self.color_pairs = {}

    def initialize(self) -> None:
        """Inizializza la libreria curses."""
        if self._is_initialized:
            return

        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.stdscr.keypad(True)
        self._is_initialized = True

        if curses.has_colors():
            self.has_colors = True
            curses.start_color()

    def _init_color_pair(self, fg: int, bg: int) -> int:
        """
        Inizializza una coppia di colori.
        
        Args:
            fg: Colore di primo piano
            bg: Colore di sfondo
            
        Returns:
            int: Indice della coppia di colori
        """
        if not self.has_colors:
            return 0
            
        self.color_counter += 1
        key = f"{fg},{bg}"
        
        try:
            curses.init_pair(self.color_counter, fg, bg)
            self.color_pairs[key] = self.color_counter
            return self.color_counter
        except:
            return 0
    
    def cleanup(self) -> None:
        """Ripristina le impostazioni del terminale."""
        if not self._is_initialized:
            return
            
        if self.stdscr:
            self.stdscr.keypad(False)
            curses.nocbreak()
            curses.echo()
            curses.endwin()
            
        self._is_initialized = False
    
    def draw_box(self, win: Any, y: int, x: int, height: int, width: int, 
                style: int = 0, color_pair: int = 0) -> None:
        """
        Disegna un box con bordi.
        
        Args:
            win: Finestra su cui disegnare
            y, x: Coordinate dell'angolo superiore sinistro
            height, width: Dimensioni del box
            style: Stile del bordo (0=singolo, 1=doppio)
            color_pair: Coppia di colori da usare
        """
        if not win:
            return
            
        attrs = curses.color_pair(color_pair)
        
        # Caratteri per i bordi
        if style == 1:  # Doppio
            tl, tr = '╔', '╗'  # top-left, top-right
            bl, br = '╚', '╝'  # bottom-left, bottom-right
            h, v = '═', '║'    # horizontal, vertical
        else:  # Singolo
            tl, tr = '┌', '┐'
            bl, br = '└', '┘'
            h, v = '─', '│'
        
        # Disegna i bordi
        win.addstr(y, x, tl, attrs)
        win.addstr(y, x + width - 1, tr, attrs)
        win.addstr(y + height - 1, x, bl, attrs)
        win.addstr(y + height - 1, x + width - 1, br, attrs)
        
        # Disegna lati orizzontali
        for i in range(1, width - 1):
            win.addstr(y, x + i, h, attrs)
            win.addstr(y + height - 1, x + i, h, attrs)
        
        # Disegna lati verticali
        for i in range(1, height - 1):
            win.addstr(y + i, x, v, attrs)
            win.addstr(y + i, x + width - 1, v, attrs)
    
    def draw_progress_bar(self, win: Any, y: int, x: int, width: int, 
                         progress: float, color_pair: int = 0) -> None:
        """
        Disegna una barra di progresso.
        
        Args:
            win: Finestra su cui disegnare
            y, x: Coordinate iniziali
            width: Larghezza totale della barra
            progress: Valore tra 0.0 e 1.0
            color_pair: Coppia di colori da usare
        """
        if not win:
            return
        
        # Limita il progresso tra 0 e 1
        progress = max(0.0, min(1.0, progress))
        
        # Calcola la larghezza della parte riempita
        filled_width = int(width * progress)
        
        # Disegna la cornice
        win.addstr(y, x, '[')
        win.addstr(y, x + width + 1, ']')
        
        # Disegna la barra
        for i in range(width):
            if i < filled_width:
                win.addstr(y, x + i + 1, '█', curses.color_pair(color_pair))
            else:
                win.addstr(y, x + i + 1, ' ')
                
        # Percentuale
        percent = int(progress * 100)
        percent_str = f" {percent}%"
        win.addstr(y, x + width + 3, percent_str)
    
    def draw_table(self, win: Any, y: int, x: int, data: List[List[str]], 
                  headers: List[str] = None, color_pair: int = 0) -> None:
        """
        Disegna una tabella.
        
        Args:
            win: Finestra su cui disegnare
            y, x: Coordinate iniziali
            data: Dati della tabella (lista di righe)
            headers: Intestazioni delle colonne
            color_pair: Coppia di colori per l'intestazione
        """
        if not win or not data:
            return
            
        # Se non ci sono dati, esci
        if not data[0]:
            return
            
        # Calcola larghezza delle colonne
        columns = len(data[0])
        col_widths = [0] * columns
        
        # Considera le intestazioni
        if headers:
            for i, header in enumerate(headers):
                col_widths[i] = max(col_widths[i], len(header))
        
        # Considera i dati
        for row in data:
            for i, cell in enumerate(row):
                if i < columns:
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Disegna le intestazioni
        current_x = x
        if headers:
            for i, header in enumerate(headers):
                win.addstr(y, current_x, header.ljust(col_widths[i]), 
                          curses.color_pair(color_pair) | curses.A_BOLD)
                current_x += col_widths[i] + 2
            y += 1
            
            # Disegna linea separatrice
            current_x = x
            for width in col_widths:
                win.addstr(y, current_x, "─" * width)
                current_x += width + 2
            y += 1
        
        # Disegna i dati
        for row in data:
            current_x = x
            for i, cell in enumerate(row):
                if i < columns:
                    win.addstr(y, current_x, str(cell).ljust(col_widths[i]))
                    current_x += col_widths[i] + 2
            y += 1
    
    def draw_banner(self, win: Any, text: str, y: int = 0, centered: bool = True,
                   color_pair: int = 0, font: str = None) -> int:
        """
        Disegna un banner ASCII art.
        
        Args:
            win: Finestra su cui disegnare
            text: Testo da convertire in ASCII art
            y: Riga di partenza
            centered: Se True, centra il banner
            color_pair: Coppia di colori da usare
            font: Nome del font pyfiglet da usare
            
        Returns:
            int: Numero di righe occupate dal banner
        """
        try:
            import pyfiglet
            
            # Crea l'ASCII art
            if font:
                fig = pyfiglet.Figlet(font=font)
            else:
                fig = pyfiglet.Figlet()
                
            banner_text = fig.renderText(text)
            lines = banner_text.split("\n")
            
            # Larghezza massima del banner
            max_width = max(len(line) for line in lines)
            
            # Disegna ogni riga
            for i, line in enumerate(lines):
                if not line.strip():  # Salta le righe vuote
                    continue
                    
                # Calcola posizione orizzontale
                if centered and win:
                    win_height, win_width = win.getmaxyx()
                    x = max(0, (win_width - len(line)) // 2)
                else:
                    x = 0
                
                if win:
                    win.addstr(y + i, x, line, curses.color_pair(color_pair))
                else:
                    print(line)
            
            return len(lines)
            
        except ImportError:
            # Fallback se pyfiglet non è disponibile
            if win:
                win.addstr(y, 0, text, curses.color_pair(color_pair) | curses.A_BOLD)
            else:
                print(text)
            return 1
        except Exception as e:
            if win:
                win.addstr(y, 0, text, curses.color_pair(color_pair))
            else:
                print(text)
            return 1
    
    def get_color_pair(self, fg: int, bg: int) -> int:
        """
        Ottiene l'indice di una coppia di colori, creandola se necessario.
        
        Args:
            fg: Colore di primo piano
            bg: Colore di sfondo
            
        Returns:
            int: Indice della coppia di colori
        """
        if not self.has_colors:
            return 0
            
        key = f"{fg},{bg}"
        
        if key in self.color_pairs:
            return self.color_pairs[key]
            
        return self._init_color_pair(fg, bg)

class OffscreenBuffer:
    """
    Buffer fuori schermo per rendering più efficiente.
    Permette di costruire un'interfaccia completa e mostrarla tutta insieme.
    """
    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.buffer = [[' ' for _ in range(width)] for _ in range(height)]
        self.colors = [[0 for _ in range(width)] for _ in range(height)]
    
    def clear(self) -> None:
        """Pulisce il buffer."""
        for y in range(self.height):
            for x in range(self.width):
                self.buffer[y][x] = ' '
                self.colors[y][x] = 0
    
    def write(self, y: int, x: int, text: str, color: int = 0) -> None:
        """
        Scrive testo nel buffer.
        
        Args:
            y, x: Coordinate
            text: Testo da scrivere
            color: Indice del colore da usare
        """
        if y < 0 or y >= self.height:
            return
            
        for i, char in enumerate(text):
            if x + i < 0 or x + i >= self.width:
                continue
                
            self.buffer[y][x + i] = char
            self.colors[y][x + i] = color
    
    def draw_to_window(self, win: Any) -> None:
        """
        Disegna il buffer su una finestra.
        
        Args:
            win: Finestra su cui disegnare
        """
        if not win:
            return
            
        for y in range(self.height):
            for x in range(self.width):
                try:
                    win.addch(y, x, self.buffer[y][x], curses.color_pair(self.colors[y][x]))
                except:
                    pass  # Ignora errori di posizionamento fuori finestra