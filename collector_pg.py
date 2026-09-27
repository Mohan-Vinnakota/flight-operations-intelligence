import requests
import psycopg2
from datetime import datetime

DB_URL = "postgresql://postgres.yalulvtrtuamcytshetg:Mohan16Sai98@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"

def create_table():
    conn = psycopg2.connect(DB_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flight_snapshots (
            id              SERIAL PRIMARY KEY,
            collected_at    TIMESTAMP NOT NULL,
            icao24          VARCHAR(10),
            callsign        VARCHAR(20),
            origin_country  VARCHAR(50),
            latitude        FLOAT,
            longitude       FLOAT,
            altitude_m      FLOAT,
            velocity_ms     FLOAT,
            heading         FLOAT,
            on_ground       BOOLEAN
        )
    """)
    conn.commit()
    conn.close()
    print("Table ready.")

def fetch_and_store():
    url = "https://opensky-network.org/api/states/all"
    params = {"lamin": 8.0, "lomin": 68.0, "lamax": 37.0, "lomax": 97.0}
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code != 200:
            print(f"API error: {response.status_code}")
            return
        data = response.json()
        states = data.get("states", [])
        collected_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        records = []
        for s in states:
            records.append((
                collected_at, s[0],
                s[1].strip() if s[1] else None,
                s[2], s[6], s[5], s[7], s[9], s[10],
                bool(s[8])
            ))
        cursor.executemany("""
            INSERT INTO flight_snapshots
            (collected_at, icao24, callsign, origin_country,
             latitude, longitude, altitude_m, velocity_ms, heading, on_ground)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, records)
        conn.commit()
        conn.close()
        print(f"[{collected_at}] Saved {len(records)} aircraft to DB.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_table()
    fetch_and_store()