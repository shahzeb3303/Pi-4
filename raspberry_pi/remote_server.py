#!/usr/bin/env python3
"""
Remote Server
TCP socket server for receiving commands from laptop
"""

import socket
import json
import threading
import time
from datetime import datetime
import config

class RemoteServer:
    """
    TCP socket server for remote control from laptop
    """

    def __init__(self):
        """Initialize remote server"""
        self.server_socket = None
        self.client_socket = None
        self.client_address = None
        self.is_running = False
        self.is_client_connected = False

        # Latest command from client
        self.latest_command = config.CMD_STOP
        self.command_timestamp = time.time()
        self.lock = threading.Lock()

        # Server thread
        self.server_thread = None
        self.client_thread = None

    def start_server(self):
        """Start TCP server"""
        if self.is_running:
            print("[RemoteServer] Server already running")
            return

        # Create socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.server_socket.bind((config.SERVER_HOST, config.SERVER_PORT))
            self.server_socket.listen(1)
            self.is_running = True

            print(f"[RemoteServer] Server started on {config.SERVER_HOST}:{config.SERVER_PORT}")
            print("[RemoteServer] Waiting for laptop connection...")

            # Start server thread
            self.server_thread = threading.Thread(target=self._accept_connections, daemon=True)
            self.server_thread.start()

        except Exception as e:
            print(f"[RemoteServer] Failed to start server: {e}")
            self.is_running = False

    def _accept_connections(self):
        """Accept incoming client connections (runs in thread)"""
        while self.is_running:
            try:
                # Accept connection (blocking)
                self.server_socket.settimeout(1.0)  # Timeout to check is_running flag
                try:
                    client_sock, client_addr = self.server_socket.accept()
                except socket.timeout:
                    continue

                print(f"[RemoteServer] Client connected from {client_addr}")

                with self.lock:
                    # Close previous client if exists
                    if self.client_socket:
                        try:
                            self.client_socket.close()
                        except:
                            pass

                    self.client_socket = client_sock
                    self.client_address = client_addr
                    self.is_client_connected = True

                # Handle client in separate thread
                self.client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_sock, client_addr),
                    daemon=True
                )
                self.client_thread.start()

            except Exception as e:
                if self.is_running:
                    print(f"[RemoteServer] Error accepting connection: {e}")
                time.sleep(1)

    def _handle_client(self, client_sock, client_addr):
        """Handle client connection (runs in thread)"""
        try:
            while self.is_running and self.is_client_connected:
                try:
                    # Receive data from client
                    client_sock.settimeout(0.5)  # Short timeout for responsiveness
                    try:
                        data = client_sock.recv(1024)
                    except socket.timeout:
                        continue

                    if not data:
                        # Client disconnected
                        print(f"[RemoteServer] Client {client_addr} disconnected")
                        break

                    # Parse JSON command
                    try:
                        message = json.loads(data.decode('utf-8'))
                        command = message.get('command', config.CMD_STOP)

                        # Validate command
                        if command in config.VALID_COMMANDS:
                            with self.lock:
                                self.latest_command = command
                                self.command_timestamp = time.time()
                            print(f"[RemoteServer] Received command: {command}")  # DEBUG: Show received commands
                        else:
                            print(f"[RemoteServer] Invalid command: {command}")

                    except json.JSONDecodeError as e:
                        print(f"[RemoteServer] Invalid JSON: {e}")

                except Exception as e:
                    if self.is_running:
                        print(f"[RemoteServer] Error handling client: {e}")
                    break

        finally:
            # Client disconnected
            with self.lock:
                self.is_client_connected = False
                self.latest_command = config.CMD_STOP  # Stop on disconnect
                try:
                    client_sock.close()
                except:
                    pass
            print(f"[RemoteServer] Connection closed: {client_addr}")

    def get_latest_command(self):
        """
        Get latest command from client

        Returns:
            str: Latest command (FORWARD, BACKWARD, STOP, etc.)

        Note: Implements watchdog - returns STOP if no command received recently
        """
        with self.lock:
            # Check watchdog timeout
            if time.time() - self.command_timestamp > config.WATCHDOG_TIMEOUT:
                if self.latest_command != config.CMD_STOP:
                    print("[RemoteServer] Watchdog timeout - stopping for safety")
                    self.latest_command = config.CMD_STOP

            return self.latest_command

    def send_status(self, status_dict):
        """
        Send status update to connected client

        Args:
            status_dict (dict): Status information to send
        """
        if not self.is_client_connected or not self.client_socket:
            return

        try:
            # Add timestamp
            status_dict['timestamp'] = datetime.now().isoformat()

            # Convert to JSON and send
            message = json.dumps(status_dict) + '\n'
            self.client_socket.sendall(message.encode('utf-8'))

        except Exception as e:
            # Client probably disconnected
            # print(f"[RemoteServer] Error sending status: {e}")
            pass

    def is_connected(self):
        """
        Check if client is connected

        Returns:
            bool: True if client is connected
        """
        with self.lock:
            return self.is_client_connected

    def stop_server(self):
        """Stop server and close all connections"""
        print("[RemoteServer] Stopping server...")
        self.is_running = False

        # Close client connection
        with self.lock:
            if self.client_socket:
                try:
                    self.client_socket.close()
                except:
                    pass
                self.client_socket = None
            self.is_client_connected = False

        # Close server socket
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None

        # Wait for threads to finish
        if self.server_thread:
            self.server_thread.join(timeout=2.0)
        if self.client_thread:
            self.client_thread.join(timeout=2.0)

        print("[RemoteServer] Server stopped")


# Test code - run this file directly to test remote server
if __name__ == "__main__":
    print("Testing Remote Server...")
    print(f"Server will listen on port {config.SERVER_PORT}")
    print("Use laptop/remote_control.py to connect\n")

    server = RemoteServer()

    try:
        server.start_server()

        print("Server running. Monitoring commands for 60 seconds...")
        print("Connect from laptop and send commands\n")

        for i in range(60):
            cmd = server.get_latest_command()
            connected = server.is_connected()

            print(f"[{i+1}/60] Connected: {connected}, Command: {cmd}")

            # Simulate sending status back
            if connected:
                status = {
                    'current_command': cmd,
                    'actual_speed': 50,
                    'test_message': f'Status update {i+1}'
                }
                server.send_status(status)

            time.sleep(1)

        print("\nTest complete!")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        server.stop_server()
