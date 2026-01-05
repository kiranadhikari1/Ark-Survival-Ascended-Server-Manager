"""
ARK: Survival Ascended Dedicated Server Manager
Main entry point and CLI interface
"""

import sys
import time
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
        self.rcon = RCONClient()
    
    def show_menu(self):
        print("\n" + "="*60)
        print("ARK: Survival Ascended Server Manager")
        print("="*60)
        print("1. Install/Update Server")
        print("2. Initial Server Settings")
        print("3. Configure Server (Frequent Multipliers)")
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
                self.configure_initial_server()
            elif choice == '3':
                self.configure_server()
            elif choice == '4':
                self.manage_mods()
            elif choice == '5':
                self.start_server()
            elif choice == '6':
                self.stop_server()
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
    
    def configure_initial_server(self):
        print("\n=== Initial Server Settings (One-time Setup) ===")
        print("These settings are typically set once and rarely changed.")
        
        current_settings = self.config.get_server_settings()
        settings = {}
        
        # Server name
        current_name = self.config.get_server_name()
        server_name = input(f"Server Name [{current_name}]: ").strip()
        if server_name:
            settings['server_name'] = sanitize_input(server_name, max_length=MAX_SERVER_NAME_LENGTH)
        
        # Max players
        current_max = current_settings.get('max_players', 70)
        max_players = input_int(f"Max Players [{current_max}]: ", default=current_max)
        if max_players != current_max:
            settings['max_players'] = max_players
        
        # Server password
        current_password = current_settings.get('server_password', '')
        server_password = input(f"Server Password (optional) [{'*' * len(current_password) if current_password else 'none'}]: ").strip()
        if server_password and server_password != current_password:
            settings['server_password'] = sanitize_input(server_password, max_length=MAX_PASSWORD_LENGTH)
        
        # Admin password
        current_admin = current_settings.get('admin_password', '')
        admin_password = input(f"Admin Password (required) [{'*' * len(current_admin) if current_admin else 'none'}]: ").strip()
        if admin_password and admin_password != current_admin:
            settings['admin_password'] = sanitize_input(admin_password, max_length=MAX_PASSWORD_LENGTH)
        
        # Boolean settings
        current_allow_imprint = current_settings.get('allow_anyone_baby_imprint', False)
        allow_imprint = input(f"Allow Anyone Baby Imprint Cuddle? (y/n) [{'y' if current_allow_imprint else 'n'}]: ").lower()
        if allow_imprint in ['y', 'n']:
            settings['allow_anyone_baby_imprint'] = allow_imprint == 'y'
        
        current_cave_building = current_settings.get('allow_cave_building_pve', False)
        cave_building = input(f"Allow Cave Building PvE? (y/n) [{'y' if current_cave_building else 'n'}]: ").lower()
        if cave_building in ['y', 'n']:
            settings['allow_cave_building_pve'] = cave_building == 'y'
        
        current_flyer_carry = current_settings.get('allow_flyer_carry_pve', False)
        flyer_carry = input(f"Allow Flyer Carry PvE? (y/n) [{'y' if current_flyer_carry else 'n'}]: ").lower()
        if flyer_carry in ['y', 'n']:
            settings['allow_flyer_carry_pve'] = flyer_carry == 'y'
        
        current_structure_pickup = current_settings.get('always_allow_structure_pickup', False)
        structure_pickup = input(f"Always Allow Structure Pickup? (y/n) [{'y' if current_structure_pickup else 'n'}]: ").lower()
        if structure_pickup in ['y', 'n']:
            settings['always_allow_structure_pickup'] = structure_pickup == 'y'
        
        current_notify_left = current_settings.get('always_notify_player_left', False)
        notify_left = input(f"Always Notify Player Left? (y/n) [{'y' if current_notify_left else 'n'}]: ").lower()
        if notify_left in ['y', 'n']:
            settings['always_notify_player_left'] = notify_left == 'y'
        
        # Dino count multiplier
        current_dino_count = current_settings.get('dino_count_multiplier', 1.0)
        dino_count = input_float(f"Dino Count Multiplier [{current_dino_count}]: ", default=current_dino_count)
        if dino_count != current_dino_count:
            settings['dino_count_multiplier'] = dino_count
        
        # Global voice chat
        current_voice = current_settings.get('global_voice_chat', False)
        voice_chat = input(f"Global Voice Chat? (y/n) [{'y' if current_voice else 'n'}]: ").lower()
        if voice_chat in ['y', 'n']:
            settings['global_voice_chat'] = voice_chat == 'y'
        
        # Player multipliers
        current_stamina_drain = current_settings.get('player_stamina_drain', 1.0)
        stamina_drain = input_float(f"Player Stamina Drain Multiplier [{current_stamina_drain}]: ", default=current_stamina_drain)
        if stamina_drain != current_stamina_drain:
            settings['player_stamina_drain'] = stamina_drain
        
        current_water_drain = current_settings.get('player_water_drain', 1.0)
        water_drain = input_float(f"Player Water Drain Multiplier [{current_water_drain}]: ", default=current_water_drain)
        if water_drain != current_water_drain:
            settings['player_water_drain'] = water_drain
        
        # More boolean settings
        current_structures_drops = current_settings.get('pve_allow_structures_at_drops', False)
        structures_drops = input(f"PvE Allow Structures At Supply Drops? (y/n) [{'y' if current_structures_drops else 'n'}]: ").lower()
        if structures_drops in ['y', 'n']:
            settings['pve_allow_structures_at_drops'] = structures_drops == 'y'
        
        current_random_crates = current_settings.get('random_supply_crate_points', False)
        random_crates = input(f"Random Supply Crate Points? (y/n) [{'y' if current_random_crates else 'n'}]: ").lower()
        if random_crates in ['y', 'n']:
            settings['random_supply_crate_points'] = random_crates == 'y'
        
        current_floating_damage = current_settings.get('show_floating_damage', False)
        floating_damage = input(f"Show Floating Damage Text? (y/n) [{'y' if current_floating_damage else 'n'}]: ").lower()
        if floating_damage in ['y', 'n']:
            settings['show_floating_damage'] = floating_damage == 'y'
        
        current_cryopod_nerf = current_settings.get('enable_cryopod_nerf', False)
        cryopod_nerf = input(f"Enable Cryopod Nerf? (y/n) [{'y' if current_cryopod_nerf else 'n'}]: ").lower()
        if cryopod_nerf in ['y', 'n']:
            settings['enable_cryopod_nerf'] = cryopod_nerf == 'y'
        
        # Upload/download prevention settings
        current_no_tribute = current_settings.get('no_tribute_downloads', False)
        no_tribute = input(f"No Tribute Downloads? (y/n) [{'y' if current_no_tribute else 'n'}]: ").lower()
        if no_tribute in ['y', 'n']:
            settings['no_tribute_downloads'] = no_tribute == 'y'
        
        current_prevent_download_dinos = current_settings.get('prevent_download_dinos', False)
        prevent_download_dinos = input(f"Prevent Download Dinos? (y/n) [{'y' if current_prevent_download_dinos else 'n'}]: ").lower()
        if prevent_download_dinos in ['y', 'n']:
            settings['prevent_download_dinos'] = prevent_download_dinos == 'y'
        
        current_prevent_download_items = current_settings.get('prevent_download_items', False)
        prevent_download_items = input(f"Prevent Download Items? (y/n) [{'y' if current_prevent_download_items else 'n'}]: ").lower()
        if prevent_download_items in ['y', 'n']:
            settings['prevent_download_items'] = prevent_download_items == 'y'
        
        current_prevent_download_survivors = current_settings.get('prevent_download_survivors', False)
        prevent_download_survivors = input(f"Prevent Download Survivors? (y/n) [{'y' if current_prevent_download_survivors else 'n'}]: ").lower()
        if prevent_download_survivors in ['y', 'n']:
            settings['prevent_download_survivors'] = prevent_download_survivors == 'y'
        
        current_prevent_upload_dinos = current_settings.get('prevent_upload_dinos', False)
        prevent_upload_dinos = input(f"Prevent Upload Dinos? (y/n) [{'y' if current_prevent_upload_dinos else 'n'}]: ").lower()
        if prevent_upload_dinos in ['y', 'n']:
            settings['prevent_upload_dinos'] = prevent_upload_dinos == 'y'
        
        current_prevent_upload_items = current_settings.get('prevent_upload_items', False)
        prevent_upload_items = input(f"Prevent Upload Items? (y/n) [{'y' if current_prevent_upload_items else 'n'}]: ").lower()
        if prevent_upload_items in ['y', 'n']:
            settings['prevent_upload_items'] = prevent_upload_items == 'y'
        
        current_prevent_upload_survivors = current_settings.get('prevent_upload_survivors', False)
        prevent_upload_survivors = input(f"Prevent Upload Survivors? (y/n) [{'y' if current_prevent_upload_survivors else 'n'}]: ").lower()
        if prevent_upload_survivors in ['y', 'n']:
            settings['prevent_upload_survivors'] = prevent_upload_survivors == 'y'
        
        if settings:
            self.config.update_game_settings(settings)
            print("✓ Initial server settings updated")
        else:
            print("No changes made")
    
    def configure_server(self):
        print("\n=== Configure Server (Frequent Multipliers) ===")
        print("Current values shown in brackets. Press Enter to keep current value.")
        
        current_settings = self.config.get_server_settings()
        current_stats = self.config.get_stat_multipliers()
        settings = {}
        
        # XP Multiplier
        current_xp = current_settings.get('xp_multiplier', 1.0)
        xp_multiplier = input_float(f"XP Multiplier [{current_xp}]: ", default=current_xp)
        if xp_multiplier != current_xp:
            settings['xp_multiplier'] = xp_multiplier
        
        # Taming Speed
        current_taming = current_settings.get('taming_speed', 1.0)
        taming_speed = input_float(f"Taming Speed Multiplier [{current_taming}]: ", default=current_taming)
        if taming_speed != current_taming:
            settings['taming_speed'] = taming_speed
        
        # Harvest Amount
        current_harvest = current_settings.get('harvest_amount', 1.0)
        harvest_amount = input_float(f"Harvest Amount Multiplier [{current_harvest}]: ", default=current_harvest)
        if harvest_amount != current_harvest:
            settings['harvest_amount'] = harvest_amount
        
        # Baby Cuddle Interval
        current_cuddle = current_stats.get('baby_cuddle_interval', 1.0)
        cuddle_input = input(f"Baby Cuddle Interval Multiplier [{current_cuddle}]: ").strip()
        if cuddle_input:
            settings['baby_cuddle_interval'] = input_float("", default=float(cuddle_input))
        elif current_cuddle != 1.0:
            settings['baby_cuddle_interval'] = current_cuddle
        
        # Baby Food Consumption
        current_food = current_stats.get('baby_food_consumption', 1.0)
        food_input = input(f"Baby Food Consumption Speed Multiplier [{current_food}]: ").strip()
        if food_input:
            settings['baby_food_consumption'] = input_float("", default=float(food_input))
        elif current_food != 1.0:
            settings['baby_food_consumption'] = current_food
        
        # Baby Imprint Amount
        current_imprint = current_stats.get('baby_imprint_amount', 1.0)
        imprint_input = input(f"Baby Imprint Amount Multiplier [{current_imprint}]: ").strip()
        if imprint_input:
            settings['baby_imprint_amount'] = input_float("", default=float(imprint_input))
        elif current_imprint != 1.0:
            settings['baby_imprint_amount'] = current_imprint
        
        # Baby Mature Speed
        current_mature = current_stats.get('baby_mature_speed', 1.0)
        mature_input = input(f"Baby Mature Speed Multiplier [{current_mature}]: ").strip()
        if mature_input:
            settings['baby_mature_speed'] = input_float("", default=float(mature_input))
        elif current_mature != 1.0:
            settings['baby_mature_speed'] = current_mature
        
        # Craft XP
        current_craft_xp = current_stats.get('craft_xp', 1.0)
        craft_xp_input = input(f"Craft XP Multiplier [{current_craft_xp}]: ").strip()
        if craft_xp_input:
            settings['craft_xp'] = input_float("", default=float(craft_xp_input))
        elif current_craft_xp != 1.0:
            settings['craft_xp'] = current_craft_xp
        
        # Crop Decay Speed
        current_decay = current_stats.get('crop_decay_speed', 1.0)
        decay_input = input(f"Crop Decay Speed Multiplier [{current_decay}]: ").strip()
        if decay_input:
            settings['crop_decay_speed'] = input_float("", default=float(decay_input))
        elif current_decay != 1.0:
            settings['crop_decay_speed'] = current_decay
        
        # Crop Growth Speed
        current_growth = current_stats.get('crop_growth_speed', 1.0)
        growth_input = input(f"Crop Growth Speed Multiplier [{current_growth}]: ").strip()
        if growth_input:
            settings['crop_growth_speed'] = input_float("", default=float(growth_input))
        elif current_growth != 1.0:
            settings['crop_growth_speed'] = current_growth
        
        # Egg Hatch Speed
        current_hatch = current_stats.get('egg_hatch_speed', 1.0)
        hatch_input = input(f"Egg Hatch Speed Multiplier [{current_hatch}]: ").strip()
        if hatch_input:
            settings['egg_hatch_speed'] = input_float("", default=float(hatch_input))
        elif current_hatch != 1.0:
            settings['egg_hatch_speed'] = current_hatch
        
        # Generic XP
        current_generic_xp = current_stats.get('generic_xp', 1.0)
        generic_xp_input = input(f"Generic XP Multiplier [{current_generic_xp}]: ").strip()
        if generic_xp_input:
            settings['generic_xp'] = input_float("", default=float(generic_xp_input))
        elif current_generic_xp != 1.0:
            settings['generic_xp'] = current_generic_xp
        
        # Harvest XP
        current_harvest_xp = current_stats.get('harvest_xp', 1.0)
        harvest_xp_input = input(f"Harvest XP Multiplier [{current_harvest_xp}]: ").strip()
        if harvest_xp_input:
            settings['harvest_xp'] = input_float("", default=float(harvest_xp_input))
        elif current_harvest_xp != 1.0:
            settings['harvest_xp'] = current_harvest_xp
        
        # Kill XP
        current_kill_xp = current_stats.get('kill_xp', 1.0)
        kill_xp_input = input(f"Kill XP Multiplier [{current_kill_xp}]: ").strip()
        if kill_xp_input:
            settings['kill_xp'] = input_float("", default=float(kill_xp_input))
        elif current_kill_xp != 1.0:
            settings['kill_xp'] = current_kill_xp
        
        # Lay Egg Interval
        current_lay_interval = current_stats.get('lay_egg_interval', 1.0)
        lay_input = input(f"Lay Egg Interval Multiplier [{current_lay_interval}]: ").strip()
        if lay_input:
            settings['lay_egg_interval'] = input_float("", default=float(lay_input))
        elif current_lay_interval != 1.0:
            settings['lay_egg_interval'] = current_lay_interval
        
        # Mating Interval
        current_mating_interval = current_stats.get('mating_interval', 1.0)
        mating_int_input = input(f"Mating Interval Multiplier [{current_mating_interval}]: ").strip()
        if mating_int_input:
            settings['mating_interval'] = input_float("", default=float(mating_int_input))
        elif current_mating_interval != 1.0:
            settings['mating_interval'] = current_mating_interval
        
        # Mating Speed
        current_mating_speed = current_stats.get('mating_speed', 1.0)
        mating_speed_input = input(f"Mating Speed Multiplier [{current_mating_speed}]: ").strip()
        if mating_speed_input:
            settings['mating_speed'] = input_float("", default=float(mating_speed_input))
        elif current_mating_speed != 1.0:
            settings['mating_speed'] = current_mating_speed
        
        if settings:
            # Split settings between GameUserSettings.ini and Game.ini
            game_user_settings = {}
            game_ini_settings = {}
            
            # GameUserSettings.ini settings
            if 'xp_multiplier' in settings:
                game_user_settings['xp_multiplier'] = settings['xp_multiplier']
            if 'taming_speed' in settings:
                game_user_settings['taming_speed'] = settings['taming_speed']
            if 'harvest_amount' in settings:
                game_user_settings['harvest_amount'] = settings['harvest_amount']
            
            # Game.ini settings (all the multipliers)
            game_ini_keys = [
                'baby_cuddle_interval', 'baby_food_consumption', 'baby_imprint_amount', 'baby_mature_speed',
                'craft_xp', 'crop_decay_speed', 'crop_growth_speed', 'egg_hatch_speed', 'generic_xp',
                'harvest_xp', 'kill_xp', 'lay_egg_interval', 'mating_interval', 'mating_speed'
            ]
            for key in game_ini_keys:
                if key in settings:
                    game_ini_settings[key] = settings[key]
            
            if game_user_settings:
                self.config.update_game_settings(game_user_settings)
            if game_ini_settings:
                self.config.update_stat_multipliers(game_ini_settings)
            print("✓ Server settings updated")
        else:
            print("No changes made")
    
    def start_server(self):
        """Start the ARK server with current configuration"""
        if not self.controller.is_installed():
            print("ERROR: Server not installed. Run 'Install/Update Server' first.")
            return
        
        # Get server settings for startup
        settings = self.config.get_server_settings()
        server_name = self.config.get_server_name()
        
        map_name = settings.get('map_name', 'TheIsland_WP')
        game_port = settings.get('game_port', 7777)
        query_port = settings.get('query_port', 27015)
        max_players = settings.get('max_players', 10)
        
        print(f"Starting server: {server_name}")
        print(f"Map: {map_name}, Port: {game_port}, Max Players: {max_players}")
        
        self.controller.start(map_name, game_port, query_port, max_players)
    
    def stop_server(self):
        """Save the world and then stop the server gracefully"""
        if not self.controller.is_running():
            print("Server is not running")
            return
        
        print("Saving world before shutdown...")
        
        # Try to save and stop via RCON
        settings = self.config.get_server_settings()
        rcon_port = settings.get('rcon_port', 27020)
        admin_password = settings.get('admin_password', '')
        
        if admin_password:
            self.rcon = RCONClient(port=rcon_port, password=admin_password)
            if self.rcon.connect():
                # Send save command
                save_response = self.rcon.send_command("saveworld")
                if save_response:
                    print("✓ World saved successfully")
                else:
                    print("WARNING: Could not save world via RCON")
                
                # Wait a moment for save to complete
                time.sleep(5)
                
                # Send graceful shutdown command
                exit_response = self.rcon.send_command("doexit")
                if exit_response:
                    print("✓ Server shutdown command sent via RCON")
                    # Wait for server to shut down
                    time.sleep(10)
                    self.rcon.disconnect()
                    
                    # Check if process is still running
                    if self.controller.is_running():
                        print("WARNING: Server still running after doexit, terminating process...")
                        self.controller.stop()
                    else:
                        print("✓ Server stopped gracefully")
                        self.controller.process = None
                    return
                else:
                    print("WARNING: Could not send shutdown command via RCON")
                self.rcon.disconnect()
            else:
                print("WARNING: Could not connect to RCON. Server will be stopped by terminating process.")
        else:
            print("WARNING: No admin password configured. Server will be stopped by terminating process.")
        
        # Fallback: terminate process
        self.controller.stop()
    
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
        
        # Get configured admin password
        settings = self.config.get_server_settings()
        admin_password = settings.get('admin_password', '')
        
        if admin_password:
            print(f"Using configured admin password for RCON")
            password = admin_password
        else:
            print("No admin password configured.")
            password = input("RCON Password (same as admin password): ")
            
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