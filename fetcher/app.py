#!/usr/bin/env python3
import os
import json
import time
from datetime import datetime, timedelta
from threading import Thread
from greenmountainpower.api import GreenMountainPowerApi, UsagePrecision
import traceback

# --- Configuration ---
GMP_ACCOUNT_NUMBER = os.environ.get("GMP_ACCOUNT_NUMBER")
GMP_USERNAME = os.environ.get("GMP_USERNAME")
GMP_PASSWORD = os.environ.get("GMP_PASSWORD")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "/app")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "gmp_usage.json")

# Default interval only matters when NOT using --once
UPDATE_INTERVAL = 60 * 120  # 2 Hours

# --- GMP API setup ---
gmp = GreenMountainPowerApi(
    account_number=GMP_ACCOUNT_NUMBER,
    username=GMP_USERNAME,
    password=GMP_PASSWORD
)

# --- Data fetch + write ---
def fetch_and_write_once():
    try:
        now_str = datetime.now().isoformat()
        print(f"[{now_str}] Polling GMP API for new data...", flush=True)

        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)

        usages = gmp.get_usage(
            start_time=start_time,
            end_time=end_time,
            precision=UsagePrecision.HOURLY
        )

        intervals = []
        for usage in usages:
            intervals.append({
                "timestamp": usage.start_time.isoformat(),
                "usage_kwh": usage.consumed_kwh,
                "date": usage.start_time.date().isoformat(),
            })

        # Daily totals
        daily_totals = {}
        for entry in intervals:
            d = entry["date"]
            daily_totals[d] = daily_totals.get(d, 0) + entry["usage_kwh"]

        output = {
            "generated_at": now_str,
            "last_accessed": None,   # left here for compatibility
            "intervals": intervals,
            "daily_totals": [
                {"date": d, "total_kwh": k} for d, k in daily_totals.items()
            ],
        }

        with open(OUTPUT_FILE, "w") as f:
            json.dump(output, f, indent=2)

        print(
            f"[{now_str}] JSON file updated: {OUTPUT_FILE} "
            f"({len(intervals)} intervals)",
            flush=True
        )

    except Exception as e:
        now_str = datetime.now().isoformat()
        print(f"[{now_str}] ERROR in fetch_and_write_once: {e}", flush=True)
        traceback.print_exc()


# --- Polling loop (only used if NOT running under cron) ---
def polling_loop():
    fetch_and_write_once()

    while True:
        time.sleep(UPDATE_INTERVAL)
        fetch_and_write_once()


def safe_thread_wrapper(func, name):
    try:
        func()
    except Exception as e:
        now_str = datetime.now().isoformat()
        print(f"[{now_str}] ERROR in {name}: {e}", flush=True)
        traceback.print_exc()


# --- Main ---
def main():
    print(
        f"[{datetime.now().isoformat()}] Fetcher starting in interval mode...",
        flush=True
    )

    Thread(
        target=lambda: safe_thread_wrapper(polling_loop, "Polling thread"),
        daemon=True
    ).start()

    # Keep the process alive
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    # If cron calls us, run once and exit
    if args.once:
        fetch_and_write_once()
    else:
        main()
