"""
Utility to output an n-level nested dictionary as a CSV
"""

import csv
import os
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def flatten_dict(
        data,
        parent_key='',
        sep='_'):
    """flatten_dict

    Flatten an n-level nested dictionary for csv output

    :param data: Dictionary to be parsed
    :param parent_key: The nested parent key
    :param sep: The separator to use between keys
    """
    items = []
    for key, value in data.items():
        new_key = parent_key + sep + key if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        elif isinstance(value, list):
            for idx, val in enumerate(value):
                temp_key = f'{new_key}_{idx}'
                items.extend(flatten_dict(
                    val,
                    temp_key,
                    sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)
# end of flatten_dict


def dict_to_csv(
        data,
        filename='test'):
    """dict_to_csv

    Convert a dictionary to an output CSV

    :param data: Dictionary to be converted
    :param filename: The name of the CSV to produce
    """
    noext_filename = os.path.splitext(filename)[0]
    log.info((f'START dict={data} conversion to csv={noext_filename}.csv'))
    flattened_data = flatten_dict(data)
    with open(f'{noext_filename}.csv', 'w') as f:
        w = csv.DictWriter(f, flattened_data.keys())
        w.writeheader()
        w.writerow(flattened_data)
# end of dict_to_csv
