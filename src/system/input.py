#!/usr/bin/env python3
"""
ONEX Input Handler
Gestisce gli input da tastiera e mouse in un ambiente terminale curses
"""

import sys
import curses
from enum import Enum, auto
from typing import Callable, Dict, Any, List, Tuple, Optional

class Key(Enum):
    """Enumerazione dei tasti speciali."""
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    ENTER = auto()
    ESCAPE = auto()
    BACKSPACE = auto()
    DELETE = auto()
    TAB = auto()
    HOME = auto()
    END = auto()
    PAGE_UP = auto()
    PAGE_DOWN = auto()
    F1 = auto()
    F2 = auto()
    F3 = auto()
    F4 = auto()
    F5 = auto()
    F6 = auto()
    F7 = auto()
    F8 = auto()
    F9 = auto()
    F10 = auto()
    F11 = auto()
    F12 = auto()

class MouseEvent(Enum):
    """Enumerazione degli eventi mouse."""
    LEFT_CLICK = auto()
    RIGHT_CLICK = auto()
    MIDDLE_CLICK = auto()
    SCROLL_UP = auto()
    SCROLL_DOWN = auto()
    DRAG = auto()
    MOVE = auto()

class InputHandler:
    """
    Gestisce l'input da tastiera e mouse usando curses.
    Fornisce un'API semplificata per gestire gli input in modalità 
    sia non bloccante che bloccante.
    """
    def __init__(self):
        self.stdscr = None
        self._key_mappings = {
            curses.KEY_UP: Key.UP,
            curses.KEY_DOWN: Key.DOWN,
            curses.KEY_LEFT: Key.LEFT,
            curses.KEY_RIGHT: Key.RIGHT,
            curses.KEY_ENTER: Key.ENTER,
            10: Key.ENTER,  # Anche il tasto Enter può essere 10 (linefeed)
            13: Key.ENTER,  # O 13 (carriage return)
            27: Key.ESCAPE,
            curses.KEY_BACKSPACE: Key.BACKSPACE,
            8: Key.BACKSPACE,  # Ctrl+H / Backspace
            127: Key.BACKSPACE,  # Alcune terminali usano 127 per Backspace
            curses.KEY_DC: Key.DELETE,
            curses.KEY_HOME: Key.HOME,
            curses.KEY_END: Key.END,
            curses.KEY_PPAGE: Key.PAGE_UP,
            curses.KEY_NPAGE: Key.PAGE_DOWN,
            9: Key.TAB,
            curses.KEY_F1: Key.F1,
            curses.KEY_F2: Key.F2,
            curses.KEY_F3: Key.F3,
            curses.KEY_F4: Key.F4,
            curses.KEY_F5: Key.F5,
            curses.KEY_F6: Key.F6,
            curses.KEY_F7: Key.F7,
            curses.KEY_F8: Key.F8,
            curses.KEY_F9: Key.F9,
            curses.KEY_F10: Key.F10,
            curses.KEY_F11: Key.F11,
            curses.KEY_F12: Key.F12,
        }
        self._mouse_mappings = {}
        self._is_initialized = False
    
    def initialize(self) -> None:
        """Inizializza curses e configura l'input."""
        if self._is_initialized:
            return
            
        self.stdscr = curses.initscr()
        curses.noecho()  # Non mostrare i tasti premuti
        curses.cbreak()  # Reazione immediata ai tasti senza buffering
        self.stdscr.keypad(True)  # Abilita i tasti speciali
        
        # Abilita il supporto al mouse se possibile
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
            self._has_mouse = True
        except:
            self._has_mouse = False
        
        # Abilita i colori se possibile
        try:
            curses.start_color()
            self._has_colors = True
        except:
            self._has_colors = False
            
        self._is_initialized = True
    
    def cleanup(self) -> None:
        """Ripristina le impostazioni del terminale."""
        if not self._is_initialized:
            return
            
        # Ripristina le impostazioni del terminale
        self.stdscr.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()
        self._is_initialized = False
    
    def getch(self, blocking: bool = True) -> Tuple[Optional[Key], Optional[str]]:
        """
        Legge un carattere dall'input.
        
        Args:
            blocking: Se True, la funzione blocca fino alla pressione di un tasto
            
        Returns:
            Tuple[Optional[Key], Optional[str]]: Il tasto premuto (speciale o carattere)
        """
        if not self._is_initialized:
            self.initialize()
            
        if not blocking:
            self.stdscr.nodelay(True)
        
        try:
            ch = self.stdscr.getch()
            
            if ch == -1:  # Nessun input disponibile in modalità non bloccante
                return None, None
                
            # Controlla se è un tasto speciale
            if ch in self._key_mappings:
                return self._key_mappings[ch], None
            elif ch == curses.KEY_MOUSE and self._has_mouse:
                return self._handle_mouse_event()
            else:
                # È un carattere normale
                try:
                    return None, chr(ch)
                except:
                    return None, None
                    
        finally:
            if not blocking:
                self.stdscr.nodelay(False)
    
    def _handle_mouse_event(self) -> Tuple[Optional[Key], Optional[str]]:
        """
        Gestisce un evento mouse.
        
        Returns:
            Tuple[Optional[Key], Optional[str]]: Evento mouse e posizione
        """
        try:
            mouse_event = curses.getmouse()
            event_id, x, y, z, button_state = mouse_event
            
            # Determina il tipo di evento
            if button_state & curses.BUTTON1_PRESSED:
                return MouseEvent.LEFT_CLICK, f"{x},{y}"
            elif button_state & curses.BUTTON3_PRESSED:
                return MouseEvent.RIGHT_CLICK, f"{x},{y}"
            elif button_state & curses.BUTTON2_PRESSED:
                return MouseEvent.MIDDLE_CLICK, f"{x},{y}"
            elif button_state & curses.BUTTON4_PRESSED:
                return MouseEvent.SCROLL_UP, f"{x},{y}"
            elif button_state & curses.BUTTON5_PRESSED:
                return MouseEvent.SCROLL_DOWN, f"{x},{y}"
            else:
                return MouseEvent.MOVE, f"{x},{y}"
        except:
            return None, None
    
    def get_input_with_prompt(self, prompt: str, max_len: int = 100) -> str:
        """
        Mostra un prompt e ottiene input dall'utente.
        
        Args:
            prompt: Il messaggio da mostrare
            max_len: Lunghezza massima dell'input
            
        Returns:
            str: L'input dell'utente
        """
        if not self._is_initialized:
            self.initialize()
            
        try:
            y, x = self.stdscr.getyx()
            self.stdscr.addstr(y, 0, prompt)
            curses.echo()  # Abilita l'echo per vedere cosa si digita
            input_str = self.stdscr.getstr(y, len(prompt), max_len).decode('utf-8')
            curses.noecho()  # Disabilita l'echo
            return input_str
        except:
            return ""
    
    def read_line(self, prompt: str = "") -> str:
        """
        Legge una linea di input con gestione base della linea di comando.
        Supporta backspace ed editing basilare.
        
        Args:
            prompt: Il messaggio da mostrare
            
        Returns:
            str: La linea inserita
        """
        if not self._is_initialized:
            self.initialize()
        
        # Temporaneamente ripristina le impostazioni del terminale
        # per permettere l'uso di input() standard di Python
        self.cleanup()
        
        try:
            result = input(prompt)
            return result
        finally:
            # Reinizializza curses
            self.initialize()
