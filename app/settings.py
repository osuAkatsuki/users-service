import os

from dotenv import load_dotenv

load_dotenv()


def read_bool(s: str) -> bool:
    return s.lower() == "true"


APP_ENV = os.environ["APP_ENV"]
APP_HOST = os.environ["APP_HOST"]
APP_PORT = int(os.environ["APP_PORT"])

CODE_HOTRELOAD = read_bool(os.environ["CODE_HOTRELOAD"])

DB_USER = os.environ["DB_USER"]
DB_PASS = os.environ["DB_PASS"]
DB_HOST = os.environ["DB_HOST"]
DB_PORT = int(os.environ["DB_PORT"])
DB_NAME = os.environ["DB_NAME"]

REDIS_HOST = os.environ["REDIS_HOST"]
REDIS_PORT = int(os.environ["REDIS_PORT"])
REDIS_DB = int(os.environ["REDIS_DB"])
REDIS_USER = os.environ["REDIS_USER"]
REDIS_PASS = os.environ["REDIS_PASS"]

AWS_S3_ENDPOINT_URL = os.environ["AWS_S3_ENDPOINT_URL"]
AWS_S3_REGION_NAME = os.environ["AWS_S3_REGION_NAME"]
AWS_S3_BUCKET_NAME = os.environ["AWS_S3_BUCKET_NAME"]
AWS_S3_ACCESS_KEY_ID = os.environ["AWS_S3_ACCESS_KEY_ID"]
AWS_S3_SECRET_ACCESS_KEY = os.environ["AWS_S3_SECRET_ACCESS_KEY"]

ASSETS_SERVICE_BASE_URL = os.environ["ASSETS_SERVICE_BASE_URL"]
ASSETS_SERVICE_API_KEY = os.environ["ASSETS_SERVICE_API_KEY"]

MAILGUN_BASE_URL = os.environ["MAILGUN_BASE_URL"]
MAILGUN_DOMAIN_NAME = os.environ["MAILGUN_DOMAIN_NAME"]
MAILGUN_API_KEY = os.environ["MAILGUN_API_KEY"]
