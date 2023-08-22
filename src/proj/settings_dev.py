from dotenv import load_dotenv

from proj.settings import *

load_dotenv(BASE_DIR.parent / '.env')

SECRET_KEY = 'some_secret_key'

DEBUG = True
TEST_RUNNER = 'pytest_runner.DjangoTestSuiteRunner'
