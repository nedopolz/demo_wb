import os
from pathlib import Path
from loguru import logger

from decouple import config

# Environment
ENV_STAGE = config('ENV_STAGE', cast=str, default='production')

# WB API urls
LOGIN_URL = 'https://seller.wildberries.ru/passport/api/v2/auth/login_by_phone'
LOGIN_SEND_SMS_URL = 'https://seller.wildberries.ru/passport/api/v2/auth/login'
LOGIN_NEED_URL = 'https://seller.wildberries.ru/passport/api/v2/auth/introspect'
PHOTO_URL = 'https://www.wildberries.ru/catalog/{}/detail.aspx?targetUrl=GP'
REPORTS_LIST = 'https://seller.wildberries.ru/ns/realization-reports/suppliers-portal-analytics/api/v1/reports?type=2'
REPORT_DOWNLOAD = 'https://seller.wildberries.ru/ns/realization-reports/suppliers-portal-analytics/api/v1/reports/{}/details/archived-excel'
REMAINS_DOWNLOAD = 'https://seller.wildberries.ru/ns/balances/analytics-back/api/v1/balances-excel'

# GS data
SERVICE_AKK_PATH = config('SERVICE_AKK_PATH', cast=str,
                          default='/home/aidar/Projects/wildberrys/wbbot2/reports_parser/akk.json')
TEMPLATE_LIST_NAME = config('TEMPLATE_LIST_NAME', cast=str, default='tamplate')
SHEET_URL = config('SHEET_URL', cast=str)
INFO_LIST_NAME = config('INFO_LIST_NAME', cast=str, default='info')

PROJECT_ID = config('PROJECT_ID', cast=str)
logger.debug(PROJECT_ID)
PRIVATE_KEY_ID = config('PRIVATE_KEY_ID', cast=str)
logger.debug(PRIVATE_KEY_ID)
PRIVATE_KEY = config('PRIVATE_KEY', cast=str)
logger.debug(PRIVATE_KEY)
CLIENT_EMAIL = config('CLIENT_EMAIL', cast=str)
logger.debug(CLIENT_EMAIL)
CLIENT_ID = config('CLIENT_ID', cast=str)
logger.debug(CLIENT_ID)
AUTH_URI = config('AUTH_URI', cast=str)
logger.debug(AUTH_URI)
TOKEN_URI = config('TOKEN_URI', cast=str)
logger.debug(TOKEN_URI)
AUTH_PROVIDER_X509_CERT_URL = config('AUTH_PROVIDER_X509_CERT_URL', cast=str)
logger.debug(AUTH_PROVIDER_X509_CERT_URL)
CLIENT_X509_CERT_URL = config('CLIENT_X509_CERT_URL', cast=str)
logger.debug(CLIENT_X509_CERT_URL)

# Postgressql
POSTGRES_HOST = config('POSTGRES_HOST', cast=str, default='172.18.0.2')
POSTGRES_PORT = config('POSTGRES_PORT', cast=int, default=5432)
POSTGRES_USER = config('POSTGRES_USER', cast=str, default='postgres')
POSTGRES_PASSWORD = config('POSTGRES_PASSWORD', cast=str, default='postgres')
POSTGRES_DB = config('POSTGRES_DB', cast=str, default='WB')
POSTGRES_URI = f'postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}'

# Cookies for session
COOKIE_PATH = Path('/opt/app/reports_parser/files/cookies')
DOCS_PATH = Path('/opt/app/reports_parser/files/docs')

# Clean env vars
os.environ.clear()
