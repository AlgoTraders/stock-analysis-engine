"""
Helper for loading a ``Trading Performance Report`` dataset
"""

import json
import zlib
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def prepare_report_dataset(
        data,
        compress=False,
        encoding='utf-8',
        convert_to_dict=False,
        dataset_names=None,
        verbose=False):
    """prepare_report_dataset

    Load a ``Trading Performance Report`` dataset into a dictionary
    with a ``pd.DataFrame`` for the trading report record
    list

    :param data: string holding contents of an ``Trading
        Performance Report`` from a file, s3 key or redis-key
    :param compress: optional - boolean flag for decompressing
        the contents of the ``data`` if necessary
        (default is ``False`` and algorithms
        use ``zlib`` for compression)
    :param convert_to_dict: optional - bool for s3 use ``False``
        and for files use ``True``
    :param encoding: optional - string for data encoding
    :param dataset_names: optional - list of string keys
        for each dataset node in:
        ``dataset[ticker][0]['data'][dataset_names[0]]``
    :param verbose: optional - bool show the logs
        (default is ``False``)
    """
    if verbose:
        log.debug('start')
    use_data = None
    parsed_data = None
    data_as_dict = None

    if compress:
        if verbose:
            log.debug('decompressing')
        parsed_data = zlib.decompress(
            data).decode(
                encoding)
    else:
        parsed_data = data

    if not parsed_data:
        log.error('failed parsing')
        return None

    if verbose:
        log.debug('loading as dict')
    use_data = {}
    if convert_to_dict:
        data_as_dict = json.loads(parsed_data)
    else:
        data_as_dict = parsed_data
    if len(data_as_dict) == 0:
        log.error(
            'empty trading performance report dictionary')
        return use_data

    for ticker in data_as_dict['tickers']:
        if ticker not in use_data:
            use_data[ticker] = []
        for node in data_as_dict[ticker]:
            new_node = {
                'id': node['id'],
                'date': node['date'],
                'data': {}
            }
            """
            for ds_key in node['data']:
                if ds_key in use_serialized_datasets:
                    new_node['data'][ds_key] = empty_pd
                    if node['data'][ds_key]:
                        new_node['data'][ds_key] = pd.read_json(
                            node['data'][ds_key],
                            orient='records')
                        num_datasets += 1
                # if supported dataset key
            # end for all datasets in this node
            """
            use_data[ticker].append(new_node)
        # end for all datasets on this date to load
    # end for all tickers in the dataset

    """
    if num_datasets:
        if verbose:
            log.info(f'found datasets={num_datasets}')
    else:
        log.error(f'did not find any datasets={num_datasets}')
    """

    return use_data
# end of prepare_report_dataset
