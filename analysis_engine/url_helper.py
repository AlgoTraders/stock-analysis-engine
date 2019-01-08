"""
Helpful wrapper taken from:
https://www.peterbe.com/plog/best-practice-with-retries-with-requests
"""

import requests
import requests.adapters as adapters
import requests.packages.urllib3.util.retry as requests_retry


def url_helper(
        sess=None,
        retries=10,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504)):
    """url_helper

    :param sess: ``requests.Session``
        object like

        .. code-block:: python

            s = requests.Session()
            s.auth = ('user', 'pass')
            s.headers.update({'x-test': 'true'})

            response = url_helper(sesssion=s).get(
                'https://www.peterbe.com'
            )

    :param retries: number of retries
        default is ``3``
    :param backoff_factor: seconds per attempt
        default is ``0.3``
    :param status_forcelist: optional tuple list
        of retry error HTTP status codes
        default is ``500, 502, 504``
    """
    session = sess or requests.Session()
    retry = requests_retry.Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session
# end of url_helper
