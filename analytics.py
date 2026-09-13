import sqlite3

DB_PATH = "flight_data.db"

def run(query, title):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    conn.close()

    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")
    print("  " + " | ".join(cols))
    print("  " + "-"*40)
    for row in rows:
        print("  " + " | ".join(str(x) for x in row))

# 1. How many snapshots collected so far
run("""
    SELECT collected_at, COUNT(*) as aircraft_count
    FROM flight_snapshots
    GROUP BY collected_at
    ORDER BY collected_at DESC
    LIMIT 10
""", "Snapshots collected so far")

# 2. Aircraft near Hyderabad region (wider box)
run("""
    SELECT icao24, callsign, latitude, longitude, altitude_m, velocity_ms
    FROM flight_snapshots
    WHERE collected_at = (SELECT MAX(collected_at) FROM flight_snapshots)
    AND latitude BETWEEN 15.0 AND 20.0
    AND longitude BETWEEN 76.0 AND 82.0
""", "Aircraft near Hyderabad RIGHT NOW")

# 3. Top origin countries
run("""
    SELECT origin_country, COUNT(DISTINCT icao24) as unique_aircraft
    FROM flight_snapshots
    WHERE collected_at = (SELECT MAX(collected_at) FROM flight_snapshots)
    GROUP BY origin_country
    ORDER BY unique_aircraft DESC
    LIMIT 10
""", "Top origin countries")

# 4. Average speed and altitude by snapshot
run("""
    SELECT collected_at,
           COUNT(DISTINCT icao24) as aircraft,
           ROUND(AVG(velocity_ms) * 1.944, 1) as avg_speed_knots,
           ROUND(AVG(altitude_m) * 3.281, 0) as avg_alt_feet
    FROM flight_snapshots
    WHERE on_ground = 0
    AND velocity_ms IS NOT NULL
    AND altitude_m IS NOT NULL
    GROUP BY collected_at
    ORDER BY collected_at DESC
    LIMIT 10
""", "Avg speed and altitude per snapshot")

# 5. Anomaly detection — traffic vs baseline
run("""
    WITH hourly AS (
        SELECT 
            STRFTIME('%Y-%m-%d %H:00', collected_at) AS hour,
            COUNT(DISTINCT icao24) AS cnt
        FROM flight_snapshots
        GROUP BY 1
    ),
    baseline AS (
        SELECT AVG(cnt) AS avg_count FROM hourly
    )
    SELECT 
        h.hour,
        h.cnt AS aircraft_count,
        ROUND(b.avg_count, 1) AS baseline_avg,
        ROUND((h.cnt - b.avg_count) / b.avg_count * 100, 1) AS pct_vs_avg,
        CASE WHEN h.cnt > b.avg_count * 1.5 THEN 'HIGH'
             WHEN h.cnt < b.avg_count * 0.5 THEN 'LOW'
             ELSE 'NORMAL' END AS status
    FROM hourly h CROSS JOIN baseline b
    ORDER BY h.hour DESC
""", "Anomaly Detection — Traffic vs Baseline")

# 6. Data quality panel
run("""
    SELECT
        COUNT(*) AS total_records,
        COUNT(DISTINCT collected_at) AS total_snapshots,
        COUNT(DISTINCT icao24) AS unique_aircraft,
        SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) AS missing_coords,
        SUM(CASE WHEN callsign IS NULL OR callsign = '' THEN 1 ELSE 0 END) AS missing_callsign,
        MAX(collected_at) AS latest_snapshot
    FROM flight_snapshots
""", "Data Quality Panel")