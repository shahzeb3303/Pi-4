/*
 * Arduino Ultrasonic Sensor Array for Laptop-Controlled Vehicle
 * HC-SR04 x 5 sensors configuration
 * Sends distance data to Raspberry Pi via Serial
 *
 * Sensor Configuration:
 *   FL = Front Left
 *   FR = Front Right
 *   BC = Back Center
 *   LS = Left Side
 *   RS = Right Side
 *
 * Note: Front Center (FW) is a waterproof sensor connected directly to Raspberry Pi
 */

// Define pins for 5 HC-SR04 sensors

// Front sensors (2 sensors)
#define TRIG_FL 2   // Front-Left Trigger
#define ECHO_FL 3   // Front-Left Echo
#define TRIG_FR 4   // Front-Right Trigger
#define ECHO_FR 5   // Front-Right Echo

// Back sensor (1 sensor)
#define TRIG_BC 6   // Back-Center Trigger
#define ECHO_BC 7   // Back-Center Echo

// Side sensors (2 sensors)
#define TRIG_LS 8   // Left-Side Trigger
#define ECHO_LS 9   // Left-Side Echo
#define TRIG_RS 10  // Right-Side Trigger
#define ECHO_RS 11  // Right-Side Echo

// Maximum distance to measure (in cm)
#define MAX_DISTANCE 400

// Sensor data structure
struct SensorData {
  float frontLeft;
  float frontRight;
  float backCenter;
  float leftSide;
  float rightSide;
};

SensorData distances;

void setup() {
  // Initialize serial communication at 115200 baud
  Serial.begin(115200);

  // Set up all trigger pins as OUTPUT
  pinMode(TRIG_FL, OUTPUT);
  pinMode(TRIG_FR, OUTPUT);
  pinMode(TRIG_BC, OUTPUT);
  pinMode(TRIG_LS, OUTPUT);
  pinMode(TRIG_RS, OUTPUT);

  // Set up all echo pins as INPUT
  pinMode(ECHO_FL, INPUT);
  pinMode(ECHO_FR, INPUT);
  pinMode(ECHO_BC, INPUT);
  pinMode(ECHO_LS, INPUT);
  pinMode(ECHO_RS, INPUT);

  // Wait for serial connection
  while (!Serial) {
    ; // wait for serial port to connect
  }

  Serial.println("5-Sensor Ultrasonic Array Initialized");
  Serial.println("Sensors: FL, FR, BC, LS, RS");
}

void loop() {
  // Read all 5 sensors with delays to avoid interference

  distances.frontLeft = readDistance(TRIG_FL, ECHO_FL);
  delay(50); // Small delay between sensor readings

  distances.frontRight = readDistance(TRIG_FR, ECHO_FR);
  delay(50);

  distances.backCenter = readDistance(TRIG_BC, ECHO_BC);
  delay(50);

  distances.leftSide = readDistance(TRIG_LS, ECHO_LS);
  delay(50);

  distances.rightSide = readDistance(TRIG_RS, ECHO_RS);
  delay(50);

  // Send data in JSON format
  sendSensorData();

  // Update rate: approximately 10Hz (100ms + 250ms delays = 350ms total)
  delay(100);
}

float readDistance(int trigPin, int echoPin) {
  // Clear the trigger pin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  // Send 10 microsecond pulse to trigger
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  // Read the echo pin with 30ms timeout
  long duration = pulseIn(echoPin, HIGH, 30000);

  // Calculate distance in cm
  // Speed of sound = 343 m/s = 0.0343 cm/µs
  // Distance = (duration * 0.0343) / 2 = duration * 0.01715
  float distance = duration * 0.01715;

  // Return 0 if out of range or no echo
  if (distance == 0 || distance > MAX_DISTANCE) {
    return 0;
  }

  return distance;
}

void sendSensorData() {
  // CRITICAL: Must use EXACT names: FL, FR, BC, LS, RS
  // Format: {"FL":123.4,"FR":234.5,"BC":345.6,"LS":456.7,"RS":567.8}

  Serial.print("{");

  Serial.print("\"FL\":");
  Serial.print(distances.frontLeft, 1);

  Serial.print(",\"FR\":");
  Serial.print(distances.frontRight, 1);

  Serial.print(",\"BC\":");
  Serial.print(distances.backCenter, 1);

  Serial.print(",\"LS\":");
  Serial.print(distances.leftSide, 1);

  Serial.print(",\"RS\":");
  Serial.print(distances.rightSide, 1);

  Serial.println("}");
}
