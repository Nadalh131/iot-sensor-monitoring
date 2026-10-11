
import csv
import os
import sqlite3
import time
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv(
    "THINGSBOARD_URL",
    "https://eu.thingsboard.cloud"
).rstrip("/")

username = os.getenv("THINGSBOARD_USERNAME", "").strip()
password = os.getenv("THINGSBOARD_PASSWORD", "")
device_id = os.getenv("THINGSBOARD_DEVICE_ID", "").strip()

csv_file = "sensor_data.csv"
db_file = "iot_data.db"
interval = 5
batch_limit = 1000

fields = [
    "timestamp",
    "temperature",
    "humidity",
    "distance_cm",
    "rssi",
    "sequence",
    "uptime_s",
]

telemetry_keys = fields[1:]


def init_db():
    with sqlite3.connect(db_file) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                ts INTEGER PRIMARY KEY,
                timestamp TEXT NOT NULL,
                temperature REAL,
                humidity REAL,
                distance_cm REAL,
                rssi REAL,
                sequence INTEGER,
                uptime_s INTEGER
            )
        """)


def init_csv():
    if not os.path.exists(csv_file) or os.path.getsize(csv_file) == 0:
        with open(csv_file, "w", newline="", encoding="utf-8") as file:
            csv.DictWriter(file, fieldnames=fields).writeheader()


def login(session):
    if not username or not password:
        raise RuntimeError(
            "Thieu THINGSBOARD_USERNAME hoac THINGSBOARD_PASSWORD."
        )

    response = session.post(
        f"{base_url}/api/auth/login",
        json={"username": username, "password": password},
        timeout=20,
    )
    response.raise_for_status()

    token = response.json().get("token")
    if not token:
        raise RuntimeError("Khong nhan duoc JWT tu ThingsBoard.")

    session.headers.update({
        "X-Authorization": f"Bearer {token}"
    })

    print("Dang nhap ThingsBoard thanh cong.")


def get_last_timestamp():
    with sqlite3.connect(db_file) as conn:
        result = conn.execute(
            "SELECT MAX(ts) FROM sensor_data"
        ).fetchone()[0]

    return result


def fetch_telemetry(session, start_ts):
    now_ms = int(time.time() * 1000)

    response = session.get(
        f"{base_url}/api/plugins/telemetry/DEVICE/"
        f"{device_id}/values/timeseries",
        params={
            "keys": ",".join(telemetry_keys),
            "startTs": start_ts,
            "endTs": now_ms,
            "limit": batch_limit,
            "agg": "NONE",
            "orderBy": "ASC",
        },
        timeout=30,
    )

    if response.status_code == 401:
        print("JWT het han, dang dang nhap lai...")
        login(session)

        response = session.get(
            f"{base_url}/api/plugins/telemetry/DEVICE/"
            f"{device_id}/values/timeseries",
            params={
                "keys": ",".join(telemetry_keys),
                "startTs": start_ts,
                "endTs": now_ms,
                "limit": batch_limit,
                "agg": "NONE",
                "orderBy": "ASC",
            },
            timeout=30,
        )

    response.raise_for_status()
    return response.json()


def convert_value(value):
    if value is None:
        return None

    try:
        number = float(value)
        if number.is_integer():
            return int(number)
        return number
    except (ValueError, TypeError):
        return value


def build_rows(data):
    samples = {}

    for key in telemetry_keys:
        for item in data.get(key, []):
            ts = int(item["ts"])

            if ts not in samples:
                samples[ts] = {
                    "timestamp": datetime.fromtimestamp(
                        ts / 1000,
                        timezone.utc,
                    ).astimezone().isoformat(timespec="seconds"),
                    **{name: None for name in telemetry_keys},
                }

            samples[ts][key] = convert_value(item.get("value"))

    return sorted(samples.items())


def save_rows(rows):
    saved = 0

    with sqlite3.connect(db_file) as conn:
        for ts, row in rows:
            cursor = conn.execute("""
                INSERT OR IGNORE INTO sensor_data (
                    ts, timestamp, temperature, humidity,
                    distance_cm, rssi, sequence, uptime_s
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ts,
                row["timestamp"],
                row["temperature"],
                row["humidity"],
                row["distance_cm"],
                row["rssi"],
                row["sequence"],
                row["uptime_s"],
            ))

            if cursor.rowcount:
                saved += 1

    if saved:
        with open(csv_file, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fields)

            for _, row in rows:
                with sqlite3.connect(db_file) as conn:
                    exists = conn.execute(
                        "SELECT 1 FROM sensor_data WHERE timestamp=? "
                        "AND temperature IS ? AND humidity IS ? "
                        "AND distance_cm IS ? AND rssi IS ? "
                        "AND sequence IS ? AND uptime_s IS ?",
                        (
                            row["timestamp"],
                            row["temperature"],
                            row["humidity"],
                            row["distance_cm"],
                            row["rssi"],
                            row["sequence"],
                            row["uptime_s"],
                        ),
                    ).fetchone()

                if exists:
                    writer.writerow(row)

    return saved


def main():
    if not device_id:
        print("Thieu THINGSBOARD_DEVICE_ID trong .env.")
        return

    init_db()
    init_csv()

    session = requests.Session()

    try:
        login(session)
    except (requests.RequestException, RuntimeError) as error:
        print("Loi dang nhap:", error)
        return

    print("Bat dau thu thap telemetry.")
    print("Device ID:", device_id)
    print("Chu ky:", interval, "giay")
    print("Nhan Ctrl+C de dung.\n")

    while True:
        try:
            last_ts = get_last_timestamp()
            start_ts = last_ts + 1 if last_ts is not None else 0

            data = fetch_telemetry(session, start_ts)
            rows = build_rows(data)

            if rows:
                saved = save_rows(rows)
                print(
                    f"Nhan {len(rows)} mau, luu moi {saved} mau. "
                    f"Timestamp cuoi: {rows[-1][0]}"
                )
            else:
                print("Chua co mau telemetry moi.")

        except requests.HTTPError as error:
            print("Loi HTTP:", error)
        except requests.RequestException as error:
            print("Loi ket noi:", error)
        except (ValueError, KeyError, sqlite3.Error, RuntimeError) as error:
            print("Loi xu ly:", error)

        time.sleep(interval)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDa dung collector.")
