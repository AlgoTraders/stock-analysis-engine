"""
Helper for loading datasets from a file

**Supported environment variables**

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

import analysis_engine.prepare_dict_for_algo as prepare_utils
from analysis_engine.consts import DEFAULT_SERIALIZED_DATASETS
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


def load_algo_dataset_from_file(
        path_to_file,
        serialize_datasets=DEFAULT_SERIALIZED_DATASETS,
        compress=False,
        encoding='utf-8'):
    """load_algo_dataset_from_file

    Load an algorithm-ready dataset for algorithm backtesting
    from a local file

    :param path_to_file: string - path to file holding an
        algorithm-ready dataset
    :param serialize_datasets: optional - list of dataset names to
        deserialize in the dataset
    :param compress: optional - boolean flag for decompressing
        the contents of the ``path_to_file`` if necessary
        (default is ``False`` and algorithms
        use ``zlib`` for compression)
    :param encoding: optional - string for data encoding
    """
    log.debug('start')
    data_from_file = None
    with open(path_to_file, 'r') as cur_file:
        data_from_file = cur_file.read()

    if not data_from_file:
        log.error('missing data from file={}'.format(
            path_to_file))
        return None

    return prepare_utils.prepare_dict_for_algo(
        data=data_from_file,
        compress=compress,
        convert_to_dict=True,
        encoding=encoding)
# end of load_algo_dataset_from_file
