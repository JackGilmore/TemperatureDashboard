#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Jack Gilmore"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import csv
import os
import requests
from datetime import datetime, timedelta
from logzero import logger

SAVE_PATH = "../site/_data/temperatures.csv"


def main(args):
    """Main entry point of the app"""
    extract_date = args.date

    logger.info(f"Polling {args.endpoint} for data on {extract_date}")

    url = f"{args.endpoint}/api/history/period/{extract_date}T00:00:00?filter_entity_id={args.entity_id}&minimal_response"

    payload = {}
    headers = {"Authorization": f"Bearer {args.token}"}

    response = requests.request("GET", url, headers=headers, data=payload)

    data = response.json()

    temperature_entries = data[0]

    logger.info(f"Received {len(temperature_entries)} entries")

    filtered_temperatures = [x for x in temperature_entries if x["state"] != "unavailable"]

    parsed_temperatures = [float(x["state"]) for x in filtered_temperatures]

    average_temperature = sum(parsed_temperatures) / len(parsed_temperatures)

    logger.info(f"Calculated average temperature of {average_temperature:.2f}")

    script_directory = os.path.dirname(__file__)
    collection_file_path = os.path.join(script_directory, SAVE_PATH)

    logger.info(f"Saving to {collection_file_path}")

    if not os.path.isfile(collection_file_path):
        logger.info("File doesn't already exist. Creating file and writing header")
        # If the file doesn't exist, create it and write the header
        with open(collection_file_path, mode="w", newline="") as file:
            writer = csv.writer(file)
            header = ["date", "temperature"]            
            writer.writerow(header)
            data = [extract_date, average_temperature]
            writer.writerow(data)
    else:
        # If the file exists, open in append mode and write your data
        with open(collection_file_path, mode="a", newline="") as file:
            logger.info("Writing to existing file")
            writer = csv.writer(file)
            data = [extract_date, average_temperature]
            writer.writerow(data)


if __name__ == "__main__":
    """This is executed when run from the command line"""
    parser = argparse.ArgumentParser()

    # Required - Long-Lived Access Token for Home Assistant
    parser.add_argument(
        "endpoint",
        help="The root endpoint for your Home Assistant instance e.g. http://homeassistant.local:8123",
    )

    # Required - Entity Id
    parser.add_argument(
        "entity_id",
        help="The entity Id for the sensor you want to extract data from e.g. sensor.office_temperature_sensor_temperature",
    )

    # Required - Long-Lived Access Token for Home Assistant
    parser.add_argument(
        "token",
        help="Long-Lived Access Token for Home Assistant. See https://developers.home-assistant.io/docs/auth_api/#long-lived-access-token for more details.",
    )

    # Optional - Target date
    parser.add_argument(
        "--date",
        help="",
        default=(datetime.today() - timedelta(1)).strftime("%Y-%m-%d"),
    )

    # Optional - Version
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__),
    )

    args = parser.parse_args()
    main(args)
