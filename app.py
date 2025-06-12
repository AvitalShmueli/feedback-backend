from flask import Flask
from flasgger import Swagger
from mongodb_connection_manager import MongoConnectionHolder
from routes import initial_routes
import os
import logging

app = Flask(__name__)
Swagger(app)

# Ensure the logs folder exists
#os.makedirs("logs", exist_ok=True)

# Configure the logging system
logging.basicConfig(
    level=logging.INFO,  # or DEBUG,INFO, WARNING, ERROR
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    #handlers=[
    #    logging.FileHandler("logs/app.log"),  # <- logs will be in logs/app.log
    #    logging.StreamHandler(),  # <- still prints to console too
    #],
)

# Reduce logs from external libraries
#logging.getLogger("pymongo").setLevel(logging.WARNING)
#logging.getLogger("werkzeug").setLevel(logging.WARNING)

# Create a logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


# Initialize Database Connection
MongoConnectionHolder.initialize_db()

# Import the routes
initial_routes(app)

#if __name__ == "__main__":
#    port = int(os.environ.get("PORT", 8088))
#    logger.info(f"Starting the server on port {port}...")
#    app.run(debug=True, host="0.0.0.0", port=port, use_reloader=False)
