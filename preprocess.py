
import pandas as pd
import numpy as np

input_file = "sensor_data.csv"
output_file = "sensor_data_clean.csv"

try:
    df = pd.read_csv(input_file)

    print("Du lieu ban dau:", len(df), "dong")

    df = df.drop_duplicates()

    numeric_columns = [
        "temperature",
        "humidity",
        "distance_cm",
        "rssi",
        "sequence",
        "uptime_s",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    print("\nSo luong gia tri thieu:")
    print(df.isnull().sum())

    df = df.dropna(subset=numeric_columns)

    valid_ranges = {
        "temperature": (-40, 80),
        "humidity": (0, 100),
        "distance_cm": (0, 400),
        "rssi": (-120, 0),
    }

    for column, (minimum, maximum) in valid_ranges.items():
        df = df[df[column].between(minimum, maximum)]

    if not df.empty:
        for column in ["temperature", "humidity", "distance_cm"]:
            minimum = df[column].min()
            maximum = df[column].max()

            if maximum != minimum:
                df[column + "_normalized"] = (
                    (df[column] - minimum) / (maximum - minimum)
                )
            else:
                df[column + "_normalized"] = 0.0

    df.to_csv(output_file, index=False, encoding="utf-8-sig")

    print("\nSo dong sau tien xu ly:", len(df))
    print("Da luu du lieu sach vao:", output_file)
    print(df.tail())

except FileNotFoundError:
    print("Khong tim thay sensor_data.csv.")
    print("Hay chay collector va gui du lieu thu truoc.")
