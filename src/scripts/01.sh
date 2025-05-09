#!/bin/bash
# ONEX Script 01
# Utility per gestione sistema e esecuzione comandi privelegiati

# Verifica se lo script è eseguito con privilegi sudo
check_sudo() {
    if [ "$(id -u)" -ne 0 ]; then
        echo "Questo script richiede privilegi sudo."
        return 1
    fi
    return 0
}

# Ottiene informazioni sul sistema
get_system_info() {
    echo "=== Informazioni di Sistema ==="
    echo "Hostname: $(hostname)"
    echo "Kernel: $(uname -r)"
    echo "Architettura: $(uname -m)"
    echo "CPU: $(grep 'model name' /proc/cpuinfo | uniq | cut -d ':' -f2 | xargs)"
    echo "RAM Totale: $(free -h | grep Mem | awk '{print $2}')"
    echo "RAM Libera: $(free -h | grep Mem | awk '{print $4}')"
    echo "Spazio su disco: $(df -h / | grep / | awk '{print $4}') liberi"
    echo ""
}

# Gestisce i pacchetti Python
manage_python_packages() {
    local action=$1
    shift
    local packages=$@
    
    if [ -z "$packages" ]; then
        echo "Nessun pacchetto specificato."
        return 1
    fi
    
    case $action in
        install)
            echo "Installazione pacchetti Python: $packages"
            pip install $packages
            ;;
        update)
            echo "Aggiornamento pacchetti Python: $packages"
            pip install --upgrade $packages
            ;;
        remove)
            echo "Rimozione pacchetti Python: $packages"
            pip uninstall -y $packages
            ;;
        *)
            echo "Azione non supportata: $action"
            return 1
            ;;
    esac
    
    return $?
}

# Gestisce operazioni sui file di sistema con privilegi
system_file_operation() {
    local action=$1
    local source=$2
    local dest=$3
    
    if ! check_sudo; then
        return 1
    fi
    
    case $action in
        copy)
            echo "Copia $source in $dest"
            cp -v "$source" "$dest"
            ;;
        move)
            echo "Sposta $source in $dest"
            mv -v "$source" "$dest"
            ;;
        link)
            echo "Crea link simbolico da $source a $dest"
            ln -sv "$source" "$dest"
            ;;
        *)
            echo "Operazione non supportata: $action"
            return 1
            ;;
    esac
    
    return $?
}

# Funzione principale
main() {
    local command=$1
    shift
    
    case $command in
        info)
            get_system_info
            ;;
        package)
            manage_python_packages $@
            ;;
        file)
            system_file_operation $@
            ;;
        *)
            echo "Comando non supportato: $command"
            echo "Comandi disponibili: info, package, file"
            return 1
            ;;
    esac
    
    return $?
}

# Se lo script è eseguito direttamente (non importato)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -eq 0 ]; then
        echo "Utilizzo: $0 <comando> [argomenti...]"
        echo "Comandi disponibili: info, package, file"
        exit 1
    fi
    
    main $@
    exit $?
fi
