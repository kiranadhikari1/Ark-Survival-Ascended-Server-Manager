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
        """Update GameUserSettings.ini"""
        config = self._read_ini(self.game_user_settings)
        
        if not config.has_section('ServerSettings'):
            config.add_section('ServerSettings')
        if not config.has_section('SessionSettings'):
            config.add_section('SessionSettings')
        
        server_settings = {
            'ServerPassword': settings.get('server_password', ''),
            'ServerAdminPassword': settings.get('admin_password', ''),
            'XPMultiplier': settings.get('xp_multiplier', 1.0),
            'TamingSpeedMultiplier': settings.get('taming_speed', 1.0),
            'HarvestAmountMultiplier': settings.get('harvest_amount', 1.0),
            'DifficultyOffset': settings.get('difficulty_offset', 0.2),
            'ServerPVE': 'True' if settings.get('pve_mode', True) else 'False',
            'RCONEnabled': 'True' if settings.get('rcon_enabled', False) else 'False',
            'RCONPort': settings.get('rcon_port', DEFAULT_RCON_PORT),
        }
        
        session_settings = {
            'SessionName': settings.get('server_name', 'ARK Server'),
            'MaxPlayers': settings.get('max_players', 10),
        }
        
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