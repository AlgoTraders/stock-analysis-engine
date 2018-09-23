"""
Helper for setting data in redis

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

log = build_colorized_logger(
    name=__name__)


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
    :param encoding: format of the encoded key in redis
    """

    data_str = None
    encoded_data = None

    rec = {}
    res = build_result.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)

    log_id = label if label else 'set-redis'

    try:
        log.info(
            '{} serializer={} encoding={} for key={}'.format(
                log_id,
                serializer,
                encoding,
                key))
        if serializer == 'json':
            data_str = json.dumps(data)
            encoded_data = data_str.encode(encoding)
        else:
            encoded_data = None
            err = (
                '{} unsupported serializer={} '
                'encoding={} key={}'.format(
                    log_id,
                    serializer,
                    encoding,
                    key))
            log.error(err)
            res = build_result.build_result(
                status=ERR,
                err=err,
                rec=rec)
            return res
        # if supported serializer

        if encoded_data:
            if ev('DEBUG_REDIS', '0') == '1':
                log.info(
                    '{} set - key={} data={}'.format(
                        log_id,
                        key,
                        encoded_data))
            else:
                log.info(
                    '{} set - key={}'.format(
                        log_id,
                        key))
            client.set(
                name=key,
                value=encoded_data,
                ex=expire,
                px=px,
                nx=nx,
                xx=xx)
            res = build_result.build_result(
                status=SUCCESS,
                err=None,
                rec=rec)
            return res
        else:
            err = (
                '{} no data for key={}'.format(
                    log_id,
                    key))
            log.error(err)
            res = build_result.build_result(
                status=ERR,
                err=err,
                rec=rec)
            return res
        # end of if have data to set
    except Exception as e:
        err = (
            '{} failed - redis set from data={} encoded_data={} '
            'key={} ex={}'.format(
                log_id,
                data,
                encoded_data,
                key,
                e))
        log.error(err)
        res = build_result.build_result(
            status=ERR,
            err=err,
            rec=rec)
    # end of try/ex for setting redis data

    return res
# end of set_data_in_redis_key
