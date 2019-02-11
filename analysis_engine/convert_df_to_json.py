"""
Convert json to a pandas dataframe
"""

import pandas as pd
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def convert_json_to_df(
        data_json,
        sorted_by_key="date",
        in_ascending=True):
    """convert_json_to_df

    Convert json to a pandas dataframe

    :param data_json: json to convert
    :param sorted_by_key: key to sort on
    :param in_ascending: ascending order (True by default)
    """
    log.info(f'start sort={sorted_by_key} asc={in_ascending}')
    new_df = pd.read_json(
        data_json).sort_values(
            by=sorted_by_key,
            ascending=in_ascending)
    log.info(
        'done')
    return new_df
# end of convert_json_to_df
