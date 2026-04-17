/*
 * All 6 HC-SR04 sensors - simple test
 * Upload, open Serial Monitor @ 9600 baud
 */

// TRIG, ECHO pins
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

void setup() {
  Serial.begin(9600);
  int trigs[] = {TRIG_FL, TRIG_FR, TRIG_FW, TRIG_BC, TRIG_RS, TRIG_LS};
  int echos[] = {ECHO_FL, ECHO_FR, ECHO_FW, ECHO_BC, ECHO_RS, ECHO_LS};
  for (int i = 0; i < 6; i++) {
    pinMode(trigs[i], OUTPUT);
    pinMode(echos[i], INPUT);
    digitalWrite(trigs[i], LOW);
  }
  delay(200);
  Serial.println("=== 6-Sensor Test ===");
}

float readCm(int trig, int echo) {
  digitalWrite(trig, LOW);
  delayMicroseconds(3);
  digitalWrite(trig, HIGH);
  delayMicroseconds(10);
  digitalWrite(trig, LOW);
  long dur = pulseIn(echo, HIGH, 30000);
  if (dur == 0) return -1;
  float cm = dur * 0.01715;
  if (cm < 2 || cm > 400) return -1;
  return cm;
}

void printSensor(const char* name, int trig, int echo) {
  float d = readCm(trig, echo);
  Serial.print(name);
  Serial.print(": ");
  if (d < 0) Serial.println("-- no echo");
  else { Serial.print(d, 1); Serial.println(" cm"); }
}

void loop() {
  Serial.println("---------");
  printSensor("FL", TRIG_FL, ECHO_FL); delay(60);
  printSensor("FR", TRIG_FR, ECHO_FR); delay(60);
  printSensor("FW", TRIG_FW, ECHO_FW); delay(60);
  printSensor("BC", TRIG_BC, ECHO_BC); delay(60);
  printSensor("LS", TRIG_LS, ECHO_LS); delay(60);
  printSensor("RS", TRIG_RS, ECHO_RS); delay(60);
  delay(300);
}
