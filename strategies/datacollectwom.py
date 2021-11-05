import csv
import logging
from flumine.strategy.strategy import BaseStrategy
from flumine.utils import get_sp, get_price

logger = logging.getLogger(__name__)
FIELDNAMES = [
    "market_id",
    "market_seconds_to_start",
    "market_total_matched",
    "selection_id",
    "selection_back",
    "selection_lay",
    "selection_wom",
    "selection_total_matched",
    "selection_status",
    "selection_actual_sp",
]


class DataCollectWOM(BaseStrategy):
    """
    Collect market/runner data every
    x update_seconds.
    """

    def add(self) -> None:
        self.context["_data"] = []
        self.context["pt"] = 0
        self._write_headers()

    def _write_headers(self):
        with open(self.context["filename"], "w") as f:
            f.write(",".join(FIELDNAMES) + "\n")

    def check_market_book(self, market, market_book) -> bool:
        if market_book.status != "OPEN":
            return False
        if market_book.inplay:
            return False
        if "data" not in market.context:
            market.context["data"] = {}
        # check update seconds
        update_seconds = self.context["update_seconds"]
        pt = self.context["pt"]
        if market_book.publish_time_epoch - pt > (update_seconds * 1000):
            self.context["pt"] = market_book.publish_time_epoch
            return True
        return False

    def process_market_book(self, market, market_book) -> None:
        for runner in market_book.runners:
            if runner.status == "ACTIVE":
                # get prices
                back, lay = _get_back_lay(runner)
                # calculate WOM
                wom = _calculate_wom(runner)

                data = {
                    # market
                    "market_id": market.market_id[2:],
                    "market_seconds_to_start": market.seconds_to_start,
                    "market_total_matched": market_book.total_matched,
                    # selection
                    "selection_id": runner.selection_id,
                    # current state
                    "selection_back": back,
                    "selection_lay": lay,
                    "selection_wom": wom,
                    "selection_total_matched": runner.total_matched,
                    # after
                    "selection_status": None,
                    "selection_actual_sp": None,
                }
                self.context["_data"].append(data)

    def process_closed_market(self, market, market_book):
        # get runnerStatus (status and BSP)
        status = {}
        for runner in market_book.runners:
            status[runner.selection_id] = (runner.status, get_sp(runner))
        # write data to csv
        with open(self.context["filename"], "a") as f:
            csv_writer = csv.DictWriter(f, delimiter=",", fieldnames=FIELDNAMES)
            for d in self.context["_data"]:
                _status = status.get(d["selection_id"])
                d["selection_status"], d["selection_actual_sp"] = _status
                csv_writer.writerow(d)
        self.context["_data"].clear()


def _get_back_lay(runner_book, level: int = 0) -> tuple:
    if runner_book is None:
        return None, None
    back = get_price(runner_book.ex.available_to_back, level)
    lay = get_price(runner_book.ex.available_to_lay, level)
    return back, lay


def _calculate_wom(runner_book):
    pass
