import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

class Trainer:
    def __init__(self, model, scaler, feature_cols):
        self.model = model
        self.scaler = scaler
        self.feature_cols = feature_cols

    def train(self, X_train, y_train, X_val, y_val, epochs=30, batch_size=32):
        history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            verbose=1
        )
        return history

    def evaluate(self, X_test, y_test):
        y_pred = self.model.predict(X_test)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mae = mean_absolute_error(y_test, y_pred)
        return y_pred, rmse, mae

    def predict_next(self, last_window):
        """Predict next step in original scale given last scaled window.
        last_window shape: (1, n_steps, n_features)
        Returns dict feature->value
        """
        y_scaled = self.model.predict(last_window)
        y_original = self.scaler.inverse_transform(y_scaled)[0]
        return {col: float(val) for col, val in zip(self.feature_cols, y_original)}

    def forecast_multi_step(self, start_window, steps):
        """Recursive multi-step forecast in original scale.
        start_window: (1, n_steps, n_features) scaled
        steps: number of future steps to predict
        Returns list of dicts [{feature: value, ...}, ...]
        """
        window = start_window.copy()
        preds = []
        for _ in range(steps):
            y_scaled = self.model.predict(window)
            preds.append(self.scaler.inverse_transform(y_scaled)[0])
            # append scaled prediction to the rolling window
            next_step = y_scaled.reshape(1, 1, -1)
            window = np.concatenate([window[:, 1:, :], next_step], axis=1)
        # Convert to list of dicts
        results = []
        for row in preds:
            results.append({col: float(val) for col, val in zip(self.feature_cols, row)})
        return results