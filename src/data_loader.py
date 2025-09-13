import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from datetime import datetime

class DataLoader:
    def __init__(self, csv_path, n_steps=30):
        self.csv_path = csv_path
        self.n_steps = n_steps
        self.scaler = MinMaxScaler()
        self.feature_cols = ["QV2M", "GWETROOT"]

    def load_data(self):
        # Tìm dòng header (NASA POWER file có metadata)
        header_idx = None
        with open(self.csv_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for i, line in enumerate(lines[:50]):
            if "YEAR" in line and "DOY" in line:
                header_idx = i
                break
        df = pd.read_csv(self.csv_path, header=header_idx)

        # Ghép YEAR + DOY thành DATE
        df["DATE"] = df.apply(lambda r: datetime.strptime(
            f"{int(r['YEAR'])}-{int(r['DOY'])}", "%Y-%j"
        ), axis=1)

        # Select only required columns
        df = df[["DATE"] + self.feature_cols]
        
        # Remove rows with missing values (-999.0 is NASA POWER missing value indicator)
        print(f"Original data shape: {df.shape}")
        
        # Remove rows where any feature column has -999.0 or NaN
        for col in self.feature_cols:
            df = df[df[col] != -999.0]
        
        # Remove NaN values
        df = df.dropna()
        
        print(f"After removing missing values: {df.shape}")
        print(f"Removed {5031 - len(df)} rows with missing data")
        
        df.sort_values("DATE", inplace=True)
        return df

    def create_sequences(self, df):
        values = df[self.feature_cols].values
        scaled = self.scaler.fit_transform(values)
        dates = df["DATE"].values

        X, y, y_dates = [], [], []
        for i in range(len(scaled) - self.n_steps):
            X.append(scaled[i:i+self.n_steps])
            y.append(scaled[i+self.n_steps])
            y_dates.append(dates[i+self.n_steps])
        return np.array(X), np.array(y), np.array(y_dates)

    def get_last_window(self, df):
        """Return the last input window (scaled) shaped for model.predict.
        Returns array with shape (1, n_steps, n_features).
        """
        values = df[self.feature_cols].values
        # Ensure scaler is fitted before transform
        if not hasattr(self.scaler, 'data_min_'):
            self.scaler.fit(values)
        scaled = self.scaler.fit_transform(values)
        if len(scaled) < self.n_steps:
            raise ValueError("Not enough data to form the last window.")
        last_window = scaled[-self.n_steps:]
        return np.expand_dims(last_window, axis=0)

    def get_window_for_target_date(self, df, target_date):
        """Return window ending right before target_date in scaled form.
        Shape: (1, n_steps, n_features)
        """
        dates = pd.to_datetime(df["DATE"]).values
        values = df[self.feature_cols].values
        # Ensure scaler is fitted before transform
        if not hasattr(self.scaler, 'data_min_'):
            self.scaler.fit(values)
        scaled = self.scaler.fit_transform(values)
        # Normalize target_date to numpy datetime64 for comparison
        target_ts = pd.to_datetime(target_date).to_datetime64()
        matches = np.where(dates == target_ts)[0]
        if len(matches) == 0:
            raise ValueError("Target date not found in data.")
        t_idx = int(matches[0])
        start_idx = t_idx - self.n_steps
        if start_idx < 0:
            raise ValueError("Not enough history for the requested target date window.")
        window = scaled[start_idx:t_idx]
        return np.expand_dims(window, axis=0)