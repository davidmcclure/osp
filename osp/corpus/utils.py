

import os
import subprocess
import requests

from osp.common.config import config
from bs4 import BeautifulSoup


def requires_attr(attr):

    """
    If the instance doesn't have an attribute, return None.

    Args:
        attr (str): The required attribute.

    Returns:
        function: The decorated function.
    """

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            if getattr(self, attr, None):
                return func(self, *args, **kwargs)
            else: return None
        return wrapper
    return decorator


def int_to_dir(i):

    """
    Convert an integer offset to a segment name.

    Args:
        i (int): The integer offset.

    Returns:
        str: The segment directory name.
    """

    return hex(i)[2:].zfill(3)


def html_to_text(path, exclude=['script', 'style']):

    """
    Convert HTML to text.

    Args:
        path (str): The file path.
        exclude (list): A list of tags to ignore.

    Returns:
        str: The extracted text.
    """

    with open(path, 'rb') as fh:

        soup = BeautifulSoup(fh)
        for script in soup(exclude):script.extract()
        return soup.get_text()


def pdf_to_text(path):

    """
    Convert a PDF to text.

    Args:
        path (str): The file path.

    Returns:
        str: The extracted text.
    """

    text = subprocess.check_output(['pdf2txt.py', path])
    return text.decode('utf8')


def office_to_text(path):

    """
    Convert to plaintext with LibreOffice.

    Args:
        path (str): The file path.

    Returns:
        str: The extracted text.
    """

    with open(path, 'rb') as fh:

        r = requests.put(
            config['tika']['server'],
            headers={'Accept': 'text/plain'},
            data=fh.read()
        )

        return r.text


def tika_is_online():

    """
    Is the Tika server available?

    Returns:
        bool: True if Tika is reachable.
    """

    try:
        r = requests.get(config['tika']['server'])
        return r.status_code == 200

    except requests.exceptions.ConnectionError:
        return False
