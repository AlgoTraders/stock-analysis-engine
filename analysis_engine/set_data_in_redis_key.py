"""
Helper for setting data in redis

Debug redis calls with:

::

    export DEBUG_REDIS=1
"""

import json
import redis
import analysis_engine.consts as ae_consts
import analysis_engine.build_result as build_result
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def set_data_in_redis_key(
        label=None,
        data=None,
        client=None,
        host=None,
        port=None,
        password=None,
        db=None,
        key=None,
        expire=None,
        px=None,
        nx=False,
        xx=False,
        already_compressed=False,
        serializer='json',
        encoding='utf-8'):
    """set_data_in_redis_key

    :param label: log tracking label
    :param data: data to set in redis
    :param client: initialized redis client
    :param host: not used yet - redis host
    :param port: not used yet - redis port
    :param password: not used yet - redis password
    :param db: not used yet - redis db
    :param key: not used yet - redis key
    :param expire: redis expire
    :param px: redis px
    :param nx: redis nx
    :param xx: redis xx
    :param serializer: not used yet - support for future
        pickle objects in redis
    :param already_compressed: bool for handling
        compression to string already has happend
    :param encoding: format of the encoded key in redis
    """

    data_str = None
    encoded_data = None

    rec = {}
    res = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=rec)

    log_id = label if label else 'set-redis'

    try:
        log.debug(
            f'{log_id} serializer={serializer} encoding={encoding} '
            f'for key={key}')
        if already_compressed:
            encoded_data = data
        else:
            if serializer == 'json':
                data_str = json.dumps(data)
                encoded_data = data_str.encode(encoding)
            else:
                encoded_data = None
                err = (
                    f'{log_id} unsupported serializer={serializer} '
                    f'encoding={encoding} key={key}')
                log.error(err)
                res = build_result.build_result(
                    status=ae_consts.ERR,
                    err=err,
                    rec=rec)
                return res
        # if supported serializer

        if encoded_data:
            if ae_consts.ev('DEBUG_REDIS', '0') == '1':
                log.debug(f'{log_id} set - key={key} data={encoded_data}')

            use_client = client
            if not use_client:
                log.debug(
                    f'{log_id} set key={key} new client={host}:{port}@{db}')
                use_client = redis.Redis(
                    host=host,
                    port=port,
                    password=password,
                    db=db)
            else:
                log.debug(f'{log_id} set key={key} client')
            # create Redis client if not set

            use_client.set(
                name=key,
                value=encoded_data,
                ex=expire,
                px=px,
                nx=nx,
                xx=xx)
            res = build_result.build_result(
                status=ae_consts.SUCCESS,
                err=None,
                rec=rec)
            return res
        else:
            err = f'{log_id} no data for key={key}'
            log.error(err)
            res = build_result.build_result(
                status=ae_consts.ERR,
                err=err,
                rec=rec)
            return res
        # end of if have data to set
    except Exception as e:
        err = (
            f'{log_id} failed - redis set from data={str(data)[0:200]} '
            f'encoded_data={str(encoded_data)[0:200]} '
            f'key={key} ex={e}')
        log.error(err)
        res = build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=rec)
    # end of try/ex for setting redis data

    return res
# end of set_data_in_redis_key
