#!/usr/bin/env python3
"""
Daily LSTM Weather Forecast - Main Entry Point
Automatically runs daily to predict next day weather
"""

import schedule
import time
import logging
from datetime import datetime, timedelta
import os
import sys

from data_loader import DataLoader
from data_fetcher import DataFetcher
from model import build_model
from trainer import Trainer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pickle

class DailyForecastMain:
    """Main class for daily weather forecasting"""
    
    def __init__(self, csv_path="data/POWER_Point_Daily_20111207_20250807_021d01N_105d83E_LST.csv"):
        self.csv_path = csv_path
        self.n_steps = 20
        self.feature_cols = ["QV2M", "GWETROOT"]
        self.model_path = "model.h5"
        self.scaler_path = "scaler.pkl"
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        # Create formatter without emoji for file logging
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        
        # File handler
        file_handler = logging.FileHandler("daily_forecast.log", encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        
        # Console handler with UTF-8 encoding
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(console_formatter)
        
        # Setup logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def update_data(self):
        """Update data from NASA POWER API"""
        try:
            self.logger.info("Updating data from NASA POWER API...")
            fetcher = DataFetcher(self.csv_path)
            
            # Try to update with more days back to ensure we get latest data
            success = fetcher.update_dataset(days_back=7)
            
            if success:
                self.logger.info("[SUCCESS] Data updated successfully")
                
                # Verify the update by checking the latest date
                df, _ = self.load_data()
                if df is not None:
                    latest_date = df["DATE"].iloc[-1].date()
                    current_date = datetime.now().date()
                    days_behind = (current_date - latest_date).days
                    self.logger.info(f"Latest data date after update: {latest_date}")
                    self.logger.info(f"Data is now {days_behind} days behind current date")
                
                return True
            else:
                self.logger.error("[ERROR] Data update failed - cannot proceed without fresh data")
                return False
        except Exception as e:
            self.logger.error(f"[ERROR] Error updating data: {e}")
            return False
    
    def load_data(self):
        """Load and preprocess data"""
        try:
            loader = DataLoader(self.csv_path, n_steps=self.n_steps)
            df = loader.load_data()
            self.logger.info(f"Data loaded: {len(df)} records")
            self.logger.info(f"Date range: {df['DATE'].min().date()} to {df['DATE'].max().date()}")
            return df, loader
        except Exception as e:
            self.logger.error(f"[ERROR] Error loading data: {e}")
            return None, None
    
    def train_model(self, df):
        """Train LSTM model"""
        try:
            self.logger.info("Training LSTM model...")
            
            # Create sequences
            loader = DataLoader(self.csv_path, n_steps=self.n_steps)
            X, y, y_dates = loader.create_sequences(df)
            
            # Train/val/test split
            X_train, X_temp, y_train, y_temp, dates_train, dates_temp = train_test_split(
                X, y, y_dates, test_size=0.2, shuffle=False
            )
            X_val, X_test, y_val, y_test, dates_val, dates_test = train_test_split(
                X_temp, y_temp, dates_temp, test_size=0.5, shuffle=False
            )
            
            # Build model
            model = build_model(self.n_steps, X.shape[2])
            
            # Train
            trainer = Trainer(model, loader.scaler, self.feature_cols)
            history = trainer.train(X_train, y_train, X_val, y_val, epochs=20)
            
            # Evaluate
            y_pred, rmse, mae = trainer.evaluate(X_test, y_test)
            self.logger.info(f"Model performance - RMSE: {rmse:.4f}, MAE: {mae:.4f}")
            
            # Save model and scaler
            model.save(self.model_path)
            with open(self.scaler_path, 'wb') as f:
                pickle.dump(loader.scaler, f)
            
            self.logger.info("[SUCCESS] Model trained and saved successfully")
            return model, loader.scaler, trainer
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error training model: {e}")
            return None, None, None
    
    def load_existing_model(self):
        """Load existing trained model"""
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.scaler_path):
                from tensorflow.keras.models import load_model
                model = load_model(self.model_path)
                with open(self.scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
                self.logger.info("[SUCCESS] Loaded existing model")
                return model, scaler
            else:
                self.logger.info("No existing model found")
                return None, None
        except Exception as e:
            self.logger.error(f"[ERROR] Error loading existing model: {e}")
            return None, None
    
    def make_forecast(self, model, scaler, forecast_days=1):
        """Make weather forecast"""
        try:
            self.logger.info(f"Making {forecast_days}-day forecast...")
            
            # Load latest data
            loader = DataLoader(self.csv_path, n_steps=self.n_steps)
            df = loader.load_data()
            
            # Get last window using the trained scaler
            values = df[self.feature_cols].values
            scaled = scaler.transform(values)
            
            if len(scaled) < self.n_steps:
                raise ValueError("Not enough data for forecasting")
            
            last_window = scaled[-self.n_steps:]
            last_window = last_window.reshape(1, self.n_steps, -1)
            
            # Make prediction
            trainer = Trainer(model, scaler, self.feature_cols)
            
            if forecast_days == 1:
                forecast = trainer.predict_next(last_window)
                forecasts = [forecast]
            else:
                forecasts = trainer.forecast_multi_step(last_window, steps=forecast_days)
            
            # Display results
            # Use current date as base for consistent forecasting
            base_date = datetime.now().date()
            for i, forecast in enumerate(forecasts):
                forecast_date = base_date + timedelta(days=i+1)
                self.logger.info(f"Forecast for {forecast_date.strftime('%Y-%m-%d')}:")
                for feature, value in forecast.items():
                    self.logger.info(f"   {feature}: {value:.4f}")
            
            return forecasts
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error making forecast: {e}")
            return None
    
    def daily_forecast_pipeline(self):
        """Complete daily forecast pipeline"""
        self.logger.info("Starting daily forecast pipeline")
        self.logger.info("=" * 60)
        
        try:
            # Step 1: Always update data first to get latest data
            self.logger.info("Step 1: Updating data from NASA POWER API...")
            data_updated = self.update_data()
            
            if not data_updated:
                self.logger.error("[ERROR] Cannot proceed without fresh data. Pipeline stopped.")
                return None
            
            # Step 2: Load latest data
            self.logger.info("Step 2: Loading latest data...")
            df, loader = self.load_data()
            if df is None:
                return None
            
            # Check data freshness
            last_data_date = df["DATE"].iloc[-1].date()
            current_date = datetime.now().date()
            days_behind = (current_date - last_data_date).days
            
            self.logger.info(f"Latest data date: {last_data_date}")
            self.logger.info(f"Current date: {current_date}")
            self.logger.info(f"Data is {days_behind} days behind")
            
            if days_behind > 2:
                self.logger.warning(f"Data is {days_behind} days old. Consider updating data source.")
            
            # Step 3: Load or train model
            self.logger.info("Step 3: Loading or training model...")
            model, scaler = self.load_existing_model()
            if model is None:
                self.logger.info("No existing model found, training new model...")
                model, scaler, trainer = self.train_model(df)
                if model is None:
                    return None
            else:
                self.logger.info("Using existing model")
                trainer = Trainer(model, scaler, self.feature_cols)
            
            # Step 4: Make forecast for tomorrow
            self.logger.info("Step 4: Making forecast...")
            forecasts = self.make_forecast(model, scaler, forecast_days=1)
            
            if forecasts:
                self.logger.info("[SUCCESS] Daily forecast completed successfully!")
                return forecasts
            else:
                self.logger.error("[ERROR] Daily forecast failed!")
                return None
                
        except Exception as e:
            self.logger.error(f"[ERROR] Pipeline error: {e}")
            return None
    
    def run_scheduler(self):
        """Run the daily scheduler"""
        self.logger.info("Starting daily forecast scheduler")
        
        # Schedule daily forecast at 6:00 AM
        schedule.every().day.at("06:00").do(self.daily_forecast_pipeline)
        
        # Schedule weekly retraining on Sunday at 2:00 AM
        schedule.every().sunday.at("02:00").do(self.weekly_retrain)
        
        self.logger.info("Scheduled jobs:")
        self.logger.info("- Daily forecast: 06:00 every day")
        self.logger.info("- Weekly retraining: 02:00 every Sunday")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            self.logger.info("Scheduler stopped by user")
    
    def weekly_retrain(self):
        """Weekly full retraining"""
        self.logger.info("Starting weekly retraining...")
        
        try:
            # Update data
            self.update_data()
            
            # Load data
            df, loader = self.load_data()
            if df is None:
                return
            
            # Train new model
            model, scaler, trainer = self.train_model(df)
            if model is not None:
                self.logger.info("[SUCCESS] Weekly retraining completed")
            else:
                self.logger.error("[ERROR] Weekly retraining failed")
                
        except Exception as e:
            self.logger.error(f"[ERROR] Weekly retraining error: {e}")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily LSTM Weather Forecast")
    parser.add_argument("--mode", choices=["once", "scheduler", "retrain"], 
                       default="once", help="Run mode")
    parser.add_argument("--csv-path", 
                       default="data/POWER_Point_Daily_20111207_20250807_021d01N_105d83E_LST.csv",
                       help="Path to CSV data file")
    
    args = parser.parse_args()
    
    # Create forecast system
    forecast_system = DailyForecastMain(args.csv_path)
    
    if args.mode == "once":
        # Run once
        forecasts = forecast_system.daily_forecast_pipeline()
        if forecasts:
            print("\nFORECAST RESULTS:")
            print("-" * 40)
            for i, forecast in enumerate(forecasts):
                tomorrow = datetime.now() + timedelta(days=i+1)
                print(f"\n{tomorrow.strftime('%Y-%m-%d')}:")
                for feature, value in forecast.items():
                    print(f"   {feature}: {value:.4f}")
        else:
            print("Forecast failed!")
            sys.exit(1)
            
    elif args.mode == "scheduler":
        # Run scheduler
        forecast_system.run_scheduler()
        
    elif args.mode == "retrain":
        # Retrain model
        forecast_system.weekly_retrain()

if __name__ == "__main__":
    main()
