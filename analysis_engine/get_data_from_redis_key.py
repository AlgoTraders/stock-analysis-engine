from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name='get-redis')


def get_data_from_redis_key(
        label,
        redis_client=None,
        redis_host=None,
        redis_port=None,
        redis_password=None,
        redis_db=None,
        redis_key=None,
        redis_expire=None):
    """get_data_from_redis_key

    :param label:
    :param redis_client: initialized redis client
    :param redis_host: not used yet - redis host
    :param redis_port: not used yet - redis port
    :param redis_password: not used yet - redis password
    :param redis_db: not used yet - redis db
    :param redis_key: not used yet - redis key
    :param redis_expire: not used yet - redis expire
    """

    data = None

    try:
        log.info(
            '{} get redis_key={}'.format(
                label,
                redis_key))
        # https://redis-py.readthedocs.io/en/latest/index.html#redis.StrictRedis.get  # noqa
        data = redis_client.get(
            name=redis_key)
        if data:
            log.debug(
                '{} - found redis_key={}'.format(
                    label,
                    redis_key))
    except Exception as e:
        data = None
        log.error(
            '{} failed - redis get from '
            'key={} ex={}'.format(
                label,
                redis_key,
                e))
    # end of try/ex for getting redis data

    return data
# end of get_data_from_redis_key
