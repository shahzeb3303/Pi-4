# Complete Pin Connection Guide

## ALL Pin Connections in One Place

---

## 1. IBT_2 Motor Driver → Raspberry Pi

### Control Wires (5 connections):

| Wire # | IBT_2 Pin | → | Raspberry Pi | Physical Pin | Description |
|--------|-----------|---|--------------|--------------|-------------|
| 1 | **RPWM** | → | **GPIO 12** | **Pin 32** | Forward PWM signal |
| 2 | **LPWM** | → | **GPIO 13** | **Pin 33** | Backward PWM signal |
| 3 | **R_EN** | → | **GPIO 23** | **Pin 16** | Right Enable |
| 4 | **L_EN** | → | **GPIO 24** | **Pin 18** | Left Enable |
| 5 | **GND** | → | **GND** | **Pin 6** | Ground |

### Power Connections:

| IBT_2 Pin | Connect To | Description |
|-----------|------------|-------------|
| **Vcc (5V small pin)** | **LM2596 OUT+** | 5V logic power from LM2596 |
| **Vcc (big terminal)** | **Power Supply +** | Motor power (12V or 24V) |
| **GND (big terminal)** | **Power Supply -** | Motor power ground |
| **B+** | **Motor +** | Motor positive wire (Red) |
| **B-** | **Motor -** | Motor negative wire (Black) |

---

## 2. Waterproof Ultrasonic Sensor → Raspberry Pi

### Sensor Wires (4 connections):

| Wire # | Sensor Wire Color | → | Raspberry Pi | Physical Pin | Description |
|--------|-------------------|---|--------------|--------------|-------------|
| 1 | **VCC (Red)** | → | **5V** | **Pin 2** | Power |
| 2 | **GND (Black)** | → | **GND** | **Pin 14** | Ground |
| 3 | **TRIG (Yellow)** | → | **GPIO 17** | **Pin 11** | Trigger signal |
| 4 | **ECHO (Green)** | → | **GPIO 27** | **Pin 13** | Echo signal |

---

## 3. Arduino → Raspberry Pi

| Arduino | → | Raspberry Pi |
|---------|---|--------------|
| **USB Port** | → | **USB Port** | (will appear as /dev/ttyUSB0 or /dev/ttyACM0) |

---

## 4. Arduino → 5 HC-SR04 Sensors

**Your Arduino code should connect:**

| Sensor Position | Sensor Name | Arduino TRIG Pin | Arduino ECHO Pin |
|-----------------|-------------|------------------|------------------|
| Front Left | **FL** | D2 | D3 |
| Front Right | **FR** | D4 | D5 |
| Back Center | **BC** | D6 | D7 |
| Left Side | **LS** | D8 | D9 |
| Right Side | **RS** | D10 | D11 |

**Note:** Each HC-SR04 also needs:
- **VCC** → Arduino 5V
- **GND** → Arduino GND

---

## 5. LM2596 Buck Converter

### Input:

| LM2596 Pin | Connect To |
|------------|------------|
| **IN+** | Power Supply + (12V/24V) |
| **IN-** | Power Supply - (GND) |

### Output (adjust to 5V with potentiometer):

| LM2596 Pin | Connect To |
|------------|------------|
| **OUT+** | IBT_2 Vcc (5V logic pin) |
| **OUT-** | Common Ground |

---

## Complete Wiring Diagram

