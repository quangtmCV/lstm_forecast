# LSTM Weather Forecast System

Hệ thống dự báo thời tiết tự động sử dụng mô hình LSTM (Long Short-Term Memory) để dự đoán độ ẩm tương đối (QV2M) và độ ẩm đất (GWETROOT) cho ngày tiếp theo.

## 🌟 Tính năng chính

- **Tự động cập nhật dữ liệu**: Kéo dữ liệu mới nhất từ NASA POWER API mỗi ngày
- **Dự báo thời tiết**: Sử dụng mô hình LSTM để dự đoán thời tiết ngày mai
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
│   └── trainer.py                # Training và prediction
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

### 4. Sử dụng batch file (Windows)

```bash
run_daily_forecast.bat
```

Chọn mode:
- **1**: Daily Forecast (once)
- **2**: Daily Scheduler (continuous) 
- **3**: Retrain Model

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

## 📈 Kết quả

Hệ thống sẽ tạo ra:
- **Dự báo hàng ngày**: QV2M và GWETROOT cho ngày tiếp theo
- **Log file**: Ghi lại toàn bộ quá trình hoạt động
- **Model files**: model.h5 và scaler.pkl được tự động cập nhật

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