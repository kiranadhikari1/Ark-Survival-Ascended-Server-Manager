"""
Log viewing utility
"""

import os
from pathlib import Path
from datetime import datetime


class LogViewer:
    """View and display server logs"""
    
    def __init__(self, server_dir: Path):
        self.log_dir = server_dir / "ShooterGame" / "Saved" / "Logs"
    
    def show(self):
        """Display log viewer menu"""
        if not self.log_dir.exists():
            print("No logs found. Server may not have been started yet.")
            return
        
        print("\n=== Server Logs ===")
        print(f"Log directory: {self.log_dir}\n")
        
        log_files = sorted(self.log_dir.glob("*.log"), 
                          key=lambda p: p.stat().st_mtime, 
                          reverse=True)
        
        if not log_files:
            print("No log files found")
            return
        
        print("Recent log files:")
        for i, log_file in enumerate(log_files[:10], 1):
            size_kb = log_file.stat().st_size / 1024
            modified = datetime.fromtimestamp(log_file.stat().st_mtime)
            print(f"{i}. {log_file.name} ({size_kb:.1f} KB, {modified.strftime('%Y-%m-%d %H:%M')})")
        
        print("\nOptions:")
        print("1. View tail of most recent log")
        print("2. Open log directory in explorer")
        print("3. Cancel")
        
        choice = input("\nChoice: ").strip()
        
        if choice == '1' and log_files:
            self._tail_log(log_files[0])
        elif choice == '2':
            try:
                os.startfile(self.log_dir)
            except Exception as e:
                print(f"Could not open directory: {e}")
                print(f"Manual path: {self.log_dir}")
    
    def _tail_log(self, log_file: Path, lines: int = 50):
        """Display last N lines of log"""
        try:
            print(f"\n=== Last {lines} lines of {log_file.name} ===\n")
            
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                all_lines = f.readlines()
                tail_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
                
                for line in tail_lines:
                    print(line.rstrip())
            
            print(f"\n=== End of log ===")
            
        except Exception as e:
            print(f"Error reading log file: {e}")