```
POWER SUPPLY (12V/24V)
        |
    ┌───┴───┐
   (+)     (-)
    │       │
    │       └────────────────────────────┐
    │                                    │
    ├──> LM2596 IN+                     │
    │                                    │
    └──> IBT_2 Motor Power Vcc          │
                                         │
LM2596                              COMMON GND
  OUT+ (5V) ──> IBT_2 Logic Vcc         │
  OUT- ────────────────────────────────>│


RASPBERRY PI (40-pin header)               COMMON GND
════════════════════════════                    │
Pin 2  [5V]       ──> Waterproof VCC           │
Pin 6  [GND]      ──> IBT_2 GND ──────────────>│
Pin 11 [GPIO 17]  ──> Waterproof TRIG          │
Pin 13 [GPIO 27]  ──> Waterproof ECHO          │
Pin 14 [GND]      ──> Waterproof GND ─────────>│
Pin 16 [GPIO 23]  ──> IBT_2 R_EN               │
Pin 18 [GPIO 24]  ──> IBT_2 L_EN               │
Pin 32 [GPIO 12]  ──> IBT_2 RPWM               │
Pin 33 [GPIO 13]  ──> IBT_2 LPWM               │
[USB Port]        ──> Arduino USB              │
                                                │
                                                │
IBT_2 MOTOR DRIVER                              │
══════════════════                              │
RPWM  <─── Pi GPIO 12                          │
LPWM  <─── Pi GPIO 13                          │
R_EN  <─── Pi GPIO 23                          │
L_EN  <─── Pi GPIO 24                          │
GND   <─── Pi GND ─────────────────────────────>│
Vcc(5V) <─ LM2596 5V                           │
Vcc(12V) <─ Power Supply +                     │
GND(pwr) <─ Power Supply - ────────────────────>│
B+    ──> Motor +                              │
B-    ──> Motor -                              │


ARDUINO UNO                                     │
═══════════                                     │
D2  ──> FL Sensor TRIG                         │
D3  ──> FL Sensor ECHO                         │
D4  ──> FR Sensor TRIG                         │
D5  ──> FR Sensor ECHO                         │
D6  ──> BC Sensor TRIG                         │
D7  ──> BC Sensor ECHO                         │
D8  ──> LS Sensor TRIG                         │
D9  ──> LS Sensor ECHO                         │
D10 ──> RS Sensor TRIG                         │
D11 ──> RS Sensor ECHO                         │
5V  ──> All 5 HC-SR04 VCC pins                 │
GND ──> All 5 HC-SR04 GND pins ────────────────>│
USB ──> Raspberry Pi USB                       │
```

---

## Sensor Layout on Vehicle

```
         FRONT OF VEHICLE

    FL          FW          FR
    👁️          👁️          👁️
  (Arduino)    (Pi)     (Arduino)
    D2/D3    GPIO17/27    D4/D5


LS 👁️  [====== VEHICLE ======]  👁️ RS
 (Arduino)                    (Arduino)
  D8/D9                        D10/D11



              BC
              👁️
          (Arduino)
           D6/D7

         BACK OF VEHICLE
```

---

## Ground Connections - CRITICAL!

**ALL these grounds MUST be connected together:**

✅ Raspberry Pi GND (Pin 6, 14, or any GND pin)
✅ IBT_2 GND (control side)
✅ IBT_2 GND (motor power side)
✅ Power Supply GND (-)
✅ LM2596 GND (OUT-)
✅ Waterproof Sensor GND
✅ Arduino GND (connected via USB already)

**Use a terminal block or breadboard to connect all grounds to one point!**

---

## Quick Checklist

### Before Powering On:

- [ ] All 5 IBT_2 control wires connected to Pi (RPWM, LPWM, R_EN, L_EN, GND)
- [ ] IBT_2 logic power from LM2596 5V output
- [ ] IBT_2 motor power from main power supply (12V/24V)
- [ ] Motor connected to IBT_2 B+ and B-
- [ ] Waterproof sensor 4 wires connected to Pi (VCC, GND, TRIG, ECHO)
- [ ] Arduino USB connected to Pi
- [ ] Arduino has 5 HC-SR04 sensors wired
- [ ] LM2596 adjusted to output exactly 5.0V
- [ ] **ALL GROUNDS CONNECTED TOGETHER**

### After Powering On:

- [ ] LM2596 outputs 5V (verify with multimeter)
- [ ] Arduino power LED on
- [ ] No smoke, burning smell, or excessive heat

---

## Wire Colors (Suggested)

| Connection | Suggested Wire Color |
|------------|---------------------|
| RPWM | Yellow |
| LPWM | Orange |
| R_EN | Blue |
| L_EN | Purple |
| GND | Black |
| 5V | Red |
| TRIG | Green |
| ECHO | White |

**Note:** These are just suggestions. Use whatever wires you have, but label them clearly!

---

## Troubleshooting Pin Connections

### Motor doesn't move:
- Check all 5 IBT_2 control wires
- Verify GPIO pin numbers in code match physical connections
- Check motor power supply is on
- Verify LM2596 outputs 5V

### Waterproof sensor reads 0:
- Check all 4 sensor wires
- Verify GPIO 17 (TRIG) and GPIO 27 (ECHO)
- Check 5V power to sensor
- Run waterproof sensor test: `sudo python3 waterproof_sensor.py`

### Arduino sensors don't work:
- Check USB connection
- Verify serial port (/dev/ttyUSB0 or /dev/ttyACM0)
- Check Arduino code is uploaded
- Verify Arduino HC-SR04 wiring
- Test with Arduino Serial Monitor (115200 baud)

---

**Print this page and keep it with your project!**
