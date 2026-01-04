"""
SteamCMD integration for server installation and updates
"""

import subprocess
from pathlib import Path
from utils.validation import validate_path
from utils.constants import ARK_APP_ID


class SteamCMDManager:
    """Manages ARK server installation via SteamCMD"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = validate_path(str(base_dir))
        self.steamcmd_dir = self.base_dir / "steamcmd"
        self.server_dir = self.base_dir / "server"
        self.steamcmd_exe = self.steamcmd_dir / "steamcmd.exe"
    
    def is_steamcmd_installed(self) -> bool:
        return self.steamcmd_exe.exists()
    
    def is_server_installed(self) -> bool:
        server_exe = self.server_dir / "ShooterGame" / "Binaries" / "Win64" / "ArkAscendedServer.exe"
        return server_exe.exists()
    
    def install_or_update(self, force_update: bool = False) -> bool:
        """Install or update ARK server"""
        if not self.is_steamcmd_installed():
            print("ERROR: SteamCMD not found. Please download and extract to:")
            print(f"  {self.steamcmd_dir}")
            print("  Download from: https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip")
            return False
        
        if self.is_server_installed():
            print(f"✓ Server files detected at: {self.server_dir}")
            if not force_update:
                print("  Using 'validate' to check for updates...")
        else:
            print(f"No server installation found. Installing to: {self.server_dir}")
        
        self.server_dir.mkdir(parents=True, exist_ok=True)
        
        cmd = [
            str(self.steamcmd_exe),
            "+force_install_dir", str(self.server_dir),
            "+login", "anonymous",
            "+app_update", ARK_APP_ID
        ]
        
        if force_update:
            cmd.append("validate")
        
        cmd.append("+quit")
        
        print(f"\n=== Running SteamCMD ===")
        print(f"Command: {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(cmd, cwd=str(self.steamcmd_dir))
            
            if result.returncode == 0:
                print("\n✓ SteamCMD completed successfully")
                if self.is_server_installed():
                    print("✓ Server installation verified")
                return True
            else:
                print(f"\nWARNING: SteamCMD returned code {result.returncode}")
                return False
                
        except Exception as e:
            print(f"ERROR: SteamCMD execution failed: {e}")
            return False