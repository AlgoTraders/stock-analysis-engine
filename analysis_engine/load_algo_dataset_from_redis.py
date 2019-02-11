"""
Helper for loading datasets from redis

**Supported environment variables**

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

import analysis_engine.consts as ae_consts
import analysis_engine.get_data_from_redis_key as redis_utils
import analysis_engine.prepare_dict_for_algo as prepare_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def load_algo_dataset_from_redis(
        redis_key,
        redis_address,
        redis_db,
        redis_password,
        redis_expire=None,
        redis_serializer='json',
        serialize_datasets=ae_consts.DEFAULT_SERIALIZED_DATASETS,
        compress=False,
        encoding='utf-8'):
    """load_algo_dataset_from_redis

    Load an algorithm-ready dataset for algorithm backtesting
    from a redis key

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

    redis_host = redis_address.split(':')[0]
    redis_port = int(redis_address.split(':')[0])

    redis_res = redis_utils.get_data_from_redis_key(
        key=redis_key,
        host=redis_host,
        port=redis_port,
        db=redis_db,
        password=redis_password,
        expire=redis_expire,
        serializer=redis_serializer,
        encoding=encoding)

    if redis_res['status'] != ae_consts.SUCCESS:
        log.error(
            'failed getting data from '
            f'redis={redis_address}:{redis_db}/{redis_key}')
        return None

    data_from_file = redis_res['rec']['data']
    if not data_from_file:
        log.error(
            f'missing data from redis={redis_address}:{redis_db}/{redis_key}')
        return None

    return prepare_utils.prepare_dict_for_algo(
        data=data_from_file,
        compress=compress,
        convert_to_dict=True,
        encoding=encoding)
# end of load_algo_dataset_from_redis
