"""
Example Minute Algorithm for showing how
to run an algorithm on intraday minute timeseries datasets

**What does the base class provide?**

Algorithms automatically provide the following
member variables to any custom algorithm that derives
the ``analysis_engine.algo.BaseAlgo.process`` method.

By deriving the ``process()`` member method using an inherited
class, you can quickly build algorithms that
determine **buy** and **sell** conditions from
any of the automatically extracted
datasets from the redis pipeline:

- ``self.df_daily``
- ``self.df_minute``
- ``self.df_calls``
- ``self.df_puts``
- ``self.df_quote``
- ``self.df_pricing``
- ``self.df_stats``
- ``self.df_peers``
- ``self.df_iex_news``
- ``self.df_financials``
- ``self.df_earnings``
- ``self.df_dividends``
- ``self.df_company``
- ``self.df_yahoo_news``

**Recent Pricing Information**

- ``self.latest_close``
- ``self.latest_high``
- ``self.latest_open``
- ``self.latest_low``
- ``self.latest_volume``
- ``self.ask``
- ``self.bid``

**Latest Backtest Date and Intraday Minute**

- ``self.latest_min``
- ``self.backtest_date``

.. note:: **self.latest_min** - Latest minute row in ``self.df_minute``

.. note:: **self.backtest_date** - Latest dataset date which is considered the
    backtest date for historical testing with the data pipeline
    structure (it's the ``date`` key in the dataset node root level)

**Balance Information**

- ``self.balance``
- ``self.prev_bal``

.. note:: If a key is not in the dataset, the
    algorithms's member variable will be an empty
    pandas DataFrame created with: ``pd.DataFrame([])``
    except ``self.pricing`` which is just a dictionary.
    Please ensure the engine successfully fetched
    and cached the dataset in redis using a tool like
    ``redis-cli`` and a query of ``keys *`` or
    ``keys <TICKER>_*`` on large deployments.

**Supported environment variables**

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

from analysis_engine.algo import BaseAlgo
from analysis_engine.utils import utc_now_str
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(name=__name__)


class ExampleMinuteAlgo(BaseAlgo):
    """ExampleMinuteAlgo"""

    def __init__(
            self,
            **kwargs):
        """__init__

        Custom ticker algo for analyzing intraday
        minute datasets

        Please refer to the `analysis_engine.algo.Ba
        seAlgo source code for the latest supported parameters <ht
        tps://github.com/AlgoTraders/stock
        -analysis-engine/blob/master/
        analysis_engine/algo.py>`__

        :param kwargs: keyword arguments
        """
        log.info('base - {}'.format(kwargs.get('name', 'no-name-set')))
        super().__init__(**kwargs)
        log.info('ready - {}'.format(self.name))
    # end of __init__

    def process(
            self,
            algo_id,
            ticker,
            dataset):
        """process

        Derive custom algorithm buy and sell conditions
        before placing orders. Just implement your own
        ``process`` method.

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param dataset: a dictionary of identifiers (for debugging) and
            multiple pandas ``pd.DataFrame`` objects. Dictionary where keys
            represent a label from one of the data sources (``IEX``,
            ``Yahoo``, ``FinViz`` or other). Here is the supported
            dataset structure for the process method:

            .. note:: There are no required keys for ``data``, the list
                below is not hard-enforced by default. This is just
                a reference for what is available with the v1 engine.

            ::

                dataset = {
                    'id': <string TICKER_DATE - redis cache key>,
                    'date': <string DATE>,
                    'data': {
                        'daily': pd.DataFrame([]),
                        'minute': pd.DataFrame([]),
                        'quote': pd.DataFrame([]),
                        'stats': pd.DataFrame([]),
                        'peers': pd.DataFrame([]),
                        'news1': pd.DataFrame([]),
                        'financials': pd.DataFrame([]),
                        'earnings': pd.DataFrame([]),
                        'dividends': pd.DataFrame([]),
                        'calls': pd.DataFrame([]),
                        'puts': pd.DataFrame([]),
                        'pricing': dictionary,
                        'news': pd.DataFrame([])
                    }
                }

            example:

            ::

                dataset = {
                    'id': 'SPY_2018-11-02
                    'date': '2018-11-02',
                    'data': {
                        'daily': pd.DataFrame,
                        'minute': pd.DataFrame,
                        'calls': pd.DataFrame,
                        'puts': pd.DataFrame,
                        'news': pd.DataFrame
                    }
                }
        """
        num_minute_rows = len(self.df_minute.index)
        label = (
            'process - {} - ticker={}'.format(
                self.name,
                ticker))
        log.info(
            '{} - start - '
            'date={} minute={} close={} '
            'high={} low={} open={} volume={} '
            'intraday rows={}'.format(
                label,
                self.backtest_date,
                self.latest_min,
                self.latest_close,
                self.latest_high,
                self.latest_low,
                self.latest_open,
                self.latest_volume,
                num_minute_rows))

        # walk through today's intraday records:
        # Provided by IEX
        num_done = 1
        total_records = num_minute_rows
        for idx, row in self.df_minute.iterrows():
            percent_label = self.build_progress_label(
                progress=num_done,
                total=total_records)
            if 'date' in row:
                # want to debug rows on stdout?
                # print(row)
                log.info(
                    '{} - ANALYZE - '
                    'date={} at {} '
                    'close={} high={} low={} open={} volume={} '
                    '- {}'.format(
                        label,
                        self.backtest_date,
                        row['date'].strftime('%H:%M:%S'),
                        row['close'],
                        row['high'],
                        row['low'],
                        row['open'],
                        row['volume'],
                        percent_label))
                num_done += 1
        # end for all rows in the dataset

        log.info(
            '{} - done - '
            'date={} minute={} '
            'balance={} previous_balance={} '
            'shares={} buys={} sells={} '
            'close={} high={} low={} open={} volume={} '
            'intraday rows={}'.format(
                label,
                self.backtest_date,
                self.latest_min,
                self.balance,
                self.prev_bal,
                self.num_owned,
                self.num_buys,
                self.num_sells,
                self.latest_close,
                self.latest_high,
                self.latest_low,
                self.latest_open,
                self.latest_volume,
                num_minute_rows))

    # end of process

    def get_result(
            self):
        """get_result"""

        log.info('building results')
        finished_date = utc_now_str()
        self.result = {
            'name': self.name,
            'created': self.created_date,
            'updated': finished_date,
            'open_positions': self.positions,
            'buys': self.get_buys(),
            'sells': self.get_sells(),
            'num_processed': len(self.order_history),
            'history': self.order_history,
            'balance': self.balance,
            'commission': self.commission
        }

        return self.result
    # end of get_result

# end of ExampleMinuteAlgo


def get_algo(
        **kwargs):
    """get_algo

    Make sure to define the ``get_algo`` for your custom
    algorithms to work as a backup with the ``sa.py`` tool...
    Not anticipating issues, but if we do with importlib
    this is the backup plan.

    Please file an issue if you see something weird and would like
    some help:
    https://github.com/AlgoTraders/stock-analysis-engine/issues

    :param kwargs: dictionary of keyword arguments
    """
    log.info('getting algo')
    return ExampleMinuteAlgo(**kwargs)
# end of get_algo
