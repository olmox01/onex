# ONEX - Guida per Sviluppatori

Questo documento fornisce dettagli tecnici per gli sviluppatori che vogliono contribuire al progetto ONEX o estenderne le funzionalità.

## Architettura del Sistema

ONEX è strutturato in diversi componenti che lavorano insieme per creare un'esperienza userland simulata:

```
┌─────────────┐
│    run.py   │ → Punto di ingresso
└─────┬───────┘
      │
┌─────▼───────┐
│  bootloader │ → Inizializzazione del sistema
└─────┬───────┘
      │
┌─────▼───────┐
│   main.py   │ → Coordinazione dei componenti
└─────┬───────┘
      │
      ▼
┌─────────────────────────────────────────────┐
│                                             │
│ ┌─────────┐ ┌─────────┐ ┌────────┐ ┌─────┐  │
│ │ userland │ │ system  │ │graphics│ │other│  │
│ └─────────┘ └─────────┘ └────────┘ └─────┘  │
│                                             │
└─────────────────────────────────────────────┘
```

### Flusso di Esecuzione

1. `run.py` → Avvia il sistema e configura l'ambiente Python
2. `bootloader/boot.py` → Verifica il sistema, installa dipendenze, crea filesystem
3. `src/main.py` → Coordina l'esecuzione dei componenti principali
4. `src/userland/userland.py` → Gestisce l'ambiente simulato e l'interazione con l'utente
5. Altri moduli → Forniscono funzionalità specializzate

## Convenzioni di Codice

- **Organizzazione dei File**: Il codice è organizzato per responsabilità
- **Docstrings**: Tutti i moduli, classi e funzioni hanno docstring in formato Google/NumPy
- **Typing**: Si utilizza la tipizzazione statica con `typing` per migliorare la manutenibilità
- **Gestione Errori**: Utilizzo di try/except con logging appropriato
- **Naming**: snake_case per funzioni e variabili, CamelCase per classi

## Pattern di Sviluppo

### Gestione delle Dipendenze

Il bootloader si occupa di verificare e installare le dipendenze necessarie. Quando aggiungi una nuova dipendenza:

1. Aggiungila alla lista `REQUIRED_PACKAGES` in `config/settings.py`
2. Documentala nei requisiti nel README
3. Assicurati che il codice gestisca correttamente l'assenza del pacchetto

### Estensione del Filesystem Virtuale

Il filesystem virtuale è implementato come una struttura di directory reale. Per estenderlo:

1. Modifica la funzione `_init_userland_filesystem()` nel bootloader
2. Aggiorna gli script in `src/scripts/02.sh` per la gestione del filesystem

### Aggiunta di Nuovi Comandi

Per aggiungere un nuovo comando alla shell simulata:

1. Modifica il metodo `_main_loop()` in `src/userland/userland.py`
2. Implementa una nuova funzione `_command_nome_comando(self, args)` per gestire la logica
3. Aggiorna il metodo `_show_help()` per documentare il nuovo comando

## Test e Debugging

### Logging

ONEX utilizza un sistema di logging centralizzato. Per utilizzarlo nei tuoi moduli:

```python
from src.system.logger import get_logger

# Ottieni un'istanza del logger
logger = get_logger()

# Usa il logger
logger.info("Messaggio informativo")
logger.error("Si è verificato un errore", exc_info=True)
```

### Debugging

Per il debugging, è possibile:

1. Utilizzare i log con livello DEBUG
2. Utilizzare il flag `--debug` all'avvio di run.py (da implementare)
3. Installare e utilizzare `pdb` o `ipdb` per il debugging interattivo

## Moduli Core

### Bootloader (bootloader/boot.py)

Responsabile dell'inizializzazione del sistema. Punti di estensione:

- `_check_and_install_dependencies()`: Per gestire nuove dipendenze
- `_init_userland_filesystem()`: Per modificare la struttura del filesystem
- `_authenticate_user()`: Per implementare un sistema di autenticazione reale

### UserLand (src/userland/userland.py)

Implementa l'ambiente simulato. Punti di estensione:

- `_main_loop()`: Per aggiungere nuovi comandi o comportamenti
- `_execute_command()`: Per migliorare l'esecuzione dei comandi di sistema
- Aggiunta di nuovi comandi interni

### File Manager (src/userland/file_manager.py)

Gestisce la navigazione e l'interazione con i file. Punti di estensione:

- `_view_file()`: Per supportare nuovi tipi di file
- `_execute_file()`: Per migliorare l'esecuzione dei file
- `_show_text_viewer()`: Per migliorare il visualizzatore di testo

## Contribuire al Progetto

1. **Stile di Codice**: Segui PEP 8 per la formattazione
2. **Documentazione**: Aggiorna la documentazione quando aggiungi/modifichi funzionalità
3. **Test**: Implementa test per le nuove funzionalità
4. **Feature Branch**: Sviluppa nuove funzionalità in branch separati
5. **Pull Request**: Descrivi chiaramente le modifiche nelle PR

## Roadmap di Sviluppo

- **Fase 1** (Completata): Architettura base e simulazione filesystem
- **Fase 2**: Miglioramento del file manager e dell'interfaccia utente
- **Fase 3**: Aggiunta di più programmi simulati e utility
- **Fase 4**: Implementazione di networking simulato e multi-utenza
- **Fase 5**: Estensione con plugin e API personalizzate
