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


class ConfigurationHelper:
    """Helper class for handling configuration input and validation"""
    
    def __init__(self, config_manager):
        self.config = config_manager
    
    def get_string_input(self, prompt: str, current_value: str = "", max_length: int = None, sanitizer=None) -> str:
        """Get string input with validation"""
        display_value = f" [{current_value}]" if current_value else ""
        user_input = input(f"{prompt}{display_value}: ").strip()
        
        if user_input:
            if sanitizer:
                user_input = sanitizer(user_input, max_length=max_length) if max_length else sanitizer(user_input)
            elif max_length and len(user_input) > max_length:
                print(f"Input too long (max {max_length} characters). Truncated.")
                user_input = user_input[:max_length]
            return user_input
        return current_value
    
    def get_int_input(self, prompt: str, current_value: int, min_val: int = None, max_val: int = None) -> int:
        """Get integer input with validation"""
        while True:
            try:
                display_value = f" [{current_value}]" if current_value is not None else ""
                user_input = input(f"{prompt}{display_value}: ").strip()
                
                if not user_input:
                    return current_value
                
                value = int(user_input)
                if min_val is not None and value < min_val:
                    print(f"Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Value must be at most {max_val}")
                    continue
                return value
            except ValueError:
                print("Please enter a valid number")
    
    def get_float_input(self, prompt: str, current_value: float, min_val: float = None, max_val: float = None) -> float:
        """Get float input with validation"""
        while True:
            try:
                display_value = f" [{current_value}]" if current_value is not None else ""
                user_input = input(f"{prompt}{display_value}: ").strip()
                
                if not user_input:
                    return current_value
                
                value = float(user_input)
                if min_val is not None and value < min_val:
                    print(f"Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Value must be at most {max_val}")
                    continue
                return value
            except ValueError:
                print("Please enter a valid number")
    
    def get_bool_input(self, prompt: str, current_value: bool) -> bool:
        """Get boolean input with validation"""
        display_value = "y" if current_value else "n"
        while True:
            user_input = input(f"{prompt} (y/n) [{display_value}]: ").lower().strip()
            
            if not user_input:
                return current_value
            
            if user_input in ['y', 'yes']:
                return True
            elif user_input in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'")


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
        self.config_helper = ConfigurationHelper(self.config)
    
    def _display_settings_summary(self, settings: dict, old_settings: dict, title: str):
        """Display a formatted summary of settings changes"""
        if not settings:
            return
            
        print(f"\n=== {title} ===")
        print(f"{'Setting':<35} {'Old Value':<20} {'New Value':<20}")
        print("-" * 77)
        
        # Mapping for user-friendly names (shared between methods)
        friendly_names = {
            # Initial server settings
            'server_name': 'Server Name',
            'max_players': 'Max Players',
            'server_password': 'Server Password',
            'admin_password': 'Admin Password',
            'allow_anyone_baby_imprint': 'Allow Anyone Baby Imprint',
            'allow_cave_building_pve': 'Allow Cave Building PvE',
            'allow_flyer_carry_pve': 'Allow Flyer Carry PvE',
            'always_allow_structure_pickup': 'Always Allow Structure Pickup',
            'always_notify_player_left': 'Always Notify Player Left',
            'dino_count_multiplier': 'Dino Count Multiplier',
            'global_voice_chat': 'Global Voice Chat',
            'player_stamina_drain': 'Player Stamina Drain',
            'player_water_drain': 'Player Water Drain',
            'pve_allow_structures_at_drops': 'PvE Allow Structures At Drops',
            'random_supply_crate_points': 'Random Supply Crate Points',
            'show_floating_damage': 'Show Floating Damage Text',
            'enable_cryopod_nerf': 'Enable Cryopod Nerf',
            'no_tribute_downloads': 'No Tribute Downloads',
            'prevent_download_dinos': 'Prevent Download Dinos',
            'prevent_download_items': 'Prevent Download Items',
            'prevent_download_survivors': 'Prevent Download Survivors',
            'prevent_upload_dinos': 'Prevent Upload Dinos',
            'prevent_upload_items': 'Prevent Upload Items',
            'prevent_upload_survivors': 'Prevent Upload Survivors',
            # Multiplier settings
            'xp_multiplier': 'XP Multiplier',
            'taming_speed': 'Taming Speed',
            'harvest_amount': 'Harvest Amount',
            'baby_cuddle_interval': 'Baby Cuddle Interval',
            'baby_food_consumption': 'Baby Food Consumption',
            'baby_imprint_amount': 'Baby Imprint Amount',
            'baby_mature_speed': 'Baby Mature Speed',
            'craft_xp': 'Craft XP',
            'crop_decay_speed': 'Crop Decay Speed',
            'crop_growth_speed': 'Crop Growth Speed',
            'egg_hatch_speed': 'Egg Hatch Speed',
            'generic_xp': 'Generic XP',
            'harvest_xp': 'Harvest XP',
            'kill_xp': 'Kill XP',
            'lay_egg_interval': 'Lay Egg Interval',
            'mating_interval': 'Mating Interval',
            'mating_speed': 'Mating Speed',
            # Difficulty settings
            'difficulty_offset': 'Difficulty Offset',
            'override_official_difficulty': 'Override Official Difficulty',
        }
        
        for key, new_value in settings.items():
            old_value = old_settings.get(key, '')
            
            # Handle password masking
            if 'password' in key:
                if old_value:
                    old_display = '*' * len(str(old_value))
                else:
                    old_display = 'none'
                if new_value:
                    new_display = '*' * len(str(new_value))
                else:
                    new_display = 'none'
            # Handle boolean values
            elif isinstance(new_value, bool):
                old_display = 'Yes' if old_value else 'No'
                new_display = 'Yes' if new_value else 'No'
            # Handle float values
            elif isinstance(new_value, float):
                try:
                    old_float = float(old_value) if old_value else 1.0
                    old_display = f"{old_float:.2f}"
                except (ValueError, TypeError):
                    old_display = "1.00"  # Default for new settings
                new_display = f"{new_value:.2f}"
            # Handle other values
            else:
                old_display = str(old_value) if old_value else 'none'
                new_display = str(new_value) if new_value else 'none'
            
            friendly_name = friendly_names.get(key, key.replace('_', ' ').title())
            print(f"{friendly_name:<35} {old_display:<20} {new_display:<20}")
    
    def show_menu(self):
        print("\n" + "="*60)
        print("ARK: Survival Ascended Server Manager")
        print("="*60)
        print("1. Install/Update Server")
        print("2. Initial Server Settings")
        print("3. Configure Server (Frequent Multipliers)")
        print("4. Manage Mods")
        print("5. Start Server")
        print("6. Stop Server (saveworld + doexit)")
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
    
    def install_update_server(self):
        """Install or update server"""
        print("\n=== Install/Update Server ===")
        force = input("Force validate? (y/n): ").lower() == 'y'
        self.steamcmd.install_or_update(force_update=force)

    def configure_initial_server(self):
        print("\n=== Initial Server Settings (One-time Setup) ===")
        print("These settings are typically set once and rarely changed.")
        
        current_settings = self.config.get_server_settings()
        settings = {}
        
        # Server name
        settings['server_name'] = self.config_helper.get_string_input(
            "Server Name", current_settings.get('server_name', ''), 
            max_length=MAX_SERVER_NAME_LENGTH, sanitizer=sanitize_input
        )
        if settings['server_name'] == current_settings.get('server_name', ''):
            del settings['server_name']
        
        # Max players
        settings['max_players'] = self.config_helper.get_int_input(
            "Max Players", current_settings.get('max_players', 70), min_val=1, max_val=1000
        )
        if settings['max_players'] == current_settings.get('max_players', 70):
            del settings['max_players']
        
        # Server password
        settings['server_password'] = self.config_helper.get_string_input(
            "Server Password (optional)", current_settings.get('server_password', ''), 
            max_length=MAX_PASSWORD_LENGTH, sanitizer=sanitize_input
        )
        if settings['server_password'] == current_settings.get('server_password', ''):
            del settings['server_password']
        
        # Admin password
        settings['admin_password'] = self.config_helper.get_string_input(
            "Admin Password (required)", current_settings.get('admin_password', ''), 
            max_length=MAX_PASSWORD_LENGTH, sanitizer=sanitize_input
        )
        if settings['admin_password'] == current_settings.get('admin_password', ''):
            del settings['admin_password']
        
        # Boolean settings
        settings['allow_anyone_baby_imprint'] = self.config_helper.get_bool_input(
            "Allow Anyone Baby Imprint Cuddle?", current_settings.get('allow_anyone_baby_imprint', False)
        )
        if settings['allow_anyone_baby_imprint'] == current_settings.get('allow_anyone_baby_imprint', False):
            del settings['allow_anyone_baby_imprint']
        
        settings['allow_cave_building_pve'] = self.config_helper.get_bool_input(
            "Allow Cave Building PvE?", current_settings.get('allow_cave_building_pve', False)
        )
        if settings['allow_cave_building_pve'] == current_settings.get('allow_cave_building_pve', False):
            del settings['allow_cave_building_pve']
        
        settings['allow_flyer_carry_pve'] = self.config_helper.get_bool_input(
            "Allow Flyer Carry PvE?", current_settings.get('allow_flyer_carry_pve', False)
        )
        if settings['allow_flyer_carry_pve'] == current_settings.get('allow_flyer_carry_pve', False):
            del settings['allow_flyer_carry_pve']
        
        settings['always_allow_structure_pickup'] = self.config_helper.get_bool_input(
            "Always Allow Structure Pickup?", current_settings.get('always_allow_structure_pickup', False)
        )
        if settings['always_allow_structure_pickup'] == current_settings.get('always_allow_structure_pickup', False):
            del settings['always_allow_structure_pickup']
        
        settings['always_notify_player_left'] = self.config_helper.get_bool_input(
            "Always Notify Player Left?", current_settings.get('always_notify_player_left', False)
        )
        if settings['always_notify_player_left'] == current_settings.get('always_notify_player_left', False):
            del settings['always_notify_player_left']
        
        # Dino count multiplier
        settings['dino_count_multiplier'] = self.config_helper.get_float_input(
            "Dino Count Multiplier", current_settings.get('dino_count_multiplier', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['dino_count_multiplier'] == current_settings.get('dino_count_multiplier', 1.0):
            del settings['dino_count_multiplier']
        
        # Difficulty Offset
        settings['difficulty_offset'] = self.config_helper.get_float_input(
            "Difficulty Offset (ASA default = 1.0)",
            current_settings.get('difficulty_offset', 1.0),
            min_val=0.01,
            max_val=1.0
        )
        if settings['difficulty_offset'] == current_settings.get('difficulty_offset', 1.0):
            del settings['difficulty_offset']

        # Override Official Difficulty
        settings['override_official_difficulty'] = self.config_helper.get_float_input(
            "Override Official Difficulty (MaxLevel ÷ 30, e.g. 6.0 = level 180)",
            current_settings.get('override_official_difficulty', 5.0),
            min_val=1.0,
            max_val=20.0
        )
        if settings['override_official_difficulty'] == current_settings.get('override_official_difficulty', 5.0):
            del settings['override_official_difficulty']

        # Global voice chat
        settings['global_voice_chat'] = self.config_helper.get_bool_input(
            "Global Voice Chat?", current_settings.get('global_voice_chat', False)
        )
        if settings['global_voice_chat'] == current_settings.get('global_voice_chat', False):
            del settings['global_voice_chat']
        
        # Player multipliers
        settings['player_stamina_drain'] = self.config_helper.get_float_input(
            "Player Stamina Drain Multiplier", current_settings.get('player_stamina_drain', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['player_stamina_drain'] == current_settings.get('player_stamina_drain', 1.0):
            del settings['player_stamina_drain']
        
        settings['player_water_drain'] = self.config_helper.get_float_input(
            "Player Water Drain Multiplier", current_settings.get('player_water_drain', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['player_water_drain'] == current_settings.get('player_water_drain', 1.0):
            del settings['player_water_drain']
        
        # More boolean settings
        settings['pve_allow_structures_at_drops'] = self.config_helper.get_bool_input(
            "PvE Allow Structures At Supply Drops?", current_settings.get('pve_allow_structures_at_drops', False)
        )
        if settings['pve_allow_structures_at_drops'] == current_settings.get('pve_allow_structures_at_drops', False):
            del settings['pve_allow_structures_at_drops']
        
        settings['random_supply_crate_points'] = self.config_helper.get_bool_input(
            "Random Supply Crate Points?", current_settings.get('random_supply_crate_points', False)
        )
        if settings['random_supply_crate_points'] == current_settings.get('random_supply_crate_points', False):
            del settings['random_supply_crate_points']
        
        settings['show_floating_damage'] = self.config_helper.get_bool_input(
            "Show Floating Damage Text?", current_settings.get('show_floating_damage', False)
        )
        if settings['show_floating_damage'] == current_settings.get('show_floating_damage', False):
            del settings['show_floating_damage']
        
        settings['enable_cryopod_nerf'] = self.config_helper.get_bool_input(
            "Enable Cryopod Nerf?", current_settings.get('enable_cryopod_nerf', False)
        )
        if settings['enable_cryopod_nerf'] == current_settings.get('enable_cryopod_nerf', False):
            del settings['enable_cryopod_nerf']
        
        # Upload/download prevention settings
        settings['no_tribute_downloads'] = self.config_helper.get_bool_input(
            "No Tribute Downloads?", current_settings.get('no_tribute_downloads', False)
        )
        if settings['no_tribute_downloads'] == current_settings.get('no_tribute_downloads', False):
            del settings['no_tribute_downloads']
        
        settings['prevent_download_dinos'] = self.config_helper.get_bool_input(
            "Prevent Download Dinos?", current_settings.get('prevent_download_dinos', False)
        )
        if settings['prevent_download_dinos'] == current_settings.get('prevent_download_dinos', False):
            del settings['prevent_download_dinos']
        
        settings['prevent_download_items'] = self.config_helper.get_bool_input(
            "Prevent Download Items?", current_settings.get('prevent_download_items', False)
        )
        if settings['prevent_download_items'] == current_settings.get('prevent_download_items', False):
            del settings['prevent_download_items']
        
        settings['prevent_download_survivors'] = self.config_helper.get_bool_input(
            "Prevent Download Survivors?", current_settings.get('prevent_download_survivors', False)
        )
        if settings['prevent_download_survivors'] == current_settings.get('prevent_download_survivors', False):
            del settings['prevent_download_survivors']
        
        settings['prevent_upload_dinos'] = self.config_helper.get_bool_input(
            "Prevent Upload Dinos?", current_settings.get('prevent_upload_dinos', False)
        )
        if settings['prevent_upload_dinos'] == current_settings.get('prevent_upload_dinos', False):
            del settings['prevent_upload_dinos']
        
        settings['prevent_upload_items'] = self.config_helper.get_bool_input(
            "Prevent Upload Items?", current_settings.get('prevent_upload_items', False)
        )
        if settings['prevent_upload_items'] == current_settings.get('prevent_upload_items', False):
            del settings['prevent_upload_items']
        
        settings['prevent_upload_survivors'] = self.config_helper.get_bool_input(
            "Prevent Upload Survivors?", current_settings.get('prevent_upload_survivors', False)
        )
        if settings['prevent_upload_survivors'] == current_settings.get('prevent_upload_survivors', False):
            del settings['prevent_upload_survivors']
        
        if settings:
            self.config.update_game_settings(settings)
            
            # Display summary of changes
            self._display_settings_summary(settings, current_settings, "Initial Settings Modified")
            
            print("\n✓ Initial server settings updated")
        else:
            print("No changes made")
    
    def configure_server(self):
        print("\n=== Configure Server (Frequent Multipliers) ===")
        print("Current values shown in brackets. Press Enter to keep current value.")
        
        current_settings = self.config.get_server_settings()
        current_stats = self.config.get_stat_multipliers()
        settings = {}
        
        # XP Multiplier
        settings['xp_multiplier'] = self.config_helper.get_float_input(
            "XP Multiplier", current_settings.get('xp_multiplier', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['xp_multiplier'] == current_settings.get('xp_multiplier', 1.0):
            del settings['xp_multiplier']
        
        # Taming Speed
        settings['taming_speed'] = self.config_helper.get_float_input(
            "Taming Speed Multiplier", current_settings.get('taming_speed', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['taming_speed'] == current_settings.get('taming_speed', 1.0):
            del settings['taming_speed']
        
        # Harvest Amount
        settings['harvest_amount'] = self.config_helper.get_float_input(
            "Harvest Amount Multiplier", current_settings.get('harvest_amount', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['harvest_amount'] == current_settings.get('harvest_amount', 1.0):
            del settings['harvest_amount']
        
        # Baby Cuddle Interval
        settings['baby_cuddle_interval'] = self.config_helper.get_float_input(
            "Baby Cuddle Interval Multiplier", current_stats.get('baby_cuddle_interval', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['baby_cuddle_interval'] == current_stats.get('baby_cuddle_interval', 1.0):
            del settings['baby_cuddle_interval']
        
        # Baby Food Consumption
        settings['baby_food_consumption'] = self.config_helper.get_float_input(
            "Baby Food Consumption Speed Multiplier", current_stats.get('baby_food_consumption', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['baby_food_consumption'] == current_stats.get('baby_food_consumption', 1.0):
            del settings['baby_food_consumption']
        
        # Baby Imprint Amount
        settings['baby_imprint_amount'] = self.config_helper.get_float_input(
            "Baby Imprint Amount Multiplier", current_stats.get('baby_imprint_amount', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['baby_imprint_amount'] == current_stats.get('baby_imprint_amount', 1.0):
            del settings['baby_imprint_amount']
        
        # Baby Mature Speed
        settings['baby_mature_speed'] = self.config_helper.get_float_input(
            "Baby Mature Speed Multiplier", current_stats.get('baby_mature_speed', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['baby_mature_speed'] == current_stats.get('baby_mature_speed', 1.0):
            del settings['baby_mature_speed']
        
        # Craft XP
        settings['craft_xp'] = self.config_helper.get_float_input(
            "Craft XP Multiplier", current_stats.get('craft_xp', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['craft_xp'] == current_stats.get('craft_xp', 1.0):
            del settings['craft_xp']
        
        # Crop Decay Speed
        settings['crop_decay_speed'] = self.config_helper.get_float_input(
            "Crop Decay Speed Multiplier", current_stats.get('crop_decay_speed', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['crop_decay_speed'] == current_stats.get('crop_decay_speed', 1.0):
            del settings['crop_decay_speed']
        
        # Crop Growth Speed
        settings['crop_growth_speed'] = self.config_helper.get_float_input(
            "Crop Growth Speed Multiplier", current_stats.get('crop_growth_speed', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['crop_growth_speed'] == current_stats.get('crop_growth_speed', 1.0):
            del settings['crop_growth_speed']
        
        # Egg Hatch Speed
        settings['egg_hatch_speed'] = self.config_helper.get_float_input(
            "Egg Hatch Speed Multiplier", current_stats.get('egg_hatch_speed', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['egg_hatch_speed'] == current_stats.get('egg_hatch_speed', 1.0):
            del settings['egg_hatch_speed']
        
        # Generic XP
        settings['generic_xp'] = self.config_helper.get_float_input(
            "Generic XP Multiplier", current_stats.get('generic_xp', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['generic_xp'] == current_stats.get('generic_xp', 1.0):
            del settings['generic_xp']
        
        # Harvest XP
        settings['harvest_xp'] = self.config_helper.get_float_input(
            "Harvest XP Multiplier", current_stats.get('harvest_xp', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['harvest_xp'] == current_stats.get('harvest_xp', 1.0):
            del settings['harvest_xp']
        
        # Kill XP
        settings['kill_xp'] = self.config_helper.get_float_input(
            "Kill XP Multiplier", current_stats.get('kill_xp', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['kill_xp'] == current_stats.get('kill_xp', 1.0):
            del settings['kill_xp']
        
        # Lay Egg Interval
        settings['lay_egg_interval'] = self.config_helper.get_float_input(
            "Lay Egg Interval Multiplier", current_stats.get('lay_egg_interval', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['lay_egg_interval'] == current_stats.get('lay_egg_interval', 1.0):
            del settings['lay_egg_interval']
        
        # Mating Interval
        settings['mating_interval'] = self.config_helper.get_float_input(
            "Mating Interval Multiplier", current_stats.get('mating_interval', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['mating_interval'] == current_stats.get('mating_interval', 1.0):
            del settings['mating_interval']
        
        # Mating Speed
        settings['mating_speed'] = self.config_helper.get_float_input(
            "Mating Speed Multiplier", current_stats.get('mating_speed', 1.0), min_val=0.1, max_val=10.0
        )
        if settings['mating_speed'] == current_stats.get('mating_speed', 1.0):
            del settings['mating_speed']
        
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
            
            # Display summary of changes
            self._display_settings_summary(settings, {**current_settings, **current_stats}, "Settings Modified")
            
            print("\n✓ Server settings updated")
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