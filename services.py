import os

from flask import Flask
from flask import render_template
from pandas import Series

from arima_predictions import PREDICTIONS_FOLDER, DATA_FOLDER

app = Flask(__name__)


@app.route("/<language>")
def python_prediction(language):
    language = language.lower()
    if language == "r":
        language = "R"
    historical_data_series = Series.from_csv(os.path.join(DATA_FOLDER, language + "_historical_repo_data.csv"))
    future_prediction_series = Series.from_csv(os.path.join(PREDICTIONS_FOLDER, language + "_sarimax_predictions.csv"))
    combined_labels = [str(each.year) + "-" + str(each.month) for each in
                       historical_data_series.keys().tolist() + future_prediction_series.keys().tolist()]
    return render_template('chart.html',
                           hist_values=historical_data_series.values.tolist(),
                           pred_values=[None for i in range(
                               len(historical_data_series.values.tolist()))] + future_prediction_series.values.tolist(),
                           labels=combined_labels, title=language + " repository counts: prediction for the next 5 years")


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001)
