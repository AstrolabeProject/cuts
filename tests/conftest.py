# Tests configuration file.
#   Written by: Tom Hicks. 1/20/2021.
#   Last Modified: Update pytest fixture annotation name.
#
import pytest

from cuts.app import create_app


@pytest.fixture(scope='session')
def app():
    """
    Setup our flask test app, this only gets executed once.

    :return: Flask app
    """
    params = {
        'DEBUG': False,
        'TESTING': True,
        'SERVER_NAME': 'localhost.localdomain:8000'
    }

    _app = create_app(settings_override=params)

    # Establish an application context before running the tests.
    ctx = _app.app_context()                # create new app context
    ctx.push()                              # save current app context

    yield _app                              # return new app

    ctx.pop()                               # restore previous app context


@pytest.fixture(scope='function')
def client(app):
    """
    Setup an app client, this gets executed for each test function.

    :param app: Pytest fixture
    :return: Flask app client
    """
    yield app.test_client()
