


       N E X S   O S


# ONEX – A Simulated Userland for Linux Terminals

## Overview

**ONEX** is a project that conjures up a fully simulated userland environment right within your Linux terminal. Think of it as a playful yet powerful mini-operating system that lives inside your terminal session, complete with its own virtual filesystem, an interactive file manager, and a curses-based user interface that’s both retro and refined.

## Key Features

* **Simulated Environment**: Dive into an interactive shell experience with a self-contained filesystem.
* **File Manager**: Navigate and manage your files through a snappy TUI (Text User Interface).
* **Virtual Filesystem**: A UNIX-style structure with mount points linking to your actual filesystem—think of it as a sandbox with a door.
* **User Management**: Authentication and user profiles add a dash of realism.
* **Shell Compatibility**: Plays nicely with your favorite Linux shells.
* **Terminal UI**: Powered by curses—classic vibes, modern purpose.

## System Requirements

* Python 3.6 or higher
* A Linux-based OS
* Required libraries (automagically installed by the bootloader):

  * `curses`
  * `pyfiglet`
  * `psutil`
  * `questionary`
  * `colorama`
  * `pillow`
  * `tqdm`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/onex.git
   cd onex
   ```

2. Launch the system:

   ```bash
   python run.py
   ```

The bootloader will handle dependency checks and installations for you, like your own personal sysadmin elf.

## Project Structure

```
/onex/
├── run.py                     # Main entry point
├── README.md                  # Documentation, this very guide!
├── bootloader/
│   └── boot.py                # Startup handler
├── src/
│   ├── main.py                # System coordinator
│   ├── graphics/
│   │   ├── ui.py              # User interface layer
│   │   └── graphics.py        # Graphic utilities
│   ├── scripts/
│   │   ├── 01.sh              # System utility scripts
│   │   └── 02.sh              # Virtual filesystem management
│   ├── system/
│   │   ├── shell_compatibility.py  # Shell integration layer
│   │   └── input.py           # User input handling
│   └── userland/
│       ├── userland.py        # Core userland system
│       └── file_manager.py    # Interactive file manager
└── userland_fs/               # The simulated filesystem
    ├── bin/
    ├── etc/
    ├── home/
    ├── usr/
    ├── var/
    ├── tmp/
    └── mnt/
        └── system/            # Mount point for the real filesystem
```

## Usage

Once ONEX is up and running, you're ready to engage with your simulated shell environment:

1. **Navigation**: Use familiar commands like `cd`, `ls`, etc.
2. **File Manager**: Type `run filemanager` to launch the interactive file explorer.
3. **Program Execution**: Run executables just like in any real Linux setup.
4. **System Utilities**: A suite of built-in commands for managing your simulated world.
5. **Exit**: Type `exit` to gracefully shut down the experience (sad, but necessary).

## File Manager

The TUI file manager responds to your keystrokes with old-school flair:

* **Arrow Keys**: Move around files and directories
* **Enter**: Open a file or step into a directory
* **Esc/Backspace**: Move up one directory
* **F5**: Refresh the view (always satisfying)
* **F1**: Summon help (you’re not alone!)
* **F10** or **Q**: Exit the file manager

## System Architecture

1. **Boot Process**:

   * `run.py` → `bootloader/boot.py` → `src/main.py` → `src/userland/userland.py`

2. **Execution Flow**:

   * Check environment and permissions
   * Detect system and current user
   * Install any missing dependencies
   * Initialize the virtual filesystem
   * Launch userland
   * Engage with the user

3. **Virtual Filesystem**:

   * UNIX-like directory hierarchy
   * Everything lives inside `userland_fs`
   * Mount point for real system access included

## Development

Want to contribute? We welcome your magic:

1. Fork the repository
2. Create your feature branch

   ```bash
   git checkout -b feature/amazing-feature
   ```
3. Commit your changes

   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. Push to your branch

   ```bash
   git push origin feature/amazing-feature
   ```
5. Open a Pull Request — and voila!
