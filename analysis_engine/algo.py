"""
Algorithm classes:
"""

import json
import analysis_engine.api_requests as api_requests
from analysis_engine.consts import TRADE_FILLED
from analysis_engine.consts import get_status
from analysis_engine.consts import get_percent_done
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


class EquityAlgo:
    """EquityAlgo

    Run an algorithm against multiple tickers at once through the
    redis dataframe pipeline provided by `analysis_engine.extract.ex
    tract <https://github.com/AlgoTraders/stock-analysis-engine/bl
    ob/master/analysis_engine/extract.py>`__.

    **Data Pipeline Structure**

    This algorithm can handle an extracted dictionary with structure:

    .. code-block:: python

        ticker = 'SPY'
        starting_capital = 1000.00
        demo_algo = EquityAlgo(
            ticker=ticker,
            balance=starting_capital,
            name='test-{}'.format(ticker))
        df_name = '{}_2018-11-05_daily'.format(
            ticker)
        data = {
            ticker: [
                {
                    df_name: [
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
                    ]
                }
            ]
        }
        demo_algo.handle_data(data=data)
    """

    def __init__(
            self,
            ticker,
            balance,
            tickers=None,
            name=None,
            auto_fill=True):
        """__init__

        :param ticker: ngle ticker string
        :param balance: starting capital balance
        :param tickers: optional - list of ticker strings
        :param name: optional - log tracking name
            or algo name
        :param auto_fill: optional - boolean for auto filling
            buy/sell orders for backtesting (default is
            ``True``)
        """
        self.commission = 6.0
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
        self.result = None
        self.name = name
        self.last_close = None
        self.positions = {}
        if not self.name:
            self.name = 'eqa'
    # end of __init__

    def analyze_dataset(
            self,
            track_id,
            ticker,
            dataset):

        num_owned, num_buys, num_sells = self.get_ticker_positions(
            ticker=ticker)
        ds_name = dataset.get('name', 'no-ds-name')

        log.info(
            '{} - az - {} - ds={} '
            'bal={} shares={} '
            'num_buys={} num_sells={}'.format(
                self.name,
                track_id,
                ds_name,
                self.balance,
                num_owned,
                len(self.buys),
                len(self.sells)))
        print(dataset)
        self.create_buy_order(
            ticker=ticker,
            row={
                'name': track_id,
                'close': 270.0,
                'date': '2018-11-02'
            },
            reason='testing')
        self.create_sell_order(
            ticker=ticker,
            row={
                'name': track_id,
                'close': 270.0,
                'date': '2018-11-02'
            },
            reason='testing')
    # end of analyze_dataset

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

    def get_result(self):
        """get_result"""
        return self.get_result
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
        num_owned = None
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
            reason=None):
        """create_buy_order

        create a buy order at the close or ask price

        :param ticker: string ticker
        :param shares: optional - integer number of shares to buy
            if None buy max number of shares at the ``close`` with the
            available ``balance`` amount.
        :param row: ``pd.DataFrame`` row record that will
            be converted to a json-serialized string
        :param reason: optional - reason for creating the order
            which is useful for troubleshooting order histories
        """
        close = row['close']
        backtest_date = row['date']
        log.info(
            '{} - buy start {}@{} - shares={}'.format(
                self.name,
                ticker,
                close,
                shares))
        new_buy = None
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
                date=backtest_date,
                details=row.to_json(
                    orient='records',
                    date_format='iso'),
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
    # end of create_buy_order

    def create_sell_order(
            self,
            ticker,
            row,
            reason=None):
        """create_sell_order

        create a sell order at the close or ask price

        :param ticker: string ticker
        :param row: ``pd.DataFrame`` row record that will
            be converted to a json-serialized string
        :param reason: optional - reason for creating the order
            which is useful for troubleshooting order histories
        """
        close = row['close']
        backtest_date = row['date']
        log.info(
            '{} - sell start {}@{}'.format(
                self.name,
                ticker,
                close))
        new_sell = None
        try:
            num_owned = self.get_owned_shares(
                ticker=ticker)
            new_sell = api_requests.build_sell_order(
                ticker=ticker,
                close=close,
                shares=num_owned,
                balance=self.balance,
                commission=self.commission,
                date=backtest_date,
                details=row.to_json(
                    orient='records',
                    date_format='iso'),
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
                    progress=idx,
                    total=num_ticker_datasets)
                track_id = 'ticker={} {}'.format(
                    ticker,
                    track_label)
                is_valid = node.get('valid', False)
                if is_valid:
                    log.info(
                        '{} - handle - {} - ds={} valid={}'.format(
                            self.name,
                            track_id,
                            node['name'],
                            node.get('valid', None)))
                    self.analyze_dataset(
                        track_id=track_id,
                        ticker=ticker,
                        dataset=node)
                else:
                    log.info(
                        '{} - handle - {} - invalid ds={}'.format(
                            self.name,
                            track_id,
                            node['name']))
                # end of if/else valid dataset
                cur_idx += 1
        # for all supported tickers

        log.info(
            '{} - handle - end tickers={}'.format(
                self.name,
                num_tickers))

    # end of handle_data

# end of EquityAlgo
