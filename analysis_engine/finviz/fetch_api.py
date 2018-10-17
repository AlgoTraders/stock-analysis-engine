"""
Supported Fetch calls

- Convert a FinViz Screener URL to a list of
  tickers.

"""

import requests
import bs4
import pandas as pd
import analysis_engine.build_result as req_utils
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.utils import get_last_close_str
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import ERR
from analysis_engine.consts import EX
from analysis_engine.finviz.consts import DEFAULT_FINVIZ_COLUMNS

log = build_colorized_logger(
    name=__name__)


def fetch_tickers_from_screener(
        url,
        columns=DEFAULT_FINVIZ_COLUMNS,
        as_json=False,
        soup_selector='td.screener-body-table-nw',
        label='fz-screen-converter'):
    """fetch_tickers_from_screener

    Convert all the tickers on a FinViz screener
    url to a ``pandas.DataFrame``. Returns a dictionary
    with a ticker list and DataFrame or a json-serialized
    DataFrame in a string (by default ``as_json=False`` will
    return a ``pandas.DataFrame`` if the
    ``returned-dictionary['status'] == SUCCESS``

    Works with urls created on:

    https://finviz.com/screener.ashx

    .. code-block:: python

        import analysis_engine.finviz.fetch_api as fv

        url = (
            'https://finviz.com/screener.ashx?'
            'v=111&'
            'f=cap_midunder,exch_nyse,fa_div_o5,idx_sp500'
            '&ft=4')
        res = fv.fetch_tickers_from_screener(url=url)
        print(res)

    :param url: FinViz screener url
    :param columns: ordered header column as a list of strings
                    and corresponds to the header row from the
                    FinViz screener table
    :param soup_selector: ``bs4.BeautifulSoup.selector`` string
                          for pulling selected html data
                          (by default ``td.screener-body-table-nw``)
    :param as_json: FinViz screener url
    :param label: log tracking label string
    """

    rec = {
        'data': None,
        'created': get_last_close_str(),
        'tickers': []
    }
    res = req_utils.build_result(
        status=NOT_RUN,
        err=None,
        rec=rec)

    try:

        log.info(
            '{} fetching url={}'.format(
                label,
                url))

        response = requests.get(url)

        if response.status_code != requests.codes.ok:
            err = (
                '{} finviz returned non-ok HTTP (200) '
                'status_code={} with text={} for url={}'.format(
                    label,
                    response.status_code,
                    response.text,
                    url))
            log.error(err)
            return req_utils.build_result(
                status=ERR,
                err=err,
                rec=rec)
        # end of checking for a good HTTP response status code

        soup = bs4.BeautifulSoup(
            response.text,
            features='html.parser')
        selected = soup.select(soup_selector)

        log.debug(
            '{} found={} url={}'.format(
                label,
                len(selected),
                url))

        ticker_list = []
        rows = []
        use_columns = columns
        num_columns = len(use_columns)
        new_row = {}
        col_idx = 0

        for idx, node in enumerate(selected):

            if col_idx >= num_columns:
                col_idx = 0
            column_name = use_columns[col_idx]
            test_text = str(node.text).lower().strip()
            col_idx += 1

            if column_name != 'ignore' and (
                    test_text != 'save as portfolio'
                    and test_text != 'export'):

                cur_text = str(node.text).strip()

                if column_name == 'ticker':
                    ticker_list.append(cur_text)
                    new_row[column_name] = cur_text.upper()
                else:
                    new_row[column_name] = cur_text
                # end of filtering bad sections around table

                if len(new_row) >= num_columns:
                    log.debug(
                        '{} adding ticker={}'.format(
                            label,
                            new_row['ticker']))
                    rows.append(new_row)
                    new_row = {}
                    col_idx = 0
                # end of if valid row
            # end if column is valid
        # end of walking through all matched html data on the screener

        log.debug(
            '{} done convert url={} to tickers={} '
            'rows={}'.format(
                label,
                url,
                ticker_list,
                len(rows)))

        df = pd.DataFrame(
            rows)

        log.info(
            '{} fetch done - df={} from url={} with tickers={} '
            'rows={}'.format(
                label,
                len(df.index),
                url,
                ticker_list,
                len(rows)))

        rec['tickers'] = ticker_list
        rec['data'] = df

        res = req_utils.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        rec['tickers'] = []
        rec['data'] = None
        err = (
            '{} failed converting screen url={} to list '
            'with ex={}'.format(
                label,
                url,
                e))
        log.error(err)
        res = req_utils.build_result(
            status=EX,
            err=err,
            rec=rec)
    # end of try/ex

    return res
# end of fetch_tickers_from_screener
