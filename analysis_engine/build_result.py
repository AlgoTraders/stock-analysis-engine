"""
Build a result dictionary
"""

from analysis_engine.consts import NOT_RUN


def build_result(
        status=NOT_RUN,
        err=None,
        rec=None):
    """build_result

    Common result builder for helping standardize
    results per function and unittesting

    :param status: starting status vaalue from ``consts.py``
    :param err: optional error message
    :param rec: dictionary for the result
    """

    res = {
        'status': status,
        'err': err,
        'rec': rec
    }
    if not res:
        res['rec'] = {}

    return res
# end of build_result
