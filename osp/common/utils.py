

import math
import numpy as np
import csv
import pkgutil

from itertools import islice, chain
from playhouse.postgres_ext import ServerSide
from io import StringIO
from clint.textui import progress


def query_bar(query):

    """
    Wrap a query in a progress bar.

    Args:
        query (peewee.Query): A query instance.

    Returns:
        The query, wrapped in a progress bar.
    """

    size = query.count()

    return progress.bar(
        ServerSide(query.naive()),
        expected_size=size
    )


def partitions(min_val, max_val, n):

    """
    Get start/stop boundaries for N partitions.

    Args:
        min_val (int): The starting value.
        max_val (int): The last value.
        n (int): The number of partitions.
    """

    pts = np.array_split(np.arange(min_val, max_val+1), n)

    bounds = []
    for pt in pts:
        bounds.append((pt[0], pt[-1]))

    return bounds


def grouper(iterable, size):

    """
    Yield "groups" from an iterable.

    Args:
        iterable (iter): The iterable.
        size (int): The number of elements in each group.

    Yields:
        The next group.
    """

    source = iter(iterable)

    while True:
        group = islice(source, size)
        yield chain([next(group)], group)


def read_csv(package, path):

    """
    Read a CSV from package data.

    Args:
        package (str): The package path.
        path (str): The path of the data file.

    Returns: csv.DictReader
    """

    data = pkgutil.get_data(package, path).decode('utf8')
    return csv.DictReader(StringIO(data))
