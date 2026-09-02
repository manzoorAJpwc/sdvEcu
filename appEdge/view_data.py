import sqlite3

conn = sqlite3.connect("battery.db")

cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM telemetry
ORDER BY id DESC
""")

rows = cursor.fetchall()

print("\n===== STORED TELEMETRY =====\n")

for row in rows:
    print(row)

print("\nTotal Records:", len(rows))

conn.close()
