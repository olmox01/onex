# ONEX - Userland Simulata per Terminali Linux

## Panoramica

ONEX è un sistema che simula un ambiente userland completo all'interno di un terminale Linux. Il progetto fornisce un'esperienza simile a un sistema operativo indipendente, con un proprio filesystem virtuale, un file manager interattivo, e un'interfaccia utente basata su curses.

## Caratteristiche Principali

- **Ambiente Simulato**: Fornisce un'esperienza di shell interattiva con proprio filesystem
- **File Manager**: Navigazione e gestione file con interfaccia TUI (Text User Interface)
- **Filesystem Virtuale**: Struttura filesystem di tipo UNIX con mount point per il filesystem reale
- **Gestione Utenti**: Autenticazione e profili utente
- **Shell Compatibility**: Integrazione con i diversi tipi di shell dei sistemi Linux
- **UI Terminale**: Interfaccia utente interattiva basata su curses

## Requisiti di Sistema

- Python 3.6 o superiore
- Sistema operativo Linux
- Librerie necessarie (installate automaticamente dal bootloader):
  - curses
  - pyfiglet
  - psutil
  - questionary
  - colorama
  - pillow
  - tqdm

## Installazione

1. Clona il repository:
   ```bash
   git clone https://github.com/yourusername/onex.git
   cd onex
   ```

2. Esegui il sistema:
   ```bash
   python run.py
   ```

Il bootloader verificherà ed installerà automaticamente le dipendenze necessarie.

## Struttura del Progetto

```
/onex/
├── run.py                     # Punto di ingresso principale
├── README.md                  # Documentazione
├── bootloader/
│   └── boot.py                # Gestore del processo di avvio
├── src/
│   ├── main.py                # Coordinatore del sistema
│   ├── graphics/
│   │   ├── ui.py              # Interfaccia utente
│   │   └── graphics.py        # Utility grafiche
│   ├── scripts/
│   │   ├── 01.sh              # Utility per gestione sistema
│   │   └── 02.sh              # Gestione filesystem virtuale
│   ├── system/
│   │   ├── shell_compatibility.py  # Compatibilità con shell
│   │   └── input.py           # Gestione input utente
│   └── userland/
│       ├── userland.py        # Sistema userland principale
│       └── file_manager.py    # Gestore file interattivo
└── userland_fs/               # Directory per il filesystem virtuale
    ├── bin/
    ├── etc/
    ├── home/
    ├── usr/
    ├── var/
    ├── tmp/
    └── mnt/
        └── system/            # Mount point per il filesystem reale
```

## Utilizzo

Dopo l'avvio del sistema, interagisci con la shell simulata:

1. **Navigazione**: Usa i comandi standard come `cd`, `ls`, etc.
2. **File Manager**: Digita `run filemanager` per avviare l'interfaccia di gestione file
3. **Esecuzione Programmi**: I file eseguibili possono essere avviati come in un normale ambiente Linux
4. **Utility di Sistema**: Comandi integrati per gestire l'ambiente simulato
5. **Chiusura**: Usa il comando `exit` per uscire dall'ambiente

## File Manager

Il file manager interattivo si naviga con:

- **Frecce direzionali**: Spostamento tra file
- **Enter**: Apri file/directory
- **Esc/Backspace**: Torna alla directory superiore
- **F5**: Aggiorna la vista
- **F1**: Mostra aiuto
- **F10/Q**: Esci dal file manager

## Architettura del Sistema

1. **Boot Process**:
   - `run.py` → `bootloader/boot.py` → `src/main.py` → `src/userland/userland.py`

2. **Flusso di Esecuzione**:
   - Verifica ambiente e privilegi
   - Rilevamento sistema e utente
   - Installazione dipendenze
   - Inizializzazione filesystem
   - Avvio userland
   - Interazione utente

3. **Filesystem Virtuale**:
   - Struttura tipo UNIX
   - Directory userland_fs con sottodirectory standard
   - Mount point per accedere al filesystem reale

## Sviluppo

Per contribuire al progetto:

1. Effettua un fork del repository
2. Crea un branch per la tua funzionalità (`git checkout -b feature/amazing-feature`)
3. Committa le modifiche (`git commit -m 'Add some amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Apri una Pull Request

## Licenza

[MIT](https://choosealicense.com/licenses/mit/)
