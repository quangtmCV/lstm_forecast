from sklearn.model_selection import train_test_split
from data_loader import DataLoader
from model import build_model
from trainer import Trainer
from plotter import Plotter
from datetime import timedelta

def main():
    CSV_PATH = "../data/POWER_Point_Daily_20111207_20250807_021d01N_105d83E_LST.csv"
    N_STEPS = 30

    # Load data
    loader = DataLoader(CSV_PATH, n_steps=N_STEPS)
    df = loader.load_data()
    X, y, y_dates = loader.create_sequences(df)

    # Train/val/test split
    X_train, X_temp, y_train, y_temp, dates_train, dates_temp = train_test_split(
        X, y, y_dates, test_size=0.2, shuffle=False
    )
    X_val, X_test, y_val, y_test, dates_val, dates_test = train_test_split(
        X_temp, y_temp, dates_temp, test_size=0.5, shuffle=False
    )

    # Build model
    model = build_model(N_STEPS, X.shape[2])

    # Train
    trainer = Trainer(model, loader.scaler, loader.feature_cols)
    history = trainer.train(X_train, y_train, X_val, y_val, epochs=20)

    # Evaluate
    y_pred, rmse, mae = trainer.evaluate(X_test, y_test)
    print(f"RMSE: {rmse:.4f}, MAE: {mae:.4f}")

    # Plot with calendar dates and original units
    plotter = Plotter(loader.feature_cols, scaler=loader.scaler)
    plotter.plot_results(y_test, y_pred, dates=dates_test, save_path="forecast_results.png")

    # Predict yesterday, tomorrow, day after
    last_date = df["DATE"].iloc[-1]
    yesterday = last_date - timedelta(days=1)
    tomorrow = last_date + timedelta(days=1)
    day_after = last_date + timedelta(days=2)

    # Yesterday: build window ending before 'yesterday' if present
    try:
        win_yesterday = loader.get_window_for_target_date(df, yesterday)
        pred_yesterday = trainer.predict_next(win_yesterday)
        print(f"Forecast for {yesterday.date()} (yesterday):")
        for k, v in pred_yesterday.items():
            print(f"  {k}: {v:.4f}")
    except Exception as e:
        print(f"Cannot forecast yesterday ({yesterday.date()}): {e}")

    # Multi-step from last known window: tomorrow and day after
    start_window = loader.get_last_window(df)
    multi_preds = trainer.forecast_multi_step(start_window, steps=2)
    print(f"Forecast for {tomorrow.date()} (tomorrow):")
    for k, v in multi_preds[0].items():
        print(f"  {k}: {v:.4f}")
    print(f"Forecast for {day_after.date()} (day after):")
    for k, v in multi_preds[1].items():
        print(f"  {k}: {v:.4f}")

if __name__ == "__main__":
    main()
