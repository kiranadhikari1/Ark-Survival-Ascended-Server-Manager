"""
ARK server configuration management
"""

import configparser
from pathlib import Path
from typing import Dict, List
from utils.validation import validate_path, validate_mod_id
from utils.constants import DEFAULT_RCON_PORT


class ServerConfig:
    """Manages GameUserSettings.ini and Game.ini"""
    
    def __init__(self, server_dir: Path):
        self.server_dir = validate_path(str(server_dir))
        self.config_dir = self.server_dir / "ShooterGame" / "Saved" / "Config" / "WindowsServer"
        self.game_user_settings = self.config_dir / "GameUserSettings.ini"
        self.game_ini = self.config_dir / "Game.ini"
    
    def _ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def _read_ini(self, file_path: Path) -> configparser.ConfigParser:
        """Read INI file preserving all keys"""
        config = configparser.ConfigParser()
        config.optionxform = str  # Case-sensitive
        
        if file_path.exists():
            try:
                config.read(file_path, encoding='utf-8')
            except Exception as e:
                print(f"WARNING: Error reading {file_path.name}: {e}")
        
        return config
    
    def _write_ini(self, file_path: Path, config: configparser.ConfigParser):
        """Write INI file safely"""
        self._ensure_config_dir()
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                config.write(f, space_around_delimiters=False)
            print(f"✓ Updated {file_path.name}")
        except Exception as e:
            print(f"ERROR: Failed to write {file_path.name}: {e}")
    
    def update_game_settings(self, settings: Dict):
        """Update GameUserSettings.ini with only provided settings"""
        config = self._read_ini(self.game_user_settings)
        
        if not config.has_section('ServerSettings'):
            config.add_section('ServerSettings')
        if not config.has_section('SessionSettings'):
            config.add_section('SessionSettings')
        
        # Only update settings that are provided
        server_settings = {}
        if 'server_password' in settings:
            server_settings['ServerPassword'] = settings['server_password']
        if 'admin_password' in settings:
            server_settings['ServerAdminPassword'] = settings['admin_password']
        if 'xp_multiplier' in settings:
            server_settings['XPMultiplier'] = settings['xp_multiplier']
        if 'taming_speed' in settings:
            server_settings['TamingSpeedMultiplier'] = settings['taming_speed']
        if 'harvest_amount' in settings:
            server_settings['HarvestAmountMultiplier'] = settings['harvest_amount']
        if 'difficulty_offset' in settings:
            server_settings['DifficultyOffset'] = settings['difficulty_offset']
        if 'pve_mode' in settings:
            server_settings['ServerPVE'] = 'True' if settings['pve_mode'] else 'False'
        if 'rcon_enabled' in settings:
            server_settings['RCONEnabled'] = 'True' if settings['rcon_enabled'] else 'False'
        if 'rcon_port' in settings:
            server_settings['RCONPort'] = settings['rcon_port']
        if 'active_mods' in settings:
            server_settings['ActiveMods'] = settings['active_mods']
        
        session_settings = {}
        if 'server_name' in settings:
            session_settings['SessionName'] = settings['server_name']
        if 'max_players' in settings:
            session_settings['MaxPlayers'] = settings['max_players']
        
        for key, value in server_settings.items():
            if value is not None and value != '':
                config.set('ServerSettings', key, str(value))
        
        for key, value in session_settings.items():
            if value is not None and value != '':
                config.set('SessionSettings', key, str(value))
        
        self._write_ini(self.game_user_settings, config)
    
    def update_stat_multipliers(self, settings: Dict):
        """Update Game.ini with stat multipliers"""
        config = self._read_ini(self.game_ini)
        
        section = '/Script/ShooterGame.ShooterGameMode'
        if not config.has_section(section):
            config.add_section(section)
        
        # Player stats: 0=Health, 1=Stamina, 5=Weight
        if settings.get('player_health_mult'):
            config.set(section, 'PerLevelStatsMultiplier_Player[0]', 
                      str(settings['player_health_mult']))
        
        if settings.get('player_stamina_mult'):
            config.set(section, 'PerLevelStatsMultiplier_Player[1]', 
                      str(settings['player_stamina_mult']))
        
        if settings.get('player_weight_mult'):
            config.set(section, 'PerLevelStatsMultiplier_Player[5]', 
                      str(settings['player_weight_mult']))
        
        # Dino stats
        if settings.get('dino_health_mult'):
            config.set(section, 'PerLevelStatsMultiplier_DinoTamed[0]', 
                      str(settings['dino_health_mult']))
        
        if settings.get('dino_stamina_mult'):
            config.set(section, 'PerLevelStatsMultiplier_DinoTamed[1]', 
                      str(settings['dino_stamina_mult']))
        
        if settings.get('dino_weight_mult'):
            config.set(section, 'PerLevelStatsMultiplier_DinoTamed[5]', 
                      str(settings['dino_weight_mult']))
        
        self._write_ini(self.game_ini, config)
    
    def get_stat_multipliers(self) -> Dict:
        """Get current stat multipliers"""
        config = self._read_ini(self.game_ini)
        section = '/Script/ShooterGame.ShooterGameMode'
        multipliers = {}
        
        if config.has_section(section):
            # Player stats
            if config.has_option(section, 'PerLevelStatsMultiplier_Player[0]'):
                multipliers['player_health_mult'] = float(config.get(section, 'PerLevelStatsMultiplier_Player[0]'))
            if config.has_option(section, 'PerLevelStatsMultiplier_Player[1]'):
                multipliers['player_stamina_mult'] = float(config.get(section, 'PerLevelStatsMultiplier_Player[1]'))
            if config.has_option(section, 'PerLevelStatsMultiplier_Player[5]'):
                multipliers['player_weight_mult'] = float(config.get(section, 'PerLevelStatsMultiplier_Player[5]'))
            
            # Dino stats
            if config.has_option(section, 'PerLevelStatsMultiplier_DinoTamed[0]'):
                multipliers['dino_health_mult'] = float(config.get(section, 'PerLevelStatsMultiplier_DinoTamed[0]'))
            if config.has_option(section, 'PerLevelStatsMultiplier_DinoTamed[1]'):
                multipliers['dino_stamina_mult'] = float(config.get(section, 'PerLevelStatsMultiplier_DinoTamed[1]'))
            if config.has_option(section, 'PerLevelStatsMultiplier_DinoTamed[5]'):
                multipliers['dino_weight_mult'] = float(config.get(section, 'PerLevelStatsMultiplier_DinoTamed[5]'))
        
        return multipliers
    
    def set_mods(self, mod_ids: List[str]) -> bool:
        """Set active mods"""
        validated = [m.strip() for m in mod_ids if validate_mod_id(m)]
        
        if not validated:
            print("No valid mods provided")
            return False
        
        config = self._read_ini(self.game_user_settings)
        if not config.has_section('ServerSettings'):
            config.add_section('ServerSettings')
        
        config.set('ServerSettings', 'ActiveMods', ','.join(validated))
        self._write_ini(self.game_user_settings, config)
        print(f"✓ Configured {len(validated)} mod(s)")
        return True
    
    def clear_mods(self):
        """Remove all mods"""
        config = self._read_ini(self.game_user_settings)
        
        if config.has_option('ServerSettings', 'ActiveMods'):
            config.remove_option('ServerSettings', 'ActiveMods')
            self._write_ini(self.game_user_settings, config)
            print("✓ Cleared all mods")
    
    def get_active_mods(self) -> List[str]:
        """Get currently active mods"""
        config = self._read_ini(self.game_user_settings)
        
        if config.has_option('ServerSettings', 'ActiveMods'):
            mods = config.get('ServerSettings', 'ActiveMods')
            return [m.strip() for m in mods.split(',') if m.strip()]
        
        return []
    
    def get_server_name(self) -> str:
        """Get current server name"""
        config = self._read_ini(self.game_user_settings)
        
        if config.has_option('SessionSettings', 'SessionName'):
            return config.get('SessionSettings', 'SessionName')
        
        return "ARK Server"
    
    def get_server_settings(self) -> Dict:
        """Get current server settings"""
        config = self._read_ini(self.game_user_settings)
        settings = {}
        
        # ServerSettings
        if config.has_option('ServerSettings', 'ServerPassword'):
            settings['server_password'] = config.get('ServerSettings', 'ServerPassword')
        if config.has_option('ServerSettings', 'ServerAdminPassword'):
            settings['admin_password'] = config.get('ServerSettings', 'ServerAdminPassword')
        if config.has_option('ServerSettings', 'XPMultiplier'):
            settings['xp_multiplier'] = float(config.get('ServerSettings', 'XPMultiplier'))
        if config.has_option('ServerSettings', 'TamingSpeedMultiplier'):
            settings['taming_speed'] = float(config.get('ServerSettings', 'TamingSpeedMultiplier'))
        if config.has_option('ServerSettings', 'HarvestAmountMultiplier'):
            settings['harvest_amount'] = float(config.get('ServerSettings', 'HarvestAmountMultiplier'))
        if config.has_option('ServerSettings', 'DifficultyOffset'):
            settings['difficulty_offset'] = float(config.get('ServerSettings', 'DifficultyOffset'))
        if config.has_option('ServerSettings', 'ServerPVE'):
            settings['pve_mode'] = config.get('ServerSettings', 'ServerPVE').lower() == 'true'
        
        # SessionSettings
        if config.has_option('SessionSettings', 'MaxPlayers'):
            settings['max_players'] = int(config.get('SessionSettings', 'MaxPlayers'))
        
        return settings