import sqlite3
import pandas as pd

DB_PATH = "flight_data.db"
conn = sqlite3.connect(DB_PATH)

# Table 1 — All snapshots
pd.read_sql("""
    SELECT * FROM flight_snapshots
""", conn).to_csv("exports/snapshots.csv", index=False)

# Table 2 — Hourly summary
pd.read_sql("""
    SELECT 
        STRFTIME('%Y-%m-%d %H:00', collected_at) AS hour,
        COUNT(DISTINCT icao24) AS aircraft_count,
        ROUND(AVG(velocity_ms) * 1.944, 1) AS avg_speed_knots,
        ROUND(AVG(altitude_m) * 3.281, 0) AS avg_alt_feet
    FROM flight_snapshots
    WHERE on_ground = 0
    AND velocity_ms IS NOT NULL
    AND altitude_m IS NOT NULL
    GROUP BY 1
    ORDER BY 1
""", conn).to_csv("exports/hourly_summary.csv", index=False)

# Table 3 — Hyderabad region traffic
pd.read_sql("""
    SELECT collected_at, icao24, callsign, 
           latitude, longitude, altitude_m, velocity_ms
    FROM flight_snapshots
    WHERE latitude BETWEEN 15.0 AND 20.0
    AND longitude BETWEEN 76.0 AND 82.0
    ORDER BY collected_at DESC
""", conn).to_csv("exports/hyderabad_traffic.csv", index=False)

# Table 4 — Top countries latest snapshot
pd.read_sql("""
    SELECT origin_country, COUNT(DISTINCT icao24) AS unique_aircraft
    FROM flight_snapshots
    WHERE collected_at = (SELECT MAX(collected_at) FROM flight_snapshots)
    GROUP BY origin_country
    ORDER BY unique_aircraft DESC
""", conn).to_csv("exports/countries.csv", index=False)

# Table 5 — Data quality
pd.read_sql("""
    SELECT
        COUNT(*) AS total_records,
        COUNT(DISTINCT collected_at) AS total_snapshots,
        COUNT(DISTINCT icao24) AS unique_aircraft,
        SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) AS missing_coords,
        SUM(CASE WHEN callsign IS NULL OR callsign = '' THEN 1 ELSE 0 END) AS missing_callsign,
        MAX(collected_at) AS latest_snapshot
    FROM flight_snapshots
""", conn).to_csv("exports/data_quality.csv", index=False)

conn.close()
print("All exports done. Check exports/ folder.")