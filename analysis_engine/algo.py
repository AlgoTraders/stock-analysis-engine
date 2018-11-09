"""
Example Equity algorithm
"""

import json
import analysis_engine.api_requests as api_requests
from analysis_engine.consts import TRADE_FILLED
from analysis_engine.consts import TRADE_SHARES
from analysis_engine.consts import get_status
from analysis_engine.consts import get_percent_done
from analysis_engine.utils import utc_now_str
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


class EquityAlgo:
    """EquityAlgo

    Run an algorithm against multiple tickers at once through the
    redis dataframe pipeline provided by
    `analysis_engine.extract.extract
    <https://github.com/AlgoTraders/stock-analysis-engine/bl
    ob/master/analysis_engine/extract.py>`__.

    **Data Pipeline Structure**

    This algorithm can handle an extracted dictionary with structure:

    .. code-block:: python

        import pandas as pd
        from analysis_engine.algo import EquityAlgo
        ticker = 'SPY'
        demo_algo = EquityAlgo(
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
            publish_report_to_slack=True):
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
        self.trailing_stop = None
        self.trailing_stop_loss = None

        self.note = None
        self.version = 1

        if not self.name:
            self.name = 'eqa'
    # end of __init__

    def process(
            self,
            algo_id,
            ticker,
            dataset):
        """process

        process buy and sell conditions and place orders here.

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param dataset: a pandas ``pd.DataFrame`` which could
            be empty
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
            are in the base class ``analysis_engine.EquityAlgo``
            will be added automatically into the returned:
            `historical transaction dictionary`

            .. tip:: if you get a `None` back it means there
                could be a bug in how you are using the member
                variables (likely created an invalid math
                calculation) or could be a bug in the helper:
                `build_trade_history_entry <https://github.c
                om/AlgoTraders/stock-analysis-engine/blob/ma
                ster/analysis_engine/api_requests.py>`__
        """
        history_dict = {}
        try:
            history_dict = api_requests.build_trade_history_entry(
                ticker=self.ticker,
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
        except Exception as e:
            msg = (
                '{} - failed building trade history node ticker={} ds={} '
                'history ex={}'.format(
                    self.name,
                    self.ticker,
                    self.ds_id,
                    e))
            log.error(msg)
            history_dict = None
        # end of try/ex

        return history_dict
    # end of get_trade_history_node

    def get_name(self):
        """get_name"""
        return self.name
    # end of get_name

    def get_result(self):
        """get_result"""

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

    def get_balance(self):
        """get_balance"""
        return self.balance
    # end of get_balance

    def get_buys(self):
        """get_buys"""
        return self.buys
    # end of get_buys

    def get_sells(self):
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
            new_buy = api_requests.build_buy_order(
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
            log.error(
                '{} - buy {}@{} - FAILED with ex={}'.format(
                    self.name,
                    ticker,
                    close,
                    e))
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
            new_sell = api_requests.build_sell_order(
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
            log.error(
                '{} - sell {}@{} - FAILED with ex={}'.format(
                    self.name,
                    ticker,
                    close,
                    e))
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

    def handle_data(
            self,
            data):
        """handle_data

        process new data for the algorithm using a multi-ticker
        mapping structure

        :param data: dictionary with structure:
            ::

                data['SPY'][0] = {
                    'name': 'SPY_2018-11-02_daily',
                    'valid_df': bool,
                    'df': pd.DataFrame
                }
        """
        log.info(
            '{} - handle - start'.format(
                self.name))

        data_for_tickers = self.get_supported_tickers_in_data(
            data=data)

        num_tickers = len(data_for_tickers)
        if num_tickers > 0:
            log.info(
                '{} - handle - tickers={}'.format(
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
                    '{} - handle - {} - ds={}'.format(
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

                self.ds_id = node.get('id', 'no-ds_id')
                self.trade_date = node.get('date', 'no-date')
                self.created_buy = False
                self.created_sell = False
                self.should_buy = False
                self.should_sell = False

                try:
                    daily_df = node.get(
                        'data', {}).get(
                            'daily', None)

                    if hasattr(daily_df, 'empty'):
                        columns = daily_df.columns.values
                        if 'high' in columns:
                            self.latest_high = float(
                                daily_df.iloc[-1]['high'])
                        if 'low' in columns:
                            self.latest_low = float(
                                daily_df.iloc[-1]['low'])
                        if 'open' in columns:
                            self.latest_open = float(
                                daily_df.iloc[-1]['open'])
                        if 'close' in columns:
                            self.latest_close = float(
                                daily_df.iloc[-1]['close'])
                        if 'volume' in columns:
                            self.latest_volume = int(
                                daily_df.iloc[-1]['volume'])
                except Exception as e:
                    log.info(
                        '{} - handle - FAILED getting latest prices '
                        'for algo={} - ds={} ex={}'.format(
                            self.name,
                            algo_id,
                            node['date'],
                            e))
                # end of trying to get the latest prices out of the
                # datasets

                # thinking this could be a separate celery task
                # to increase horizontal scaling to crunch
                # datasets faster like:
                # http://jsatt.com/blog/class-based-celery-tasks/
                self.process(
                    algo_id=algo_id,
                    ticker=self.ticker,
                    dataset=node)

                # always record the trade history for
                # analysis/review using: myalgo.get_result()
                self.last_history_dict = self.get_trade_history_node()
                if self.last_history_dict:
                    self.order_history.append(self.last_history_dict)

                cur_idx += 1
        # for all supported tickers

        log.info(
            '{} - handle - end tickers={}'.format(
                self.name,
                num_tickers))

    # end of handle_data

# end of EquityAlgo
