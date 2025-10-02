# LSTM Weather Forecast System

Hệ thống dự báo thời tiết tự động sử dụng mô hình LSTM (Long Short-Term Memory) để dự đoán độ ẩm tương đối (QV2M) và độ ẩm đất (GWETROOT) cho ngày tiếp theo.

## 🌟 Tính năng chính

- **Tự động cập nhật dữ liệu**: Kéo dữ liệu mới nhất từ NASA POWER API mỗi ngày
- **Dự báo thời tiết**: Sử dụng mô hình LSTM để dự đoán thời tiết ngày mai
- **Web Dashboard**: Giao diện web đẹp mắt để xem kết quả dự báo
- **Lên lịch tự động**: Chạy tự động mỗi ngày lúc 6:00 AM
- **Retrain định kỳ**: Tự động retrain model mỗi Chủ nhật lúc 2:00 AM
- **Logging chi tiết**: Ghi log đầy đủ quá trình hoạt động
- **Xử lý dữ liệu thiếu**: Tự động loại bỏ dữ liệu không hợp lệ (-999.0)

## 📁 Cấu trúc dự án

```
lstm_forecast/
├── src/                          # Source code chính
│   ├── main.py                   # Entry point chính
│   ├── data_loader.py            # Load và xử lý dữ liệu
│   ├── data_fetcher.py           # Kéo dữ liệu từ NASA POWER API
│   ├── model.py                  # Định nghĩa mô hình LSTM
│   ├── trainer.py                # Training và prediction
│   ├── web_dashboard.py          # Web dashboard module
│   └── templates/                # HTML templates
│       └── dashboard.html        # Dashboard template
├── data/                         # Dữ liệu thời tiết
│   └── POWER_Point_Daily_*.csv   # File dữ liệu chính
├── results/                      # Kết quả dự báo
├── requirements.txt              # Dependencies
├── setup.py                      # Script cài đặt
├── run_daily_forecast.bat        # Script chạy trên Windows
├── start_daily_forecast.bat      # Script khởi động scheduler
├── model.h5                      # Mô hình đã train
├── scaler.pkl                    # Scaler đã fit
└── daily_forecast.log            # Log file
```

## 🚀 Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

Hoặc sử dụng script cài đặt:

```bash
python setup.py
```

### 2. Kiểm tra dữ liệu

Đảm bảo file dữ liệu tồn tại trong thư mục `data/`:
- `POWER_Point_Daily_20111207_20250807_021d01N_105d83E_LST.csv`

## 🎯 Cách sử dụng

### 1. Chạy dự báo một lần

```bash
python src/main.py --mode once
```

### 2. Chạy scheduler (tự động mỗi ngày)

```bash
python src/main.py --mode scheduler
```

### 3. Retrain model

```bash
python src/main.py --mode retrain
```

