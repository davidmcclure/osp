

from .conftest import get_config, get_path


def test_read_defaults():

    """
    When initialized, Config should read the default paths and expose the
    underlying configuration object.
    """

    config = get_config('read/default')

    assert config['key1'] == 'val1'
    assert config['key2'] == 'val2'
    assert config['key3'] == 'val3'


def test_revert_changes():

    """
    If read() is called on an existing instance, the configuration files
    should be reloaded, reverting any changes to the values.
    """

    config = get_config('read/revert')
    config.config.update({'key': 'updated'})
    config.read()

    assert config['key'] == 'original'
