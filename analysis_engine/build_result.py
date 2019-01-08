"""
Build a result dictionary
"""

import analysis_engine.consts as ae_consts


def build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=None):
    """build_result

    Common result builder for helping standardize
    results per function and unittesting

    :param status: starting status value from ``consts.py``
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
