import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, feature_cols, scaler=None):
        self.feature_cols = feature_cols
        self.scaler = scaler

    def plot_results(self, y_test, y_pred, dates=None, save_path="forecast.png"):
        # If a scaler is provided, inverse-transform to original scale
        if self.scaler is not None:
            y_test = self.scaler.inverse_transform(y_test)
            y_pred = self.scaler.inverse_transform(y_pred)

        fig, axes = plt.subplots(len(self.feature_cols), 1, figsize=(12, 6), sharex=True)
        if len(self.feature_cols) == 1:
            axes = [axes]

        x_values = range(len(y_test)) if dates is None else dates

        for i, col in enumerate(self.feature_cols):
            axes[i].plot(x_values, y_test[:, i], label="Actual")
            axes[i].plot(x_values, y_pred[:, i], label="Predicted")
            axes[i].set_title(f"Forecast for {col}")
            axes[i].legend()

        if dates is not None:
            # Rotate x labels for readability
            axes[-1].tick_params(axis='x', rotation=45)

        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()
