

import networkx as nx

from osp.citations.hlom.models.record import HLOM_Record
from osp.citations.hlom.models.citation import HLOM_Citation
from itertools import combinations
from playhouse.postgres_ext import ServerSide
from clint.textui.progress import bar
from peewee import fn


def query_bar(q):
    return bar(ServerSide(q), expected_size=q.count())


class Network:


    @classmethod
    def from_gml(cls, file_path):

        """
        Hydrate the network from a GML file.

        Args:
            file_path (str)

        Returns:
            Network
        """

        pass


    def __init__(self, graph=None):

        """
        Set the graph instance.

        Args:
            graph (networkx.Graph)
        """

        self.graph = graph if graph else nx.Graph()


    def add_nodes(self):

        """
        Register unique HLOM records as nodes.
        """

        # Select cited HLOM records.
        texts = (
            HLOM_Citation
            .select(HLOM_Citation.record)
            .distinct(HLOM_Citation.record)
        )

        # Add each record as a node.
        for row in query_bar(texts):

            title  = row.record.pymarc.title()
            author = row.record.pymarc.author()

            self.graph.add_node(
                row.record.id,
                title=title,
                author=author
            )


    def add_edges(self):

        """
        For each syllabus, register citation pairs as edges.

        Args:
            max_texts (int)
        """

        self.clear_edges()

        # Aggregate the CNs.
        cns = (
            fn.array_agg(HLOM_Record.id)
            .coerce(False)
            .alias('texts')
        )

        # Select syllabi and cited CNs.
        documents = (
            HLOM_Citation
            .select(HLOM_Citation.document, cns)
            .join(HLOM_Record)
            .distinct(HLOM_Citation.document)
            .group_by(HLOM_Citation.document)
        )

        print(documents.sql())

        for row in query_bar(documents):
            for id1, id2 in combinations(row.texts, 2):

                # If the edge exists, +1 the weight.
                if self.graph.has_edge(id1, id2):
                    self.graph[id1][id2]['weight'] += 1

                # Otherwise, initialize the edge.
                else: self.graph.add_edge(id1, id2, weight=1)


    def clear_edges(self):

        """
        Clear all edges.
        """

        cleared = nx.Graph()
        cleared.add_nodes_from(self.graph.nodes(data=True))
        self.graph = cleared


    def write_gml(self):

        """
        Serialize the graph as GML.
        """

        pass
