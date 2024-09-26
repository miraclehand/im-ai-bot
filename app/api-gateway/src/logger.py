import logging

def setup_logging():
    logging.basicConfig(level=logging.INFO, force=True)
    logger = logging.getLogger(__name__)
    return logger
