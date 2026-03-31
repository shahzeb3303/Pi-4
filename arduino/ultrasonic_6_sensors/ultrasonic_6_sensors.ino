/*
 * Arduino Ultrasonic Sensor Array - 6 Sensors
 * 5 HC-SR04 + 1 Waterproof Ultrasonic
 * Sends distance data to Raspberry Pi via Serial
 *
 * Sensor Configuration:
 *   FL = Front Left
 *   FR = Front Right
 *   FW = Front Waterproof (center)
 *   BC = Back Center
 *   LS = Left Side
 *   RS = Right Side
 */

// Pin definitions based on your wiring
#define TRIG_FL 5   // Front Left
#define ECHO_FL 4

#define TRIG_FR 3   // Front Right
#define ECHO_FR 2

#define TRIG_FW 13  // Front Waterproof (center)
#define ECHO_FW 12

#define TRIG_BC 11  // Back Center
#define ECHO_BC 10

#define TRIG_RS 9   // Right Side
#define ECHO_RS 8

#define TRIG_LS 7   // Left Side
#define ECHO_LS 6

// Maximum distance to measure (in cm)
#define MAX_DISTANCE 400

// Sensor data structure
struct SensorData {
  float frontLeft;
  float frontRight;
  float frontWaterproof;
  float backCenter;
  float rightSide;
  float leftSide;
};

SensorData distances;

void setup() {
  // Initialize serial communication at 115200 baud
  Serial.begin(115200);

  // Set up all trigger pins as OUTPUT
  pinMode(TRIG_FL, OUTPUT);
  pinMode(TRIG_FR, OUTPUT);
  pinMode(TRIG_FW, OUTPUT);
  pinMode(TRIG_BC, OUTPUT);
  pinMode(TRIG_RS, OUTPUT);
  pinMode(TRIG_LS, OUTPUT);

  // Set up all echo pins as INPUT
  pinMode(ECHO_FL, INPUT);
  pinMode(ECHO_FR, INPUT);
  pinMode(ECHO_FW, INPUT);
  pinMode(ECHO_BC, INPUT);
  pinMode(ECHO_RS, INPUT);
  pinMode(ECHO_LS, INPUT);

  // Wait for serial connection
  while (!Serial) {
    ; // wait for serial port to connect
  }

  Serial.println("6-Sensor Ultrasonic Array Initialized");
  Serial.println("Sensors: FL, FR, FW, BC, RS, LS");
}

void loop() {
  // Read all 6 sensors with delays to avoid interference

  distances.frontLeft = readDistance(TRIG_FL, ECHO_FL);
  delay(50);

  distances.frontRight = readDistance(TRIG_FR, ECHO_FR);
  delay(50);

  distances.frontWaterproof = readDistance(TRIG_FW, ECHO_FW);
  delay(50);

  distances.backCenter = readDistance(TRIG_BC, ECHO_BC);
  delay(50);

  distances.rightSide = readDistance(TRIG_RS, ECHO_RS);
  delay(50);

  distances.leftSide = readDistance(TRIG_LS, ECHO_LS);
  delay(50);

  // Send data in JSON format
  sendSensorData();

  // Update rate: approximately 10Hz
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
  // CRITICAL: Must use EXACT names: FL, FR, FW, BC, RS, LS
  // Format: {"FL":123.4,"FR":234.5,"FW":345.6,"BC":456.7,"RS":567.8,"LS":678.9}

  Serial.print("{");

  Serial.print("\"FL\":");
  Serial.print(distances.frontLeft, 1);

  Serial.print(",\"FR\":");
  Serial.print(distances.frontRight, 1);

  Serial.print(",\"FW\":");
  Serial.print(distances.frontWaterproof, 1);

  Serial.print(",\"BC\":");
  Serial.print(distances.backCenter, 1);

  Serial.print(",\"RS\":");
  Serial.print(distances.rightSide, 1);

  Serial.print(",\"LS\":");
  Serial.print(distances.leftSide, 1);

  Serial.println("}");
}
