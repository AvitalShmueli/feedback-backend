from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
import logging

# Load the environment variables
load_dotenv()

logger = logging.getLogger(__name__)

DB_CONNECTION_STRING = os.getenv("DB_CONNECTION_STRING")
DB_NAME = os.getenv("DB_NAME")
DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

MONGO_URI = f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@{DB_CONNECTION_STRING}/{DB_NAME}?retryWrites=true&w=majority&appName=FeedbackDB"


class MongoConnectionHolder:
    __db = None

    @staticmethod
    def initialize_db():
        """
        Initialize the database connection

        :return: MongoDB connection
        :rtype: Database
        """
        if MongoConnectionHolder.__db is None:
            try:
                # Create a new client and connect to the server
                client = MongoClient(MONGO_URI, server_api=ServerApi("1"))

                # Send a ping to confirm a successful connection
                client.admin.command("ping")
                logger.info("Pinged your deployment. You successfully connected to MongoDB!")

                MongoConnectionHolder.__db = client[DB_NAME]
            except Exception as e:
                print(e)
        return MongoConnectionHolder.__db

    @staticmethod
    def get_db():
        """
        Get the database connection

        :return: MongoDB connection
        :rtype: Database
        """
        if MongoConnectionHolder.__db is None:
            MongoConnectionHolder.initialize_db()

        return MongoConnectionHolder.__db
