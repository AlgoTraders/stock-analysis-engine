"""
Helper for compressing a ``dict`` or ``pandas.DataFrame``
"""

import json
import zlib
import analysis_engine.consts as ae_consts


def compress_data(
        data,
        encoding='utf-8',
        date_format=None):
    """compress_data

    Helper for compressing ``data`` which can be
    either a ``dict`` or a ``pandas.DataFrame``
    objects with zlib.

    :param data: ``dict`` or ``pandas.DataFrame`` object
        to compress
    :param encoding: optional encoding - default is ``utf-8``
    :param date_format: optional date format - default is ``None``
    """

    converted_json = None
    if ae_consts.is_df(df=data):
        if date_format:
            converted_json = data.to_json(
                orient='records',
                date_format=date_format)
        else:
            converted_json = data.to_json(
                orient='records')
    else:
        converted_json = data

    converted_str = json.dumps(
        converted_json).encode(
            encoding)
    compressed_str = zlib.compress(converted_str, 9)

    return compressed_str
# end of compress_data
