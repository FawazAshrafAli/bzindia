import logging
from locations.views import get_ksa_locations
from celery import shared_task
import os

from directory.views import fetch_destination_locations, logger, fetch_police_locations, fetch_court_locations

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
    logger.info("Starting run1 (KSA Stage 1)\n")

    # Stage 1
    top_left = (32.2, 34.4)
    bottom_right = (26.9, 55.7)

    top_left = (30.18, 34.4)

    api_key = os.getenv('OPENCAGE_API_KEY_1')
    opencage_cache = "opencage_requested_1"

    get_ksa_locations(top_left, bottom_right, api_key, opencage_cache)

@shared_task(queue="worker2_queue")
def run2():
    logger = configure_logger("run2.log")
    logger.info("Starting run2 (KSA Stage 2)\n")

    # Stage 2
    top_left = (26.9, 34.4)
    bottom_right = (21.6, 55.7)

    top_left = (24.88, 34.4)

    api_key = os.getenv('OPENCAGE_API_KEY_2')
    opencage_cache = "opencage_requested_2"

    get_ksa_locations(top_left, bottom_right, api_key, opencage_cache)

@shared_task(queue="worker3_queue")
def run3():
    logger = configure_logger("run3.log")
    logger.info("Starting run3 (KSA Stage 3)\n")

    # Stage 3
    top_left = (21.6, 34.4)
    bottom_right = (16.3, 55.7)    

    top_left = (19.74, 34.4)

    api_key = os.getenv('OPENCAGE_API_KEY_3')
    opencage_cache = "opencage_requested_3"

    get_ksa_locations(top_left, bottom_right, api_key, opencage_cache)

@shared_task(bind=True, queue="worker1_queue", autoretry_for=(Exception,), retry_backoff=10, max_retries=5)
def fetch_locations_1(self):
    logger.info("Starting destination location fetching task via Celery")
    try:
        fetch_destination_locations()
        logger.info("Destination location fetching task completed successfully")
    except Exception as e:
        logger.error(f"Destination location fetching task failed: {e}")
        raise e
    

@shared_task(bind=True, queue="worker2_queue", autoretry_for=(Exception,), retry_backoff=10, max_retries=5)
def fetch_locations_2(self):
    logger.info("Starting police location fetching task via Celery")
    try:
        fetch_police_locations()
        logger.info("Police location fetching task completed successfully")
    except Exception as e:
        logger.error(f"Police location fetching task failed: {e}")
        raise e
    
@shared_task(bind=True, queue="worker3_queue", autoretry_for=(Exception,), retry_backoff=10, max_retries=5)
def fetch_locations_3(self):
    logger.info("Starting court location fetching task via Celery")
    try:
        fetch_court_locations()
        logger.info("Court location fetching task completed successfully")
    except Exception as e:
        logger.error(f"Court location fetching task failed: {e}")
        raise e