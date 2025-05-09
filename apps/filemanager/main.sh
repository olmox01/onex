#!/bin/bash
# Name: filemanager
# Description: File manager interattivo con interfaccia curses
# Version: 1.0.0
# Author: ONEX Team
# System: true

# Ottieni il percorso dello script corrente
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
BASE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
MAIN_PY="$SCRIPT_DIR/main.py"

# Verifica che il file main.py esista
if [ ! -f "$MAIN_PY" ]; then
  echo "Errore: File main.py non trovato in $SCRIPT_DIR"
  exit 1
fi

# Imposta le variabili d'ambiente necessarie
export ONEX_APP_PATH="$SCRIPT_DIR"
export ONEX_APP_NAME="filemanager"
export ONEX_FS_ROOT="${ONEX_FS_ROOT:-"$BASE_DIR/userland_fs"}"

# Salva lo stato del terminale
stty_save=$(stty -g 2>/dev/null) || true

# Stampa un messaggio di avvio
echo "Avvio del file manager..."

# Esegui il file manager Python
python3 "$MAIN_PY" "$@"
EXIT_CODE=$?

# Ripristina lo stato del terminale
stty $stty_save 2>/dev/null || true

# Pulisci lo schermo e posiziona il cursore in alto
clear
echo ""  # Stampa una riga vuota per migliorare l'aspetto del prompt

exit $EXIT_CODE
