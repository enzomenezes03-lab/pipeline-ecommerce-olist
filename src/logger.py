import logging
from pathlib import Path

Path("logs").mkdir(exist_ok=True)

def get_logger(name):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/ingest_bronze.log"),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(name)