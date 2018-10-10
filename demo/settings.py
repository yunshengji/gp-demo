import os

PROJECT_ENV = os.environ.get('PROJECT_ENV', 'dev')
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'geekpark-jwt')
JWT_EXPIRATION_DELTA = os.environ.get('JWT_EXPIRATION_DELTA', 6)
DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = int(os.environ.get('DB_PORT', '27017'))
DB_NAME = os.environ.get('DB_NAME', 'demo')
SKR_API_KEY = os.environ.get('SKR_API_KEY',
                             '87f5c0f0-fa55-4d22-a0b4-56fd6cc4d5b6')
MD5_SALT = os.environ.get('MD5_SALT', '')
