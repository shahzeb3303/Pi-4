/*
 * HC-SR04 Production Sketch (6 sensors -> JSON over serial)
 *
 * Open Serial Monitor @ 115200 baud (this is what the Pi uses).
 * Emits one line of JSON per cycle, ~10Hz:
 *   {"FL":123.4,"FR":145.0,"FW":200.0,"BC":80.0,"LS":90.0,"RS":110.5}
 *
 * This format is what raspberry_pi/obstacle_monitor.py expects.
 * Invalid readings (no echo / out of range) are reported as 0.
 */

// ---------- YOUR WIRING (same as test sketch) ----------
#define TRIG_FL 5
#define ECHO_FL 4

#define TRIG_FR 3
#define ECHO_FR 2

#define TRIG_FW 13
#define ECHO_FW 12

#define TRIG_BC 11
#define ECHO_BC 10

#define TRIG_RS 9
#define ECHO_RS 8

#define TRIG_LS 7
#define ECHO_LS 6
// -------------------------------------------------------

#define MAX_DISTANCE 400
const unsigned long PULSE_TIMEOUT_US = 30000UL;

struct SensorData {
  float FL, FR, FW, BC, LS, RS;
} d;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_FL, OUTPUT); pinMode(ECHO_FL, INPUT);
  pinMode(TRIG_FR, OUTPUT); pinMode(ECHO_FR, INPUT);
  pinMode(TRIG_FW, OUTPUT); pinMode(ECHO_FW, INPUT);
  pinMode(TRIG_BC, OUTPUT); pinMode(ECHO_BC, INPUT);
  pinMode(TRIG_RS, OUTPUT); pinMode(ECHO_RS, INPUT);
  pinMode(TRIG_LS, OUTPUT); pinMode(ECHO_LS, INPUT);
  while (!Serial) { ; }
  delay(100);
}

float readDistance(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(3);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, PULSE_TIMEOUT_US);
  if (duration == 0) return 0.0;
  float distance = duration * 0.01715;
  if (distance < 2.0 || distance > MAX_DISTANCE) return 0.0;
  return distance;
}

void loop() {
  d.FL = readDistance(TRIG_FL, ECHO_FL); delay(40);
  d.FR = readDistance(TRIG_FR, ECHO_FR); delay(40);
  d.FW = readDistance(TRIG_FW, ECHO_FW); delay(40);
  d.BC = readDistance(TRIG_BC, ECHO_BC); delay(40);
  d.RS = readDistance(TRIG_RS, ECHO_RS); delay(40);
  d.LS = readDistance(TRIG_LS, ECHO_LS); delay(40);

  Serial.print(F("{"));
  Serial.print(F("\"FL\":")); Serial.print(d.FL, 1);
  Serial.print(F(",\"FR\":")); Serial.print(d.FR, 1);
  Serial.print(F(",\"FW\":")); Serial.print(d.FW, 1);
  Serial.print(F(",\"BC\":")); Serial.print(d.BC, 1);
  Serial.print(F(",\"LS\":")); Serial.print(d.LS, 1);
  Serial.print(F(",\"RS\":")); Serial.print(d.RS, 1);
  Serial.println(F("}"));
}
