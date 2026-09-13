import requests

url = "https://opensky-network.org/api/states/all"

params = {
    "lamin": 8.0,
    "lomin": 68.0,
    "lamax": 37.0,
    "lomax": 97.0
}

response = requests.get(url, params=params, timeout=15)

if response.status_code == 200:
    data = response.json()
    states = data.get("states", [])
    print(f"Aircraft visible over India right now: {len(states)}")
    print("\nFirst 3 aircraft:")
    for s in states[:3]:
        print(f"  ICAO: {s[0]} | Callsign: {s[1]} | Lat: {s[6]} | Lon: {s[5]} | Alt: {s[7]}m | Speed: {s[9]}m/s")
else:
    print(f"API error: {response.status_code}")

    