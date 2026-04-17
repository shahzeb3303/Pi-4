#!/usr/bin/env python3
"""
Obstacle Monitor
Monitors ultrasonic sensor distances and calculates safe speeds
Integrates sensors from Arduino (5 sensors) + Pi waterproof sensor (1 sensor) = 6 total
"""

import sys
import os
import time
import threading

# Add path to import from existing autonomous vehicle project
sys.path.append('/home/sherry007/AUTONOMOUS SOLAR VEHICLE/raspberry_pi')

from sensor_reader import UltrasonicSensorReader
import config

class ObstacleMonitor:
    """
    Monitors obstacles and calculates safe speeds based on distance thresholds
    All 6 sensors connected to Arduino
    """

    def __init__(self):
        """Initialize obstacle monitor"""
        # Arduino sensors (6 sensors: FL, FR, FW, BC, LS, RS)
        # Pass port and baudrate to constructor
        self.sensor_reader = UltrasonicSensorReader(
            port=config.SERIAL_PORT,
            baudrate=config.SERIAL_BAUD
        )

        self.is_monitoring = False
        self.lock = threading.Lock()

    def start_monitoring(self):
        """Start sensor monitoring"""
        if self.is_monitoring:
            print("[ObstacleMonitor] Already monitoring")
            return

        # Connect to Arduino (6 sensors)
        print("[ObstacleMonitor] Connecting to Arduino...")
        if not self.sensor_reader.connect():
            raise RuntimeError("Failed to connect to Arduino")

        # Start reading Arduino sensors
        self.sensor_reader.start_reading()

        self.is_monitoring = True
        print("[ObstacleMonitor] Monitoring started (6 sensors from Arduino)")

    def stop_monitoring(self):
        """Stop sensor monitoring"""
        if not self.is_monitoring:
            return

        print("[ObstacleMonitor] Stopping monitoring...")

        # Stop Arduino sensors
        self.sensor_reader.stop_reading()

        self.is_monitoring = False
        print("[ObstacleMonitor] Monitoring stopped")

    def get_all_distances(self):
        """
        Get distances from all 6 sensors from Arduino

        Returns:
            dict: Dictionary with sensor names as keys and distances as values
                  FL, FR, FW, BC, LS, RS (all from Arduino)
        """
        # Get all sensor data from Arduino (6 sensors)
        return self.sensor_reader.get_latest_data()

    def get_minimum_distance(self, direction):
        """
        Get minimum distance in specified direction

        Args:
            direction (str): 'front', 'back', or 'all'

        Returns:
            float: Minimum distance in cm (or None if no valid readings)

        TEMPORARY: Ignoring FW, LS, RS sensors - only using FL, FR, BC
        """
        all_distances = self.get_all_distances()

        # TEMPORARY: Only use specific sensors (ignore FW, LS, RS)
        if direction == 'front':
            sensors_to_check = ['FL', 'FR']  # ONLY front left and right (ignore FW)
        elif direction == 'back':
            sensors_to_check = ['BC']  # ONLY back center
        else:  # 'all'
            sensors_to_check = ['FL', 'FR', 'BC']  # Only these 3 (ignore FW, LS, RS)

        # Get valid distances for these sensors
        valid_distances = []
        for sensor in sensors_to_check:
            dist = all_distances.get(sensor, 0)
            # Validate distance
            if config.MIN_SENSOR_DISTANCE <= dist <= config.MAX_SENSOR_DISTANCE:
                valid_distances.append(dist)

        # Return minimum or None if no valid readings
        if valid_distances:
            return min(valid_distances)
        else:
            return None

    def get_safe_speed(self, direction):
        """
        Calculate safe speed based on obstacle distance

        Args:
            direction (str): 'FORWARD' or 'BACKWARD'

        Returns:
            int: Safe speed percentage (0-100)

        Speed Logic:
            Distance >= 300cm:     100% speed (full speed)
            200cm <= Distance < 300cm:  60% speed (moderate)
            100cm <= Distance < 200cm:  30% speed (slow)
            Distance < 50cm (front) OR < 80cm (back): 0% speed (STOP)
        """
        # Map command direction to sensor direction
        if direction == config.CMD_FORWARD:
            sensor_direction = 'front'
            emergency_threshold = config.DISTANCE_EMERGENCY_FRONT  # 50cm for front
        elif direction == config.CMD_BACKWARD:
            sensor_direction = 'back'
            emergency_threshold = config.DISTANCE_EMERGENCY_BACK  # 80cm for back
        else:
            return config.SPEED_STOP

        # Get minimum distance in this direction
        min_distance = self.get_minimum_distance(sensor_direction)

        # If no valid reading, allow full speed — no data means no confirmed obstacle
        if min_distance is None or min_distance <= 0:
            return config.SPEED_FULL

        # Apply speed thresholds
        if min_distance >= config.DISTANCE_SAFE:
            return config.SPEED_FULL  # >= 300cm: Full speed (100%)
        elif min_distance >= config.DISTANCE_WARNING:
            return config.SPEED_MODERATE  # 200-299cm: Moderate speed (60%)
        elif min_distance >= config.DISTANCE_CRITICAL:
            return config.SPEED_SLOW  # 100-199cm: Slow speed (30%)
        elif min_distance >= emergency_threshold:
            return config.SPEED_SLOW  # Between 100cm and emergency: Slow (30%)
        else:
            return config.SPEED_STOP  # < 50cm (front) or < 80cm (back): STOP

    def get_alert_status(self, direction):
        """
        Get alert level based on obstacle distance

        Args:
            direction (str): 'FORWARD' or 'BACKWARD'

        Returns:
            str: Alert level - 'CLEAR', 'WARNING', 'CRITICAL', or 'EMERGENCY'
        """
        # Map command direction to sensor direction and get emergency threshold
        if direction == config.CMD_FORWARD:
            sensor_direction = 'front'
            emergency_threshold = config.DISTANCE_EMERGENCY_FRONT  # 50cm for front
        elif direction == config.CMD_BACKWARD:
            sensor_direction = 'back'
            emergency_threshold = config.DISTANCE_EMERGENCY_BACK  # 80cm for back
        else:
            return config.ALERT_CLEAR

        # Get minimum distance
        min_distance = self.get_minimum_distance(sensor_direction)

        # If no valid reading, return clear — no data means no confirmed obstacle
        if min_distance is None or min_distance <= 0:
            return config.ALERT_CLEAR

        # Determine alert level
        if min_distance >= config.DISTANCE_SAFE:
            return config.ALERT_CLEAR  # >= 300cm: No obstacles
        elif min_distance >= config.DISTANCE_WARNING:
            return config.ALERT_WARNING  # 200-299cm: Warning
        elif min_distance >= config.DISTANCE_CRITICAL:
            return config.ALERT_CRITICAL  # 100-199cm: Critical
        elif min_distance >= emergency_threshold:
            return config.ALERT_CRITICAL  # Between 100cm and emergency: Critical
        else:
            return config.ALERT_EMERGENCY  # < 50cm (front) or < 80cm (back): Emergency

    def get_obstacle_status(self, threshold_cm=None):
        """
        Get which sensors detect obstacles below threshold

        Args:
            threshold_cm (float): Distance threshold in cm (default: DISTANCE_CRITICAL)

        Returns:
            dict: Dictionary with boolean values for each sensor
        """
        if threshold_cm is None:
            threshold_cm = config.DISTANCE_CRITICAL

        all_distances = self.get_all_distances()
        status = {}

        for sensor, distance in all_distances.items():
            status[sensor] = (distance < threshold_cm and distance > 0)

        return status

    def get_detailed_status(self, direction):
        """
        Get detailed status including distances, speed, and alert

        Args:
            direction (str): 'FORWARD' or 'BACKWARD'

        Returns:
            dict: Detailed status information
        """
        all_distances = self.get_all_distances()
        safe_speed = self.get_safe_speed(direction)
        alert = self.get_alert_status(direction)

        # Get minimum distance per direction
        min_front = self.get_minimum_distance('front')
        min_back = self.get_minimum_distance('back')

        return {
            'distances': all_distances,
            'safe_speed': safe_speed,
            'alert_level': alert,
            'min_distance_front': min_front if min_front else 0,
            'min_distance_back': min_back if min_back else 0
        }


