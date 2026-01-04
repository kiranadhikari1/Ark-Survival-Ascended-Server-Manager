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
        
        current_name = self.config.get_server_name()
        current_settings = self.config.get_server_settings()
        
        settings = {}
        
        # Server name
        server_name = input(f"Server Name [{current_name}]: ").strip()
        if server_name:
            settings['server_name'] = sanitize_input(server_name, max_length=MAX_SERVER_NAME_LENGTH)
        
        # Max players
        current_max = current_settings.get('max_players', 10)
        max_players = input_int(f"Max Players [{current_max}]: ", default=current_max)
        if max_players != current_max:
            settings['max_players'] = max_players
        
        # Server password
        server_password = input("Server Password (optional, Enter to skip): ").strip()
        if server_password:
            settings['server_password'] = sanitize_input(server_password, max_length=MAX_PASSWORD_LENGTH)
        elif current_settings.get('server_password'):
            # Keep existing password if not changing
            settings['server_password'] = current_settings['server_password']
        
        # Admin password (required)
        current_admin = current_settings.get('admin_password', '')
        while True:
            admin_password = input(f"Admin Password [{current_admin or 'required'}]: ").strip()
            if not admin_password and current_admin:
                # Keep existing password
                settings['admin_password'] = current_admin
                break
            elif validate_strong_password(admin_password):
                settings['admin_password'] = sanitize_input(admin_password, max_length=MAX_PASSWORD_LENGTH)
                break
            else:
                print(f"Password must be {MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH} characters")
        
        # XP Multiplier
        current_xp = current_settings.get('xp_multiplier', 1.0)
        xp_multiplier = input_float(f"XP Multiplier [{current_xp}]: ", default=current_xp)
        if xp_multiplier != current_xp:
            settings['xp_multiplier'] = xp_multiplier
        
        # Taming Speed
        current_taming = current_settings.get('taming_speed', 1.0)
        taming_speed = input_float(f"Taming Speed [{current_taming}]: ", default=current_taming)
        if taming_speed != current_taming:
            settings['taming_speed'] = taming_speed
        
        # Harvest Amount
        current_harvest = current_settings.get('harvest_amount', 1.0)
        harvest_amount = input_float(f"Harvest Amount [{current_harvest}]: ", default=current_harvest)
        if harvest_amount != current_harvest:
            settings['harvest_amount'] = harvest_amount
        
        # Difficulty Offset
        current_difficulty = current_settings.get('difficulty_offset', 0.2)
        difficulty_offset = input_float(f"Difficulty Offset [{current_difficulty}]: ", default=current_difficulty)
        if difficulty_offset != current_difficulty:
            settings['difficulty_offset'] = difficulty_offset
        
        # PvE Mode
        current_pve = current_settings.get('pve_mode', True)
        pve_input = input(f"PvE Mode? (y/n) [{'y' if current_pve else 'n'}]: ").lower()
        if pve_input in ['y', 'n']:
            settings['pve_mode'] = pve_input == 'y'
        
        if settings:
            self.config.update_game_settings(settings)
            print("✓ Server settings updated")
        else:
            print("No changes made")
    
    def configure_stats(self):
        print("\n=== Stat Multipliers (Phase 1 - Basic) ===")
        print("Current values shown in brackets. Press Enter to keep current value.\n")
        
        current_stats = self.config.get_stat_multipliers()
        settings = {}
        
        print("--- Player Stats ---")
        
        current_health = current_stats.get('player_health_mult', 1.0)
        health_input = input(f"Player Health per level [{current_health}]: ").strip()
        if health_input:
            settings['player_health_mult'] = input_float("", default=float(health_input))
        elif current_health != 1.0:
            # Keep current value
            settings['player_health_mult'] = current_health
        
        current_stamina = current_stats.get('player_stamina_mult', 1.0)
        stamina_input = input(f"Player Stamina per level [{current_stamina}]: ").strip()
        if stamina_input:
            settings['player_stamina_mult'] = input_float("", default=float(stamina_input))
        elif current_stamina != 1.0:
            settings['player_stamina_mult'] = current_stamina
        
        current_weight = current_stats.get('player_weight_mult', 1.0)
        weight_input = input(f"Player Weight per level [{current_weight}]: ").strip()
        if weight_input:
            settings['player_weight_mult'] = input_float("", default=float(weight_input))
        elif current_weight != 1.0:
            settings['player_weight_mult'] = current_weight
        
        print("\n--- Dino Stats ---")
        
        current_dino_health = current_stats.get('dino_health_mult', 1.0)
        dino_health_input = input(f"Dino Health per level [{current_dino_health}]: ").strip()
        if dino_health_input:
            settings['dino_health_mult'] = input_float("", default=float(dino_health_input))
        elif current_dino_health != 1.0:
            settings['dino_health_mult'] = current_dino_health
        
        current_dino_stamina = current_stats.get('dino_stamina_mult', 1.0)
        dino_stamina_input = input(f"Dino Stamina per level [{current_dino_stamina}]: ").strip()
        if dino_stamina_input:
            settings['dino_stamina_mult'] = input_float("", default=float(dino_stamina_input))
        elif current_dino_stamina != 1.0:
            settings['dino_stamina_mult'] = current_dino_stamina
        
        current_dino_weight = current_stats.get('dino_weight_mult', 1.0)
        dino_weight_input = input(f"Dino Weight per level [{current_dino_weight}]: ").strip()
        if dino_weight_input:
            settings['dino_weight_mult'] = input_float("", default=float(dino_weight_input))
        elif current_dino_weight != 1.0:
            settings['dino_weight_mult'] = current_dino_weight
        
        if settings:
            self.config.update_stat_multipliers(settings)
            print("✓ Stat multipliers updated")
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
        max_players = input_int("Max Players: ", default=10)
        
        self.controller.start(map_name, game_port, query_port, max_players)
    
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