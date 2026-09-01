import sqlite3

conn = sqlite3.connect("battery.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE telemetry (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    vehicle_id TEXT,
    soc REAL,
    temperature REAL,
    voltage REAL,

    speed REAL,
    rpm REAL,

    battery_health TEXT,
    driver_status TEXT,

    bms_enabled INTEGER,
    dms_enabled INTEGER,

    timestamp TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully")