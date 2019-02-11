"""
Helper for loading a ``Trading History`` dataset
"""

import json
import zlib
import pandas as pd
import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def prepare_history_dataset(
        data,
        compress=False,
        encoding='utf-8',
        convert_to_dict=False,
        include_keys=None,
        ignore_keys=None,
        convert_to_dates=None,
        verbose=False):
    """prepare_history_dataset

    Load a ``Trading History`` dataset into a dictionary
    with a ``pd.DataFrame`` for the trading history record
    list

    :param data: string holding contents of a ``Trading History``
        from a file, s3 key or redis-key
    :param compress: optional - boolean flag for decompressing
        the contents of the ``data`` if necessary
        (default is ``False`` and algorithms
        use ``zlib`` for compression)
    :param convert_to_dict: optional - bool for s3 use ``False``
        and for files use ``True``
    :param encoding: optional - string for data encoding
    :param include_keys: optional - list of string keys
        to include before from the dataset
        .. note:: tickers are automatically included in the ``pd.DataFrame``
    :param ignore_keys: optional - list of string keys
        to remove before building the ``pd.DataFrame``
    :param convert_to_dates: optional - list of string keys
        to convert to datetime before building the ``pd.DataFrame``
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
        try:
            data_as_dict = json.loads(parsed_data)
        except Exception as e:
            if (
                    'the JSON object must be str, bytes or '
                    'bytearray, not') in str(e):
                log.critical(
                    f'failed decoding json for string - double '
                    f'compression for history dataset found ex={e}')
            data_as_dict = parsed_data
    else:
        data_as_dict = parsed_data
    if len(data_as_dict) == 0:
        log.error(
            'empty trading history dictionary')
        return use_data

    convert_these_date_keys = [
        'date',
        'minute',
        'exp_date'
    ]

    use_include_keys = [
        'tickers',
        'version',
        'last_trade_data',
        'algo_config_dict',
        'algo_name',
        'created'
    ]
    if include_keys:
        use_include_keys = include_keys

    use_ignore_keys = []
    if ignore_keys:
        use_ignore_keys = ignore_keys

    for k in data_as_dict:
        if k in use_include_keys:
            use_data[k] = data_as_dict[k]

    all_records = []
    num_records = 0
    for ticker in data_as_dict['tickers']:
        if ticker not in use_data:
            use_data[ticker] = []
        for node in data_as_dict[ticker]:

            for ignore in use_ignore_keys:
                node.pop(ignore, None)

            all_records.append(node)
        # end for all datasets on this date to load

        num_records = len(all_records)

        if num_records:
            if verbose:
                log.info(f'found records={num_records}')
            history_df = pd.DataFrame(all_records)
            for dc in convert_these_date_keys:
                if dc in history_df:
                    history_df[dc] = pd.to_datetime(
                        history_df[dc],
                        format=ae_consts.COMMON_TICK_DATE_FORMAT)
            # end of converting all date columns
            use_data[ticker] = history_df
        else:
            log.error(
                f'did not find any records={num_records} in history dataset')
    # end for all tickers in the dataset

    return use_data
# end of prepare_history_dataset
