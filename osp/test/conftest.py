

import pytest

# Globals
from osp.workers.server import app
from osp.common import config as _config

# Models
from osp.corpus.models import Document
from osp.corpus.models import Document_Format
from osp.corpus.models import Document_Text
from osp.corpus.models import Document_Index
from osp.citations.models import Text
from osp.citations.models import Text_Index
from osp.citations.models import Citation
from osp.citations.models import Citation_Index
from osp.institutions.models import Institution
from osp.institutions.models import Institution_Document
from osp.institutions.models import Institution_Index
from osp.fields.models import Field
from osp.fields.models import Field_Index
from osp.fields.models import Subfield
from osp.fields.models import Subfield_Index
from osp.fields.models import Subfield_Document

# Helpers
from playhouse.test_utils import test_database
from osp.test.mock_osp import Mock_OSP
from osp.test.mock_hlom import Mock_HLOM
from osp.test.mock_jstor import Mock_JSTOR
from osp.test.helpers import *


@pytest.fixture(scope='session', autouse=True)
def test_env():

    """
    Merge the testing parameters into the configuration.
    """

    # Inject the testing values.
    _config.paths.append('/etc/osp/osp.test.yml')
    _config.read()


@pytest.yield_fixture()
def db():

    """
    Assign models to the testing database.

    Yields:
        A context with the wrapped model.
    """

    tables = [
        Document,
        Document_Format,
        Document_Text,
        Text,
        Citation,
        Institution,
        Institution_Document,
        Field,
        Subfield,
        Subfield_Document,
    ]

    with test_database(_config.get_db(), tables):
        yield


@pytest.fixture
def es():

    """
    Reset Elasticsearch.
    """

    for index in [
        Document_Index,
        Citation_Index,
        Text_Index,
        Institution_Index,
        Field_Index,
        Subfield_Index,
    ]:

        index.es_reset()


@pytest.fixture
def rq():

    """
    Clear the RQ queue.
    """

    _config.rq.connection.flushdb()


@pytest.fixture
def redis():

    """
    Clear Redis.
    """

    _config.redis.flushdb()


@pytest.yield_fixture
def config():

    """
    Reset the configuration object after each test.

    Yields:
        The modify-able config object.
    """

    yield _config
    _config.read()


@pytest.yield_fixture
def mock_osp(config):

    """
    Provide a Mock_OSP instance, and automatically point the configuration
    object at the path of the mock corpus.

    Yields:
        Mock_OSP
    """

    osp = Mock_OSP()

    # Point config -> mock.
    config.config.update_w_merge({
        'osp': {
            'corpus': osp.path
        }
    })

    yield osp
    osp.teardown()


@pytest.yield_fixture
def mock_hlom(config):

    """
    Provide a Mock_HLOM instance, and automatically point the configuration
    object at the path of the mock corpus.

    Yields:
        Mock_HLOM
    """

    hlom = Mock_HLOM()

    # Point config -> mock.
    config.config.update_w_merge({
        'hlom': {
            'corpus': hlom.path
        }
    })

    yield hlom
    hlom.teardown()


@pytest.yield_fixture
def mock_jstor(config):

    """
    Provide a Mock_JSTOR instance, and automatically point the configuration
    object at the path of the mock corpus.

    Yields:
        Mock_JSTOR
    """

    jstor = Mock_JSTOR()

    # Point config -> mock.
    config.config.update_w_merge({
        'jstor': {
            'corpus': jstor.path
        }
    })

    yield jstor
    jstor.teardown()


@pytest.yield_fixture
def api_client():

    """
    Get a test client for the worker API.

    Yields:
        The test client.
    """

    app.testing = True
    yield app.test_client()
