import os
import unittest


class BaseTestCase(unittest.TestCase):

    debug = False
    celery_disabled_value = None
    debug_get_pricing = None
    debug_pub_pricing = None

    def setUp(self):
        self.celery_disabled_value = None
        self.debug_get_pricing = None
        if os.getenv(
                'CELERY_DISABLED',
                'not-set') != 'not-set':
            self.celery_disabled_value = os.getenv(
                'CELERY_DISABLED',
                None)
        os.environ['CELERY_DISABLED'] = '1'
        if os.getenv(
                'DEBUG_GET_PRICING',
                'not-set') != 'not-set':
            self.debug_get_pricing = os.getenv(
                'DEBUG_GET_PRICING',
                None)
        os.environ['DEBUG_GET_PRICING'] = '1'
        if os.getenv(
                'DEBUG_PUB_PRICING',
                'not-set') != 'not-set':
            self.debug_pub_pricing = os.getenv(
                'DEBUG_PUB_PRICING',
                None)
        os.environ['DEBUG_PUB_PRICING'] = '1'
    # end of setUp

    def tearDown(self):
        if self.celery_disabled_value:
            os.environ['CELERY_DISABLED'] = self.celery_disabled_value
        else:
            os.environ.pop('CELERY_DISABLED', None)
        if self.debug_get_pricing:
            os.environ['DEBUG_GET_PRICING'] = self.debug_get_pricing
        else:
            os.environ.pop('DEBUG_GET_PRICING', None)
        if self.debug_pub_pricing:
            os.environ['DEBUG_PUB_PRICING'] = self.debug_pub_pricing
        else:
            os.environ.pop('DEBUG_PUB_PRICING', None)
    # end of tearDown

# end of BaseTestCase
