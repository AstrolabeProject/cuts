import os

from config.settings import APP_ROOT

TEST_DIR = None
TEST_DBCONFIG_FILEPATH = None

if (os.environ.get('RUNNING_IN_CONTAINER') is not None):
    TEST_DIR = "{}/tests".format(APP_ROOT)
    TEST_DBCONFIG_FILEPATH = "{}/resources/container-dbconfig.ini".format(TEST_DIR)
else:
    TEST_DIR = "{}/tests".format(os.getcwd())
    TEST_DBCONFIG_FILEPATH = "{}/resources/venv-dbconfig.ini".format(TEST_DIR)
