"""
Algorithms automatically provide the following
member variables to any custom algorithm that derives
the ``analysis_engine.algo.BaseAlgo.process`` method.

By deriving the ``process`` method using an inherited
class, you can quickly build algorithms that
determine **buy** and **sell** conditions from
any of the automatically extracted
datasets from the redis pipeline:

- ``self.df_daily``
- ``self.df_minute``
- ``self.df_quote``
- ``self.df_stats``
- ``self.df_peers``
- ``self.df_iex_news``
- ``self.df_financials``
- ``self.df_earnings``
- ``self.df_dividends``
- ``self.df_company``
- ``self.df_yahoo_news``
- ``self.df_options``
- ``self.df_pricing``

.. note:: If a key is not in the dataset, the
    algorithms's member variable will be an empty
    pandas DataFrame created with: ``pd.DataFrame([])``
    except ``self.pricing`` which is just a dictionary.
    Please ensure the engine successfully fetched
    and cached the dataset in redis using a tool like
    ``redis-cli`` and a query of ``keys *`` or
    ``keys <TICKER>_*`` on large deployments.
"""

import json
import pandas as pd
import analysis_engine.build_trade_history_entry as history_utils
import analysis_engine.build_buy_order as buy_utils
import analysis_engine.build_sell_order as sell_utils
from analysis_engine.consts import TRADE_FILLED
from analysis_engine.consts import TRADE_SHARES
from analysis_engine.consts import get_status
from analysis_engine.consts import get_percent_done
from analysis_engine.utils import utc_now_str
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


