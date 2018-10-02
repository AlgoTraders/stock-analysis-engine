"""
Test file for:
IEX Fetch Data
"""

from analysis_engine.mocks.base_test import BaseTestCase
from analysis_engine.consts import ev
from analysis_engine.iex.fetch_data \
    import fetch_data
from analysis_engine.api_requests \
    import build_iex_fetch_daily_request


class TestIEXFetchData(BaseTestCase):
    """TestIEXFetchData"""

    """
    Integration Tests

    Please ensure redis and minio are running and run this:

    ::

        export INT_TESTS=1

    """

    def test_integration_fetch_daily(self):
        """test_integration_fetch_daily"""
        if ev('INT_TESTS', '0') == '0':
            return

        # store data
        work = build_iex_fetch_daily_request(
            label='test_integration_fetch_daily')

        res = fetch_data(
            work_dict=work)
        self.assertIsNotNone(
            res)
        print(res)
    # end of test_integration_fetch_daily

# end of TestIEXFetchData
