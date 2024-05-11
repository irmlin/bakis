from passlib.context import CryptContext
import sys


def generate_hash(password: str):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hash = pwd_context.hash(password)
    print(hash)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('ERROR. Usage: python generate_hashed_password.py <password>')
        exit()

    password = sys.argv[1]
    generate_hash(password)
