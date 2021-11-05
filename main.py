from os import listdir
from os.path import isfile, join
import smart_open
from unittest.mock import patch as mock_patch
from flumine import FlumineBacktest, clients
from strategies.datacollectwom import DataCollectWOM

from utils import setup_logging

"""
WOM data collection script
Restricted to final 300s before start of race
Data saved to context["filename"]
Collects data every 5s

# todo multiprocessing to speed up processing
"""

setup_logging(level="CRITICAL")

client = clients.BacktestClient()

framework = FlumineBacktest(client=client)

directory = "/Users/liampauling/Desktop/marketdata-day"  # update to market data dir
markets = [
    join(directory, f)
    for f in listdir(directory)
    if isfile(join(directory, f)) and f.endswith(".gz")
]

with mock_patch("builtins.open", smart_open.open):
    framework.add_strategy(
        DataCollectWOM(
            market_filter={
                "markets": markets,
                "listener_kwargs": {"seconds_to_start": 300},
            },
            context={
                "filename": "/tmp/datacollect-all.csv",
                "update_seconds": 5,  # seconds
            },
        )
    )
    framework.run()
