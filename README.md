# ARK: Survival Ascended Server Manager

A comprehensive command-line interface for managing dedicated ARK: Survival Ascended servers on Windows. This tool provides an easy-to-use menu system for configuring, running, and maintaining your ARK server.

## Features

### Server Management
- **Server Control**: Start, stop, and monitor your ARK server
- **Status Monitoring**: Check server installation status, running state, and process information
- **Automatic Configuration**: Uses saved settings for server startup parameters

### Configuration Management
- **Initial Server Settings**: Configure basic server parameters (server name, passwords, player limits, multipliers, PvE settings, etc.)
- **Frequent Multipliers**: Adjust XP rates, taming speeds, harvest amounts, breeding settings, and other gameplay multipliers
- **Settings Summary**: View detailed summaries of configuration changes with old/new value comparisons
- **Secure Password Handling**: Passwords are masked in all displays and logs

### Mod Management
- **Add/Remove Mods**: Install and manage ARK mods via CurseForge mod IDs
- **Mod Status**: View currently active mods
- **Automatic Restart Notifications**: Reminds users when server restart is required for mod changes

### Backup & Recovery
- **Automated Backups**: Create backups of your server data and configurations
- **Organized Storage**: Backups are stored in timestamped directories

### Remote Administration
- **RCON Console**: Remote console access for server administration
- **Real-time Commands**: Execute commands like `SaveWorld`, `ListPlayers`, `Broadcast`
- **Secure Authentication**: Uses configured admin password for RCON connections

### Logging & Monitoring
- **Log Viewer**: Browse and analyze server logs
- **Comprehensive Logging**: Track server events, player activity, and errors

## Prerequisites

- **Operating System**: Windows 10/11 (PowerShell)
- **Python**: Version 3.10 or newer
- **Storage**: At least 20GB free space for ARK server files
- **Network**: Stable internet connection for downloads and online play

## Installation

1. **Clone the Repository**
   ```powershell
   git clone https://github.com/kiranadhikari1/Ark-Survival-Ascended-Server-Manager.git
   cd "Ark-Survival-Ascended-Server-Manager"
   ```

2. **Run the Manager**
   ```powershell
   python manager.py
   ```

   The application will create a default base directory at `./ArkServerManager` or you can specify a custom path:
   ```powershell
   python manager.py "C:\MyArkServer"
   ```

## Usage

The application provides an interactive menu system with the following options:

1. **Install/Update Server** - Download and update ARK server files via SteamCMD
2. **Initial Server Settings** - Configure basic server parameters (one-time setup)
3. **Configure Server (Frequent Multipliers)** - Adjust gameplay multipliers and rates
4. **Manage Mods** - Add, remove, or view installed mods
5. **Start Server** - Launch the server with current configuration
6. **Stop Server** - Gracefully shut down the server
7. **Server Status** - Check installation and running status
8. **Create Backup** - Generate a backup of server data
9. **RCON Console** - Access remote console for administration
10. **View Logs** - Browse server log files
0. **Exit** - Close the application

### First-Time Setup

1. Run the manager and select option **1** to install the ARK server
2. Choose option **2** to configure initial server settings (server name, passwords, etc.)
3. Optionally configure multipliers with option **3**
4. Add mods if desired with option **4**
5. Start your server with option **5**

## Configuration Files

The manager creates and manages these configuration files in your server directory:

- `GameUserSettings.ini` - Basic server settings and multipliers
- `Game.ini` - Advanced stat multipliers and breeding settings
- `Mods.txt` - List of active mod IDs

## Security Features

- **Password Masking**: All passwords are masked with asterisks in displays and logs
- **Input Validation**: Comprehensive validation for all configuration inputs
- **Secure Defaults**: Sensible default values for all settings
- **No Data Exposure**: Sensitive information is never logged or displayed in plain text

## Project Structure

```
├── manager.py              # Main CLI application and menu system
├── core/
│   ├── config.py           # Configuration file management
│   ├── server.py           # Server process control
│   ├── steamcmd.py         # SteamCMD integration
│   ├── backup.py           # Backup functionality
│   └── rcon.py             # Remote console client
├── utils/
│   ├── constants.py        # Application constants
│   ├── validation.py       # Input validation utilities
│   └── log_viewer.py       # Log file viewer
└── steamcmd/               # SteamCMD wrapper utilities
```

## Troubleshooting

### Server Won't Start
- Ensure all configuration is complete (options 1-2 in menu)
- Check that ports 7777 (game) and 27015 (query) are available
- Verify sufficient RAM (8GB+ recommended)

### RCON Connection Issues
- Ensure RCON is enabled in server settings
- Verify admin password is configured
- Check that server is running and ports are accessible

### Mod Installation Problems
- Use CurseForge mod IDs (numbers only)
- Server restart is required after mod changes
- Check server logs for mod-related errors

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes with clear commit messages
4. Test thoroughly on Windows
5. Submit a pull request

### Development Guidelines
- Follow existing code style and patterns
- Add input validation for new features
- Include docstrings for new methods
- Test on clean Windows environment
- Ensure no sensitive data exposure

## License

This project is open-source and available under standard open-source licensing terms.

## Disclaimer

This tool is not officially affiliated with Studio Wildcard or ARK: Survival Ascended. Use at your own risk and ensure compliance with ARK's terms of service.