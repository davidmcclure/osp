

import os
import subprocess
import requests

from osp.common.config import config
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader


def requires_attr(attr):

    """
    If the instance doesn't have a defined value for a key, return None.

    :param attr: The syllabus path.
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
    Convert an integer offset to a segment directory name.

    :param i: The integer.
    """

    return hex(i)[2:].zfill(3)


def html_to_text(html, exclude=['script', 'style']):

    """
    Convert HTML to text.

    :param html: The raw HTML.
    :param exclude: An array of tags to exclude.
    """

    soup = BeautifulSoup(html)

    # Stript excluded tags.
    for script in soup(exclude):
        script.extract()

    return soup.get_text()


def pdf_to_text(pdf):

    """
    Convert HTML to text.

    :param pdf: A PDF file handle.
    """

    reader = PdfFileReader(pdf)

    pages = []
    for page in reader.pages:
        pages.append(page.extractText())

    return ' '.join(pages)


def office_to_text(data):

    """
    Convert to plaintext with LibreOffice.

    :param data: The raw file data.
    """

    headers = {
        'Accept': 'text/plain'
    }

    r = requests.put(
        config['tika']['server'],
        data=data,
        headers=headers
    )

    return r.text
