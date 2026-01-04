"""
ARK server process management
"""

import subprocess
from pathlib import Path
from typing import Optional
from utils.validation import validate_path, validate_port, sanitize_input


class ServerController:
    """Manages server process lifecycle"""
    
    def __init__(self, server_dir: Path):
        self.server_dir = validate_path(str(server_dir))
        self.server_exe = self.server_dir / "ShooterGame" / "Binaries" / "Win64" / "ArkAscendedServer.exe"
        self.process: Optional[subprocess.Popen] = None
    
    def is_installed(self) -> bool:
        return self.server_exe.exists()
    
    def is_running(self) -> bool:
        if self.process is None:
            return False
        return self.process.poll() is None
    
    def get_pid(self) -> Optional[int]:
        return self.process.pid if self.process else None
    
    def _build_command(self, map_name: str, game_port: int, query_port: int, max_players: int):
        """Build server launch command"""
        if not self.is_installed():
            raise FileNotFoundError(f"Server executable not found: {self.server_exe}")
        
        map_name = sanitize_input(map_name, max_length=64)
        game_port = validate_port(game_port)
        query_port = validate_port(query_port)
        
        return [
            str(self.server_exe),
            f"{map_name}?listen",
            f"-Port={game_port}",
            f"-QueryPort={query_port}",
            f"-MaxPlayers={max_players}",
            "-WinLiveMaxPlayers=10",
            "-server",
            "-log"
        ]
    
    def start(self, map_name: str = "TheIsland_WP", game_port: int = 7777,
              query_port: int = 27015, max_players: int = 10) -> bool:
        """Start the server"""
        if self.is_running():
            print("Server is already running")
            return False
        
        try:
            cmd = self._build_command(map_name, game_port, query_port, max_players)
            
            print("\n=== Starting ARK Server ===")
            print(f"Command: {' '.join(cmd)}\n")
            
            self.process = subprocess.Popen(cmd, cwd=str(self.server_dir))
            
            print(f"✓ Server started (PID: {self.process.pid})")
            print("  Server output will appear in this console")
            print("  Check logs in: ShooterGame/Saved/Logs/")
            return True
            
        except Exception as e:
            print(f"ERROR: Failed to start server: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop the server gracefully"""
        if not self.is_running():
            print("Server is not running")
            return False
        
        try:
            print("Stopping server gracefully...")
            self.process.terminate()
            self.process.wait(timeout=30)
            print("✓ Server stopped")
            self.process = None
            return True
        except subprocess.TimeoutExpired:
            print("WARNING: Graceful shutdown timed out, forcing...")
            self.process.kill()
            self.process = None
            return True
        except Exception as e:
            print(f"ERROR: Failed to stop server: {e}")
            return False