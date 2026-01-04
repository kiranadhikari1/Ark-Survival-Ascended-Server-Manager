"""
Server backup management
"""

import shutil
from pathlib import Path
from datetime import datetime
from utils.validation import validate_path


class BackupManager:
    """Handles manual backups of server data"""
    
    def __init__(self, server_dir: Path, base_dir: Path):
        self.server_dir = validate_path(str(server_dir))
        self.base_dir = validate_path(str(base_dir))
        self.backup_dir = self.base_dir / "backups"
    
    def create_backup(self) -> bool:
        """Create timestamped backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        
        try:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            saved_dir = self.server_dir / "ShooterGame" / "Saved"
            if not saved_dir.exists():
                print("WARNING: No Saved directory found - nothing to backup")
                return False
            
            print(f"Backing up save data and configuration...")
            print(f"  Source: {saved_dir}")
            print(f"  Including: SavedArks/, Config/ (GameUserSettings.ini, Game.ini), Logs/")
            
            shutil.copytree(saved_dir, backup_path / "Saved", dirs_exist_ok=True)
            
            total_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
            size_mb = total_size / (1024 * 1024)
            
            print(f"✓ Backup created: {backup_path}")
            print(f"  Size: {size_mb:.2f} MB")
            return True
            
        except Exception as e:
            print(f"ERROR: Backup failed: {e}")
            return False