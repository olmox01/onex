#!/bin/bash
# Tool per eseguire direttamente un'app ONEX senza avviare tutto il sistema

# Percorso base
BASE_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
APPS_DIR="$BASE_DIR/apps"

# Controllo degli argomenti
if [ $# -lt 1 ]; then
    echo "Utilizzo: $0 <nome_app> [argomenti...]"
    echo "Esegue un'applicazione ONEX direttamente."
    exit 1
fi

APP_NAME="$1"
shift

# Verifica se l'app esiste
APP_DIR="$APPS_DIR/$APP_NAME"
if [ ! -d "$APP_DIR" ]; then
    echo "Errore: Applicazione '$APP_NAME' non trovata."
    exit 1
fi

# Determina il tipo di app
if [ -f "$APP_DIR/main.py" ]; then
    echo "Esecuzione dell'applicazione Python: $APP_NAME"
    python3 "$APP_DIR/main.py" "$@"
elif [ -f "$APP_DIR/main.sh" ]; then
    echo "Esecuzione dello script shell: $APP_NAME"
    bash "$APP_DIR/main.sh" "$@"
else
    echo "Errore: Non è stato trovato né main.py né main.sh in $APP_DIR"
    exit 1
fi
