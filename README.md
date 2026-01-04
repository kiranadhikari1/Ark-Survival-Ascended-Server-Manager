# Ark Survival Ascended Server Manager
Simple GUI for hosting your own dedicated Ark: Survival Ascended dedicated server.

A lightweight project that provides helpers and a minimal GUI to configure, run, and manage a dedicated Ark server locally. The codebase contains server management logic in `core/`, SteamCMD helpers in `steamcmd/`, and utility modules in `utils/`.

**Features**
- **Start/stop server:** Basic management for launching and stopping the game server via `manager.py`.
- **Backup helpers:** Utilities for creating/restoring server backups (`core/backup.py`).
- **RCON support:** Remote console support for server commands (`core/rcon.py`).
- **SteamCMD integration:** Helpers to download/update server files (`steamcmd/`).

**Prerequisites**
- **Python:** 3.10 or newer recommended.
- **OS:** Tested on Windows (PowerShell). Other platforms may work but commands in this README assume Windows.

**Quick Install**
Clone the repository:

```powershell
git clone https://github.com/kiranadhikari1/Ark-Survival-Ascended-Server-Manager.git
cd "Ark-Survival-Ascended-Server-Manager"
```

**Running the Manager**
Run the main manager script to open the GUI or start the management workflow:

```powershell
python manager.py
```

Depending on the implementation, the script may open a GUI window or provide a command-line interface. See `core/config.py` for configuration options and `core/server.py` for server-launch parameters.

**Configuration**
- Default configuration and constants are located in `core/config.py` and `utils/constants.py`.
- Edit these files or provide environment variables if supported by the code.

**Development**
- Project layout:
	- `manager.py` — entry point
	- `core/` — server logic, rcon, backup, config
	- `steamcmd/` — SteamCMD helpers
	- `utils/` — helper utilities and validators
- Run code with the virtual environment active and use your editor's linter/formatter.

**Contributing**
- Open an issue to discuss larger changes before implementing them.
- Submit pull requests against `main` with focused changes and clear commit messages.
- Keep code style consistent with existing files and add tests where applicable.

**License & Acknowledgements**
- This project is open-source and free to use.