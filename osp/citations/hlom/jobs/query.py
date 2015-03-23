

from osp.common.config import config
from osp.citations.hlom.models.record import HLOM_Record
from osp.citations.hlom.models.citation import HLOM_Citation
from osp.citations.hlom.utils import sanitize_query


def query(id):

    """
    Query a MARC record against the OSP corpus.

    :param id: The hlom_record row id.
    """

    row = HLOM_Record.get(HLOM_Record.id==id)

    # Scrub Lucene-reserved chars.
    title  = sanitize_query(row.pymarc.title())
    author = sanitize_query(row.pymarc.author())

    # Execute the query.
    results = config.es.search('osp', 'syllabus', timeout=30, body={
        'fields': ['doc_id'],
        'size': 100000,
        'query': {
            'bool': {
                'must': [
                    {
                        'match_phrase': {
                            'body': {
                                'query': title
                            }
                        }
                    },
                    {
                        'match_phrase': {
                            'body': {
                                'query': author,
                                'slop': 2
                            }
                        }
                    }
                ]
            }
        }
    })

    if results['hits']['total'] > 0:

        citations = []
        for hit in results['hits']['hits']:
            citations.append({
                'document': hit['fields']['doc_id'][0],
                'record': row.id
            })

        # Write the citation links.
        HLOM_Citation.insert_many(citations).execute()
