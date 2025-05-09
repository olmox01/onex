# ONEX - Sistema di Applicazioni

Questo documento descrive come funziona il sistema di applicazioni in ONEX e come creare nuove applicazioni.

## Panoramica

Il sistema di applicazioni ONEX permette di:

1. Creare applicazioni in Python o come script shell
2. Organizzarle in modo modulare nel filesystem virtuale
3. Eseguirle dall'ambiente userland

Le applicazioni sono divise in due categorie:
- **App di Sistema**: Integrate nell'ambiente e disponibili automaticamente
- **App Utente**: Installate nella directory /usr/apps e richiedono il comando `run`

## Struttura di un'Applicazione

Un'applicazione ONEX deve avere la seguente struttura:

