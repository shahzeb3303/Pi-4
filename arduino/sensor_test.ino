/*
 * HC-SR04 Ultrasonic Test Sketch (6 sensors)
 *
 * Prints each sensor on its own line, labelled.
 * Open Serial Monitor @ 9600 baud.
 *
 * Valid range 2-400cm. "-- no echo" means nothing detected / wire issue.
 */

// ---------- YOUR WIRING ----------
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
// ---------------------------------

const unsigned long PULSE_TIMEOUT_US = 30000UL;  // 30ms

struct Sensor {
  const char* name;
  uint8_t trigPin;
  uint8_t echoPin;
};

Sensor sensors[] = {
  {"FL", TRIG_FL, ECHO_FL},
  {"FR", TRIG_FR, ECHO_FR},
  {"FW", TRIG_FW, ECHO_FW},
  {"BC", TRIG_BC, ECHO_BC},
  {"LS", TRIG_LS, ECHO_LS},
  {"RS", TRIG_RS, ECHO_RS},
};
const int NUM_SENSORS = sizeof(sensors) / sizeof(sensors[0]);

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < NUM_SENSORS; i++) {
    pinMode(sensors[i].trigPin, OUTPUT);
    pinMode(sensors[i].echoPin, INPUT);
    digitalWrite(sensors[i].trigPin, LOW);
  }
  delay(100);
  Serial.println(F("===== HC-SR04 6-SENSOR TEST ====="));
  Serial.println(F("Reading each sensor one at a time"));
  Serial.println(F("================================="));
}

float readDistanceCm(uint8_t trigPin, uint8_t echoPin) {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(3);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  unsigned long duration = pulseIn(echoPin, HIGH, PULSE_TIMEOUT_US);
  if (duration == 0) return 0.0;
  float d = duration * 0.01715;        // = duration * 0.0343 / 2
  if (d < 2.0 || d > 400.0) return 0.0;
  return d;
}

void loop() {
  for (int i = 0; i < NUM_SENSORS; i++) {
    float d = readDistanceCm(sensors[i].trigPin, sensors[i].echoPin);
    Serial.print(F("["));
    Serial.print(sensors[i].name);
    Serial.print(F("] "));
    if (d <= 0) {
      Serial.println(F("-- no echo"));
    } else {
      Serial.print(d, 1);
      Serial.println(F(" cm"));
    }
    delay(80);   // gap to avoid cross-talk + give you time to read
  }
  Serial.println(F("---------"));
  delay(500);
}
