import os
from dotenv import load_dotenv


load_dotenv()

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
DB_URI = os.getenv('DB_URI')
EMAIL_SECRET = os.getenv('EMAIL_SECRET')
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES'))
