#!/bin/bash
# Name: sysinfo
# Description: Mostra informazioni sul sistema
# Version: 1.0.0
# Author: ONEX Team
# System: true

echo "=== Informazioni di Sistema ==="
echo "Hostname: $(hostname)"
echo "Sistema operativo: $(uname -s)"
echo "Kernel: $(uname -r)"
echo "Architettura: $(uname -m)"
echo "CPU: $(grep 'model name' /proc/cpuinfo | head -1 | cut -d ':' -f 2 | xargs)"
echo "Memoria totale: $(free -h | grep Mem | awk '{print $2}')"
echo "Memoria libera: $(free -h | grep Mem | awk '{print $4}')"

echo -e "\n=== Utilizzo Disco ==="
df -h / | grep -v Filesystem

echo -e "\n=== Uptime ==="
uptime
