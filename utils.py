import time
import logging
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()


def setup_logging(
    level: str = logging.INFO, custom_format: str = "%(asctime) %(levelname) %(message)"
):
    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(custom_format)
    formatter.converter = time.gmtime
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)
    logger.setLevel(level)
