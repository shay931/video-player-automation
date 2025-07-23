import pytest
import logging
import os
from datetime import datetime



PROJECT_ROOT = os.getenv("PROJECT_ROOT")
if not PROJECT_ROOT:
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

LOG_DIR = os.path.join(PROJECT_ROOT, "reports", "logs")
SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "reports", "screenshots")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)


# === Setup logging to file and console ===
log_file = os.path.join(LOG_DIR, f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


@pytest.fixture
def test_logger():
    return logger
