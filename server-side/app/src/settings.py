import os
from dotenv import load_dotenv


load_dotenv()

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
DB_URI = os.getenv('DB_URI')