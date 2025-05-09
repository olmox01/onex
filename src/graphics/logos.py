#!/usr/bin/env python3
"""
ONEX ASCII Logos
Contiene loghi e banner ASCII che possono essere utilizzati nel sistema
"""

# Logo principale ONEX
ONEX_LOGO = """
·······························
:                             :
:       ::::::::  ::::    ::: :
:     :+:    :+: :+:+:   :+:  :
:    +:+    +:+ :+:+:+  +:+   :
:   +#+    +:+ +#+ +:+ +#+    :
:  +#+    +#+ +#+  +#+#+#     :
: #+#    #+# #+#   #+#+#      :
: ########  ###    ####       :
:       :::::::::: :::    ::: :
:      :+:        :+:    :+:  :
:     +:+         +:+  +:+    :
:    +#++:++#     +#++:+      :
:   +#+         +#+  +#+      :
:  #+#        #+#    #+#      :
: ########## ###    ###       :
:                             :
·······························
"""

# Logo ONEX miniaturizzato per spazi più ristretti
ONEX_MINI_LOGO = """
.---.
|OEX|
'---'
"""

# Banner per il boot
BOOT_BANNER = """
██████╗  ██████╗  ██████╗ ████████╗
██╔══██╗██╔═══██╗██╔═══██╗╚══██╔══╝
██████╔╝██║   ██║██║   ██║   ██║   
██╔══██╗██║   ██║██║   ██║   ██║   
██████╔╝╚██████╔╝╚██████╔╝   ██║   
╚═════╝  ╚═════╝  ╚═════╝    ╚═╝   
"""

# Banner per errori e messaggi critici
ERROR_BANNER = """
███████╗██████╗ ██████╗  ██████╗ ██████╗ 
██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗
█████╗  ██████╔╝██████╔╝██║   ██║██████╔╝
██╔══╝  ██╔══██╗██╔══██╗██║   ██║██╔══██╗
███████╗██║  ██║██║  ██║╚██████╔╝██║  ██║
╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝
"""

def print_logo(logo_type="default"):
    """
    Stampa un logo ASCII sul terminale
    
    Args:
        logo_type: Il tipo di logo da stampare ("default", "mini", "boot", "error")
    """
    if logo_type == "mini":
        print(ONEX_MINI_LOGO)
    elif logo_type == "boot":
        print(BOOT_BANNER)
    elif logo_type == "error":
        print(ERROR_BANNER)
    else:
        print(ONEX_LOGO)
