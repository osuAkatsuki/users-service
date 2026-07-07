import os

# app.settings reads every variable at import time (and fails fast if any is
# missing), so defaults must be in place before any test imports an app
# module. Values already present in the environment take precedence.
_TEST_ENV_DEFAULTS = {
    "APP_ENV": "test",
    "APP_HOST": "localhost",
    "APP_PORT": "80",
    "CODE_HOTRELOAD": "false",
    "DB_USER": "test",
    "DB_PASS": "test",
    "DB_HOST": "localhost",
    "DB_PORT": "3306",
    "DB_NAME": "test",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "REDIS_DB": "0",
    "REDIS_USER": "default",
    "REDIS_PASS": "",
    "AWS_S3_ENDPOINT_URL": "http://localhost:9000",
    "AWS_S3_REGION_NAME": "us-east-1",
    "AWS_S3_BUCKET_NAME": "test",
    "AWS_S3_ACCESS_KEY_ID": "test",
    "AWS_S3_SECRET_ACCESS_KEY": "test",
    "ASSETS_SERVICE_BASE_URL": "http://localhost:9001",
    "ASSETS_SERVICE_API_KEY": "test",
    "MAILGUN_BASE_URL": "https://api.mailgun.net",
    "MAILGUN_DOMAIN_NAME": "test.example.com",
    "MAILGUN_API_KEY": "test",
    "RECAPTCHA_SECRET_KEY": "test",
}

for _key, _value in _TEST_ENV_DEFAULTS.items():
    os.environ.setdefault(_key, _value)
