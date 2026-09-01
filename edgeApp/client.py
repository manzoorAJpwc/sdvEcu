import requests
import random
import time

from datetime import datetime

url = "http://127.0.0.1:5000/telemetry"

soc = 100

speed = 0

while True:

    # Battery Drain

    soc = soc - random.uniform(4, 7)

    if soc < 5:
        soc = 100

    # Speed Variation

    speed = speed + random.randint(-15, 15)

    speed = max(0, min(speed, 180))

    # RPM Follows Speed

    rpm = 800 + (speed * 35)

    rpm = min(rpm, 7000)

    # Temperature Variation

    temperature = 25 + (speed * 0.15) + random.randint(-3, 5)

    temperature = round(temperature, 1)

    # Voltage Variation

    voltage = 300 + (soc * 1.2)

    voltage = round(voltage, 1)

    # Battery Health

    if soc < 20 or temperature > 50:
        battery_health = "CRITICAL"
    else:
        battery_health = "HEALTHY"

    # Driver Monitoring

    driver_status = random.choice([
        "ALERT",
        "ALERT",
        "ALERT",
        "ALERT",
        "DROWSY"
    ])

    payload = {

        "vehicle_id": "VEH001",

        "soc": round(soc, 1),

        "temperature": temperature,

        "voltage": voltage,

        "speed": speed,

        "rpm": int(rpm),

        "battery_health": battery_health,

        "driver_status": driver_status,

        "bms_enabled": 1,

        "dms_enabled": 1,

        "timestamp": str(datetime.now())
    }

    try:

        response = requests.post(
            url,
            json=payload
        )

        print(
            f"""
Vehicle : {payload['vehicle_id']}
SOC     : {payload['soc']} %
Speed   : {payload['speed']} km/h
RPM     : {payload['rpm']}
Temp    : {payload['temperature']} C
Voltage : {payload['voltage']} V
Battery : {payload['battery_health']}
Driver  : {payload['driver_status']}
--------------------------------------------------
"""
        )

    except Exception as e:

        print("Error:", e)

    time.sleep(2)