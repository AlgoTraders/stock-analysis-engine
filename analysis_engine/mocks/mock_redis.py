"""
Mock redis objects
"""

import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


class MockRedisFailToConnect:
    """MockRedisFailToConnect"""

    def __init__(
            self,
            host=None,
            port=None,
            password=None,
            db=None):
        """__init__

        build a mock redis client that will raise an exception
        to test failures during connection

        :param host: hostname
        :param port: port
        :param password: password
        :param db: database number
        """
        raise Exception(
            'test MockRedisFailToConnect')
    # end of __init__

# end of MockRedisFailToConnect


class MockRedis:
    """MockRedis"""

    def __init__(
            self,
            host=None,
            port=None,
            password=None,
            db=None):
        """__init__

        build mock redis client

        :param host: hostname
        :param port: port
        :param password: password
        :param db: database number
        """
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.cache_dict = {}  # cache dictionary replicating redis
        self.keys = []        # cache redis keys
    # end of __init__

    def set(
            self,
            name=None,
            value=None,
            ex=None,
            px=None,
            nx=False,
            xx=False):
        """set

        mock redis set

        :param name: cache key name
        :param value: value to cache
        :param ex: expire time
        :param px: redis values
        :param nx: redis values
        :param xx: redis values
        """

        log.info(
            'mock - MockRedis.set('
            f'name={name}, '
            f'value={value}, '
            f'ex={ex}, '
            f'px={px}, '
            f'nx={nx}, '
            f'xx={xx})')
        self.cache_dict[name] = value
        self.keys.append(name)
    # end of set

    def get(
            self,
            name=None):
        """get

        mock redis get

        :param name: name of the key to check
        """
        if not name:
            err = (
                'mock - MockRedis.get('
                f'name={name}'
                ') - missing a name')
            log.error(err)
            raise Exception(err)
        value_in_dict = self.cache_dict.get(
            name,
            None)
        if not value_in_dict:
            value_in_env = ae_consts.ev(
                name,
                None)
            log.info(
                'mock - MockRedis.get('
                f'name={name}) env={value_in_env}')
            if value_in_env:
                return value_in_env.encode('utf-8')
            else:
                return None
        else:
            log.info(
                'mock - MockRedis.get('
                f'name={name}) cached_value={value_in_dict}')
            return value_in_dict
        # end of get data from dict vs in the env
    # end of get

# end of MockRedis
