#!/usr/bin/env python3
"""
Main Integration Script
Integrates motor control, obstacle monitoring, and remote server
"""

import time
import signal
import sys
from datetime import datetime

import config
from motor_controller import MotorController
from obstacle_monitor import ObstacleMonitor
from remote_server import RemoteServer

class VehicleController:
    """
    Main vehicle controller - integrates all subsystems
    """

    def __init__(self):
        """Initialize vehicle controller"""
        self.motor_controller = MotorController()
        self.obstacle_monitor = ObstacleMonitor()
        self.remote_server = RemoteServer()
        self.running = False

        # State tracking
        self.current_command = config.CMD_STOP
        self.actual_speed = 0
        self.requested_speed = 100

        # TEST MODE - Set to True to automatically move forward for testing
        self.TEST_MODE = False  # Changed back to normal mode
        self.test_speed = 50  # Test speed percentage

    def initialize(self):
        """Initialize all subsystems"""
        print("=" * 60)
        print("VEHICLE CONTROL SYSTEM - INITIALIZATION")
        print("=" * 60)

        try:
            # Initialize motor controller
            print("\n[1/3] Initializing motor controller...")
            self.motor_controller.setup()
            print("✓ Motor controller ready")

            # Initialize obstacle monitor
            print("\n[2/3] Initializing obstacle monitor...")
            self.obstacle_monitor.start_monitoring()
            print("✓ Obstacle monitor ready")

            # Initialize remote server
            print("\n[3/3] Starting remote server...")
            self.remote_server.start_server()
            print("✓ Remote server ready")

            print("\n" + "=" * 60)
            print("INITIALIZATION COMPLETE")
            print("=" * 60)

            if self.TEST_MODE:
                print("\n*** TEST MODE ENABLED ***")
                print(f"Motor will automatically move FORWARD at {self.test_speed}% speed")
                print("This bypasses laptop control and obstacle detection")
                print("Use this to verify motor hardware is working")
                print("\nPress Ctrl+C to stop")
            else:
                print("\nWaiting for laptop connection...")
                print(f"Laptop should connect to: <Pi IP Address>:{config.SERVER_PORT}")
                print("\nPress Ctrl+C to stop")

            print("=" * 60 + "\n")

            return True

        except Exception as e:
            print(f"\n✗ Initialization failed: {e}")
            return False

    def start(self):
        """Start main control loop"""
        if not self.initialize():
            print("Failed to initialize. Exiting.")
            return

        self.running = True

        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Main control loop
        self._control_loop()

    def _control_loop(self):
        """Main control loop (10Hz)"""
        loop_count = 0

        while self.running:
            try:
                loop_start = time.time()

                # 1. Get command from remote server (or use test mode)
                if self.TEST_MODE:
                    # TEST MODE: Automatically move forward at test speed
                    self.current_command = config.CMD_FORWARD
                    safe_speed = self.test_speed  # Fixed test speed, ignore obstacles for testing
                    alert = "TEST_MODE"
                else:
                    # Normal mode: Get command from laptop
                    self.current_command = self.remote_server.get_latest_command()

                    # 2. Get safe speed from obstacle monitor
                    if self.current_command == config.CMD_FORWARD:
                        safe_speed = self.obstacle_monitor.get_safe_speed(config.CMD_FORWARD)
                        alert = self.obstacle_monitor.get_alert_status(config.CMD_FORWARD)
                    elif self.current_command == config.CMD_BACKWARD:
                        safe_speed = self.obstacle_monitor.get_safe_speed(config.CMD_BACKWARD)
                        alert = self.obstacle_monitor.get_alert_status(config.CMD_BACKWARD)
                    elif self.current_command == config.CMD_EMERGENCY:
                        safe_speed = 0
                        alert = config.ALERT_EMERGENCY
                    else:  # STOP
                        safe_speed = 0
                        alert = config.ALERT_CLEAR

                # Store actual speed
                self.actual_speed = safe_speed

                # 3. Apply speed to motor controller
                self.motor_controller.set_speed(self.current_command, safe_speed)

                # 4. Get all distances
                distances = self.obstacle_monitor.get_all_distances()
                min_front = self.obstacle_monitor.get_minimum_distance('front')
                min_back = self.obstacle_monitor.get_minimum_distance('back')

                # 5. Build status dictionary
                status = {
                    'current_command': self.current_command,
                    'actual_speed': self.actual_speed,
                    'requested_speed': self.requested_speed,
                    'alert_level': alert,
                    'distances': distances,
                    'min_distance_front': min_front if min_front else 0,
                    'min_distance_back': min_back if min_back else 0,
                    'connected': self.remote_server.is_connected()
                }

                # 6. Send status back to laptop
                if self.remote_server.is_connected():
                    self.remote_server.send_status(status)

                # 7. Print status (every 7 loops = ~3 times per second at 20Hz)
                loop_count += 1
                if loop_count % 7 == 0:
                    self._print_status(status)

                # DEBUG: Print every command and speed (comment out after debugging)
                if loop_count % 10 == 0:  # Every 0.5 seconds at 20Hz
                    print(f"[DEBUG] Command={self.current_command}, Safe Speed={safe_speed}%, Alert={alert}")

                # 8. Sleep to maintain loop frequency
                elapsed = time.time() - loop_start
                sleep_time = max(0, config.CONTROL_LOOP_INTERVAL - elapsed)
                time.sleep(sleep_time)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"\n[ERROR] Control loop error: {e}")
                # Don't stop completely, try to continue
                time.sleep(0.1)

    def _print_status(self, status):
        """Print status to console"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        connected = "CONNECTED" if status['connected'] else "DISCONNECTED"

        print(f"[{timestamp}] {connected:12s} | "
              f"Cmd: {status['current_command']:8s} | "
              f"Speed: {status['actual_speed']:3d}% | "
              f"Alert: {status['alert_level']:9s} | "
              f"Front: {status['min_distance_front']:6.1f}cm | "
              f"Back: {status['min_distance_back']:6.1f}cm")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\n\nReceived shutdown signal...")
        self.stop()

    def stop(self):
        """Stop all subsystems"""
        if not self.running:
            return

        print("\n" + "=" * 60)
        print("SHUTTING DOWN")
        print("=" * 60)

        self.running = False

        # Stop motor first (safety)
        print("\n[1/4] Stopping motor...")
        try:
            self.motor_controller.stop()
            print("✓ Motor stopped")
        except Exception as e:
            print(f"✗ Error stopping motor: {e}")

        # Stop remote server
        print("\n[2/4] Stopping remote server...")
        try:
            self.remote_server.stop_server()
            print("✓ Remote server stopped")
        except Exception as e:
            print(f"✗ Error stopping server: {e}")

        # Stop obstacle monitor
        print("\n[3/4] Stopping obstacle monitor...")
        try:
            self.obstacle_monitor.stop_monitoring()
            print("✓ Obstacle monitor stopped")
        except Exception as e:
            print(f"✗ Error stopping monitor: {e}")

        # Cleanup motor controller GPIO
        print("\n[4/4] Cleaning up GPIO...")
        try:
            self.motor_controller.cleanup()
            print("✓ GPIO cleanup complete")
        except Exception as e:
            print(f"✗ Error cleaning up GPIO: {e}")

        print("\n" + "=" * 60)
        print("SHUTDOWN COMPLETE")
        print("=" * 60 + "\n")


def main():
    """Main entry point"""
    print("\n")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                                                            ║")
    print("║       LAPTOP-CONTROLLED VEHICLE CONTROL SYSTEM             ║")
    print("║                                                            ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    # Create and start controller
    controller = VehicleController()

    try:
        controller.start()
    except Exception as e:
        print(f"\nFatal error: {e}")
    finally:
        controller.stop()
        print("\nGoodbye!\n")


if __name__ == "__main__":
    main()
