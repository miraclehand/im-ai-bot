import threading
import atexit
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from kafka_service import consume_and_answer, shutdown_consumer
from logger import setup_logging

logger = setup_logging()

def create_app():
    # Load environment variables
    load_dotenv(verbose=True)

    app = Flask(__name__)
    CORS(app)

    atexit.register(shutdown_consumer)

    logger.info('Flask app started. Initializing consumer thread.')
    threading.Thread(target=consume_and_answer, daemon=True).start()

    return app
