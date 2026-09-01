from flask import Flask, request, jsonify
import sqlite3

from alerts import check_alerts

app = Flask(__name__)


@app.route("/")
def home():
    return "Battery Telemetry Server Running"


@app.route("/telemetry", methods=["POST"])
def telemetry():

    data = request.json

    alerts = check_alerts(data)

    conn = sqlite3.connect("battery.db")
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO telemetry (
        vehicle_id,
        soc,
        temperature,
        voltage,
        speed,
        rpm,
        battery_health,
        driver_status,
        bms_enabled,
        dms_enabled,
        timestamp
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
    (
        data["vehicle_id"],
        data["soc"],
        data["temperature"],
        data["voltage"],
        data["speed"],
        data["rpm"],
        data["battery_health"],
        data["driver_status"],
        data["bms_enabled"],
        data["dms_enabled"],
        data["timestamp"]
    ))

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success",
        "alerts": alerts
    })


@app.route("/latest_data")
def latest_data():

    conn = sqlite3.connect("battery.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        vehicle_id,
        soc,
        temperature,
        voltage,
        speed,
        rpm,
        battery_health,
        driver_status,
        bms_enabled,
        dms_enabled,
        timestamp
    FROM telemetry
    ORDER BY id DESC
    LIMIT 1
    """)

    row = cursor.fetchone()

    conn.close()

    if row:

        return jsonify({
            "vehicle_id": row[0],
            "soc": row[1],
            "temperature": row[2],
            "voltage": row[3],
            "speed": row[4],
            "rpm": row[5],
            "battery_health": row[6],
            "driver_status": row[7],
            "bms_enabled": row[8],
            "dms_enabled": row[9],
            "timestamp": row[10]
        })

    return jsonify({"message": "No Data"})


@app.route("/latest_alerts")
def latest_alerts():

    conn = sqlite3.connect("battery.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT
        soc,
        temperature,
        voltage,
        driver_status
    FROM telemetry
    ORDER BY id DESC
    LIMIT 1
    """)

    row = cursor.fetchone()

    conn.close()

    if row is None:

        return jsonify({
            "alerts": []
        })

    data = {
        "soc": row[0],
        "temperature": row[1],
        "voltage": row[2],
        "driver_status": row[3]
    }

    alerts = check_alerts(data)

    return jsonify({
        "alerts": alerts
    })


if __name__ == "__main__":
    app.run(debug=True)