"""
Base Test Case class

This class provides common functionality for most
unittests:

- turns on debugging values
- adds and removes test environment variables
- interface for building test data
"""

import os
import unittest
from analysis_engine.api_requests \
    import build_cache_ready_pricing_dataset


class BaseTestCase(unittest.TestCase):
    """BaseTestCase"""

    debug = False
    celery_disabled_value = None
    debug_get_pricing = None
    debug_pub_pricing = None
    backup_s3_contents = None

    def setUp(
            self):
        """setUp"""
        self.backup_s3_contents = None
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
        if os.getenv(
                'TEST_S3_CONTENTS',
                'not-set') != 'not-set':
            self.backup_s3_contents = os.getenv(
                'TEST_S3_CONTENTS',
                None)
        os.environ.pop('TEST_S3_CONTENTS', None)
    # end of setUp

    def tearDown(
            self):
        """tearDown"""
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
        if self.backup_s3_contents:
            os.environ['TEST_S3_CONTENTS'] = self.backup_s3_contents
        else:
            os.environ.pop('TEST_S3_CONTENTS', None)
    # end of tearDown

    def get_pricing_test_data(
            self,
            test_name=None):
        """get_pricing_test_data"""
        test_data = build_cache_ready_pricing_dataset()
        if test_name:
            test_data['_TEST_NAME'] = test_name
        else:
            test_data['_TEST_NAME'] = 'not-set'
        return test_data
    # end of get_pricing_test_data

# end of BaseTestCase
