from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

def build_model(n_steps, n_features, n_units=64, dropout=0.2):
    model = Sequential()
    model.add(LSTM(n_units, activation="tanh", input_shape=(n_steps, n_features)))
    model.add(Dropout(dropout))
    model.add(Dense(n_features))  # dự báo cả QV2M và GWETROOT
    model.compile(optimizer="adam", loss="mse", metrics=["mae"])
    return model    