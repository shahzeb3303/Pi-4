#!/usr/bin/env python3
"""
Laptop Remote Control - FIXED VERSION
Continuously sends commands while keys are held
"""

import socket
import json
import threading
import time
import sys
import os
from datetime import datetime

# Check if pynput is installed
try:
    from pynput import keyboard
except ImportError:
    print("ERROR: pynput library not installed")
    print("Please install it with: pip install pynput")
    sys.exit(1)

# Configuration
PI_IP = input("Enter Raspberry Pi IP address (e.g., 192.168.1.100): ").strip()
PI_PORT = 5555

# Commands
CMD_FORWARD = 'FORWARD'
CMD_BACKWARD = 'BACKWARD'
CMD_LEFT = 'LEFT'
CMD_RIGHT = 'RIGHT'
CMD_STEER_STOP = 'STEER_STOP'
CMD_STOP = 'STOP'
CMD_EMERGENCY = 'EMERGENCY'
CMD_AUTONOMOUS = 'AUTONOMOUS'

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'

class RemoteControl:
    """
    Remote control client with continuous command sending
    """

    def __init__(self, pi_ip, pi_port):
        """Initialize remote control"""
        self.pi_ip = pi_ip
        self.pi_port = pi_port
        self.sock = None
        self.connected = False
        self.running = True

        # Current command (press once to set, stays until changed)
        self.current_command = CMD_STOP
        self.current_steer = CMD_STEER_STOP
        self.autonomous_mode = False
        self.command_lock = threading.Lock()
        self.status = None
        self.status_lock = threading.Lock()

        # Threads
        self.receive_thread = None
        self.display_thread = None
        self.command_thread = None

    def connect(self):
        """Connect to Raspberry Pi"""
        print(f"\nConnecting to Raspberry Pi at {self.pi_ip}:{self.pi_port}...")

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            self.sock.connect((self.pi_ip, self.pi_port))
            self.sock.settimeout(0.5)
            self.connected = True
            print(f"{Colors.GREEN}✓ Connected!{Colors.RESET}\n")
            return True

        except Exception as e:
            print(f"{Colors.RED}✗ Connection failed: {e}{Colors.RESET}")
            self.connected = False
            return False

    def disconnect(self):
        """Disconnect from Raspberry Pi"""
        self.connected = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

    def send_command(self, command):
        """Send command to Raspberry Pi"""
        if not self.connected:
            return False

        try:
            message = json.dumps({'command': command})
            self.sock.sendall(message.encode('utf-8'))
            return True

        except Exception as e:
            self.connected = False
            return False

    def command_sender_loop(self):
        """Continuously send current command (runs in thread)"""
        while self.running and self.connected:
            try:
                with self.command_lock:
                    cmd = self.current_command
                    steer = self.current_steer

                # Send drive command
                self.send_command(cmd)

                # Send steer command if steering
                if steer != CMD_STEER_STOP:
                    time.sleep(0.05)
                    self.send_command(steer)

                # Send every 0.5 seconds (faster than 2-second watchdog)
                time.sleep(0.5)

            except Exception as e:
                if self.running:
                    self.connected = False
                break

    def receive_status(self):
        """Receive status updates from Pi (runs in thread)"""
        buffer = ""

        while self.running and self.connected:
            try:
                data = self.sock.recv(4096)
                if not data:
                    self.connected = False
                    break

                buffer += data.decode('utf-8')

                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    try:
                        status = json.loads(line)
                        with self.status_lock:
                            self.status = status
                    except json.JSONDecodeError:
                        pass

            except socket.timeout:
                continue
            except Exception as e:
                if self.running:
                    self.connected = False
                break

    def get_alert_color(self, alert_level):
        """Get color for alert level"""
        if alert_level == 'CLEAR':
            return Colors.GREEN
        elif alert_level == 'WARNING':
            return Colors.YELLOW
        elif alert_level == 'CRITICAL':
            return Colors.MAGENTA
        elif alert_level == 'EMERGENCY':
            return Colors.RED
        else:
            return Colors.RESET

    def display_status(self):
        """Display status in terminal (runs in thread)"""
        while self.running:
            # Clear screen
            os.system('clear' if os.name != 'nt' else 'cls')

            # Header
            print(Colors.BOLD + "╔" + "═" * 62 + "╗" + Colors.RESET)
            print(Colors.BOLD + "║" + " " * 16 + "VEHICLE REMOTE CONTROL" + " " * 24 + "║" + Colors.RESET)
            print(Colors.BOLD + "╠" + "═" * 62 + "╣" + Colors.RESET)

            # Mode display
            if self.status:
                mode = self.status.get('mode', 'MANUAL')
                auto_state = self.status.get('auto_state', '')
            else:
                mode = "AUTO" if self.autonomous_mode else "MANUAL"
                auto_state = ""

            if mode == "AUTO":
                mode_text = f"{Colors.GREEN}AUTONOMOUS{Colors.RESET}"
                if auto_state:
                    mode_text += f" - {Colors.CYAN}{auto_state}{Colors.RESET}"
            else:
                mode_text = f"{Colors.YELLOW}MANUAL{Colors.RESET}"

            print(f"║  Mode: {mode_text:55s}    ║")
            print(Colors.BOLD + "╠" + "═" * 62 + "╣" + Colors.RESET)

            # Connection status
            if self.connected:
                conn_text = f"{Colors.GREEN}CONNECTED{Colors.RESET} to {self.pi_ip}"
            else:
                conn_text = f"{Colors.RED}DISCONNECTED{Colors.RESET}"

            print(f"║  Connection: {conn_text:45s}     ║")
            print(Colors.BOLD + "╠" + "═" * 62 + "╣" + Colors.RESET)

            # Status from Pi
            if self.status:
                with self.status_lock:
                    cmd = self.status.get('current_command', 'UNKNOWN')
                    actual_speed = self.status.get('actual_speed', 0)
                    requested_speed = self.status.get('requested_speed', 0)
                    alert = self.status.get('alert_level', 'UNKNOWN')
                    distances = self.status.get('distances', {})
                    min_front = self.status.get('min_distance_front', 0)
                    min_back = self.status.get('min_distance_back', 0)

                # Command and speed
                steer = self.status.get('current_steer', 'STRAIGHT')
                cmd_color = Colors.CYAN if cmd in [CMD_FORWARD, CMD_BACKWARD] else Colors.RESET
                steer_color = Colors.MAGENTA if steer in [CMD_LEFT, CMD_RIGHT] else Colors.RESET
                print(f"║  Drive: {cmd_color}{cmd:8s}{Colors.RESET}  "
                      f"Steer: {steer_color}{steer:10s}{Colors.RESET}  "
                      f"Speed: {actual_speed:3d}%          ║")

                # Alert
                alert_color = self.get_alert_color(alert)
                alert_text = f"{alert_color}{alert}{Colors.RESET}"
                padding = " " * (9 - len(alert))
                print(f"║  Alert: {alert_text}{padding}                                             ║")

                print(Colors.BOLD + "╠" + "═" * 62 + "╣" + Colors.RESET)

                # Sensor distances
                print("║  Sensor Distances:                                         ║")

                fl = distances.get('FL', 0)
                fr = distances.get('FR', 0)
                fw = distances.get('FW', 0)
                bc = distances.get('BC', 0)
                ls = distances.get('LS', 0)
                rs = distances.get('RS', 0)

                print(f"║    Front:  FL={fl:5.1f}cm  FW={fw:5.1f}cm  FR={fr:5.1f}cm  "
                      f"[MIN: {min_front:5.1f}cm] ║")
                print(f"║    Back:   BC={bc:5.1f}cm                      "
                      f"[MIN: {min_back:5.1f}cm] ║")
                print(f"║    Sides:  LS={ls:5.1f}cm  RS={rs:5.1f}cm                             ║")

            else:
                print("║  Waiting for status data from Pi...                       ║")

            # Controls
            print(Colors.BOLD + "╠" + "═" * 62 + "╣" + Colors.RESET)
            print("║  Controls:                                                 ║")
            print(f"║    {Colors.GREEN}A{Colors.RESET}              : Toggle Autonomous Mode                 ║")
            print("║    ↑ (Up Arrow)    : Move Forward  (manual only)           ║")
            print("║    ↓ (Down Arrow)  : Move Backward (manual only)           ║")
            print("║    ← (Left Arrow)  : Steer Left    (manual only, HOLD)     ║")
            print("║    → (Right Arrow) : Steer Right   (manual only, HOLD)     ║")
            print("║    SPACE           : Stop All + Exit Auto Mode             ║")
            print("║    ESC             : Emergency Stop & Quit                 ║")
            print(Colors.BOLD + "╚" + "═" * 62 + "╝" + Colors.RESET)

            # Current command indicator
            with self.command_lock:
                cmd_display = self.current_command
                steer_display = self.current_steer

            if cmd_display == CMD_FORWARD:
                cmd_display = f"{Colors.CYAN}↑ FORWARD{Colors.RESET}"
            elif cmd_display == CMD_BACKWARD:
                cmd_display = f"{Colors.CYAN}↓ BACKWARD{Colors.RESET}"
            elif cmd_display == CMD_STOP:
                cmd_display = f"{Colors.YELLOW}■ STOPPED{Colors.RESET}"

            if steer_display == CMD_LEFT:
                steer_display = f"{Colors.MAGENTA}← LEFT{Colors.RESET}"
            elif steer_display == CMD_RIGHT:
                steer_display = f"{Colors.MAGENTA}→ RIGHT{Colors.RESET}"
            else:
                steer_display = f"STRAIGHT"

            print(f"\nDrive: {cmd_display}   Steer: {steer_display}")

            time.sleep(0.1)

    def on_key_press(self, key):
        """Handle key press events - press once to set command"""
        try:
            with self.command_lock:
                # Check for 'A' key to toggle autonomous mode
                if hasattr(key, 'char') and key.char == 'a':
                    self.autonomous_mode = not self.autonomous_mode
                    self.send_command(CMD_AUTONOMOUS)
                    if self.autonomous_mode:
                        self.current_command = CMD_STOP
                        self.current_steer = CMD_STEER_STOP
                    return

                if key == keyboard.Key.up:
                    if self.autonomous_mode:
                        return  # Ignore manual controls in auto mode
                    self.current_command = CMD_FORWARD
                elif key == keyboard.Key.down:
                    if self.autonomous_mode:
                        return
                    self.current_command = CMD_BACKWARD
                elif key == keyboard.Key.left:
                    if self.autonomous_mode:
                        return
                    self.current_steer = CMD_LEFT
                elif key == keyboard.Key.right:
                    if self.autonomous_mode:
                        return
                    self.current_steer = CMD_RIGHT
                elif key == keyboard.Key.space:
                    # Space always works - stops everything and exits auto mode
                    self.autonomous_mode = False
                    self.current_command = CMD_STOP
                    self.current_steer = CMD_STEER_STOP
                elif key == keyboard.Key.esc:
                    self.autonomous_mode = False
                    self.current_command = CMD_EMERGENCY
                    self.send_command(CMD_EMERGENCY)
                    time.sleep(0.2)
                    self.running = False
                    return False

        except Exception as e:
            pass

    def on_key_release(self, key):
        """Handle key release - stop steering when arrow released"""
        try:
            with self.command_lock:
                if key in [keyboard.Key.left, keyboard.Key.right]:
                    self.current_steer = CMD_STEER_STOP
        except Exception as e:
            pass

    def run(self):
        """Main run loop"""
        # Connect to Pi
        if not self.connect():
            print("\nFailed to connect. Please check:")
            print("1. Raspberry Pi IP address is correct")
            print("2. Raspberry Pi is running main.py")
            print("3. Network connection is working")
            return

        # Start receive thread
        self.receive_thread = threading.Thread(target=self.receive_status, daemon=True)
        self.receive_thread.start()

        # Start command sender thread
        self.command_thread = threading.Thread(target=self.command_sender_loop, daemon=True)
        self.command_thread.start()

        # Start display thread
        self.display_thread = threading.Thread(target=self.display_status, daemon=True)
        self.display_thread.start()

        # Wait for first status
        time.sleep(0.5)

        # Start keyboard listener
        print("Starting keyboard listener...")
        with keyboard.Listener(on_press=self.on_key_press, on_release=self.on_key_release) as listener:
            listener.join()

        # Cleanup
        print("\nStopping vehicle...")
        self.send_command(CMD_STOP)
        time.sleep(0.2)
        self.disconnect()
        print("Disconnected.\n")


def main():
    """Main entry point"""
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║           VEHICLE REMOTE CONTROL - FIXED VERSION           ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")

    if not PI_IP:
        print("\nERROR: No IP address provided")
        return

    try:
        controller = RemoteControl(PI_IP, PI_PORT)
        controller.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")

    print("\nGoodbye!\n")


if __name__ == "__main__":
    main()
