

import math
import numpy as np

from itertools import islice, chain
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
        query.naive().iterator(),
        expected_size=size
    )


def partitions(total, n):

    """
    Get start/stop boundaries for N partitions.

    Args:
        total (int): The total number of objects.
        n (int): The number of partitions.
    """

    pts = np.array_split(np.arange(total), n)

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
