"""
Helper for building an algorithm trading and performance history
as a dictionary that can be reviewed during or after an
algorithm finishes running
"""

import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def build_trade_history_entry(
        ticker,
        num_owned,
        close,
        balance,
        commission,
        date,
        trade_type,
        algo_start_price,
        original_balance,
        minute=None,
        high=None,
        low=None,
        open_val=None,
        volume=None,
        ask=None,
        bid=None,
        today_high=None,
        today_low=None,
        today_open_val=None,
        today_close=None,
        today_volume=None,
        stop_loss=None,
        trailing_stop_loss=None,
        buy_hold_units=None,
        sell_hold_units=None,
        spread_exp_date=None,
        spread_id=None,
        low_strike=None,
        low_bid=None,
        low_ask=None,
        low_volume=None,
        low_open_int=None,
        low_delta=None,
        low_gamma=None,
        low_theta=None,
        low_vega=None,
        low_rho=None,
        low_impl_vol=None,
        low_intrinsic=None,
        low_extrinsic=None,
        low_theo_price=None,
        low_theo_volatility=None,
        low_max_covered=None,
        low_exp_date=None,
        high_strike=None,
        high_bid=None,
        high_ask=None,
        high_volume=None,
        high_open_int=None,
        high_delta=None,
        high_gamma=None,
        high_theta=None,
        high_vega=None,
        high_rho=None,
        high_impl_vol=None,
        high_intrinsic=None,
        high_extrinsic=None,
        high_theo_price=None,
        high_theo_volatility=None,
        high_max_covered=None,
        high_exp_date=None,
        prev_balance=None,
        prev_num_owned=None,
        total_buys=None,
        total_sells=None,
        buy_triggered=None,
        buy_strength=None,
        buy_risk=None,
        sell_triggered=None,
        sell_strength=None,
        sell_risk=None,
        num_indicators_buy=None,
        num_indicators_sell=None,
        min_buy_indicators=None,
        min_sell_indicators=None,
        net_gain=None,
        net_value=None,
        ds_id=None,
        note=None,
        err=None,
        entry_spread_dict=None,
        version=1):
    """build_trade_history_entry

    Build a dictionary for tracking an algorithm profitability per ticker
    and for ``TRADE_SHARES``, ``TRADE_VERTICAL_BULL_SPREAD``, or
    ``TRADE_VERTICAL_BEAR_SPREAD`` trading types.

    .. note:: setting the ``minute`` is required to build
        a minute-by-minute ``Trading History``

    :param ticker: string ticker or symbol
    :param num_owned: integer current owned
        number of ``shares`` for this asset or number of
        currently owned ``contracts`` for an options
        spread.
    :param close: float ``close`` price of the
        underlying asset
    :param balance: float amount of available capital
    :param commission: float for commission costs
    :param date: string trade date for that row usually
        ``COMMON_DATE_FORMAT`` (``YYYY-MM-DD``)
    :param minute: optional - string for recording the minute
        the trade was place, and the format is
        ``COMMON_TICK_DATE_FORMAT`` (``YYYY-MM-DD HH:MM:SS``)
        this is optional if the algorithm is set up to
        trade using a ``day`` value for timeseries.
    :param trade_type: type of the trade - supported values:
            ``TRADE_SHARES``,
            ``TRADE_VERTICAL_BULL_SPREAD``,
            ``TRADE_VERTICAL_BEAR_SPREAD``
    :param algo_start_price: float starting close/contract price
        for this algo
    :param original_balance: float starting original account
        balance for this algo
    :param high: optional - float underlying stock asset ``high`` price
    :param low: optional - float underlying stock asset ``low`` price
    :param open_val: optional - float underlying stock asset ``open`` price
    :param volume: optional - integer underlying stock asset ``volume``
    :param ask: optional - float ``ask`` price of the
        stock (for buying ``shares``)
    :param bid: optional - float ``bid`` price of the
        stock (for selling ``shares``)
    :param today_high: optional - float ``high`` from
        the daily dataset (if available)
    :param today_low: optional - float ``low`` from
        the daily dataset (if available)
    :param today_open_val: optional - float ``open`` from
        the daily dataset (if available)
    :param today_close: optional - float ``close`` from
        the daily dataset (if available)
    :param today_volume: optional - float ``volume`` from
        the daily dataset (if available)
    :param stop_loss: optional - float ``stop_loss`` price of the
        stock/spread (for selling ``shares`` vs ``contracts``)
    :param trailing_stop_loss: optional - float ``trailing_stop_loss``
        price of the stock/spread (for selling ``shares`` vs ``contracts``)
    :param buy_hold_units: optional - number of units
        to hold buys - helps with algorithm tuning
    :param sell_hold_units: optional - number of units
        to hold sells - helps with algorithm tuning
    :param spread_exp_date: optional - string spread contract
        expiration date (``COMMON_DATE_FORMAT`` (``YYYY-MM-DD``)
    :param spread_id: optional - spread identifier for reviewing
        spread performances
    :param low_strike: optional
        - only for vertical bull/bear trade types
        ``low leg strike price`` of the spread
    :param low_bid: optional
        - only for vertical bull/bear trade types
        ``low leg bid`` of the spread
    :param low_ask: optional
        - only for vertical bull/bear trade types
        ``low leg ask`` of the spread
    :param low_volume: optional
        - only for vertical bull/bear trade types
        ``low leg volume`` of the spread
    :param low_open_int: optional
        - only for vertical bull/bear trade types
        ``low leg open interest`` of the spread
    :param low_delta: optional
        - only for vertical bull/bear trade types
        ``low leg delta`` of the spread
    :param low_gamma: optional
        - only for vertical bull/bear trade types
        ``low leg gamma`` of the spread
    :param low_theta: optional
        - only for vertical bull/bear trade types
        ``low leg theta`` of the spread
    :param low_vega: optional
        - only for vertical bull/bear trade types
        ``low leg vega`` of the spread
    :param low_rho: optional
        - only for vertical bull/bear trade types
        ``low leg rho`` of the spread
    :param low_impl_vol: optional
        - only for vertical bull/bear trade types
        ``low leg implied volatility`` of the spread
    :param low_intrinsic: optional
        - only for vertical bull/bear trade types
        ``low leg intrinsic`` of the spread
    :param low_extrinsic: optional
        - only for vertical bull/bear trade types
        ``low leg extrinsic`` of the spread
    :param low_theo_price: optional
        - only for vertical bull/bear trade types
        ``low leg theoretical price`` of the spread
    :param low_theo_volatility: optional
        - only for vertical bull/bear trade types
        ``low leg theoretical volatility`` of the spread
    :param low_max_covered: optional
        - only for vertical bull/bear trade types
        ``low leg max covered returns`` of the spread
    :param low_exp_date: optional
        - only for vertical bull/bear trade types
        ``low leg expiration date`` of the spread
    :param high_strike: optional
        - only for vertical bull/bear trade types
        ``high leg strike price`` of the spread
    :param high_bid: optional
        - only for vertical bull/bear trade types
        ``high leg bid`` of the spread
    :param high_ask: optional
        - only for vertical bull/bear trade types
        ``high leg ask`` of the spread
    :param high_volume: optional
        - only for vertical bull/bear trade types
        ``high leg volume`` of the spread
    :param high_open_int: optional
        - only for vertical bull/bear trade types
        ``high leg open interest`` of the spread
    :param high_delta: optional
        - only for vertical bull/bear trade types
        ``high leg delta`` of the spread
    :param high_gamma: optional
        - only for vertical bull/bear trade types
        ``high leg gamma`` of the spread
    :param high_theta: optional
        - only for vertical bull/bear trade types
        ``high leg theta`` of the spread
    :param high_vega: optional
        - only for vertical bull/bear trade types
        ``high leg vega`` of the spread
    :param high_rho: optional
        - only for vertical bull/bear trade types
        ``high leg rho`` of the spread
    :param high_impl_vol: optional
        - only for vertical bull/bear trade types
        ``high leg implied volatility`` of the spread
    :param high_intrinsic: optional
        - only for vertical bull/bear trade types
        ``high leg intrinsic`` of the spread
    :param high_extrinsic: optional
        - only for vertical bull/bear trade types
        ``high leg extrinsic`` of the spread
    :param high_theo_price: optional
        - only for vertical bull/bear trade types
        ``high leg theoretical price`` of the spread
    :param high_theo_volatility: optional
        - only for vertical bull/bear trade types
        ``high leg theoretical volatility`` of the spread
    :param high_max_covered: optional
        - only for vertical bull/bear trade types
        ``high leg max covered returns`` of the spread
    :param high_exp_date: optional
        - only for vertical bull/bear trade types
        ``high leg expiration date`` of the spread
    :param prev_balance: optional - previous balance
        for this algo
    :param prev_num_owned: optional - previous num of
        ``shares`` or ``contracts``
    :param total_buys: optional - total buy orders
        for this algo
    :param total_sells: optional - total sell orders
        for this algo
    :param buy_triggered: optional - bool
        ``buy`` conditions in the algorithm triggered
    :param buy_strength: optional - float
        custom strength/confidence rating for tuning
        algorithm performance for desirable
        sensitivity and specificity
    :param buy_risk: optional - float
        custom risk rating for tuning algorithm
        peformance for avoiding custom risk for buy
        conditions
    :param sell_triggered: optional - bool
        ``sell`` conditions in the algorithm triggered
    :param sell_strength: optional - float
        custom strength/confidence rating for tuning
        algorithm performance for desirable
        sensitivity and specificity
    :param sell_risk: optional - float
        custom risk rating for tuning algorithm
        peformance for avoiding custom risk for buy
        conditions
    :param num_indicators_buy: optional - integer
        number of indicators the ``IndicatorProcessor``
        processed and said to ``buy`` an asset
    :param num_indicators_sell: optional - integer
        number of indicators the ``IndicatorProcessor``
        processed and said to ``sell`` an asset
    :param min_buy_indicators: optional - integer
        minimum number of indicators required to trigger
        a ``buy`` order
    :param min_sell_indicators: optional - integer
        minimum number of indicators required to trigger
        a ``sell`` order
        net_gain=None,
        net_value=None,
    :param net_value: optional - float total value the algorithm
        has left remaining since starting trading. this includes
        the number of ``self.num_owned`` shares with the
        ``self.latest_close`` price included
    :param net_gain: optional - float amount the algorithm has
        made since starting including owned shares
        with the ``self.latest_close`` price included

    :param ds_id: optional - datset id for debugging
    :param note: optional - string for tracking high level
        testing notes on algorithm indicator ratings and
        internal message passing during an algorithms's
        ``self.process`` method
    :param err: optional - string for tracking errors
    :param entry_spread_dict: optional - on exit spreads
        the calculation of net gain can use the entry
        spread to determine specific performance metrics
        (work in progress)
    :param version: optional - version tracking order history
    """
    status = ae_consts.NOT_RUN
    algo_status = ae_consts.NOT_RUN
    err = None
    balance_net_gain = 0.0
    breakeven_price = None
    max_profit = None  # only for option spreads
    max_loss = None  # only for option spreads
    exp_date = None  # only for option spreads

    # latest price - start price of the algo
    price_change_since_start = close - algo_start_price

    if close:
        if close < 0.01:
            status = ae_consts.INVALID

    history_dict = {
        'ticker': ticker,
        'algo_start_price': ae_consts.to_f(algo_start_price),
        'algo_price_change': ae_consts.to_f(price_change_since_start),
        'original_balance': ae_consts.to_f(original_balance),
        'status': status,
        'algo_status': algo_status,
        'num_indicators_buy': num_indicators_buy,
        'num_indicators_sell': num_indicators_sell,
        'min_buy_indicators': min_buy_indicators,
        'min_sell_indicators': min_sell_indicators,
        'ds_id': ds_id,
        'num_owned': num_owned,
        'close': ae_consts.to_f(close),
        'balance': ae_consts.to_f(balance),
        'commission': ae_consts.to_f(commission),
        'date': date,
        'minute': minute,
        'trade_type': trade_type,
        'high': ae_consts.to_f(high),
        'low': ae_consts.to_f(low),
        'open': ae_consts.to_f(open_val),
        'volume': volume,
        'ask': ae_consts.to_f(ask),
        'bid': ae_consts.to_f(bid),
        'today_high': ae_consts.to_f(today_high),
        'today_low': ae_consts.to_f(today_low),
        'today_open_val': ae_consts.to_f(today_open_val),
        'today_close': ae_consts.to_f(today_close),
        'today_volume': ae_consts.to_f(today_volume),
        'stop_loss': ae_consts.to_f(stop_loss),
        'trailing_stop_loss': ae_consts.to_f(trailing_stop_loss),
        'buy_hold_units': buy_hold_units,
        'sell_hold_units': sell_hold_units,
        'low_strike': low_strike,
        'low_bid': ae_consts.to_f(low_bid),
        'low_ask': ae_consts.to_f(low_ask),
        'low_volume': low_volume,
        'low_open_int': low_open_int,
        'low_delta': low_delta,
        'low_gamma': low_gamma,
        'low_theta': low_theta,
        'low_vega': low_vega,
        'low_rho': low_rho,
        'low_impl_vol': low_impl_vol,
        'low_intrinsic': low_intrinsic,
        'low_extrinsic': low_extrinsic,
        'low_theo_price': low_theo_price,
        'low_theo_volatility': low_theo_volatility,
        'low_max_covered': low_max_covered,
        'low_exp_date': low_exp_date,
        'high_strike': high_strike,
        'high_bid': ae_consts.to_f(high_bid),
        'high_ask': ae_consts.to_f(high_ask),
        'high_volume': high_volume,
        'high_open_int': high_open_int,
        'high_delta': high_delta,
        'high_gamma': high_gamma,
        'high_theta': high_theta,
        'high_vega': high_vega,
        'high_rho': high_rho,
        'high_impl_vol': high_impl_vol,
        'high_intrinsic': high_intrinsic,
        'high_extrinsic': high_extrinsic,
        'high_theo_price': high_theo_price,
        'high_theo_volatility': high_theo_volatility,
        'high_max_covered': high_max_covered,
        'high_exp_date': high_exp_date,
        'spread_id': spread_id,
        'net_gain': net_gain,
        'net_value': net_value,
        'breakeven_price': breakeven_price,
        'max_profit': ae_consts.to_f(max_profit),
        'max_loss': ae_consts.to_f(max_loss),
        'exp_date': exp_date,
        'prev_balance': ae_consts.to_f(prev_balance),
        'prev_num_owned': ae_consts.to_f(prev_num_owned),
        'total_buys': total_buys,
        'total_sells': total_sells,
        'note': note,
        'err': err,
        'version': version
    }

    # evaluate if the algorithm is gaining
    # cash over the test
    if balance and original_balance:
        # net change on the balance
        # note this needs to be upgraded to
        # support orders per ticker
        # single tickers will work for v1
        balance_net_gain = balance - original_balance
        if balance_net_gain > 0.0:
            algo_status = ae_consts.ALGO_PROFITABLE
        else:
            algo_status = ae_consts.ALGO_NOT_PROFITABLE
    else:
        history_dict['err'] = (
            '{} ds_id={} missing balance={} and '
            'original_balance={}'.format(
                ticker,
                ds_id,
                balance,
                original_balance))
        algo_status = ae_consts.ALGO_ERROR
    # if starting balance and original_balance exist
    # to determine algorithm trade profitability

    # if there are no shares to sell then
    # there's no current trade open
    if num_owned and num_owned < 1:
        status = ae_consts.TRADE_NO_SHARES_TO_SELL
    else:
        if close < 0.01:
            history_dict['err'] = (
                '{} ds_id={} close={} must be greater '
                'than 0.01'.format(
                    ticker,
                    ds_id,
                    close))
            status = ae_consts.TRADE_ERROR
        elif algo_start_price < 0.01:
            history_dict['err'] = (
                '{} ds_id={} algo_start_price={} must be greater '
                'than 0.01'.format(
                    ticker,
                    ds_id,
                    algo_start_price))
            status = ae_consts.TRADE_ERROR
        else:
            price_net_gain = close - algo_start_price
            if price_net_gain > 0.0:
                status = ae_consts.TRADE_PROFITABLE
            else:
                status = ae_consts.TRADE_NOT_PROFITABLE
    # if starting price when algo started and close exist
    # determine if this trade profitability

    # Assign calculated values:
    history_dict['net_gain'] = net_gain
    history_dict['balance_net_gain'] = balance_net_gain
    history_dict['breakeven_price'] = breakeven_price
    history_dict['max_profit'] = max_profit
    history_dict['max_loss'] = max_loss
    history_dict['exp_date'] = exp_date

    # assign statuses
    history_dict['status'] = status
    history_dict['algo_status'] = algo_status

    use_date = minute
    if not use_date:
        use_date = date

    log.debug(
        '{} ds_id={} {} algo={} trade={} history={}'.format(
            ticker,
            ds_id,
            use_date,
            ae_consts.get_status(status=history_dict['algo_status']),
            ae_consts.get_status(status=history_dict['status']),
            ae_consts.ppj(history_dict)))

    return history_dict
# end of build_trade_history_entry
