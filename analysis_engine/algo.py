"""
Algorithm classes:

- EquityAlgo
"""

import analysis_engine.api_requests as api_requests
from analysis_engine.consts import TRADE_FILLED
from analysis_engine.consts import get_status
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


class EquityAlgo:
    """EquityAlgo"""

    def __init__(
            self,
            tickers,
            balance,
            name=None):
        """__init__

        :param balance: starting capital balance
        :param tickers: list of ticker strings
        :param name: optional - log tracking name
            or algo name
        """
        self.commission = 6.0
        self.buys = []
        self.sells = []
        self.num_shares = 0
        self.tickers = tickers
        self.balance = balance
        self.result = None
        self.name = name
        if not self.name:
            self.name = 'eqa'
    # end of __init__

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

    def buy(
            self,
            ticker,
            row,
            reason=None):
        """buy

        create a buy order at the close or ask price

        :param ticker: string ticker
        :param row: ``pd.DataFrame`` row record that will
            be converted to a json-serialized string
        :param reason: optional - reason for creating the order
            which is useful for troubleshooting order histories
        """
        close = row['close']
        backtest_date = row['date']
        log.info(
            '{} - buy start {}@{}'.format(
                self.name,
                ticker,
                close))
        new_buy = None
        try:
            new_buy = api_requests.build_buy_order(
                ticker=ticker,
                close=close,
                shares=self.shares,
                balance=self.balance,
                commission=self.commission,
                date=backtest_date,
                details=row.to_json(
                    orient='records',
                    date_format='iso'),
                reason=reason)

            prev_shares = self.shares
            prev_bal = self.balance
            if new_buy['status'] == TRADE_FILLED:
                self.shares = new_buy['shares']
                self.balance = new_buy['balance']
                log.info(
                    '{} - buy end {}@{} {} shares={} cost={} bal={} '
                    'prev_shares={} prev_bal={}'.format(
                        self.name,
                        ticker,
                        close,
                        get_status(status=new_buy['status']),
                        self.shares,
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
                        self.shares,
                        new_buy['buy_price'],
                        self.balance))
            # end of if trade worked or not

            self.buys.append(new_buy)
        except Exception as e:
            log.error(
                '{} - buy {}@{} - FAILED with ex={}'.format(
                    self.name,
                    ticker,
                    close))
        # end of try/ex
    # end of buy

    def sell(
            self,
            ticker,
            row,
            reason=None):
        """sell

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
            new_sell = api_requests.build_sell_order(
                ticker=ticker,
                close=close,
                shares=self.shares,
                balance=self.balance,
                commission=self.commission,
                date=backtest_date,
                details=row.to_json(
                    orient='records',
                    date_format='iso'),
                reason=reason)

            prev_shares = self.shares
            prev_bal = self.balance
            if new_sell['status'] == TRADE_FILLED:
                self.shares = new_sell['shares']
                self.balance = new_sell['balance']
                log.info(
                    '{} - sell end {}@{} {} shares={} cost={} bal={} '
                    'prev_shares={} prev_bal={}'.format(
                        self.name,
                        ticker,
                        close,
                        get_status(status=new_sell['status']),
                        self.shares,
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
                        self.shares,
                        new_sell['sell_price'],
                        self.balance))
            # end of if trade worked or not

            self.sells.append(new_sell)
        except Exception as e:
            log.error(
                '{} - sell {}@{} - FAILED with ex={}'.format(
                    self.name,
                    ticker,
                    close))
        # end of try/ex
    # end of sell

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
            '{} - handle data - start'.format(
                self.name))
        for ticker in self.tickers:
            if ticker in data:
                for node in data[ticker]:
                    log.info(
                        '{} - handle data - ticker={} ds={} valid={}'.format(
                            self.name,
                            ticker,
                            node['name'],
                            node.get('valid', None)))
        # for all tickers

        log.info(
            '{} - handle data - end'.format(
                self.name))
    # end of handle_data

# end of EquityAlgo
