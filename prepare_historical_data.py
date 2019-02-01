import csv
import os
from string import Template

import requests
from matplotlib import pyplot
from pandas import Series
from ratelimit import limits, sleep_and_retry

PYTHON_LANGUAGE = "python"
R_LANGUAGE = "R"
CSV_FILE_SUFFIX = '_historical_repo_data.csv'

ONE_MINUTE = 60
FIFTEEN_MINUTES = 900
ONE_HOUR = 3600
token = ""

AUTH_TOKEN_FILE = "token_file.txt"
with open(AUTH_TOKEN_FILE, "r") as f:
    token = f.read().rstrip()

headers = {"Authorization": "token " + token}
GRAPHQL_URL = 'https://api.github.com/graphql'

FIRST_YEAR = 2008  # no python/R github repositories before 2008
END_YEAR = 2019
PREDICTION_END_YEAR = 2023
DATE = "01"
months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
DATA_FOLDER = "data"


@sleep_and_retry
@limits(calls=5000, period=ONE_HOUR)
def get_repo_count(query):
    current_request = requests.post(GRAPHQL_URL, json={'query': query}, headers=headers)

    if current_request.status_code != 200:
        raise Exception('API response: {}'.format(current_request.status_code))

    return current_request.json()["data"]["search"]["repositoryCount"]


def get_historical_repo_data(language):
    year = FIRST_YEAR

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    data_file_name = os.path.join(DATA_FOLDER, language + CSV_FILE_SUFFIX)

    with open(data_file_name, mode='w', newline='') as data_file:
        while year < END_YEAR:
            for month in months:
                limit_year = year
                limit_month = ""
                if month == months[-1]:
                    limit_year = year + 1
                    limit_month = "01"
                else:
                    limit_month = months[months.index(month) + 1]

                query = Template("""
                query {
                  search(type: REPOSITORY, query: "language:$language created:$dates") {
                    repositoryCount
                  }
                }
                """)

                query = query.substitute(language=language,
                                         dates=str(year) + '-' + month + '-01..' + str(
                                             limit_year) + '-' + limit_month + '-01')

                repo_count = get_repo_count(query)
                data_writer = csv.writer(data_file, delimiter=',')
                data_writer.writerow([str(year) + '-' + month, repo_count])

                print("year,month,count", year, month, repo_count)
                year = limit_year


def plot_historical_data(language):
    pyplot.figure()
    series = Series.from_csv(os.path.join(DATA_FOLDER, language + CSV_FILE_SUFFIX))
    series.plot()
    pyplot.title("Number of " + language + " repositions created (per month)")
    pyplot.savefig(os.path.join(DATA_FOLDER, language + '_data.png'))


if __name__ == '__main__':
    get_historical_repo_data(PYTHON_LANGUAGE)
    plot_historical_data(PYTHON_LANGUAGE)

    get_historical_repo_data(R_LANGUAGE)
    plot_historical_data(R_LANGUAGE)
