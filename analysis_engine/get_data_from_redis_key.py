"""
Helper for getting data from redis

Debug redis calls with:

::

    export DEBUG_REDIS=1

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json

"""

import json
import redis
import analysis_engine.build_result as build_result
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import ERR
from analysis_engine.consts import ev
from analysis_engine.consts import ppj

log = build_colorized_logger(
    name=__name__)


def get_data_from_redis_key(
        label=None,
        client=None,
        host=None,
        port=None,
        password=None,
        db=None,
        key=None,
        expire=None,
        serializer='json',
        encoding='utf-8'):
    """get_data_from_redis_key

    :param label: log tracking label
    :param client: initialized redis client
    :param host: not used yet - redis host
    :param port: not used yet - redis port
    :param password: not used yet - redis password
    :param db: not used yet - redis db
    :param key: not used yet - redis key
    :param expire: not used yet - redis expire
    :param serializer: not used yet - support for future
                       pickle objects in redis
    :param encoding: format of the encoded key in redis
    """

    decoded_data = None
    data = None

    rec = {
        'data': data
    }
    res = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)

    log_id = label if label else 'get-data'

    try:

        use_client = client
        if not use_client:
            log.debug(
                '{} get key={} new client={}:{}@{}'.format(
                    log_id,
                    key,
                    host,
                    port,
                    db))
            use_client = redis.Redis(
                host=host,
                port=port,
                password=password,
                db=db)
        else:
            log.debug(
                '{} get key={} client'.format(
                    log_id,
                    key))
        # create Redis client if not set

        # https://redis-py.readthedocs.io/en/latest/index.html#redis.StrictRedis.get  # noqa
        raw_data = use_client.get(
            name=key)

        if raw_data:
            log.debug(
                '{} decoding key={} encoding={}'.format(
                    log_id,
                    key,
                    encoding))
            decoded_data = raw_data.decode(encoding)

            log.debug(
                '{} deserial key={} serializer={}'.format(
                    log_id,
                    key,
                    serializer))

            if serializer == 'json':
                data = json.loads(decoded_data)
            elif serializer == 'df':
                data = decoded_data
            else:
                data = decoded_data

            if data:
                if ev('DEBUG_REDIS', '0') == '1':
                    log.info(
                        '{} - found key={} data={}'.format(
                            log_id,
                            key,
                            ppj(data)))
                else:
                    log.debug(
                        '{} - found key={}'.format(
                            log_id,
                            key))
            # log snippet - if data

            rec['data'] = data

            return build_result.build_result(
                status=SUCCESS,
                err=None,
                rec=rec)
        else:
            log.debug(
                '{} no data key={}'.format(
                    log_id,
                    key))
            return build_result.build_result(
                status=SUCCESS,
                err=None,
                rec=rec)
    except Exception as e:
        err = (
            '{} failed - redis get from decoded={} data={} '
            'key={} ex={}'.format(
                log_id,
                decoded_data,
                data,
                key,
                e))
        log.error(err)
        res = build_result.build_result(
            status=ERR,
            err=err,
            rec=rec)
    # end of try/ex for getting redis data

    return res
# end of get_data_from_redis_key
