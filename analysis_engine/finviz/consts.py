"""
FinViz constants and static values
"""

FETCH_SCREENER_TICKERS = 1200

DATAFEED_SCREENER_TICKERS = 1300

DEFAULT_FINVIZ_COLUMNS = [
    'ticker_id',
    'ticker',
    'company',
    'sector',
    'industry',
    'country',
    'market_cap',
    'pe',
    'price',
    'change',
    'volume'
]


def get_ft_str_finviz(
        ft_type):
    """get_ft_str_finviz

    :param ft_type: enum fetch type value to return
                    as a string
    """
    if ft_type == FETCH_SCREENER_TICKERS:
        return 'fv_screener'
    else:
        return 'unsupported ft_type={}'.format(
            ft_type)
    # end of if/else
# end of get_ft_str_finviz


def get_datafeed_str_finviz(
        df_type):
    """get_ft_str_finviz

    :param df_type: enum fetch type value to return
                    as a string
    """
    if df_type == DATAFEED_SCREENER_TICKERS:
        return 'fv_screener'
    else:
        return 'unsupported df_type={}'.format(
            df_type)
# end of get_datafeed_str_finviz
