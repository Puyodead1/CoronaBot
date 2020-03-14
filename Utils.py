#  Copyright (C) 2020  Puyodead1
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.

import coloredlogs
import requests
import verboselogs
import logging
import pandas as pd


class SetupLogger:
    def __init__(self, full_debug=False):
        verboselogs.install()
        self.logger = logging.getLogger(__name__)
        coloredlogs.install(level="DEBUG", logger=self.logger if not full_debug else None,
                            fmt="[%(levelname)s] %(asctime)s: %(message)s",
                            datefmt="[%m-%d-%Y %I:%M:%S]")


def getLogger():
    return logging.getLogger(__name__)


class CoronaAPI:
    def __init__(self):
        self.all_url = "https://corona.lmao.ninja/all"
        self.countries_url = "https://corona.lmao.ninja/countries"
        self.states_url = "https://api.github.com/repos/CSSEGISandData/COVID-19/contents/csse_covid_19_data/csse_covid_19_daily_reports"

    def getAll(self):
        response = requests.get(self.all_url)
        if response.status_code == 200:
            return response.json()
        else:
            getLogger().error(
                f"[CoronaAPI] Failed to call All Information url! Status Code: {response.status_code}; Response Text: {response.text}")
            return None

    def getCountry(self, country):
        response = requests.get(self.countries_url)
        if response.status_code == 200:
            json = response.json()
            countries = dict()
            for key in json:
                countries[str(key["country"]).lower()] = key

            if str(country).lower() in countries:
                return countries.get(str(country).lower())
            else:
                return None
        else:
            getLogger().error(
                f"[CoronaAPI] Failed to call Countries Information url! Status Code: {response.status_code}; Response Text: {response.text}")
            return None

    def getCountries(self):
        response = requests.get(self.countries_url)
        if response.status_code == 200:
            json = response.json()
            countries = []
            for key in json:
                countries.append(key["country"])

            return countries
        else:
            getLogger().error(
                f"[CoronaAPI] Failed to call Countries Information url! Status Code: {response.status_code}; Response Text: {response.text}")
            return None

    def getCountriesOverview(self):
        response = requests.get(self.countries_url)
        if response.status_code == 200:
            json = response.json()
            countries = []
            for key in json:
                countries.append(key["country"] + " - ``Cases: " + str(key["cases"]) + "`` | ``Cases Today: " + str(key["todayCases"]) + "`` | ``Deaths: " + str(key["deaths"]) + "`` | ``Deaths Today: " + str(key["todayDeaths"]) + "`` | ``Recoveries: " + str(key["recovered"]) + "`` | ``Critical: " + str(key["critical"]) + "``\n")

            return countries
        else:
            getLogger().error(
                f"[CoronaAPI] Failed to call Countries Information url! Status Code: {response.status_code}; Response Text: {response.text}")
            return None

    def getStates(self):
        response = requests.get(self.states_url)
        if response.status_code == 200:
            json = response.json()
            objs = []
            for key in json:
                if "README.md" not in key["name"] and ".gitignore" not in key["name"]:
                    objs.append(key)

            a = objs[-1]["download_url"]
            data = pd.read_csv(a)
            data = data.fillna("N/A")
            json_data = data.to_dict(orient='records')

            states = []
            for key in json_data:
                if key["Province/State"] != "N/A":
                    states.append(key["Province/State"] + " - " + key["Country/Region"])

            return states
        else:
            getLogger().error(
                f"[CoronaAPI] Failed to call States Information url! Status Code: {response.status_code}; Response Text: {response.text}")
            return None

    def getState(self, state):
        response = requests.get(self.states_url)
        if response.status_code == 200:
            json = response.json()
            objs = []
            for key in json:
                if "README.md" not in key["name"] and ".gitignore" not in key["name"]:
                    objs.append(key)

            a = objs[-1]["download_url"]
            data = pd.read_csv(a)
            data = data.fillna("N/A")
            json_data = data.to_dict(orient='records')

            for key in json_data:
                if key["Province/State"] != "N/A" and key["Province/State"] == state:
                    return key

            return None
        else:
            getLogger().error(
                f"[CoronaAPI] Failed to call States Information url! Status Code: {response.status_code}; Response Text: {response.text}")
            return None
