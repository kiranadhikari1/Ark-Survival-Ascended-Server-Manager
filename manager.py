"""
ARK: Survival Ascended Dedicated Server Manager
Main entry point and CLI interface
"""

import sys
from pathlib import Path

from core.config import ServerConfig
from core.steamcmd import SteamCMDManager
from core.server import ServerController
from core.backup import BackupManager
from core.rcon import RCONClient
from utils.validation import input_int, input_float, validate_strong_password, sanitize_input
from utils.constants import (
    DEFAULT_GAME_PORT, DEFAULT_QUERY_PORT, 
    MIN_PASSWORD_LENGTH, MAX_PASSWORD_LENGTH,
    MAX_SERVER_NAME_LENGTH
)


class ServerManager:
    """Main server manager interface"""
    
    def __init__(self, base_dir: str = "./ArkServerManager"):
        self.base_dir = Path(base_dir).resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.steamcmd = SteamCMDManager(self.base_dir)
        self.config = ServerConfig(self.steamcmd.server_dir)
        self.controller = ServerController(self.steamcmd.server_dir)
        self.backup = BackupManager(self.steamcmd.server_dir, self.base_dir)
    
    def show_menu(self):
        print("\n" + "="*60)
        print("ARK: Survival Ascended Server Manager (Phase 1)")
        print("="*60)
        print("1. Install/Update Server")
        print("2. Configure Server Settings")
        print("3. Configure Stat Multipliers")
        print("4. Manage Mods")
        print("5. Start Server")
        print("6. Stop Server")
        print("7. Server Status")
        print("8. Create Backup")
        print("9. RCON Console")
        print("10. View Logs")
        print("0. Exit")
        print("="*60)
    
    def run(self):
        print("\nWelcome to ARK Server Manager")
        print(f"Base directory: {self.base_dir}\n")
        
        while True:
            self.show_menu()
            choice = input("\nSelect option: ").strip()
            
            if choice == '1':
                self.install_update_server()
            elif choice == '2':
                self.configure_server()
            elif choice == '3':
                self.configure_stats()
            elif choice == '4':
                self.manage_mods()
            elif choice == '5':
                self.start_server()
            elif choice == '6':
                self.controller.stop_server()
            elif choice == '7':
                self.show_status()
            elif choice == '8':
                self.backup.create_backup()
            elif choice == '9':
                self.rcon_console()
            elif choice == '10':
                self.view_logs()
            elif choice == '0':
                self._shutdown()
                break
            else:
                print("Invalid option")
            
            input("\nPress Enter to continue...")
    
    def install_update_server(self):
        print("\n=== Install/Update Server ===")
        force = input("Force validate? (y/n): ").lower() == 'y'
        self.steamcmd.install_or_update(force_update=force)
    
    def configure_server(self):
        print("\n=== Server Configuration ===")
        
        settings = {}
        server_name = input("Server Name [ARK Server]: ").strip()
        settings['server_name'] = sanitize_input(
            server_name or "ARK Server", 
            max_length=MAX_SERVER_NAME_LENGTH
        )
        
        settings['max_players'] = input_int("Max Players [10]: ", default=10)
        
        server_password = input("Server Password (optional, Enter to skip): ").strip()
        if server_password:
            settings['server_password'] = sanitize_input(
                server_password, 
                max_length=MAX_PASSWORD_LENGTH
            )
        
        while True:
            admin_password = input("Admin Password (required, min 8 chars): ").strip()
            if validate_strong_password(admin_password):
                settings['admin_password'] = sanitize_input(
                    admin_password,
                    max_length=MAX_PASSWORD_LENGTH
                )
                break
            else:
                print(f"Password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters")
        
        settings['xp_multiplier'] = input_float("XP Multiplier [1.0]: ", default=1.0)
        settings['taming_speed'] = input_float("Taming Speed [1.0]: ", default=1.0)
        settings['harvest_amount'] = input_float("Harvest Amount [1.0]: ", default=1.0)
        settings['difficulty_offset'] = input_float("Difficulty Offset [0.2]: ", default=0.2)
        
        pve = input("PvE Mode? (y/n) [y]: ").lower()
        settings['pve_mode'] = pve != 'n'
        
        self.config.update_game_settings(settings)
    
    def configure_stats(self):
        print("\n=== Stat Multipliers (Phase 1 - Basic) ===")
        print("Leave blank to skip a multiplier\n")
        
        settings = {}
        
        print("--- Player Stats ---")
        if input("Configure player health? (y/n): ").lower() == 'y':
            settings['player_health_mult'] = input_float("Player Health per level [1.0]: ", default=1.0)
        
        if input("Configure player stamina? (y/n): ").lower() == 'y':
            settings['player_stamina_mult'] = input_float("Player Stamina per level [1.0]: ", default=1.0)
        
        if input("Configure player weight? (y/n): ").lower() == 'y':
            settings['player_weight_mult'] = input_float("Player Weight per level [1.0]: ", default=1.0)
        
        print("\n--- Dino Stats ---")
        if input("Configure dino health? (y/n): ").lower() == 'y':
            settings['dino_health_mult'] = input_float("Dino Health per level [1.0]: ", default=1.0)
        
        if input("Configure dino stamina? (y/n): ").lower() == 'y':
            settings['dino_stamina_mult'] = input_float("Dino Stamina per level [1.0]: ", default=1.0)
        
        if input("Configure dino weight? (y/n): ").lower() == 'y':
            settings['dino_weight_mult'] = input_float("Dino Weight per level [1.0]: ", default=1.0)
        
        if settings:
            self.config.update_stat_multipliers(settings)
            print("✓ Stat multipliers configured")
        else:
            print("No changes made")
    
    def manage_mods(self):
        print("\n=== Mod Management ===")
        
        current_mods = self.config.get_active_mods()
        if current_mods:
            print(f"Current mods: {', '.join(current_mods)}")
        else:
            print("No mods currently active")
        
        print("\nOptions:")
        print("1. Add/Replace mods")
        print("2. Remove all mods")
        print("3. Cancel")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1':
            print("\nEnter mod IDs (comma-separated, CurseForge)")
            mod_input = input("Mod IDs: ")
            
            if mod_input:
                mod_ids = [m.strip() for m in mod_input.split(',')]
                if self.config.set_mods(mod_ids):
                    print("NOTE: Server restart required for mod changes")
        
        elif choice == '2':
            confirm = input("Remove all mods? (y/n): ").lower()
            if confirm == 'y':
                self.config.clear_mods()
                print("NOTE: Server restart required for mod changes")
        
        else:
            print("Cancelled")
    
    def start_server(self):
        print("\n=== Start Server ===")
        map_name = input("Map Name [TheIsland_WP]: ") or "TheIsland_WP"
        game_port = input_int(f"Game Port [{DEFAULT_GAME_PORT}]: ", default=DEFAULT_GAME_PORT)
        query_port = input_int(f"Query Port [{DEFAULT_QUERY_PORT}]: ", default=DEFAULT_QUERY_PORT)
        
        self.controller.start(map_name, game_port, query_port)
    
    def show_status(self):
        print("\n=== Server Status ===")
        print(f"Server installed: {self.controller.is_installed()}")
        print(f"Server running: {self.controller.is_running()}")
        
        if self.controller.is_running():
            print(f"Process ID: {self.controller.get_pid()}")
        
        mods = self.config.get_active_mods()
        if mods:
            print(f"Active mods: {', '.join(mods)}")
    
    def rcon_console(self):
        print("\n=== RCON Console ===")
        print("WARNING: RCON must be enabled in server settings")
        print("         Requires strong password (min 8 characters)")
        
        password = input("RCON Password: ")
        
        if not validate_strong_password(password):
            print(f"ERROR: Password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters")
            return
        
        rcon = RCONClient(password=password)
        if not rcon.connect():
            print("Connection failed. Ensure:")
            print("  1. Server is running")
            print("  2. RCON is enabled in server settings")
            print("  3. Password is correct")
            return
        
        print("✓ Connected. Type 'exit' to quit.")
        print("Common commands: SaveWorld, ListPlayers, Broadcast <message>")
        
        while True:
            cmd = input("RCON> ")
            if cmd.lower() == 'exit':
                break
            
            if not cmd.strip():
                continue
            
            response = rcon.send_command(cmd)
            if response:
                print(response)
        
        rcon.disconnect()
    
    def view_logs(self):
        from utils.log_viewer import LogViewer
        viewer = LogViewer(self.steamcmd.server_dir)
        viewer.show()
    
    def _shutdown(self):
        print("\nShutting down...")
        if self.controller.is_running():
            self.controller.stop()
        print("Goodbye!")


def main():
    print("ARK: Survival Ascended Dedicated Server Manager")
    print("Phase 1 - Minimal Secure Implementation")
    print("="*60)
    
    base_dir = sys.argv[1] if len(sys.argv) > 1 else "./ArkServerManager"
    
    try:
        manager = ServerManager(base_dir)
        manager.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()