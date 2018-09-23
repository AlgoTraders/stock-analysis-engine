"""
Helper for getting data from redis

Debug redis calls with:

::

    export DEBUG_REDIS=1

"""
import json
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

    log_id = label if label else 'set-redis'

    try:
        log.info(
            '{} get key={}'.format(
                log_id,
                key))

        # https://redis-py.readthedocs.io/en/latest/index.html#redis.StrictRedis.get  # noqa
        raw_data = client.get(
            name=key)

        if raw_data:
            log.info(
                '{} decoding key={} encoding={}'.format(
                    log_id,
                    key,
                    encoding))
            decoded_data = raw_data.decode(encoding)

            log.info(
                '{} deserial key={} serializer={}'.format(
                    log_id,
                    key,
                    serializer))

            if serializer == 'json':
                data = json.loads(decoded_data)

            if data:
                if ev('DEBUG_REDIS', '0') == '1':
                    log.info(
                        '{} - found key={} data={}'.format(
                            log_id,
                            key,
                            ppj(data)))
                else:
                    log.info(
                        '{} - found key={}'.format(
                            log_id,
                            key))
            # log snippet - if data

            rec['data'] = data

            res = build_result.build_result(
                status=SUCCESS,
                err=None,
                rec=rec)
            return res
        else:
            log.info(
                '{} no data key={}'.format(
                    log_id,
                    key))
            res = build_result.build_result(
                status=SUCCESS,
                err=None,
                rec=rec)
            return res
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
