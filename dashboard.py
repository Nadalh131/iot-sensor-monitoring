
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="IoT Sensor Dashboard", layout="wide")
st.title("IoT Sensor Dashboard")
st.caption("Bai thuc hanh so 2 - Thu thap va tien xu ly du lieu IoT")

data_file = "sensor_data.csv"
clean_file = "sensor_data_clean.csv"

if not os.path.exists(data_file):
    st.warning("Chua co sensor_data.csv. Hay chay collector.py va gui du lieu MQTT.")
else:
    df = pd.read_csv(data_file)

    if df.empty:
        st.warning("File du lieu chua co ban ghi.")
    else:
        for column in ["temperature", "humidity", "distance_cm"]:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        latest = df.iloc[-1]

        col1, col2, col3 = st.columns(3)
        col1.metric("Nhiet do", f"{latest['temperature']:.2f} °C")
        col2.metric("Do am", f"{latest['humidity']:.2f} %")
        col3.metric("Khoang cach", f"{latest['distance_cm']:.2f} cm")

        st.subheader("Bieu do cam bien")

        chart_data = df[["temperature", "humidity", "distance_cm"]].copy()
        chart_data.index = range(1, len(chart_data) + 1)
        st.line_chart(chart_data)

        st.subheader("Du lieu thu thap")
        st.dataframe(df, use_container_width=True)

        if os.path.exists(clean_file):
            st.subheader("Du lieu sau tien xu ly")
            clean_df = pd.read_csv(clean_file)
            st.dataframe(clean_df, use_container_width=True)
