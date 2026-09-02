def check_alerts(data):

    alerts = []

    if data["temperature"] > 50:
        alerts.append("HIGH TEMPERATURE ALERT")

    if data["soc"] < 20:
        alerts.append("LOW BATTERY ALERT")

    if data["voltage"] < 320:
        alerts.append("LOW VOLTAGE ALERT")

    if data["driver_status"] == "DROWSY":
        alerts.append("DRIVER DROWSINESS DETECTED")

    return alerts