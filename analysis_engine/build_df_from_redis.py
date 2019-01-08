"""
Helper for getting json-serialized pandas DataFrames
from redis

Debug redis calls with:

::

    export DEBUG_REDIS=1

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json

"""

import redis
import pandas as pd
import analysis_engine.consts as ae_consts
import analysis_engine.build_result as build_result
import analysis_engine.get_data_from_redis_key as redis_get
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def build_df_from_redis(
        label=None,
        client=None,
        address=None,
        host=None,
        port=None,
        password=None,
        db=None,
        key=None,
        expire=None,
        is_compressed=True,
        serializer='json',
        encoding='utf-8',
        orient='records'):
    """build_df_from_redis

    :param label: log tracking label
    :param client: initialized redis client
    :param address: redis address: <host:port>
    :param host: redis host
    :param port: redis port
    :param password: redis password
    :param db: redis db
    :param key: redis key
    :param expire: not used yet - redis expire
    :param is_compressed: optional boolean - the
        object is a compressed string and the
        default is ``True``
    :param serializer: support for future
        pickle objects in redis
    :param encoding: format of the encoded key in redis
    :param orient: use the same orient value as
        the ``to_json(orient='records')`` used
        to deserialize the DataFrame correctly.
    """

    data = None
    valid_df = False
    df = None

    rec = {
        'valid_df': valid_df,
        'data': data
    }
    res = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=rec)

    log_id = label if label else 'build-df'

    try:
        log.debug(
            '{} calling get redis key={}'.format(
                log_id,
                key))

        use_host = host
        use_port = port
        if not use_host and not use_port:
            if address:
                use_host = address.split(':')[0]
                use_port = int(address.split(':')[1])

        use_client = client
        if not use_client:
            log.debug(
                '{} connecting to redis={}:{}@{}'.format(
                    log_id,
                    use_host,
                    use_port,
                    db))
            use_client = redis.Redis(
                host=use_host,
                port=use_port,
                password=password,
                db=db)

        redis_res = redis_get.get_data_from_redis_key(
            label=log_id,
            client=use_client,
            host=use_host,
            port=use_port,
            password=password,
            db=db,
            key=key,
            expire=expire,
            decompress_df=is_compressed,
            serializer='json',
            encoding=encoding)

        valid_df = False
        if redis_res['status'] == ae_consts.SUCCESS:
            data = redis_res['rec'].get(
                'data',
                None)
            if data:
                if ae_consts.ev('DEBUG_REDIS', '0') == '1':
                    log.info(
                        '{} - found key={} data={}'.format(
                            log_id,
                            key,
                            ae_consts.ppj(data)))
                else:
                    log.debug(
                        '{} - loading df from key={}'.format(
                            log_id,
                            key))
                    df = pd.read_json(
                        data,
                        orient='records')
                    valid_df = True
            else:
                log.debug(
                    '{} key={} no data'.format(
                        log_id,
                        key))
            # if data

            rec['data'] = df
            rec['valid_df'] = valid_df

            res = build_result.build_result(
                status=ae_consts.SUCCESS,
                err=None,
                rec=rec)
            return res
        else:
            log.debug(
                '{} no data key={}'.format(
                    log_id,
                    key))
            res = build_result.build_result(
                status=ae_consts.SUCCESS,
                err=None,
                rec=rec)
            return res
    except Exception as e:
        err = (
            '{} failed - build_df_from_redis data={} '
            'key={} ex={}'.format(
                log_id,
                (data == '0'),
                key,
                e))
        log.error(err)
        res = build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=rec)
    # end of try/ex for getting redis data

    return res
# end of build_df_from_redis
