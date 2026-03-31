#!/usr/bin/env python3
"""
Configuration file for Laptop-Controlled Vehicle System
All configurable parameters in one place
"""

# ==============================================================================
# GPIO Pin Configuration (IBT_2 Motor Driver)
# ==============================================================================
MOTOR_RPWM = 4       # GPIO 4 (Physical pin 7) - Forward PWM
MOTOR_LPWM = 17      # GPIO 17 (Physical pin 11) - Backward PWM
MOTOR_R_EN = 18      # GPIO 18 (Physical pin 12) - Right Enable
MOTOR_L_EN = 27      # GPIO 27 (Physical pin 13) - Left Enable
PWM_FREQUENCY = 1000 # Hz

# ==============================================================================
# Serial Configuration (Arduino Communication)
# ==============================================================================
SERIAL_PORT = '/dev/ttyUSB0'  # Arduino serial port
SERIAL_BAUD = 115200          # Baud rate (must match Arduino sketch)
SERIAL_TIMEOUT = 0.05         # Timeout in seconds (50ms for fast response)

# ==============================================================================
# Network Configuration (Laptop Communication)
# ==============================================================================
SERVER_HOST = '0.0.0.0'  # Listen on all network interfaces
SERVER_PORT = 5555       # TCP port for laptop connection

# ==============================================================================
# Distance Thresholds (centimeters)
# ==============================================================================
DISTANCE_SAFE = 300            # >= 300cm: Full speed (100%)
DISTANCE_WARNING = 200         # 200-299cm: Reduced speed (60%)
DISTANCE_CRITICAL = 100        # 100-199cm: Very slow (30%)
DISTANCE_EMERGENCY_FRONT = 50  # < 50cm (front): STOP (0%)
DISTANCE_EMERGENCY_BACK = 80   # < 80cm (back): STOP (0%)

# ==============================================================================
# Speed Settings (percentage 0-100)
# ==============================================================================
SPEED_FULL = 100         # Full speed (no obstacles)
SPEED_MODERATE = 60      # Moderate speed (warning level)
SPEED_SLOW = 30          # Slow speed (critical level)
SPEED_STOP = 0           # Stopped

# ==============================================================================
# Control Loop Timing
# ==============================================================================
CONTROL_LOOP_HZ = 20     # Main control loop frequency (Hz) - Optimal balance: fast response, stable
STATUS_UPDATE_HZ = 10    # Status update frequency (Hz)
CONTROL_LOOP_INTERVAL = 1.0 / CONTROL_LOOP_HZ  # Loop interval in seconds

# ==============================================================================
# Safety Settings
# ==============================================================================
WATCHDOG_TIMEOUT = 2.0   # Seconds - stop motor if no command received
CONNECTION_TIMEOUT = 5.0 # Seconds - reconnect attempt interval
MAX_SENSOR_DISTANCE = 400.0  # Maximum valid sensor reading (cm)
MIN_SENSOR_DISTANCE = 2.0    # Minimum valid sensor reading (cm)

# ==============================================================================
# Sensor Configuration
# ==============================================================================
# All sensors connected to Arduino (6 sensors total):
#   FL = Front Left
#   FR = Front Right
#   FW = Front Waterproof (center)
#   BC = Back Center
#   LS = Left Side
#   RS = Right Side

# Sensors by position
FRONT_SENSORS = ['FL', 'FR', 'FW']          # 3 front sensors
BACK_SENSORS = ['BC']                        # 1 back sensor
SIDE_SENSORS = ['LS', 'RS']                  # 2 side sensors

ALL_SENSORS = ['FL', 'FR', 'FW', 'BC', 'LS', 'RS']  # All 6 sensors from Arduino

# ==============================================================================
# Alert Levels
# ==============================================================================
ALERT_CLEAR = 'CLEAR'        # No obstacles (>= 300cm)
ALERT_WARNING = 'WARNING'    # Obstacle detected (100-299cm)
ALERT_CRITICAL = 'CRITICAL'  # Very close obstacle (30-99cm)
ALERT_EMERGENCY = 'EMERGENCY'  # Immediate danger (< 30cm)

# ==============================================================================
# Command Types
# ==============================================================================
CMD_FORWARD = 'FORWARD'
CMD_BACKWARD = 'BACKWARD'
CMD_STOP = 'STOP'
CMD_EMERGENCY = 'EMERGENCY'
CMD_STATUS = 'STATUS'

VALID_COMMANDS = [CMD_FORWARD, CMD_BACKWARD, CMD_STOP, CMD_EMERGENCY, CMD_STATUS]
