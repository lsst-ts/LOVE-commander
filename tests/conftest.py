import pytest

from commander import create_app


@pytest.fixture(scope='module')
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    return app.test_client()
