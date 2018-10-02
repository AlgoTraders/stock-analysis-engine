"""
Wrapper for getting a Distributer:

https://github.com/timkpaine/hedgedata/blob/master/hedgedata/distributor.py

"""

import hedgedata.hedgedata.distributor
from analysis_engine.iex.consts import DEFAULT_DISTRIBUTER


def get_distributer(
        version=None):
    """get_distributer

    :param version: version of distributer to build
    """

    use_version = version

    if use_version == DEFAULT_DISTRIBUTER:
        return hedgedata.hedgedata.distributor.Distributer.default()
    else:
        return hedgedata.hedgedata.distributor.Distributer.default()
# end of get_distributer
