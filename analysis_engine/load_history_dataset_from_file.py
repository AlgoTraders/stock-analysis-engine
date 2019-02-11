"""
Helper for loading ``Trading History`` dataset from a file

**Supported environment variables**

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

import analysis_engine.prepare_history_dataset as prepare_history
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def load_history_dataset_from_file(
        path_to_file,
        compress=False,
        encoding='utf-8'):
    """load_history_dataset_from_file

    Load a ``Trading History`` dataset from a local file

    :param path_to_file: string - path to file holding an
        ``Trading History`` dataset
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
        log.error(f'missing data from file={path_to_file}')
        return None

    return prepare_history.prepare_history_dataset(
        data=data_from_file,
        compress=compress,
        convert_to_dict=True,
        encoding=encoding)
# end of load_history_dataset_from_file
