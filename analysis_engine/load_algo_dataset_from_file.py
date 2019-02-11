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

import analysis_engine.consts as ae_consts
import analysis_engine.prepare_dict_for_algo as prepare_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def load_algo_dataset_from_file(
        path_to_file,
        serialize_datasets=ae_consts.DEFAULT_SERIALIZED_DATASETS,
        compress=True,
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
        (default is ``True`` and algorithms
        use ``zlib`` for compression)
    :param encoding: optional - string for data encoding
    """
    log.info(
        f'start: {path_to_file}')
    data_from_file = None
    file_args = 'rb'
    if not compress:
        file_args = 'r'
    with open(path_to_file, file_args) as cur_file:
        data_from_file = cur_file.read()

    if not data_from_file:
        log.error(f'missing data from file={path_to_file}')
        return None

    return prepare_utils.prepare_dict_for_algo(
        data=data_from_file,
        compress=compress,
        convert_to_dict=True,
        encoding=encoding)
# end of load_algo_dataset_from_file
