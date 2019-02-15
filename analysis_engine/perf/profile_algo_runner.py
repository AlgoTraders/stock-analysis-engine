"""
Example tool for to profiling algorithm performance for:

- CPU
- Memory
- Profiler
- Heatmap

The pip includes `vprof for profiling algorithm code
performance <https://github.com/nvdv/vprof>`__

#.  Start vprof in remote mode in a first terminal

    .. note:: This command will start a webapp on port ``3434``

    ::

        vprof -r -p 3434

#.  Start Profiler in a second terminal

    .. note:: This command pushes data to the webapp
        in the other terminal listening on port ``3434``

    ::

        vprof -c cm ./analysis_engine/perf/profile_algo_runner.py
"""

import datetime
import vprof.runner as perf_runner
import analysis_engine.consts as ae_consts
import analysis_engine.algo_runner as algo_runner
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(
    name='profile-algo')


def start():
    """start"""

    back_a_few_days = (
        datetime.datetime.now() - datetime.timedelta(days=3))
    start_date = back_a_few_days.strftime(
        ae_consts.COMMON_DATE_FORMAT)

    ticker = 'SPY'
    s3_bucket = 'perftests'
    s3_key = (
        f'{ticker}_{start_date}')

    algo_config = (
        f'./cfg/default_algo.json')
    history_loc = (
        f's3://{s3_bucket}/{s3_key}')

    log.info(
        f'building {ticker} trade history '
        f'start_date={start_date} '
        f'config={algo_config} '
        f'history_loc={history_loc}')

    runner = algo_runner.AlgoRunner(
        ticker=ticker,
        start_date=start_date,
        history_loc=history_loc,
        algo_config=algo_config,
        verbose_algo=False,
        verbose_processor=False,
        verbose_indicators=False)

    runner.start()
# end of start


if __name__ == '__main__':
    perf_runner.run(start, 'cm', args=(), host='0.0.0.0', port=3434)
