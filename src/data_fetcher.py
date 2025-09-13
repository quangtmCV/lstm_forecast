import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json

class DataFetcher:
    """
    Fetches daily weather data from NASA POWER API and updates the local dataset.
    """
    
    def __init__(self, base_csv_path, lat=21.01, lon=105.83):
        self.base_csv_path = base_csv_path
        self.lat = lat
        self.lon = lon
        self.base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
        self.feature_cols = ["QV2M", "GWETROOT"]
        
    def fetch_daily_data(self, start_date, end_date):
        """
        Fetch data from NASA POWER API for the given date range.
        
        Args:
            start_date (str): Start date in YYYYMMDD format
            end_date (str): End date in YYYYMMDD format
            
        Returns:
            dict: API response data
        """
        params = {
            "parameters": "QV2M,GWETROOT",
            "community": "RE",
            "longitude": self.lon,
            "latitude": self.lat,
            "start": start_date,
            "end": end_date,
            "format": "JSON"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from NASA POWER API: {e}")
            return None
    
    def parse_api_response(self, api_data):
        """
        Parse NASA POWER API response into DataFrame format.
        
        Args:
            api_data (dict): API response data
            
        Returns:
            pd.DataFrame: Parsed data with DATE, QV2M, GWETROOT columns
        """
        if not api_data or "properties" not in api_data:
            return None
            
        properties = api_data["properties"]
        parameter_data = properties["parameter"]
        
        # Extract QV2M and GWETROOT data
        qv2m_data = parameter_data.get("QV2M", {})
        gwetroot_data = parameter_data.get("GWETROOT", {})
        
        # Get all available dates
        all_dates = set(qv2m_data.keys()) | set(gwetroot_data.keys())
        all_dates = sorted(all_dates)
        
        data = []
        for date_str in all_dates:
            try:
                # Convert YYYYMMDD to datetime
                date_obj = datetime.strptime(date_str, "%Y%m%d")
                
                # Get values, use NaN if missing
                qv2m_val = qv2m_data.get(date_str, np.nan)
                gwetroot_val = gwetroot_data.get(date_str, np.nan)
                
                # Convert -999.0 to NaN (NASA POWER missing value indicator)
                if qv2m_val == -999.0:
                    qv2m_val = np.nan
                if gwetroot_val == -999.0:
                    gwetroot_val = np.nan
                
                # Keep all data, even if missing - we'll handle it in data_loader
                # Don't skip any data points
                    
                data.append({
                    "DATE": date_obj,
                    "QV2M": qv2m_val,
                    "GWETROOT": gwetroot_val
                })
            except ValueError:
                continue
                
        if not data:
            return None
            
        df = pd.DataFrame(data)
        df = df.sort_values("DATE").reset_index(drop=True)
        return df
    
    def get_last_date_from_csv(self):
        """
        Get the last date from the existing CSV file.
        
        Returns:
            datetime: Last date in the CSV file, or None if file doesn't exist
        """
        if not os.path.exists(self.base_csv_path):
            return None
            
        try:
            # Read the last few lines to find the last date
            with open(self.base_csv_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                
            # Find header line
            header_idx = None
            for i, line in enumerate(lines[:50]):
                if "YEAR" in line and "DOY" in line:
                    header_idx = i
                    break
                    
            if header_idx is None:
                return None
                
            # Read data starting from header
            df = pd.read_csv(self.base_csv_path, header=header_idx)
            
            # Convert YEAR + DOY to DATE
            df["DATE"] = df.apply(lambda r: datetime.strptime(
                f"{int(r['YEAR'])}-{int(r['DOY'])}", "%Y-%j"
            ), axis=1)
            
            return df["DATE"].max()
        except Exception as e:
            print(f"Error reading last date from CSV: {e}")
            return None
    
    def update_dataset(self, days_back=7):
        """
        Update the dataset with new data from NASA POWER API.
        
        Args:
            days_back (int): Number of days back to fetch (to ensure we don't miss any data)
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        # Get the last date from existing CSV
        last_date = self.get_last_date_from_csv()
        
        if last_date is None:
            print("No existing data found. Please ensure the base CSV file exists.")
            return False
            
        # Calculate date range for fetching
        start_date = last_date - timedelta(days=days_back)
        end_date = datetime.now()  # Today to get the latest available data
        
        # Always fetch new data - no skipping
        print(f"Force fetching new data. Last date: {last_date.date()}")
            
        print(f"Fetching data from {start_date.date()} to {end_date.date()}")
        
        # Fetch new data
        start_str = start_date.strftime("%Y%m%d")
        end_str = end_date.strftime("%Y%m%d")
        
        api_data = self.fetch_daily_data(start_str, end_str)
        if api_data is None:
            return False
            
        # Parse the response
        new_df = self.parse_api_response(api_data)
        if new_df is None or new_df.empty:
            print("No new data received from API")
            return False
            
        print(f"Received {len(new_df)} new data points")
        
        # Load existing data
        try:
            with open(self.base_csv_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                
            header_idx = None
            for i, line in enumerate(lines[:50]):
                if "YEAR" in line and "DOY" in line:
                    header_idx = i
                    break
                    
            if header_idx is None:
                print("Could not find header in existing CSV")
                return False
                
            existing_df = pd.read_csv(self.base_csv_path, header=header_idx)
            existing_df["DATE"] = existing_df.apply(lambda r: datetime.strptime(
                f"{int(r['YEAR'])}-{int(r['DOY'])}", "%Y-%j"
            ), axis=1)
            
        except Exception as e:
            print(f"Error loading existing data: {e}")
            return False
            
        # Merge new data with existing data
        # Remove duplicates and keep the latest
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=["DATE"], keep="last")
        combined_df = combined_df.sort_values("DATE").reset_index(drop=True)
        
        # Convert back to YEAR + DOY format for NASA POWER format
        combined_df["YEAR"] = combined_df["DATE"].dt.year
        combined_df["DOY"] = combined_df["DATE"].dt.dayofyear
        
        # Reorder columns to match original format
        output_df = combined_df[["YEAR", "DOY", "QV2M", "GWETROOT"]]
        
        # Save updated data
        try:
            # Create backup
            backup_path = self.base_csv_path.replace(".csv", "_backup.csv")
            if os.path.exists(self.base_csv_path):
                os.rename(self.base_csv_path, backup_path)
                
            # Write new data
            output_df.to_csv(self.base_csv_path, index=False)
            print(f"Dataset updated successfully. Total records: {len(output_df)}")
            
            # Remove backup if successful
            if os.path.exists(backup_path):
                os.remove(backup_path)
                
            return True
            
        except Exception as e:
            print(f"Error saving updated dataset: {e}")
            # Restore backup if it exists
            backup_path = self.base_csv_path.replace(".csv", "_backup.csv")
            if os.path.exists(backup_path):
                os.rename(backup_path, self.base_csv_path)
            return False
    
    def get_today_forecast_data(self):
        """
        Get the latest data window for today's forecast.
        
        Returns:
            np.array: Latest data window for forecasting, or None if not enough data
        """
        try:
            with open(self.base_csv_path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                
            header_idx = None
            for i, line in enumerate(lines[:50]):
                if "YEAR" in line and "DOY" in line:
                    header_idx = i
                    break
                    
            if header_idx is None:
                return None
                
            df = pd.read_csv(self.base_csv_path, header=header_idx)
            df["DATE"] = df.apply(lambda r: datetime.strptime(
                f"{int(r['YEAR'])}-{int(r['DOY'])}", "%Y-%j"
            ), axis=1)
            
            # Get the last 30 days of data for forecasting
            latest_data = df.tail(30)[self.feature_cols].values
            
            if len(latest_data) < 30:
                print(f"Not enough data for forecasting. Need 30 days, have {len(latest_data)}")
                return None
                
            return latest_data
            
        except Exception as e:
            print(f"Error getting forecast data: {e}")
            return None
