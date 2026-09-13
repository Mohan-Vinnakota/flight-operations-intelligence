import requests
import sqlite3
from datetime import datetime

DB_PATH = "flight_data.db"

def create_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flight_snapshots (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            collected_at    TEXT NOT NULL,
            icao24          TEXT,
            callsign        TEXT,
            origin_country  TEXT,
            latitude        REAL,
            longitude       REAL,
            altitude_m      REAL,
            velocity_ms     REAL,
            heading         REAL,
            on_ground       INTEGER
        )
    """)
    conn.commit()
    conn.close()
    print("Table ready.")

def fetch_and_store():
    url = "https://opensky-network.org/api/states/all"
    params = {
        "lamin": 8.0,
        "lomin": 68.0,
        "lamax": 37.0,
        "lomax": 97.0
    }

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            return

        data = response.json()
        states = data.get("states", [])
        collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        records = []
        for s in states:
            records.append((
                collected_at,
                s[0],           # icao24
                s[1].strip() if s[1] else None,  # callsign
                s[2],           # origin_country
                s[6],           # latitude
                s[5],           # longitude
                s[7],           # altitude_m
                s[9],           # velocity_ms
                s[10],          # heading
                1 if s[8] else 0  # on_ground
            ))

        cursor.executemany("""
            INSERT INTO flight_snapshots
            (collected_at, icao24, callsign, origin_country,
             latitude, longitude, altitude_m, velocity_ms, heading, on_ground)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)

        conn.commit()
        conn.close()

        print(f"[{collected_at}] Saved {len(records)} aircraft to DB.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_table()
    fetch_and_store()