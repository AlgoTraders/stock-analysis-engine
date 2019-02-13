"""
Build an authenticated url for IEX Cloud
"""


def build_auth_url(
        url,
        token=None):
    """build_auth_url

    Helper for constructing authenticated IEX urls
    using an ``IEX Publishable Token`` with a valid
    `IEX Cloud Beta Account <https://
    iexcloud.io/cloud-login#/register/>`__

    This will return a string with the token as a query
    parameter on the HTTP url

    :param url: initial url to make authenticated
    :param token: optional - string ``IEX Publishable Token``
        (defaults to ``IEX_TOKEN`` environment variable or
        ``None``)
    """
    if token:
        return (
            f'{url}?token={token}')
    else:
        return url
# end of build_auth_url