# Test code - run this file directly to test obstacle monitor
if __name__ == "__main__":
    print("Testing Obstacle Monitor...")
    print("Make sure Arduino is connected with 5 sensors!")
    print("Make sure waterproof sensor is connected to Pi GPIO!\n")

    om = ObstacleMonitor()

    try:
        om.start_monitoring()

        print("Monitoring obstacles for 20 seconds...")
        print("Move objects in front of sensors to see speed adjustments\n")

        for i in range(20):
            # Test for forward direction
            safe_speed_fwd = om.get_safe_speed(config.CMD_FORWARD)
            alert_fwd = om.get_alert_status(config.CMD_FORWARD)
            distances = om.get_all_distances()
            min_front = om.get_minimum_distance('front')
            min_back = om.get_minimum_distance('back')

            print(f"[{i+1}/20] Forward Speed: {safe_speed_fwd:3d}%, Alert: {alert_fwd:9s}, "
                  f"Min Front: {min_front:6.1f}cm, Min Back: {min_back:6.1f}cm")

            # Display all 6 sensors
            fl = distances.get('FL', 0)
            fr = distances.get('FR', 0)
            fw = distances.get('FW', 0)
            bc = distances.get('BC', 0)
            ls = distances.get('LS', 0)
            rs = distances.get('RS', 0)

            print(f"        Front:  FL={fl:6.1f}  FW={fw:6.1f}  FR={fr:6.1f}")
            print(f"        Back:   BC={bc:6.1f}")
            print(f"        Sides:  LS={ls:6.1f}  RS={rs:6.1f}")
            print()

            time.sleep(1)

        print("Test complete!")

    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        om.stop_monitoring()
