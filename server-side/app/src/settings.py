import os
from dotenv import load_dotenv


load_dotenv()

HOST = os.getenv('HOST')
PORT = int(os.getenv('PORT'))
DB_URI = os.getenv('DB_URI')
EMAIL_SECRET = os.getenv('EMAIL_SECRET')


print('aaaaaaaaaaaaaa')
print(DB_URI)