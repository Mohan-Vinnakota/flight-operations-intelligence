# ✈️ Real-Time Flight Operations Intelligence Platform

> Live aircraft tracking pipeline — Python · SQLite · Power BI

---

## Overview

An end-to-end real-time aviation analytics platform that automatically collects live aircraft data from the OpenSky Network API every 5 minutes, stores time-series snapshots in a SQLite database, and visualizes operational intelligence through a 3-page Power BI dashboard.

Built entirely from scratch as a portfolio project demonstrating: API consumption, automated ETL pipeline, time-series data engineering, SQL analytics, and operational BI dashboarding.

---

## Architecture

```
OpenSky Network API (Live Aircraft Data)
            │
            ▼
    Python Collector (every 5 min)
            │
    ┌───────┴────────┐
    │  Data Cleaning │
    │  & Validation  │
    └───────┬────────┘
            │
            ▼
     SQLite Database
    (flight_data.db)
            │
    ┌───────┴────────────┐
    ▼                    ▼
SQL Analytics       Historical
  Queries           Snapshots
    │                    │
    └────────┬───────────┘
             ▼
        CSV Exports
             │
             ▼
     Power BI Dashboard
    ┌────────────────────┐
    │  Live Operations   │
    │  Historical Trends │
    │  Data Quality      │
    └────────────────────┘
```

---

## Dashboard Pages

### Page 1 — Live Operations
- Aircraft currently tracked over India
- Average speed (m/s) and altitude (m)
- Aircraft near Hyderabad region
- Live aircraft map (latitude/longitude)
- Aircraft count by origin country

### Page 2 — Historical Trends
- Aircraft activity over time (line chart)
- Average speed & altitude by hour (dual axis)
- Aircraft near Hyderabad table with callsigns

### Page 3 — Data Quality Monitor
- Total records collected
- Total snapshots taken
- Unique aircraft tracked
- Missing coordinates count
- Missing callsign count
- Latest snapshot timestamp

---

## Tech Stack

| Layer | Technology |
|---|---|
| Data Source | OpenSky Network REST API |
| Collection | Python (requests, schedule) |
| Storage | SQLite |
| Analytics | SQL, Pandas |
| Visualization | Power BI (DAX, Map, Line, Bar) |
| Environment | Windows, VS Code, venv |

---

## Database Schema

```sql
CREATE TABLE flight_snapshots (
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
);
```

---

## Key SQL Queries

**Hourly aircraft activity:**
```sql
SELECT STRFTIME('%Y-%m-%d %H:00', collected_at) AS hour,
       COUNT(DISTINCT icao24) AS aircraft_count
FROM flight_snapshots
GROUP BY 1 ORDER BY 1;
```

**Aircraft near Hyderabad:**
```sql
SELECT collected_at, icao24, callsign, latitude, longitude, altitude_m
FROM flight_snapshots
WHERE latitude BETWEEN 15.0 AND 20.0
  AND longitude BETWEEN 76.0 AND 82.0
ORDER BY collected_at DESC;
```

**Anomaly detection — traffic vs baseline:**
```sql
WITH hourly AS (
    SELECT STRFTIME('%Y-%m-%d %H:00', collected_at) AS hour,
           COUNT(DISTINCT icao24) AS cnt
    FROM flight_snapshots GROUP BY 1
),
baseline AS (
    SELECT AVG(cnt) AS avg_count FROM hourly
)
SELECT h.hour, h.cnt,
       ROUND(b.avg_count, 1) AS baseline_avg,
       ROUND((h.cnt - b.avg_count) / b.avg_count * 100, 1) AS pct_vs_avg,
       CASE WHEN h.cnt > b.avg_count * 1.5 THEN 'HIGH'
            WHEN h.cnt < b.avg_count * 0.5 THEN 'LOW'
            ELSE 'NORMAL' END AS status
FROM hourly h CROSS JOIN baseline b
ORDER BY h.hour DESC;
```

**Data quality panel:**
```sql
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT collected_at) AS total_snapshots,
    COUNT(DISTINCT icao24) AS unique_aircraft,
    SUM(CASE WHEN latitude IS NULL OR longitude IS NULL THEN 1 ELSE 0 END) AS missing_coords,
    SUM(CASE WHEN callsign IS NULL OR callsign = '' THEN 1 ELSE 0 END) AS missing_callsign,
    MAX(collected_at) AS latest_snapshot
FROM flight_snapshots;
```

---

## Project Structure

```
flight_project/
│
├── collector.py              # Core data collection logic
├── run_collector.py          # Scheduler — runs every 5 minutes
├── analytics.py              # SQL analytics queries (terminal output)
├── export_for_powerbi.py     # Exports CSVs for Power BI refresh
│
├── flight_data.db            # SQLite database (auto-created)
│
├── exports/                  # Power BI CSV exports
│   ├── snapshots.csv
│   ├── hourly_summary.csv
│   ├── hyderabad_traffic.csv
│   ├── countries.csv
│   └── data_quality.csv
│
├── FlightOperationsDashboard.pbix   # Power BI dashboard
└── README.md
```

---

## Setup & Run

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/flight-operations-intelligence.git
cd flight-operations-intelligence
```

**2. Create virtual environment**
```bash
py -m venv venv
venv\Scripts\activate
```

**3. Install dependencies**
```bash
python.exe -m pip install requests schedule pandas sqlalchemy
```

**4. Start the collector**
```bash
python.exe run_collector.py
```

**5. Export data for Power BI**
```bash
python.exe export_for_powerbi.py
```

**6. Open Power BI**
- Open `FlightOperationsDashboard.pbix`
- Click `Home` → `Refresh`

---

## Data Source

[OpenSky Network](https://opensky-network.org/) — open-access aircraft surveillance data network providing live and historical ADS-B/Mode S data.

> Note: This project uses publicly available aircraft position data only. No ticket, booking, or passenger data is used or claimed.

---

## Results

After running the collector for ~2 hours:
- **5,200+ records** collected
- **20 snapshots** taken
- **737 unique aircraft** tracked
- **0 missing coordinates** — clean pipeline
- **34 aircraft** identified near Hyderabad at peak

---

## Author

**Mohan Sai Vinnakota**  
Data Analyst | Microsoft Search Team | Power BI PL-300 Certified  
[LinkedIn](https://linkedin.com/in/YOUR_PROFILE) · [GitHub](https://github.com/YOUR_USERNAME)
