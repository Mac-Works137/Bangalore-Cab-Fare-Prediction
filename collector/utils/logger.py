import logging
from pathlib import Path
from datetime import datetime


def get_logger(name="fare_collection"):

    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d")

    log_file = log_dir / f"fare_collection_{timestamp}.log"

    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    #
    # File logger
    #

    file_handler = logging.FileHandler(log_file)

    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    #
    # Console logger
    #

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(console_handler)

    return logger