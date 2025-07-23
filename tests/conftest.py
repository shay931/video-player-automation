import pytest
import logging
import os
from datetime import datetime

# === Define Project Root and Reports Directories ===
PROJECT_ROOT = os.getenv("PROJECT_ROOT")
if not PROJECT_ROOT:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

LOG_DIR = os.path.join(PROJECT_ROOT, "reports", "logs")
SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "reports", "screenshots")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# === Setup logging ===
logger = logging.getLogger("test_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    log_file = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    logger.propagate = False

logger.info("Logger initialized.")

@pytest.fixture
def test_logger():
    return logger
