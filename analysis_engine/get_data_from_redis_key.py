"""
Helper for getting data from redis

Debug redis calls with:

::

    export DEBUG_REDIS=1

"""
import json
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import ev
from analysis_engine.consts import ppj

log = build_colorized_logger(
    name=__name__)


def get_data_from_redis_key(
        label,
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

    :param label:
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

    try:
        log.info(
            '{} get key={}'.format(
                label,
                key))
        # https://redis-py.readthedocs.io/en/latest/index.html#redis.StrictRedis.get  # noqa
        raw_data = client.get(
            name=key)

        if raw_data:
            log.info(
                '{} decoding key={} encoding={}'.format(
                    label,
                    key,
                    encoding))
            decoded_data = raw_data.decode(encoding)

            log.info(
                '{} deserial key={} format={}'.format(
                    label,
                    key,
                    serializer))

            if serializer == 'json':
                data = json.loads(decoded_data)

            if data:
                if ev('DEBUG_REDIS', '0') == '1':
                    log.info(
                        '{} - found key={} data={}'.format(
                            label,
                            key,
                            ppj(data)))
                else:
                    log.info(
                        '{} - found key={}'.format(
                            label,
                            key))
        else:
            log.info(
                '{} no data key={}'.format(
                    label,
                    key))
    except Exception as e:
        data = None
        log.error(
            '{} failed - redis get from decoded={} data={} '
            'key={} ex={}'.format(
                label,
                decoded_data,
                data,
                key,
                e))
    # end of try/ex for getting redis data

    return data
# end of get_data_from_redis_key
