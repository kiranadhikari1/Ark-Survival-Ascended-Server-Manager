"""
ARK server configuration management
"""

import configparser
from pathlib import Path
from typing import Dict, List
from utils.validation import validate_path, validate_mod_id


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
        session_settings = {}
        
        # Basic server settings
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
        
        # Initial server settings (one-time setup)
        if 'allow_anyone_baby_imprint' in settings:
            server_settings['AllowAnyoneBabyImprintCuddle'] = 'True' if settings['allow_anyone_baby_imprint'] else 'False'
        if 'allow_cave_building_pve' in settings:
            server_settings['AllowCaveBuildingPvE'] = 'True' if settings['allow_cave_building_pve'] else 'False'
        if 'allow_flyer_carry_pve' in settings:
            server_settings['AllowFlyerCarryPvE'] = 'True' if settings['allow_flyer_carry_pve'] else 'False'
        if 'always_allow_structure_pickup' in settings:
            server_settings['AlwaysAllowStructurePickup'] = 'True' if settings['always_allow_structure_pickup'] else 'False'
        if 'always_notify_player_left' in settings:
            server_settings['AlwaysNotifyPlayerLeft'] = 'True' if settings['always_notify_player_left'] else 'False'
        if 'dino_count_multiplier' in settings:
            server_settings['DinoCountMultiplier'] = settings['dino_count_multiplier']
        if 'global_voice_chat' in settings:
            server_settings['globalVoiceChat'] = 'True' if settings['global_voice_chat'] else 'False'
        if 'player_stamina_drain' in settings:
            server_settings['PlayerCharacterStaminaDrainMultiplier'] = settings['player_stamina_drain']
        if 'player_water_drain' in settings:
            server_settings['PlayerCharacterWaterDrainMultiplier'] = settings['player_water_drain']
        if 'pve_allow_structures_at_drops' in settings:
            server_settings['PvEAllowStructuresAtSupplyDrops'] = 'True' if settings['pve_allow_structures_at_drops'] else 'False'
        if 'random_supply_crate_points' in settings:
            server_settings['RandomSupplyCratePoints'] = 'True' if settings['random_supply_crate_points'] else 'False'
        if 'show_floating_damage' in settings:
            server_settings['ShowFloatingDamageText'] = 'True' if settings['show_floating_damage'] else 'False'
        if 'enable_cryopod_nerf' in settings:
            server_settings['EnableCryopodNerf'] = 'True' if settings['enable_cryopod_nerf'] else 'False'
        if 'no_tribute_downloads' in settings:
            server_settings['noTributeDownloads'] = 'True' if settings['no_tribute_downloads'] else 'False'
        if 'prevent_download_dinos' in settings:
            server_settings['PreventDownloadDinos'] = 'True' if settings['prevent_download_dinos'] else 'False'
        if 'prevent_download_items' in settings:
            server_settings['PreventDownloadItems'] = 'True' if settings['prevent_download_items'] else 'False'
        if 'prevent_download_survivors' in settings:
            server_settings['PreventDownloadSurvivors'] = 'True' if settings['prevent_download_survivors'] else 'False'
        if 'prevent_upload_dinos' in settings:
            server_settings['PreventUploadDinos'] = 'True' if settings['prevent_upload_dinos'] else 'False'
        if 'prevent_upload_items' in settings:
            server_settings['PreventUploadItems'] = 'True' if settings['prevent_upload_items'] else 'False'
        if 'prevent_upload_survivors' in settings:
            server_settings['PreventUploadSurvivors'] = 'True' if settings['prevent_upload_survivors'] else 'False'
        
        # Session settings
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
        """Update Game.ini with stat multipliers and game settings"""
        config = self._read_ini(self.game_ini)
        
        section = '/Script/ShooterGame.ShooterGameMode'
        if not config.has_section(section):
            config.add_section(section)
        
        # Player stats
        if 'player_health_mult' in settings:
            config.set(section, 'PerLevelStatsMultiplier_Player[0]', str(settings['player_health_mult']))
        if 'player_stamina_mult' in settings:
            config.set(section, 'PerLevelStatsMultiplier_Player[1]', str(settings['player_stamina_mult']))
        if 'player_weight_mult' in settings:
            config.set(section, 'PerLevelStatsMultiplier_Player[5]', str(settings['player_weight_mult']))
        
        # Dino stats
        if 'dino_health_mult' in settings:
            config.set(section, 'PerLevelStatsMultiplier_DinoTamed[0]', str(settings['dino_health_mult']))
        if 'dino_stamina_mult' in settings:
            config.set(section, 'PerLevelStatsMultiplier_DinoTamed[1]', str(settings['dino_stamina_mult']))
        if 'dino_weight_mult' in settings:
            config.set(section, 'PerLevelStatsMultiplier_DinoTamed[5]', str(settings['dino_weight_mult']))
        
        # Baby/dino multipliers
        if 'baby_cuddle_interval' in settings:
            config.set(section, 'BabyCuddleIntervalMultiplier', str(settings['baby_cuddle_interval']))
        if 'baby_food_consumption' in settings:
            config.set(section, 'BabyFoodConsumptionSpeedMultiplier', str(settings['baby_food_consumption']))
        if 'baby_imprint_amount' in settings:
            config.set(section, 'BabyImprintAmountMultiplier', str(settings['baby_imprint_amount']))
        if 'baby_mature_speed' in settings:
            config.set(section, 'BabyMatureSpeedMultiplier', str(settings['baby_mature_speed']))
        
        # XP multipliers
        if 'craft_xp' in settings:
            config.set(section, 'CraftXPMultiplier', str(settings['craft_xp']))
        if 'generic_xp' in settings:
            config.set(section, 'GenericXPMultiplier', str(settings['generic_xp']))
        if 'harvest_xp' in settings:
            config.set(section, 'HarvestXPMultiplier', str(settings['harvest_xp']))
        if 'kill_xp' in settings:
            config.set(section, 'KillXPMultiplier', str(settings['kill_xp']))
        
        # Farming multipliers
        if 'crop_decay_speed' in settings:
            config.set(section, 'CropDecaySpeedMultiplier', str(settings['crop_decay_speed']))
        if 'crop_growth_speed' in settings:
            config.set(section, 'CropGrowthSpeedMultiplier', str(settings['crop_growth_speed']))
        
        # Egg/breeding multipliers
        if 'egg_hatch_speed' in settings:
            config.set(section, 'EggHatchSpeedMultiplier', str(settings['egg_hatch_speed']))
        if 'lay_egg_interval' in settings:
            config.set(section, 'LayEggIntervalMultiplier', str(settings['lay_egg_interval']))
        if 'mating_interval' in settings:
            config.set(section, 'MatingIntervalMultiplier', str(settings['mating_interval']))
        if 'mating_speed' in settings:
            config.set(section, 'MatingSpeedMultiplier', str(settings['mating_speed']))
        
        # Loot quality
        if 'supply_crate_loot_quality' in settings:
            config.set(section, 'SupplyCrateLootQualityMultiplier', str(settings['supply_crate_loot_quality']))
        
        # Structure settings
        if 'structure_damage_repair_cooldown' in settings:
            config.set(section, 'StructureDamageRepairCooldown', str(settings['structure_damage_repair_cooldown']))
        
        # Boolean settings
        if 'allow_flyer_speed_leveling' in settings:
            config.set(section, 'bAllowFlyerSpeedLeveling', 'True' if settings['allow_flyer_speed_leveling'] else 'False')
        if 'allow_speed_leveling' in settings:
            config.set(section, 'bAllowSpeedLeveling', 'True' if settings['allow_speed_leveling'] else 'False')
        if 'auto_unlock_engrams' in settings:
            config.set(section, 'bAutoUnlockAllEngrams', 'True' if settings['auto_unlock_engrams'] else 'False')
        if 'disable_friendly_fire' in settings:
            config.set(section, 'bDisableFriendlyFire', 'True' if settings['disable_friendly_fire'] else 'False')
        
        self._write_ini(self.game_ini, config)
    
    def get_stat_multipliers(self) -> Dict:
        """Get current stat multipliers and game settings"""
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
            
            # Baby/dino multipliers
            if config.has_option(section, 'BabyCuddleIntervalMultiplier'):
                multipliers['baby_cuddle_interval'] = float(config.get(section, 'BabyCuddleIntervalMultiplier'))
            if config.has_option(section, 'BabyFoodConsumptionSpeedMultiplier'):
                multipliers['baby_food_consumption'] = float(config.get(section, 'BabyFoodConsumptionSpeedMultiplier'))
            if config.has_option(section, 'BabyImprintAmountMultiplier'):
                multipliers['baby_imprint_amount'] = float(config.get(section, 'BabyImprintAmountMultiplier'))
            if config.has_option(section, 'BabyMatureSpeedMultiplier'):
                multipliers['baby_mature_speed'] = float(config.get(section, 'BabyMatureSpeedMultiplier'))
            
            # XP multipliers
            if config.has_option(section, 'CraftXPMultiplier'):
                multipliers['craft_xp'] = float(config.get(section, 'CraftXPMultiplier'))
            if config.has_option(section, 'GenericXPMultiplier'):
                multipliers['generic_xp'] = float(config.get(section, 'GenericXPMultiplier'))
            if config.has_option(section, 'HarvestXPMultiplier'):
                multipliers['harvest_xp'] = float(config.get(section, 'HarvestXPMultiplier'))
            if config.has_option(section, 'KillXPMultiplier'):
                multipliers['kill_xp'] = float(config.get(section, 'KillXPMultiplier'))
            
            # Farming multipliers
            if config.has_option(section, 'CropDecaySpeedMultiplier'):
                multipliers['crop_decay_speed'] = float(config.get(section, 'CropDecaySpeedMultiplier'))
            if config.has_option(section, 'CropGrowthSpeedMultiplier'):
                multipliers['crop_growth_speed'] = float(config.get(section, 'CropGrowthSpeedMultiplier'))
            
            # Egg/breeding multipliers
            if config.has_option(section, 'EggHatchSpeedMultiplier'):
                multipliers['egg_hatch_speed'] = float(config.get(section, 'EggHatchSpeedMultiplier'))
            if config.has_option(section, 'LayEggIntervalMultiplier'):
                multipliers['lay_egg_interval'] = float(config.get(section, 'LayEggIntervalMultiplier'))
            if config.has_option(section, 'MatingIntervalMultiplier'):
                multipliers['mating_interval'] = float(config.get(section, 'MatingIntervalMultiplier'))
            if config.has_option(section, 'MatingSpeedMultiplier'):
                multipliers['mating_speed'] = float(config.get(section, 'MatingSpeedMultiplier'))
            
            # Loot quality
            if config.has_option(section, 'SupplyCrateLootQualityMultiplier'):
                multipliers['supply_crate_loot_quality'] = float(config.get(section, 'SupplyCrateLootQualityMultiplier'))
            
            # Structure damage repair
            if config.has_option(section, 'StructureDamageRepairCooldown'):
                multipliers['structure_damage_repair_cooldown'] = int(config.get(section, 'StructureDamageRepairCooldown'))
            
            # Boolean settings in Game.ini
            if config.has_option(section, 'bAllowFlyerSpeedLeveling'):
                multipliers['allow_flyer_speed_leveling'] = config.get(section, 'bAllowFlyerSpeedLeveling').lower() == 'true'
            if config.has_option(section, 'bAllowSpeedLeveling'):
                multipliers['allow_speed_leveling'] = config.get(section, 'bAllowSpeedLeveling').lower() == 'true'
            if config.has_option(section, 'bAutoUnlockAllEngrams'):
                multipliers['auto_unlock_engrams'] = config.get(section, 'bAutoUnlockAllEngrams').lower() == 'true'
            if config.has_option(section, 'bDisableFriendlyFire'):
                multipliers['disable_friendly_fire'] = config.get(section, 'bDisableFriendlyFire').lower() == 'true'
        
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
        if config.has_option('ServerSettings', 'TamedDinoDamageMultiplier'):
            settings['tamed_dino_damage'] = float(config.get('ServerSettings', 'TamedDinoDamageMultiplier'))
        if config.has_option('ServerSettings', 'TheMaxStructuresInRange'):
            settings['max_structures_in_range'] = int(config.get('ServerSettings', 'TheMaxStructuresInRange'))
        if config.has_option('ServerSettings', 'DifficultyOffset'):
            settings['difficulty_offset'] = float(config.get('ServerSettings', 'DifficultyOffset'))
        if config.has_option('ServerSettings', 'ServerPVE'):
            settings['pve_mode'] = config.get('ServerSettings', 'ServerPVE').lower() == 'true'
        if config.has_option('ServerSettings', 'RCONEnabled'):
            settings['rcon_enabled'] = config.get('ServerSettings', 'RCONEnabled').lower() == 'true'
        if config.has_option('ServerSettings', 'RCONPort'):
            settings['rcon_port'] = int(config.get('ServerSettings', 'RCONPort'))
        
        # Initial server settings (one-time setup)
        if config.has_option('ServerSettings', 'AllowAnyoneBabyImprintCuddle'):
            settings['allow_anyone_baby_imprint'] = config.get('ServerSettings', 'AllowAnyoneBabyImprintCuddle').lower() == 'true'
        if config.has_option('ServerSettings', 'AllowCaveBuildingPvE'):
            settings['allow_cave_building_pve'] = config.get('ServerSettings', 'AllowCaveBuildingPvE').lower() == 'true'
        if config.has_option('ServerSettings', 'AllowFlyerCarryPvE'):
            settings['allow_flyer_carry_pve'] = config.get('ServerSettings', 'AllowFlyerCarryPvE').lower() == 'true'
        if config.has_option('ServerSettings', 'AlwaysAllowStructurePickup'):
            settings['always_allow_structure_pickup'] = config.get('ServerSettings', 'AlwaysAllowStructurePickup').lower() == 'true'
        if config.has_option('ServerSettings', 'AlwaysNotifyPlayerLeft'):
            settings['always_notify_player_left'] = config.get('ServerSettings', 'AlwaysNotifyPlayerLeft').lower() == 'true'
        if config.has_option('ServerSettings', 'DinoCountMultiplier'):
            settings['dino_count_multiplier'] = float(config.get('ServerSettings', 'DinoCountMultiplier'))
        if config.has_option('ServerSettings', 'globalVoiceChat'):
            settings['global_voice_chat'] = config.get('ServerSettings', 'globalVoiceChat').lower() == 'true'
        if config.has_option('ServerSettings', 'PlayerCharacterStaminaDrainMultiplier'):
            settings['player_stamina_drain'] = float(config.get('ServerSettings', 'PlayerCharacterStaminaDrainMultiplier'))
        if config.has_option('ServerSettings', 'PlayerCharacterWaterDrainMultiplier'):
            settings['player_water_drain'] = float(config.get('ServerSettings', 'PlayerCharacterWaterDrainMultiplier'))
        if config.has_option('ServerSettings', 'PvEAllowStructuresAtSupplyDrops'):
            settings['pve_allow_structures_at_drops'] = config.get('ServerSettings', 'PvEAllowStructuresAtSupplyDrops').lower() == 'true'
        if config.has_option('ServerSettings', 'RandomSupplyCratePoints'):
            settings['random_supply_crate_points'] = config.get('ServerSettings', 'RandomSupplyCratePoints').lower() == 'true'
        if config.has_option('ServerSettings', 'ShowFloatingDamageText'):
            settings['show_floating_damage'] = config.get('ServerSettings', 'ShowFloatingDamageText').lower() == 'true'
        if config.has_option('ServerSettings', 'EnableCryopodNerf'):
            settings['enable_cryopod_nerf'] = config.get('ServerSettings', 'EnableCryopodNerf').lower() == 'true'
        if config.has_option('ServerSettings', 'noTributeDownloads'):
            settings['no_tribute_downloads'] = config.get('ServerSettings', 'noTributeDownloads').lower() == 'true'
        if config.has_option('ServerSettings', 'PreventDownloadDinos'):
            settings['prevent_download_dinos'] = config.get('ServerSettings', 'PreventDownloadDinos').lower() == 'true'
        if config.has_option('ServerSettings', 'PreventDownloadItems'):
            settings['prevent_download_items'] = config.get('ServerSettings', 'PreventDownloadItems').lower() == 'true'
        if config.has_option('ServerSettings', 'PreventDownloadSurvivors'):
            settings['prevent_download_survivors'] = config.get('ServerSettings', 'PreventDownloadSurvivors').lower() == 'true'
        if config.has_option('ServerSettings', 'PreventUploadDinos'):
            settings['prevent_upload_dinos'] = config.get('ServerSettings', 'PreventUploadDinos').lower() == 'true'
        if config.has_option('ServerSettings', 'PreventUploadItems'):
            settings['prevent_upload_items'] = config.get('ServerSettings', 'PreventUploadItems').lower() == 'true'
        if config.has_option('ServerSettings', 'PreventUploadSurvivors'):
            settings['prevent_upload_survivors'] = config.get('ServerSettings', 'PreventUploadSurvivors').lower() == 'true'
        
        # SessionSettings
        if config.has_option('SessionSettings', 'MaxPlayers'):
            settings['max_players'] = int(config.get('SessionSettings', 'MaxPlayers'))
        
        return settings