import csv
import datetime as dt
import os

import numpy as np
from matplotlib import pyplot
from pandas import datetime
from pandas import read_csv
from sklearn.metrics import mean_squared_error
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX

from prepare_historical_data import PREDICTION_END_YEAR, months, DATA_FOLDER, PYTHON_LANGUAGE, R_LANGUAGE, \
    CSV_FILE_SUFFIX

SARIMAX_ = "sarimax"

PREDICTIONS_FOLDER = "results"


def write_to_csv(dates, predictions, language, model):
    data_file_name = os.path.join(PREDICTIONS_FOLDER, language + "_" + model + "_predictions.csv")

    with open(data_file_name, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(zip(dates, predictions))
    return True


def create_predictions_folder():
    if not os.path.exists(PREDICTIONS_FOLDER):
        os.makedirs(PREDICTIONS_FOLDER)


def RMSE(actual, pred):
    mse = mean_squared_error(actual, pred)
    rmse = np.sqrt(mse)
    return rmse


def parser(x):
    return datetime.strptime(x, '%Y-%m')


def get_future_date_list():
    future_dates = [str(year) + "-" + month for year in range(2019, PREDICTION_END_YEAR + 1) for month in
                    months]

    dates_list = [dt.datetime.strptime(date, '%Y-%m').date() for date in future_dates]
    print(dates_list)
    return dates_list


def run_arima(language):
    create_predictions_folder()
    series = read_csv(os.path.join(DATA_FOLDER, language + CSV_FILE_SUFFIX), header=0, parse_dates=[0], index_col=0,
                      squeeze=True,
                      date_parser=parser)

    data = series.values.tolist()
    train, test = data[:-12], data[-12:]
    model = ARIMA(train, order=(1, 1, 1))
    model_fit = model.fit(disp=False,
                          start_params=[1, .1, .1])  # , start_params=[np.mean(data), .1, np.mean(data)]
    dates_list = get_future_date_list()
    test_pred = model_fit.predict(len(train) + 1, len(data) - 1, typ='levels')
    future_pred = model_fit.predict(len(data), len(data) + 59, typ='levels')
    future_pred = future_pred[12:]
    pyplot.figure()
    pyplot.title("Predictions based on ARIMA model : " + language + " repositories")
    pyplot.plot(series, label='Historical data')
    pyplot.plot(series.keys().tolist(), [None for i in range(len(train))] + test_pred.tolist(),
                label='Predictions - Test data')
    pyplot.plot(dates_list, future_pred, label='Predictions - 2019 to 2023')
    pyplot.legend()
    pyplot.savefig(os.path.join(PREDICTIONS_FOLDER, language + "_predictions_arima.png"))

    rmse = RMSE(test, test_pred)
    print('ARIMA RMSE: %.3f' % rmse + " for " + language + " repos test set")
    write_to_csv([str(date_)[:-3] for date_ in dates_list], future_pred, language, "arima")
    return future_pred


def run_sarimax(language):
    create_predictions_folder()
    series = read_csv(os.path.join(DATA_FOLDER, language + CSV_FILE_SUFFIX), header=0, parse_dates=[0], index_col=0,
                      squeeze=True,
                      date_parser=parser)

    data = series.values.tolist()
    train, test = data[:-12], data[-12:]
    model_fit = SARIMAX(train, order=(2, 1, 4), seasonal_order=(1, 1, 1, 12)).fit()
    dates_list = get_future_date_list()
    print(len(dates_list))
    test_pred = model_fit.predict(len(train) + 1, len(data), dynamic=True)
    future_pred = model_fit.predict(len(data), len(data) + 59, dynamic=True)
    pyplot.figure()
    pyplot.title("Predictions based on SARIMAX model : " + language + " repositories")
    pyplot.plot(series, label='Historical data')
    pyplot.plot(series.keys().tolist(), [None for i in range(len(train))] + test_pred.tolist(),
                label='Predictions - Test data')
    pyplot.plot(dates_list, future_pred, label='Predictions - 2019 to 2023')
    pyplot.legend()
    pyplot.savefig(os.path.join(PREDICTIONS_FOLDER, language + "_predictions_SARIMAX.png"))

    rmse = RMSE(test, test_pred)
    print('SARIMAX RMSE: %.3f' % rmse + " for " + language + " repos test set")
    write_to_csv([str(date_)[:-3] for date_ in dates_list], future_pred, language, SARIMAX_)
    return future_pred


if __name__ == '__main__':
    run_arima(PYTHON_LANGUAGE)
    run_arima(R_LANGUAGE)
    run_sarimax(PYTHON_LANGUAGE)
    run_sarimax(R_LANGUAGE)
