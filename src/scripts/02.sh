#!/bin/bash
# ONEX Script 02
# Gestione del filesystem userland e operazioni di virtualizzazione

# Variabili globali
USERLAND_FS_ROOT=""
REAL_SYSTEM_MOUNT=""

# Inizializza le variabili basate sui parametri
init_variables() {
    if [ -z "$1" ]; then
        echo "Errore: percorso root del filesystem userland non specificato."
        return 1
    fi
    
    USERLAND_FS_ROOT="$1"
    REAL_SYSTEM_MOUNT="${USERLAND_FS_ROOT}/mnt/system"
    
    return 0
}

# Crea la struttura base del filesystem
create_fs_structure() {
    echo "Creazione della struttura del filesystem in ${USERLAND_FS_ROOT}..."
    
    # Crea la directory root se non esiste
    mkdir -p "${USERLAND_FS_ROOT}"
    
    # Crea le directory standard UNIX
    for dir in bin etc home usr var tmp opt mnt dev proc sys; do
        mkdir -p "${USERLAND_FS_ROOT}/${dir}"
        echo "Creata directory: ${dir}"
    done
    
    # Crea il mount point per il filesystem reale
    mkdir -p "${REAL_SYSTEM_MOUNT}"
    echo "Creato mount point per il filesystem reale: ${REAL_SYSTEM_MOUNT}"
    
    return 0
}

# Crea la home directory per un utente
create_user_home() {
    local username=$1
    
    if [ -z "$username" ]; then
        echo "Errore: nome utente non specificato."
        return 1
    fi
    
    local user_home="${USERLAND_FS_ROOT}/home/${username}"
    
    if [ -d "$user_home" ]; then
        echo "Home directory per l'utente ${username} già esistente."
        return 0
    fi
    
    echo "Creazione home directory per l'utente ${username}..."
    mkdir -p "${user_home}"
    
    # Crea sottodirectory standard nella home
    for dir in Documents Downloads Pictures Videos Music .config; do
        mkdir -p "${user_home}/${dir}"
    done
    
    # Crea file di configurazione base
    touch "${user_home}/.bashrc"
    touch "${user_home}/.profile"
    
    echo "Home directory creata con successo in ${user_home}"
    return 0
}

# Crea file di base nel filesystem
create_base_files() {
    echo "Creazione dei file di base nel filesystem..."
    
    # /etc/passwd (semplificato)
    cat > "${USERLAND_FS_ROOT}/etc/passwd" << EOF
root:x:0:0:root:/root:/bin/bash
nobody:x:99:99:Nobody:/:/usr/sbin/nologin
EOF

    # /etc/group (semplificato)
    cat > "${USERLAND_FS_ROOT}/etc/group" << EOF
root:x:0:
users:x:100:
EOF

    # /etc/hosts
    cat > "${USERLAND_FS_ROOT}/etc/hosts" << EOF
127.0.0.1   localhost
::1         localhost ip6-localhost
EOF

    # /etc/fstab (semplificato)
    cat > "${USERLAND_FS_ROOT}/etc/fstab" << EOF
# Filesystem virtuale ONEX
none    /proc    proc    defaults    0 0
none    /sys     sysfs   defaults    0 0
EOF

    echo "File di base creati con successo."
    return 0
}

# Aggiunge un utente al filesystem virtuale
add_user_to_virtual_fs() {
    local username=$1
    local uid=$2
    
    if [ -z "$username" ] || [ -z "$uid" ]; then
        echo "Errore: nome utente o UID non specificati."
        return 1
    fi
    
    # Aggiungi l'utente a /etc/passwd
    echo "${username}:x:${uid}:${uid}:${username}:/home/${username}:/bin/bash" \
        >> "${USERLAND_FS_ROOT}/etc/passwd"
    
    # Aggiungi il gruppo dell'utente a /etc/group
    echo "${username}:x:${uid}:" >> "${USERLAND_FS_ROOT}/etc/group"
    
    # Aggiungi l'utente al gruppo users
    sed -i "/^users/ s/$/,${username}/" "${USERLAND_FS_ROOT}/etc/group"
    
    echo "Utente ${username} (UID: ${uid}) aggiunto al filesystem virtuale."
    return 0
}

# Copia file o directory nel filesystem virtuale
copy_to_virtual_fs() {
    local source=$1
    local dest=$2
    
    if [ -z "$source" ] || [ -z "$dest" ]; then
        echo "Errore: percorso sorgente o destinazione non specificati."
        return 1
    fi
    
    # Percorso completo nel filesystem virtuale
    local full_dest="${USERLAND_FS_ROOT}/${dest}"
    
    # Assicurati che la directory esista
    mkdir -p "$(dirname "${full_dest}")"
    
    # Copia il file o la directory
    cp -r "${source}" "${full_dest}"
    
    echo "Copiato ${source} in ${dest} nel filesystem virtuale."
    return 0
}

# Funzione principale
main() {
    local command=$1
    shift
    
    # Inizializza variabili
    if ! init_variables "$@"; then
        return 1
    fi
    
    case $command in
        create-fs)
            create_fs_structure
            ;;
        create-home)
            create_user_home $1
            ;;
        create-files)
            create_base_files
            ;;
        add-user)
            add_user_to_virtual_fs $1 $2
            ;;
        copy)
            copy_to_virtual_fs $1 $2
            ;;
        *)
            echo "Comando non supportato: $command"
            echo "Comandi disponibili: create-fs, create-home, create-files, add-user, copy"
            return 1
            ;;
    esac
    
    return $?
}

# Se lo script è eseguito direttamente (non importato)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -lt 2 ]; then
        echo "Utilizzo: $0 <comando> <fs_root> [argomenti...]"
        echo "Comandi disponibili: create-fs, create-home, create-files, add-user, copy"
        exit 1
    fi
    
    main $@
    exit $?
fi