[//]: # (### 4. Chạy web dashboard)

[//]: # ()
[//]: # (```bash)

[//]: # (python src/main.py --mode web)

[//]: # (```)

### 4. Chạy dự báo với web dashboard

```bash
python src/main.py --mode once
# Web dashboard sẽ tự động mở tại http://127.0.0.1:5000
```

### 5. Tắt web dashboard

```bash
python src/main.py --mode once --no-web
```

### 6. Sử dụng batch file (Windows)

```bash
run_daily_forecast.bat
```

Chọn mode:
- **1**: Daily Forecast (once) - không có web
- **2**: Daily Scheduler (continuous) - có web dashboard
- **3**: Retrain Model - không có web
- **4**: Web Dashboard Only
- **5**: Daily Forecast + Web Dashboard

## ⚙️ Cấu hình

### Thông số mô hình

- **n_steps**: 30 (số ngày dữ liệu để dự đoán)
- **Features**: QV2M (độ ẩm tương đối), GWETROOT (độ ẩm đất)
- **Model**: LSTM với 64 units, dropout 0.2
- **Optimizer**: Adam
- **Loss**: MSE

### Lịch trình tự động

- **Daily forecast**: 6:00 AM mỗi ngày
- **Weekly retrain**: 2:00 AM mỗi Chủ nhật

## 📊 Dữ liệu

### Nguồn dữ liệu
- **NASA POWER API**: Dữ liệu thời tiết hàng ngày
- **Tọa độ**: 21°01'N, 105°83'E (Hà Nội, Việt Nam)
- **Thời gian**: Từ 2011 đến hiện tại

### Xử lý dữ liệu
- Tự động loại bỏ dữ liệu thiếu (-999.0)
- Chuẩn hóa dữ liệu bằng MinMaxScaler
- Tạo sequences cho LSTM (30 ngày → 1 ngày dự đoán)

## 🔧 Troubleshooting

### Lỗi thường gặp

1. **ModuleNotFoundError**: Cài đặt dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. **CSV file not found**: Kiểm tra đường dẫn file dữ liệu

3. **Not enough data**: Cần ít nhất 30 ngày dữ liệu hợp lệ

4. **Model shape mismatch**: Retrain model với dữ liệu mới
   ```bash
   python src/main.py --mode retrain
   ```

### Kiểm tra log

Xem file `daily_forecast.log` để theo dõi quá trình hoạt động:

```bash
tail -f daily_forecast.log
```

## 🌐 Web Dashboard

### Tính năng web dashboard:
- **Giao diện đẹp mắt**: Thiết kế responsive, hiện đại
- **Hiển thị trực quan**: Cards cho từng ngày dự báo
- **Tự động cập nhật**: Refresh dữ liệu mỗi 5 phút
- **API endpoints**: `/api/forecast`, `/api/status`
- **Real-time**: Cập nhật ngay khi có dự báo mới

### Truy cập web dashboard:
- **URL**: http://127.0.0.1:5000
- **Tự động mở**: Khi chạy `--mode once` hoặc `--mode scheduler`
- **Chỉ web**: Khi chạy `--mode web`

## 📈 Kết quả

Hệ thống sẽ tạo ra:
- **Dự báo hàng ngày**: QV2M và GWETROOT cho ngày tiếp theo
- **Web dashboard**: Giao diện web để xem kết quả
- **Log file**: Ghi lại toàn bộ quá trình hoạt động
- **Model files**: model.h5 và scaler.pkl được tự động cập nhật

## 📘 Giải thích các thông số (ví dụ)

- **QV2M**: 20.1268
  - Thường là Specific Humidity at 2 m (độ ẩm riêng phần của không khí ở cao độ 2 m).
  - Đơn vị tùy nguồn, phổ biến là g/kg (hoặc kg/kg). Giá trị ~20 thường hiểu là g/kg.

- **GWETROOT**: 0.8380
  - Soil Moisture in Root Zone (độ ẩm đất vùng rễ), chuẩn hóa trong khoảng 0–1.
  - 0.8380 nghĩa là đất vùng rễ đang 83.8% ẩm, gần mức Field Capacity.

- **IRRIGATION_NET_MM**: 0.0000
  - Net irrigation water requirement (mm): lượng nước cần bổ sung để đưa ẩm độ đất về Field Capacity.
  - Đơn vị: mm lớp nước. Bằng 0 → chưa cần tưới vì đất còn đủ ẩm.

- **IRRIGATION_GROSS_MM**: 0.0000
  - Lượng nước thực tế phải tưới có tính tổn thất do hiệu suất hệ thống tưới < 100%.
  - Công thức: Gross = Net / IrrigationEfficiency
  - Ví dụ Net = 10 mm, Efficiency = 0.8 → Gross = 12.5 mm.

- **DEPLETION_FRAC**: 0.0000
  - Tỷ lệ nước đã bị khai thác/thiếu hụt so với lượng nước có thể khai thác (AWC) trong vùng rễ.
  - 0 nghĩa là đất chưa bị thiếu nước. Nếu vượt ngưỡng (thường 0.3–0.5 tùy cây trồng) thì cần tưới.

## 🔄 Quy trình hoạt động

1. **Cập nhật dữ liệu**: Kéo dữ liệu mới từ NASA POWER API
2. **Kiểm tra dữ liệu**: Xác minh độ mới và chất lượng dữ liệu
3. **Load model**: Sử dụng model đã train hoặc train mới
4. **Tạo dự báo**: Dự đoán thời tiết ngày mai
5. **Ghi log**: Lưu kết quả và thông tin hoạt động

## 📝 Lưu ý

- Hệ thống yêu cầu kết nối internet để cập nhật dữ liệu
- Model sẽ được tự động retrain khi có dữ liệu mới
- Dữ liệu được lưu trữ local trong file CSV
- Log file được ghi đè mỗi ngày

## 🤝 Đóng góp

Để đóng góp vào dự án, vui lòng:
1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Tạo Pull Request

## 📄 License

Dự án này được phát triển cho mục đích học tập và nghiên cứu.