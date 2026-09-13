import schedule
import time
from collector import create_table, fetch_and_store

create_table()
fetch_and_store()  # run immediately on start

schedule.every(5).minutes.do(fetch_and_store)

print("Collector running. Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(1)