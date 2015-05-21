

from osp.citations.hlom.ranking import Ranking


r = Ranking()


def print_rank(query):
    for t in query:
        print(
            t['rank'],
            round(t['score'], 2),
            t['record'].count,
            t['record'].pymarc.title(),
            t['record'].pymarc.author()
        )


def all_ranks(page_num=1, page_len=100):

    """
    Get unfiltered rankings.
    """

    r.reset()
    print_rank(r.rank(page_num, page_len))


def institution_ranks(iid, page_num=1, page_len=100):

    """
    Get text rankings for an institution.

    Args:
        iid (int): The institution id.
    """

    r.reset()
    r.filter_institution(iid)
    print_rank(r.rank(page_num, page_len))


def state_ranks(state, page_num=1, page_len=100):

    """
    Get text rankings for a state.

    Args:
        state (str): The state abbreviation.
    """

    r.reset()
    r.filter_state(state)
    print_rank(r.rank(page_num, page_len))
