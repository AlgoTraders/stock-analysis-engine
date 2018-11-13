"""
This is a wrapper for running your own custom algorithms

.. note:: Please refer to the `sa.py <https://github.com/Algo
    Traders/stock-analysis-engine/blob/master/analysi
    s_engine/scripts/sa.py>`__ for the lastest usage examples.

Example with the command line tool:

::

    sa.py -t SPY -g /opt/sa/analysis_engine/mocks/example_algo_minute.py

"""

import inspect
import types
import importlib.machinery
import datetime
import analysis_engine.build_algo_request as build_algo_request
import analysis_engine.build_result as build_result
import analysis_engine.run_algo as run_algo
import analysis_engine.consts as sa_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def run_custom_algo(
        mod_path,
        ticker='SPY',
        balance=50000,
        commission=6.0,
        start_date=None,
        end_date=None,
        config_file=None,
        name='myalgo',
        raise_on_err=True):
    """run_custom_algo

    Run a custom algorithm that derives the
    ``analysis_engine.algo.BaseAlgo`` class

    .. note:: Make sure to only have **1**
        class defined in an algo module. Imports from
        other modules should work just fine.

    :param mod_path: file path to custom
        algorithm class module
    :param ticker: ticker symbol
    :param balance: float - starting balance capital
        for creating buys and sells
    :param commission: float - cost pet buy or sell
    :param start_date: string - start date for backtest with
        format ``YYYY-MM-DD HH:MM:SS``
    :param end_date: end date for backtest with
        format ``YYYY-MM-DD HH:MM:SS``
    :param config_file: path to a json file
        containing custom algorithm object
        member values
    :param raise_on_err: boolean - set this to ``False`` on prod
        to ensure exceptions do not interrupt services.
        With the default (``True``) any exceptions from the library
        and your own algorithm are sent back out immediately exiting
        the backtest.
    """
    module_name = mod_path.split('/')[-1]
    loader = importlib.machinery.SourceFileLoader(
        module_name, mod_path)
    mod = types.ModuleType(loader.name)
    loader.exec_module(mod)

    use_start_date = start_date
    use_end_date = end_date
    if not use_end_date:
        end_date = datetime.datetime.utcnow()
        use_end_date = end_date.strftime(
            sa_consts.COMMON_TICK_DATE_FORMAT)
    if not use_start_date:
        start_date = end_date - datetime.timedelta(days=75)
        use_start_date = start_date.strftime(
            sa_consts.COMMON_TICK_DATE_FORMAT)

    algo_req = build_algo_request.build_algo_request(
        ticker=ticker,
        balance=balance,
        commission=commission,
        start_date=use_start_date,
        end_date=use_end_date,
        label=name)
    for member in inspect.getmembers(mod):
        if module_name in str(member):
            log.info(
                'start {} with {}'.format(
                    name,
                    member[1]))
            # heads up - logging this might have passwords in the algo_req
            # log.debug(
            #     '{} algorithm request: {}'.format(
            #         name,
            #         algo_req))
            algo_req['name'] = name
            custom_algo = member[1](
                **algo_req)
            log.debug(
                '{} run'.format(
                    name))
            algo_res = run_algo.run_algo(
                algo=custom_algo,
                raise_on_err=raise_on_err,
                **algo_req)
            algo_res['algo'] = custom_algo
            log.info(
                'done algorithm: {} with name={} '
                'from file={}'.format(
                    module_name,
                    name,
                    mod_path))
            return algo_res
    # end of looking over the class definition but did not find it

    log.error(
        'missing a derive analysis_engine.algo.BaseAlgo '
        'class in the module file={} for ticker={} algo_name={}'.format(
            mod_path,
            ticker,
            name))

    return build_result.build_result(
        status=sa_consts.ERR,
        rec=None)
# end of run_custom_algo
