# IoT Sensor Data Collection and Dashboard

## 1. Gioi thieu

Du an mo phong he thong IoT su dung ESP32 tren Wokwi de gui du lieu cam bien
len ThingsBoard Cloud. Python thu thap telemetry, luu tru du lieu bang SQLite
va CSV, tien xu ly du lieu bang Pandas va hien thi ket qua tren Streamlit.

## 2. Chuc nang

- Thu thap telemetry tu ThingsBoard Cloud.
- Luu du lieu vao SQLite va tep CSV.
- Tien xu ly du lieu va tao tep sensor_data_clean.csv.
- Chuan hoa cac truong nhiet do, do am va khoang cach.
- Hien thi chi so cam bien, bieu do va bang du lieu tren dashboard.

## 3. Cong nghe

- ESP32 va Wokwi
- ThingsBoard Cloud
- Python 3.13
- SQLite
- Pandas, NumPy, Requests, python-dotenv, Streamlit

## 4. Cau truc du an

- firmware/: ma nguon ESP32 va cac tep mo phong Wokwi.
- collector.py: thu thap telemetry va luu du lieu.
- preprocess.py: tien xu ly du lieu.
- dashboard.py: giao dien dashboard.
- requirements.txt: danh sach thu vien Python.
- .env.example: mau cau hinh ket noi.
- sensor_data.csv: du lieu thu thap.
- sensor_data_clean.csv: du lieu sau tien xu ly.
- iot_data.db: co so du lieu SQLite.

## 5. Cai dat

Mo PowerShell tai thu muc du an va tao moi truong ao neu chua co:

    py -3.13 -m venv .venv313

Kich hoat moi truong ao:

    .\.venv313\Scripts\Activate.ps1

Cai dat thu vien:

    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt

Neu da co moi truong .venv313 hoat dong, co the bo qua buoc tao moi truong ao.

## 6. Cau hinh ThingsBoard

1. Sao chep .env.example thanh .env.
2. Dien cac gia tri ket noi ThingsBoard vao .env.
3. Dam bao Device ID dung voi thiet bi dang su dung.
4. Khong dua file .env chua thong tin dang nhap len GitHub.

Cac bien cau hinh:

- THINGSBOARD_URL
- THINGSBOARD_USERNAME
- THINGSBOARD_PASSWORD
- THINGSBOARD_DEVICE_ID

## 7. Chay chuong trinh

### 7.1. Thu thap du lieu

Mo terminal thu nhat:

    python collector.py

Collector se dang nhap ThingsBoard, lay telemetry theo chu ky duoc cau hinh
va luu du lieu vao SQLite va CSV.

### 7.2. Tien xu ly

Sau khi co du lieu, chay:

    python preprocess.py

Chuong trinh tao hoac cap nhat tep sensor_data_clean.csv.

### 7.3. Khoi dong dashboard

Mo terminal thu hai tai thu muc du an va chay:

    python -m streamlit run dashboard.py

Mo dia chi localhost duoc hien thi trong terminal de xem dashboard.

## 8. Co so du lieu

Du an su dung SQLite, du lieu duoc luu trong tep iot_data.db.

Bang sensor_data luu cac truong telemetry, gom:

- timestamp: thoi gian thu thap.
- temperature: nhiet do.
- humidity: do am.
- distance_cm: khoang cach tinh bang centimet.
- rssi: cuong do tin hieu Wi-Fi.
- sequence: so thu tu ban tin.
- uptime_s: thoi gian hoat dong cua thiet bi tinh bang giay.

Kieu du lieu cu the va khoa cua bang duoc xac dinh theo schema trong
collector.py va co so du lieu thuc te.

## 9. Tep du lieu

- sensor_data.csv: du lieu goc dang CSV.
- sensor_data_clean.csv: du lieu sau tien xu ly.
- iot_data.db: co so du lieu SQLite.

Cac tep du lieu nay co the duoc tao trong qua trinh chay chuong trinh.

## 10. Bao mat

Khong cong khai mat khau, token truy cap hoac noi dung file .env.
Chi dua file .env.example voi gia tri mau len kho ma nguon.

## 11. Huong phat trien

- Thu thap du lieu trong thoi gian dai hon.
- Cai thien xu ly du lieu bat thuong va mat ket noi.
- Bo sung canh bao khi gia tri cam bien vuot nguong.
- Nang cao kha nang tu dong cap nhat va giam sat dashboard.
