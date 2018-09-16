"""
Mock redis objects
"""

from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


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

        :param name: cache key name
        :param value: value to cache
        :param ex: expire time
        :param px: redis values
        :param nx: redis values
        :param xx: redis values
        """

        log.info(
            'mock - MockRedis.set('
            'name={}, '
            'value={}, '
            'ex={}, '
            'px={}, '
            'nx={}, '
            'xx={})'.format(
                name,
                value,
                ex,
                px,
                nx,
                xx))
        self.cache_dict[name] = value
        self.keys.append(name)
    # end of set

# end of MockRedis
