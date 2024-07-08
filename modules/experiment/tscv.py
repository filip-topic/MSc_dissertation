from sklearn.model_selection import TimeSeriesSplit
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import sys
import os

# Get the path of the MSc_dissertation directory
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Add the modules directory to the sys.path
sys.path.append(base_dir)




from modules.models import arima, lag_llama, autoregressor


def mean_directional_accuracy(actual, predicted, last_train_point):
    
    a = actual.copy()
    p = predicted.copy()

    a.append(last_train_point)
    p.append(last_train_point)

    a = pd.Series(a)
    p = pd.Series(p)

    actual_diff = a.diff().dropna()
    predicted_diff = p.diff().dropna()
    
    # Align the series after dropping NaN values due to differencing
    #actual_diff = actual_diff 
    #predicted_diff = predicted_diff 
    
    correct_directions = (actual_diff * predicted_diff > 0).sum()
    total_directions = len(actual_diff)
    
    mda_value = correct_directions / total_directions
    
    return mda_value


def get_summary(results):
    summary = pd.DataFrame({
    'r2': [results['r2'].mean(), results['r2'].median(), results['r2'].std()],
    'mse': [results['mse'].mean(), results['mse'].median(), results['mse'].std()],
    'mae': [results['mae'].mean(), results['mae'].median(), results['mae'].std()],
    'rmse': [results['rmse'].mean(), results['rmse'].median(), results['rmse'].std()],
    'mda': [results['mda'].mean(), results['mda'].median(), results['mda'].std()]
    }, index=['mean', 'median', 'std'])
    return summary


def get_tscv_results(data, prediction_horizon, context_length, folds):

    tscv = TimeSeriesSplit(n_splits=folds, test_size=prediction_horizon)

    """
    models=["arima", "llama"]
    results = {metric: {model: {f"fold_{i}": [] for i in range(folds)} for model in models} for metric in metrics}
    """
    
    results = []

    metrics=["r2", "mse", "mae", "rmse", "mda"] 

    arima_results = pd.DataFrame(columns=metrics)
    llama_results = pd.DataFrame(columns= metrics)
    autoregressor_results = pd.DataFrame(columns=metrics)

    series = data["y"]

    i = 0

    for train_index, test_index in tscv.split(series):
    # subsetting the original data according to train/test split
        train = data.iloc[train_index]
        valid = list(data.iloc[test_index]["y"])


        # inputting data into the models
        arima_model = arima.get_autoarima(train)
        autoarima_predictions = arima.autoarima_predictions(arima_model, prediction_horizon)
        lag_llama_predictions, tss = lag_llama.get_lam_llama_forecast(train, prediction_horizon, context_length=context_length)
        lag_llama_predictions = list(lag_llama_predictions[0].samples.mean(axis = 0))
        autoregressor_predictions = autoregressor.get_autoregressor_prediction(train, prediction_horizon)

        # for my own testing purposes
        """
        print(autoarima_predictions)
        print(lag_llama_predictions)
        print(valid)
        """

        """
        # recording the metrics
        results["r2"]["arima"][f"fold_{i}"].append(r2_score(valid, autoarima_predictions))
        results["mse"]["arima"][f"fold_{i}"].append(mean_squared_error(valid, autoarima_predictions))
        results["mae"]["arima"][f"fold_{i}"].append(mean_absolute_error(valid, autoarima_predictions))
        results["rmse"]["arima"][f"fold_{i}"].append(np.sqrt(mean_squared_error(valid, autoarima_predictions)))
        results["mda"]["arima"][f"fold_{i}"].append(mean_directional_accuracy(valid, autoarima_predictions))

        results["r2"]["llama"][f"fold_{i}"].append(r2_score(valid, lag_llama_predictions))
        results["mse"]["llama"][f"fold_{i}"].append(mean_squared_error(valid, lag_llama_predictions))
        results["mae"]["llama"][f"fold_{i}"].append(mean_absolute_error(valid, lag_llama_predictions))
        results["rmse"]["llama"][f"fold_{i}"].append(np.sqrt(mean_squared_error(valid, lag_llama_predictions)))
        results["mda"]["llama"][f"fold_{i}"].append(mean_directional_accuracy(valid, lag_llama_predictions))
        """

        arima_metrics = [r2_score(valid, autoarima_predictions), 
               mean_squared_error(valid, autoarima_predictions), 
               mean_absolute_error(valid, autoarima_predictions),
               np.sqrt(mean_squared_error(valid, autoarima_predictions)),
               mean_directional_accuracy(valid, autoarima_predictions, train["y"].iloc[-1])]
    
        llama_metrics = [r2_score(valid, lag_llama_predictions), 
               mean_squared_error(valid, lag_llama_predictions), 
               mean_absolute_error(valid, lag_llama_predictions),
               np.sqrt(mean_squared_error(valid, lag_llama_predictions)),
               mean_directional_accuracy(valid, lag_llama_predictions, train["y"].iloc[-1])]
    
        autoregressor_metrics = [r2_score(valid, autoregressor_predictions), 
               mean_squared_error(valid, autoregressor_predictions), 
               mean_absolute_error(valid, autoregressor_predictions),
               np.sqrt(mean_squared_error(valid, autoregressor_predictions)),
               mean_directional_accuracy(valid, autoregressor_predictions, train["y"].iloc[-1])]

        arima_results = pd.concat([arima_results, pd.DataFrame([arima_metrics], columns=metrics)], ignore_index=True)
        llama_results = pd.concat([llama_results, pd.DataFrame([llama_metrics], columns=metrics)], ignore_index=True)
        autoregressor_results = pd.concat([autoregressor_results, pd.DataFrame([autoregressor_metrics], columns=metrics)], ignore_index=True)

        results = [arima_results, llama_results, autoregressor_results]
        
        i += 1
    
    return results



if __name__ == "__main__":
    
    actual = pd.Series([100, 102, 101, 103, 105])
    predicted = pd.Series([100, 101, 102, 104, 106])

    print(f"Mean Directional Accuracy: {mean_directional_accuracy(actual, predicted)}")
