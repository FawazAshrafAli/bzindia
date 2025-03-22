import logging
from locations.views import get_locations, get_uae_locations
from celery import shared_task
import os

def configure_logger(log_filename):
    logger = logging.getLogger(log_filename)
    if not logger.hasHandlers():  # Prevent duplicate handlers
        handler = logging.FileHandler(log_filename, mode='w')
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


@shared_task(queue="worker1_queue")
def run1():
    logger = configure_logger("run1.log")
    logger.info("Starting run1 (UAE Stage 1)\n")

    # Stage 1
    top_left = (26.1, 51.5) # fetched till 0.03 precision
    bottom_right = (25.0, 56.4) # fetched till 0.03 precision

    top_left = (25.88, 51.5)

    api_key = os.getenv('OPENCAGE_API_KEY_1')
    opencage_cache = "opencage_requested_1"

    get_uae_locations(top_left, bottom_right, api_key, opencage_cache)

@shared_task(queue="worker2_queue")
def run2():
    logger = configure_logger("run2.log")
    logger.info("Starting run1 (UAE Stage 2)\n")

    # Stage 2
    top_left = (25.0, 51.5) # fetched till 0.03 precision
    bottom_right = (23.9, 56.4) # fetched till 0.03 precision

    top_left = (24.69, 51.5)

    api_key = os.getenv('OPENCAGE_API_KEY_2')
    opencage_cache = "opencage_requested_2"

    get_uae_locations(top_left, bottom_right, api_key, opencage_cache)

@shared_task(queue="worker3_queue")
def run3():
    logger = configure_logger("run3.log")
    logger.info("Starting run1 (UAE Stage 3)\n")

    # Stage 3
    top_left = (23.9, 51.5) # fetched till 0.03 precision
    bottom_right = (22.6, 56.4) # fetched till 0.03 precision

    top_left = (23.66, 51.5)

    api_key = os.getenv('OPENCAGE_API_KEY_2')
    opencage_cache = "opencage_requested_2"

    get_uae_locations(top_left, bottom_right, api_key, opencage_cache)