"""
Helper for converting a dictionary to an algorithm-ready
dataset
"""

import json
import zlib
import pandas as pd
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


def prepare_dict_for_algo(
        data,
        compress=False,
        encoding='utf-8'):
    """prepare_dict_for_algo

    :param data: string holding contents of an algorithm-ready
        file, s3 key or redis-key
    :param compress: optional - boolean flag for decompressing
        the contents of the ``data`` if necessary
        (default is ``False`` and algorithms
        use ``zlib`` for compression)
    :param encoding: optional - string for data encoding
    """
    log.debug('start')
    use_data = None
    parsed_data = None
    data_as_dict = None

    if compress:
        log.debug('decompressing')
        parsed_data = zlib.decompress(
            data).decode(
                encoding)
    else:
        parsed_data = data

    if not parsed_data:
        log.error('failed parsing')
        return None

    log.debug('loading as dict')
    use_data = None
    data_as_dict = json.loads(parsed_data)
    if len(data_as_dict) == 0:
        log.error(
            'empty algorithm-ready dictionary')
        return use_data

    empty_pd = pd.DataFrame([{}])

    log.info('converting')
    num_datasets = 0
    for ticker in data_as_dict:
        if ticker not in use_data:
            use_data[ticker] = []
        for node in data_as_dict[ticker]:
            new_node = {
                'id': node['id'],
                'date': node['date'],
                'data': {}
            }

            for ds_key in node['data']:
                new_node[ds_key] = empty_pd
                if node['data'][ds_key]:
                    new_node[ds_key] = pd.read_json(
                        node['data'][ds_key],
                        orient='records')
                    num_datasets += 1
            # end for all datasets in this node
            use_data[ticker].append(new_node)
        # end for all datasets on this date to load
    # end for all tickers in the dataset

    if num_datasets:
        log.info('found datasets={}'.format(
            num_datasets))
    else:
        log.error('did not find any datasets={}'.format(
            num_datasets))

    return use_data
# end of prepare_dict_for_algo
