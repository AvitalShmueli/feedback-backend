from flask import Flask
from flasgger import Swagger
from mongodb_connection_manager import MongoConnectionHolder
from routes import initial_routes
import os
import sys
import logging

app = Flask(__name__)
Swagger(app)

# Configure the logging system
logging.basicConfig(
    level=logging.DEBUG, # or DEBUG,INFO, WARNING, ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler(sys.stdout),  # Use stdout instead of default stderr
    ],
)

# Create a logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Initialize Database Connection
MongoConnectionHolder.initialize_db()

# Import the routes
initial_routes(app)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8088))
    logger.info(f"Starting the server on port {port}...")
    app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)
