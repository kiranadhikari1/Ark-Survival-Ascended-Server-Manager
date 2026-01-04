"""
RCON client for server communication
"""

import socket
import struct
from typing import Optional
from utils.validation import validate_port, sanitize_input
from utils.constants import (
    DEFAULT_RCON_PORT,
    RCON_AUTH, RCON_EXECCOMMAND,
    RCON_AUTH_RESPONSE, RCON_RESPONSE_VALUE
)


class RCONClient:
    """Simple RCON client implementation"""
    
    def __init__(self, host: str = "127.0.0.1", port: int = DEFAULT_RCON_PORT, password: str = ""):
        self.host = host
        self.port = validate_port(port)
        self.password = password
        self.socket: Optional[socket.socket] = None
        self.authenticated = False
    
    def connect(self) -> bool:
        """Connect and authenticate"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(5)
            self.socket.connect((self.host, self.port))
            return self._authenticate()
        except Exception as e:
            print(f"RCON connection failed: {e}")
            return False
    
    def _authenticate(self) -> bool:
        self._send_packet(RCON_AUTH, self.password)
        response = self._receive_packet()
        self.authenticated = response is not None
        return self.authenticated
    
    def send_command(self, command: str) -> Optional[str]:
        """Send command to server"""
        if not self.authenticated:
            print("ERROR: Not authenticated")
            return None
        
        command = sanitize_input(command)
        self._send_packet(RCON_EXECCOMMAND, command)
        response = self._receive_packet()
        return response[1] if response else None
    
    def _send_packet(self, packet_type: int, body: str):
        packet_id = 1
        body_bytes = body.encode('utf-8') + b'\x00\x00'
        length = 4 + 4 + len(body_bytes)
        
        packet = struct.pack('<iii', length, packet_id, packet_type) + body_bytes
        self.socket.sendall(packet)
    
    def _receive_packet(self) -> Optional[tuple]:
        try:
            header = self.socket.recv(12)
            if len(header) < 12:
                return None
            
            length, packet_id, packet_type = struct.unpack('<iii', header)
            body = self.socket.recv(length - 8)
            
            return (packet_id, body.decode('utf-8', errors='ignore').rstrip('\x00'))
        except:
            return None
    
    def disconnect(self):
        if self.socket:
            self.socket.close()
            self.socket = None