class BaseAlgo:
    """BaseAlgo

    Run an algorithm against multiple tickers at once through the
    redis dataframe pipeline provided by
    `analysis_engine.extract.extract
    <https://github.com/AlgoTraders/stock-analysis-engine/bl
    ob/master/analysis_engine/extract.py>`__.

    **Data Pipeline Structure**

    This algorithm can handle an extracted dictionary with structure:

    .. code-block:: python

        import pandas as pd
        from analysis_engine.algo import BaseAlgo
        ticker = 'SPY'
        demo_algo = BaseAlgo(
            ticker=ticker,
            balance=1000.00,
            commission=6.00,
            name='test-{}'.format(ticker))
        date = '2018-11-05'
        dataset_id = '{}_{}'.format(
            ticker,
            date)
        # mock the data pipeline in redis:
        data = {
            ticker: [
                {
                    'id': dataset_id,
                    'date': date,
                    'data': {
                        'daily': pd.DataFrame([
                            {
                                'high': 280.01,
                                'low': 270.01,
                                'open': 275.01,
                                'close': 272.02,
                                'volume': 123,
                                'date': '2018-11-01 15:59:59'
                            },
                            {
                                'high': 281.01,
                                'low': 271.01,
                                'open': 276.01,
                                'close': 273.02,
                                'volume': 124,
                                'date': '2018-11-02 15:59:59'
                            },
                            {
                                'high': 282.01,
                                'low': 272.01,
                                'open': 277.01,
                                'close': 274.02,
                                'volume': 121,
                                'date': '2018-11-05 15:59:59'
                            }
                        ]),
                        'minute': pd.DataFrame([]),
                        'news': pd.DataFrame([]),
                        'options': pd.DataFrame([])
                        # etc
                    }
                }
            ]
        }

        # run the algorithm
        demo_algo.handle_data(data=data)

        # get the algorithm results
        results = demo_algo.get_result()

        print(results)
    """

    def __init__(
            self,
            ticker,
            balance,
            commission=6.0,
            tickers=None,
            name=None,
            auto_fill=True,
            config_dict=None,
            publish_to_slack=True,
            publish_to_s3=True,
            publish_to_redis=True,
            raise_on_err=False):
        """__init__

        :param ticker: single ticker string
        :param balance: starting capital balance
        :param commission: cost for commission
            for a single buy or sell trade
        :param tickers: optional - list of ticker strings
        :param name: optional - log tracking name
            or algo name
        :param config_dict: optional - configuration dictionary
            for passing complex attributes or properties for this
            algo
        :param auto_fill: optional - boolean for auto filling
            buy/sell orders for backtesting (default is
            ``True``)
        :param publish_to_slack: optional - boolean for
            publishing to slack (coming soon)
        :param publish_to_s3: optional - boolean for
            publishing to s3 (coming soon)
        :param publish_to_redis: optional - boolean for
            publishing to redis (coming soon)
        :param raise_on_err: optional - boolean for
            unittests and developing algorithms with the
            ``analysis_engine.run_algo.run_algo`` helper.
            .. note:: When set to ``True`` exceptions will
                are raised to the calling functions

        """
        self.buys = []
        self.sells = []
        self.num_shares = 0
        self.tickers = tickers
        if not self.tickers:
            if ticker:
                self.tickers = [
                    ticker
                ]
        self.balance = balance
        self.starting_balance = balance
        self.starting_close = 0.0
        self.commission = commission
        self.result = None
        self.name = name
        self.num_owned = None
        self.num_buys = None
        self.num_sells = None
        self.trade_price = 0.0
        self.latest_close = 0.0
        self.latest_high = 0.0
        self.latest_open = 0.0
        self.latest_low = 0.0
        self.latest_volume = 0.0
        self.ask = 0.0
        self.bid = 0.0
        self.prev_bal = None
        self.prev_num_owned = None
        self.ds_id = None
        self.trade_date = None
        self.trade_type = TRADE_SHARES
        self.buy_hold_units = 20
        self.sell_hold_units = 20
        self.spread_exp_date = None
        self.last_close = None
        self.order_history = []
        self.config_dict = config_dict
        self.positions = {}
        self.created_date = utc_now_str()
        self.created_buy = False
        self.should_buy = False
        self.buy_strength = None
        self.buy_risk = None
        self.created_sell = False
        self.should_sell = False
        self.sell_strength = None
        self.sell_risk = None
        self.stop_loss = None
        self.trailing_stop_loss = None

        self.last_ds_id = None
        self.last_ds_date = None
        self.last_ds_data = None

        self.ds_date = None
        self.ds_data = None
        self.df_daily = pd.DataFrame([])
        self.df_minute = pd.DataFrame([])
        self.df_stats = pd.DataFrame([])
        self.df_peers = pd.DataFrame([])
        self.df_financials = pd.DataFrame([])
        self.df_earnings = pd.DataFrame([])
        self.df_dividends = pd.DataFrame([])
        self.df_quote = pd.DataFrame([])
        self.df_company = pd.DataFrame([])
        self.df_iex_news = pd.DataFrame([])
        self.df_yahoo_news = pd.DataFrame([])
        self.df_options = pd.DataFrame([])
        self.empty_pd = pd.DataFrame([])
        self.df_pricing = {}

        self.note = None
        self.debug_msg = ''
        self.version = 1

        self.publish_to_slack = publish_to_slack
        self.publish_to_s3 = publish_to_s3
        self.publish_to_redis = publish_to_redis
        self.raise_on_err = raise_on_err

        if not self.name:
            self.name = 'eqa'

        self.load_from_config(
            config_dict=config_dict)
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
                        'options': pd.DataFrame([]),
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
                        'options': pd.DataFrame,
                        'news': pd.DataFrame
                    }
                }
        """

        log.info(
            'process - ticker={} balance={} owned={} date={} '
            'high={} low={} open={} close={} vol={} '
            'comm={} '
            'buy_str={} buy_risk={} '
            'sell_str={} sell_risk={} '
            'num_buys={} num_sells={} '
            'id={}'.format(
                self.ticker,
                self.balance,
                self.num_owned,
                self.trade_date,
                self.latest_high,
                self.latest_low,
                self.latest_open,
                self.latest_close,
                self.latest_volume,
                self.commission,
                self.buy_strength,
                self.buy_risk,
                self.sell_strength,
                self.sell_risk,
                len(self.buys),
                len(self.sells),
                algo_id))

        # flip these on to sell/buy
        # buys will not FILL if there's not enough funds to buy
        # sells will not FILL if there's nothing already owned
        self.should_sell = False
        self.should_buy = False

        log.info(
            'process has df_daily rows={}'.format(
                len(self.df_daily.index)))

        """
        Want to iterate over daily pricing data
        to determine buys or sells from the:
        self.df_daily dataset fetched from IEX?

        # loop over the rows in the daily dataset:
        for idx, row in self.df_daily.iterrows():
            print(row)
        """

        if self.num_owned and self.should_sell:
            self.create_sell_order(
                ticker=ticker,
                row={
                    'name': algo_id,
                    'close': 270.0,
                    'date': '2018-11-02'
                },
                reason='testing')

        if self.should_buy:
            self.create_buy_order(
                ticker=ticker,
                row={
                    'name': algo_id,
                    'close': 270.0,
                    'date': '2018-11-02'
                },
                reason='testing')

        # if still owned and have not already created
        # a sell already
        # self.num_owned automatically updates on sell and buy orders
        if self.num_owned and not self.created_sell:
            self.create_sell_order(
                ticker=ticker,
                row={
                    'name': algo_id,
                    'close': 270.0,
                    'date': '2018-11-02'
                },
                reason='testing')

    # end of process

    def get_ticker_positions(
            self,
            ticker):
        """get_ticker_positions

        get the current positions for a ticker and
        returns a tuple:
        ``num_owned (integer), buys (list), sells (list)```

        .. code-block:: python

            num_owned, buys, sells = self.get_ticker_positions(
                ticker=ticker)

        :param ticker: ticker to lookup
        """
        buys = None
        sells = None
        num_owned = None
        if ticker in self.positions:
            num_owned = self.positions[ticker].get(
                'shares',
                None)
            buys = self.positions[ticker].get(
                'buys',
                [])
            sells = self.positions[ticker].get(
                'sells',
                [])
        return num_owned, buys, sells
    # end of get_ticker_positions

    def get_trade_history_node(
                self):
        """get_trade_history_node

            Helper for quickly building a history node
            on a derived algorithm. Whatever member variables
            are in the base class ``analysis_engine.algo.BaseAlgo``
            will be added automatically into the returned:
            ``historical transaction dictionary``

            .. tip:: if you get a ``None`` back it means there
                could be a bug in how you are using the member
                variables (likely created an invalid math
                calculation) or could be a bug in the helper:
                `build_trade_history_entry <https://github.c
                om/AlgoTraders/stock-analysis-engine/blob/ma
                ster/analysis_engine/build_trade_history_entry.py>`__
        """
        history_dict = history_utils.build_trade_history_entry(
            ticker=self.ticker,
            algo_start_price=self.starting_close,
            original_balance=self.starting_balance,
            num_owned=self.num_owned,
            close=self.trade_price,
            balance=self.balance,
            commission=self.commission,
            date=self.trade_date,
            trade_type=self.trade_type,
            high=self.latest_high,
            low=self.latest_low,
            open_val=self.latest_open,
            volume=self.latest_volume,
            ask=self.ask,
            bid=self.bid,
            stop_loss=self.stop_loss,
            trailing_stop_loss=self.trailing_stop_loss,
            buy_hold_units=self.buy_hold_units,
            sell_hold_units=self.sell_hold_units,
            spread_exp_date=self.spread_exp_date,
            prev_balance=self.prev_bal,
            prev_num_owned=self.prev_num_owned,
            total_buys=self.num_buys,
            total_sells=self.num_sells,
            buy_triggered=self.should_buy,
            buy_strength=self.buy_strength,
            buy_risk=self.buy_risk,
            sell_triggered=self.should_sell,
            sell_strength=self.sell_strength,
            sell_risk=self.sell_risk,
            note=self.note,
            ds_id=self.ds_id,
            version=self.version)
        return history_dict
    # end of get_trade_history_node

    def load_from_config(
            self,
            config_dict):
        """load_config

        support for replaying algorithms from a trading history

        :param config_dict: algorithm configuration values
            usually from a previous trading history or for
            quickly testing dataset theories in a development
            environment
        """
        if config_dict:
            for k in config_dict:
                if k in self.__dict__:
                    self.__dict__[k] = config_dict[k]
    # end of load_from_config

    def get_name(self):
        """get_name"""
        return self.name
    # end of get_name

    def get_result(self):
        """get_result"""

        self.debug_msg = (
            'building results')
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

    def get_debug_msg(
            self):
        """get_debug_msg

        debug algorithms that failed
        by viewing the last ``self.debug_msg`` they
        set
        """
        return self.debug_msg
    # end of get_debug_msg

    def get_balance(
            self):
        """get_balance"""
        return self.balance
    # end of get_balance

    def get_buys(
            self):
        """get_buys"""
        return self.buys
    # end of get_buys

    def get_sells(
            self):
        """get_sells"""
        return self.sells
    # end of get_sells

    def get_owned_shares(
            self,
            ticker):
        """get_owned_shares

        :param ticker: ticker to lookup
        """
        num_owned = 0
        if ticker in self.positions:
            num_owned = self.positions[ticker].get(
                'shares',
                None)
        return num_owned
    # end of get_owned_shares

    def create_buy_order(
            self,
            ticker,
            row,
            shares=None,
            reason=None,
            orient='records',
            date_format='iso'):
        """create_buy_order

        create a buy order at the close or ask price

        :param ticker: string ticker
        :param shares: optional - integer number of shares to buy
            if None buy max number of shares at the ``close`` with the
            available ``balance`` amount.
        :param row: ``dictionary`` or ``pd.DataFrame``
            row record that will be converted to a
            json-serialized string
        :param reason: optional - reason for creating the order
            which is useful for troubleshooting order histories
        :param orient: optional - pandas orient for ``row.to_json()``
        :param date_format: optional - pandas date_format
            parameter for ``row.to_json()``
        """
        close = row['close']
        dataset_date = row['date']
        log.info(
            '{} - buy start {}@{} - shares={}'.format(
                self.name,
                ticker,
                close,
                shares))
        new_buy = None

        order_details = row
        if hasattr(row, 'to_json'):
            order_details = row.to_json(
                orient='records',
                date_format='iso'),
        try:
            num_owned = self.get_owned_shares(
                ticker=ticker)
            new_buy = buy_utils.build_buy_order(
                ticker=ticker,
                close=close,
                num_owned=num_owned,
                shares=shares,
                balance=self.balance,
                commission=self.commission,
                date=dataset_date,
                use_key='{}_{}'.format(
                    ticker,
                    dataset_date),
                details=order_details,
                reason=reason)

            prev_shares = num_owned
            if not prev_shares:
                prev_shares = 0
            prev_bal = self.balance
            if new_buy['status'] == TRADE_FILLED:
                if ticker in self.positions:
                    self.positions[ticker]['shares'] += int(
                        new_buy['shares'])
                    self.positions[ticker]['buys'].append(
                        new_buy)
                    (self.num_owned,
                     self.num_buys,
                     self.num_sells) = self.get_ticker_positions(
                        ticker=ticker)
                    self.created_buy = True
                else:
                    self.positions[ticker] = {
                        'shares': new_buy['shares'],
                        'buys': [
                            new_buy
                        ],
                        'sells': []
                    }
                self.balance = new_buy['balance']
                log.info(
                    '{} - buy end {}@{} {} shares={} cost={} bal={} '
                    'prev_shares={} prev_bal={}'.format(
                        self.name,
                        ticker,
                        close,
                        get_status(status=new_buy['status']),
                        new_buy['shares'],
                        new_buy['buy_price'],
                        self.balance,
                        prev_shares,
                        prev_bal))
            else:
                log.error(
                    '{} - buy failed {}@{} {} shares={} cost={} '
                    'bal={} '.format(
                        self.name,
                        ticker,
                        close,
                        get_status(status=new_buy['status']),
                        num_owned,
                        new_buy['buy_price'],
                        self.balance))
            # end of if trade worked or not

            self.buys.append(new_buy)
        except Exception as e:
            self.debug_msg = (
                '{} - buy {}@{} - FAILED with ex={}'.format(
                    self.name,
                    ticker,
                    close,
                    e))
            log.error(self.debug_msg)
            if self.raise_on_err:
                raise e
        # end of try/ex

        (self.num_owned,
         self.num_buys,
         self.num_sells) = self.get_ticker_positions(
            ticker=ticker)

    # end of create_buy_order

    def create_sell_order(
            self,
            ticker,
            row,
            shares=None,
            reason=None,
            orient='records',
            date_format='iso'):
        """create_sell_order

        create a sell order at the close or ask price

        :param ticker: string ticker
        :param shares: optional - integer number of shares to sell
            if None sell all owned shares at the ``close``
        :param row: ``pd.DataFrame`` row record that will
            be converted to a json-serialized string
        :param reason: optional - reason for creating the order
            which is useful for troubleshooting order histories
        :param orient: optional - pandas orient for ``row.to_json()``
        :param date_format: optional - pandas date_format
            parameter for ``row.to_json()``
        """
        close = row['close']
        dataset_date = row['date']
        log.info(
            '{} - sell start {}@{}'.format(
                self.name,
                ticker,
                close))
        new_sell = None
        order_details = row
        if hasattr(row, 'to_json'):
            order_details = row.to_json(
                orient=orient,
                date_format=date_format),
        try:
            num_owned = self.get_owned_shares(
                ticker=ticker)
            new_sell = sell_utils.build_sell_order(
                ticker=ticker,
                close=close,
                num_owned=num_owned,
                shares=shares,
                balance=self.balance,
                commission=self.commission,
                date=dataset_date,
                use_key='{}_{}'.format(
                    ticker,
                    dataset_date),
                details=order_details,
                reason=reason)

            prev_shares = num_owned
            if not prev_shares:
                prev_shares = 0
            prev_bal = self.balance
            if new_sell['status'] == TRADE_FILLED:
                if ticker in self.positions:
                    self.positions[ticker]['shares'] += int(
                        new_sell['shares'])
                    self.positions[ticker]['sells'].append(
                        new_sell)
                    (self.num_owned,
                     self.num_buys,
                     self.num_sells) = self.get_ticker_positions(
                        ticker=ticker)
                    self.created_sell = True
                else:
                    self.positions[ticker] = {
                        'shares': new_sell['shares'],
                        'buys': [],
                        'sells': [
                            new_sell
                        ]
                    }
                self.balance = new_sell['balance']
                log.info(
                    '{} - sell end {}@{} {} shares={} cost={} bal={} '
                    'prev_shares={} prev_bal={}'.format(
                        self.name,
                        ticker,
                        close,
                        get_status(status=new_sell['status']),
                        num_owned,
                        new_sell['sell_price'],
                        self.balance,
                        prev_shares,
                        prev_bal))
            else:
                log.error(
                    '{} - sell failed {}@{} {} shares={} cost={} '
                    'bal={} '.format(
                        self.name,
                        ticker,
                        close,
                        get_status(status=new_sell['status']),
                        num_owned,
                        new_sell['sell_price'],
                        self.balance))
            # end of if trade worked or not

            self.sells.append(new_sell)
        except Exception as e:
            self.debug_msg = (
                '{} - sell {}@{} - FAILED with ex={}'.format(
                    self.name,
                    ticker,
                    close,
                    e))
            log.error(self.debug_msg)
            if self.raise_on_err:
                raise e
        # end of try/ex

        (self.num_owned,
         self.num_buys,
         self.num_sells) = self.get_ticker_positions(
            ticker=ticker)

    # end of create_sell_order

    def build_progress_label(
            self,
            progress,
            total):
        """build_progress_label

        create a progress label string for the logs

        :param progress: progress counter
        :param total: total number of counts
        """
        percent_done = get_percent_done(
            progress=progress,
            total=total)
        progress_label = '{} {}/{}'.format(
            percent_done,
            progress,
            total)
        return progress_label
    # end of build_progress_label

    def get_supported_tickers_in_data(
            self,
            data):
        """get_supported_tickers_in_data

        For all updates found in ``data`` compare to the
        supported list of ``self.tickers`` to make sure
        the updates are relevant for this algorithm.

        :param data: new data stream to process in this
            algo
        """
        data_for_tickers = []
        for ticker in self.tickers:
            if ticker in data:
                data_for_tickers.append(
                    ticker)
        # end of finding tickers for this algo

        return data_for_tickers
    # end of get_supported_tickers_in_data

    def load_from_dataset(
            self,
            ds_data):
        """load_from_dataset

        Load the member variables from the extracted
        ``ds_data`` dataset.

        algorithms automatically provide the following
        member variables to  ``myalgo.process()`` for
        quickly building algorithms:

        - ``self.df_daily``
        - ``self.df_minute``
        - ``self.df_quote``
        - ``self.df_stats``
        - ``self.df_peers``
        - ``self.df_iex_news``
        - ``self.df_financials``
        - ``self.df_earnings``
        - ``self.df_dividends``
        - ``self.df_company``
        - ``self.df_yahoo_news``
        - ``self.df_options``
        - ``self.df_pricing``

        .. note:: If a key is not in the dataset, the
            algorithms's member variable will be an empty
            ``pd.DataFrame([])``. Please ensure the engine
            cached the dataset in redis using a tool like
            ``redis-cli`` to verify the values are in
            memory.

        :param ds_data: extracted, structured
            dataset from redis
        """

        # back up for debugging/tracking/comparing
        self.last_ds_id = self.ds_id
        self.last_ds_date = self.ds_date
        self.last_ds_data = self.ds_data

        # load the new one
        self.ds_data = ds_data

        self.ds_id = self.ds_data.get(
            'id',
            'missing-ID')
        self.ds_date = self.ds_data.get(
            'date',
            'missing-DATE')
        self.ds_data = self.ds_data.get(
            'data',
            'missing-DATA')
        self.df_daily = self.ds_data.get(
            'daily',
            self.empty_pd)
        self.df_minute = self.ds_data.get(
            'minute',
            self.empty_pd)
        self.df_stats = self.ds_data.get(
            'stats',
            self.empty_pd)
        self.df_peers = self.ds_data.get(
            'peers',
            self.empty_pd)
        self.df_financials = self.ds_data.get(
            'financials',
            self.empty_pd)
        self.df_earnings = self.ds_data.get(
            'earnings',
            self.empty_pd)
        self.df_dividends = self.ds_data.get(
            'dividends',
            self.empty_pd)
        self.df_quote = self.ds_data.get(
            'quote',
            self.empty_pd)
        self.df_company = self.ds_data.get(
            'company',
            self.empty_pd)
        self.df_iex_news = self.ds_data.get(
            'news1',
            self.empty_pd)
        self.df_yahoo_news = self.ds_data.get(
            'news',
            self.empty_pd)
        self.df_options = self.ds_data.get(
            'options',
            self.empty_pd)
        self.df_pricing = self.ds_data.get(
            'pricing',
            {})

        if not hasattr(self.df_daily, 'empty'):
            self.df_daily = self.empty_pd
        if not hasattr(self.df_minute, 'empty'):
            self.df_minute = self.empty_pd
        if not hasattr(self.df_stats, 'empty'):
            self.df_stats = self.empty_pd
        if not hasattr(self.df_peers, 'empty'):
            self.df_peers = self.empty_pd
        if not hasattr(self.df_financials, 'empty'):
            self.df_financials = self.empty_pd
        if not hasattr(self.df_earnings, 'empty'):
            self.df_earnings = self.empty_pd
        if not hasattr(self.df_dividends, 'empty'):
            self.df_dividends = self.empty_pd
        if not hasattr(self.df_quote, 'empty'):
            self.df_quote = self.empty_pd
        if not hasattr(self.df_company, 'empty'):
            self.df_company = self.empty_pd
        if not hasattr(self.df_iex_news, 'empty'):
            self.df_iex_news = self.empty_pd
        if not hasattr(self.df_yahoo_news, 'empty'):
            self.df_yahoo_news = self.empty_pd
        if not hasattr(self.df_options, 'empty'):
            self.df_options = self.empty_pd
        if not hasattr(self.df_pricing, 'empty'):
            self.df_pricing = self.empty_pd

        # set internal values:
        self.trade_date = self.ds_date
        self.created_buy = False
        self.created_sell = False
        self.should_buy = False
        self.should_sell = False

        try:
            if hasattr(self.df_daily, 'empty'):
                columns = self.df_daily.columns.values
                if 'high' in columns:
                    self.latest_high = float(
                        self.df_daily.iloc[-1]['high'])
                if 'low' in columns:
                    self.latest_low = float(
                        self.df_daily.iloc[-1]['low'])
                if 'open' in columns:
                    self.latest_open = float(
                        self.df_daily.iloc[-1]['open'])
                if 'close' in columns:
                    self.latest_close = float(
                        self.df_daily.iloc[-1]['close'])
                    self.trade_price = self.latest_close
                    if not self.starting_close:
                        self.starting_close = self.latest_close
                if 'volume' in columns:
                    self.latest_volume = int(
                        self.df_daily.iloc[-1]['volume'])
        except Exception as e:
            self.debug_msg = (
                '{} handle - FAILED getting latest prices '
                'for algo={} - ds={} ex={}'.format(
                    self.name,
                    self.ds_id,
                    self.ds_date,
                    e))
            log.error(self.debug_msg)
            if self.raise_on_err:
                raise e
        # end of trying to get the latest prices out of the
        # datasets
    # end of load_from_dataset

    def handle_data(
            self,
            data):
        """handle_data

        process new data for the algorithm using a multi-ticker
        mapping structure

        :param data: dictionary of extracted data from
            the redis pipeline with a structure:
            ::

                ticker = 'SPY'
                # string usually: YYYY-MM-DD
                date = '2018-11-05'
                # redis cache key for the dataset format: <ticker>_<date>
                dataset_id = '{}_{}'.format(
                    ticker,
                    date)
                dataset = {
                    ticker: [
                        {
                            'id': dataset_id,
                            'date': date,
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
                                'options': pd.DataFrame([]),
                                'pricing': dictionary,
                                'news': pd.DataFrame([])
                            }
                        }
                    ]
                }

        """
        self.debug_msg = (
            '{} handle - start'.format(
                self.name))

        log.info(self.debug_msg)

        data_for_tickers = self.get_supported_tickers_in_data(
            data=data)

        num_tickers = len(data_for_tickers)
        if num_tickers > 0:
            self.debug_msg = (
                '{} handle - tickers={}'.format(
                    self.name,
                    json.dumps(data_for_tickers)))

        for ticker in data_for_tickers:
            num_ticker_datasets = len(data[ticker])
            cur_idx = 1
            for idx, node in enumerate(data[ticker]):
                track_label = self.build_progress_label(
                    progress=cur_idx,
                    total=num_ticker_datasets)
                algo_id = 'ticker={} {}'.format(
                    ticker,
                    track_label)
                log.info(
                    '{} handle - {} - ds={}'.format(
                        self.name,
                        algo_id,
                        node['date']))

                self.ticker = ticker
                self.prev_bal = self.balance
                self.prev_num_owned = self.num_owned

                (self.num_owned,
                 self.num_buys,
                 self.num_sells) = self.get_ticker_positions(
                    ticker=ticker)

                # parse the dataset node and set member variables
                self.debug_msg = (
                    '{} START - load dataset id={}'.format(
                        ticker,
                        node.get('id', 'missing-id')))
                self.load_from_dataset(
                    ds_data=node)
                self.debug_msg = (
                    '{} END - load dataset id={}'.format(
                        ticker,
                        node.get('id', 'missing-id')))

                # thinking this could be a separate celery task
                # to increase horizontal scaling to crunch
                # datasets faster like:
                # http://jsatt.com/blog/class-based-celery-tasks/
                self.debug_msg = (
                    '{} START - process id={}'.format(
                        ticker,
                        node.get('id', 'missing-id')))
                self.process(
                    algo_id=algo_id,
                    ticker=self.ticker,
                    dataset=node)
                self.debug_msg = (
                    '{} END - process id={}'.format(
                        ticker,
                        node.get('id', 'missing-id')))

                # always record the trade history for
                # analysis/review using: myalgo.get_result()
                self.debug_msg = (
                    '{} START - history id={}'.format(
                        ticker,
                        node.get('id', 'missing-id')))
                self.last_history_dict = self.get_trade_history_node()
                if self.last_history_dict:
                    self.order_history.append(self.last_history_dict)
                self.debug_msg = (
                    '{} END - history id={}'.format(
                        ticker,
                        node.get('id', 'missing-id')))

                cur_idx += 1
        # for all supported tickers

        self.debug_msg = (
            '{} handle - end tickers={}'.format(
                self.name,
                num_tickers))

    # end of handle_data

# end of BaseAlgo
