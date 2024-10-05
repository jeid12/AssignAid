from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pymongo import MongoClient
import os

# Load environment variables from .env file
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")





# Create the client connection to MongoDB Atlas
client = AsyncIOMotorClient(MONGODB_URL)
database = client.get_database("mydb")
assignment_collection = database.get_collection("assignments")
solution_collection = database.get_collection("solutions")
user_collection = database.get_collection("users")
