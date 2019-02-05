"""
Indicator Processor

- v1 Indicator type: ``supported``
    Binary decision support on buys and sells
    This is like an alert threshold that is ``on`` or ``off``

- v2 Indicator type: ``not supported``
    Support for buy or sell value range
    This is like an alert threshold between a ``lower``
    and ``upper`` bound
"""

import os
import json
import analysis_engine.consts as ae_consts
import analysis_engine.indicators.build_indicator_node as build_indicator
import analysis_engine.indicators.load_indicator_from_module as load_indicator
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


class IndicatorProcessor:
    """IndicatorProcessor"""

    def __init__(
            self,
            config_dict,
            config_file=None,
            ticker=None,
            label=None,
            verbose=False,
            verbose_indicators=False):
        """__init__

        Algorithm's use the ``IndicatorProcessor`` to drive
        how the underlying indicators are created and configured
        to determine buy and sell conditions. Create an
        IndicatorProcessor by passing in a valid:

        ``config_dict`` or a path to a local `config_file``

        Please refer to the `included algorithm config file <http
        s://github.com/AlgoTraders/stock-analysis-engine/blob/mas
        ter/tests/algo_configs/test_5_days_ahead.json>`__ for
        more details on how to create your own.

        :param config_dict: - dictionary for creating
            indicators and rules for buy/sell conditions
            and parameters for each indicator
        :param config_file: path to a json file
            containing custom algorithm object
            member values (like indicator configuration and
            predict future date units ahead for a backtest)
        :param ticker: optional - single ticker string
            indicators should focus on math, fundamentals,
            sentiment and other data, but the context about
            which ticker this is for should hopefully be
            abstracted from how an indicator predicts
            buy and sell conditions
        :param label: optional - string log tracking
            this class in the logs (usually just the algo
            name is good enough to help debug issues
            when running distributed)
        :param verbose: optional - bool for more logging
            (default is ``False``)
        :param verbose_indicators: optional - bool for more logging
            for all indicators managed by this ``IndicatorProcessor``
            (default is ``False``)
        """

        self.config_dict = config_dict
        if not self.config_dict:
            if config_file:
                if not os.path.exists(config_file):
                    raise Exception(
                        f'Unable to find config_file: {config_file}')
                # end of if file does not exist on the disk
                self.config_dict = json.loads(
                    open(config_file, 'r').read())
        # end of trying to ensure the config_dict is ready

        if not self.config_dict:
            raise Exception(
                'Missing either a config_dict or a config_file to '
                'create the IndicatorProcessor')

        self.last_ind_obj = None
        self.ticker = ticker
        self.ind_dict = {}
        self.num_indicators = len(self.config_dict.get(
            'indicators',
            []))
        self.label = label
        if not self.label:
            self.label = 'idprc'

        self.latest_report = {}
        self.reports = []

        self.verbose = verbose
        self.verbose_indicators = verbose_indicators

        if not self.verbose_indicators:
            self.verbose_indicators = self.config_dict.get(
                'verbose_indicators',
                False)

        self.build_indicators_for_config(
            config_dict=self.config_dict)
    # end of __init__

    def get_last_ind_obj(
            self):
        """get_last_ind_obj"""
        return self.last_ind_obj
    # end of get_last_ind_obj

    def get_latest_report(
            self,
            algo_id=None,
            ticker=None,
            dataset=None):
        """get_latest_report

        Return the latest report as a method that can be
        customized by a derived class from the
        ``IndicatorProcessor``

        :param algo_id: optional - string -
            algo identifier label for debugging datasets
            during specific dates
        :param ticker: optional - string - ticker
        :param dataset: optional - a dictionary of
            identifiers (for debugging) and
            multiple pandas ``pd.DataFrame`` objects. Dictionary where keys
            represent a label from one of the data sources (``IEX``,
            ``Yahoo``, ``FinViz`` or other). Here is the supported
            dataset structure for the process method:
        """

        return self.latest_report
    # end of get_latest_report

    def get_num_indicators(
            self):
        """get_num_indicators"""
        return self.num_indicators
    # end of get_num_indicators

    def get_label(
            self):
        """get_label"""
        return self.label
    # end of get_label

    def get_indicators(
            self):
        """get_indicators"""
        return self.ind_dict
    # end of get_indicators

    def build_indicators_for_config(
            self,
            config_dict):
        """build_indicators_for_config

        Convert the dictionary into an internal dictionary
        for quickly processing results

        :param config_dict: initailized algorithm config
            dictionary
        """

        if 'indicators' not in config_dict:
            log.error('missing "indicators" list in the config_dict')
            return

        if self.verbose:
            log.info(
                f'{self.label} start - '
                f'building indicators={self.num_indicators}')

        for idx, node in enumerate(config_dict['indicators']):
            percent_done = ae_consts.get_percent_done(
                progress=(idx + 1),
                total=self.num_indicators)
            percent_label = (
                f'ticker={self.ticker} {percent_done} '
                f'{idx+1}/{self.num_indicators}')
            # this will throw on errors parsing to make
            # it easeir to debug
            # before starting the algo and waiting for an error
            # in the middle of a backtest
            new_node = build_indicator.build_indicator_node(
                node=node)
            if new_node:
                indicator_key_name = new_node['report']['name']
                if self.verbose:
                    log.info(
                        f'{self.label} - '
                        f'preparing indicator={indicator_key_name} '
                        f'node={new_node} {percent_label}')
                else:
                    log.debug(
                        f'{self.label} - '
                        f'preparing indicator={indicator_key_name} '
                        f'{percent_label}')
                self.ind_dict[indicator_key_name] = new_node
                self.ind_dict[indicator_key_name]['obj'] = None

                base_class_indicator = node.get(
                    'base_class',
                    'BaseIndicator')

                self.ind_dict[indicator_key_name]['obj'] = \
                    load_indicator.load_indicator_from_module(
                        module_name=new_node['report']['module_name'],
                        path_to_module=new_node['report']['path_to_module'],
                        ind_dict=new_node,
                        log_label=indicator_key_name,
                        base_class_module_name=base_class_indicator,
                        verbose=self.verbose_indicators)

                log.debug(
                    f'{self.label} - '
                    f'created indicator={indicator_key_name} '
                    f'{percent_label}')
            else:
                raise Exception(
                    f'{self.label} - '
                    f'failed creating indicator {idx} node={node}')
        # end for all indicators in the config

        if self.verbose:
            log.info(
                f'{self.label} done - '
                f'built={len(self.ind_dict)} '
                f'from indicators={self.num_indicators}')
    # end of build_indicators_for_config

    def process(
            self,
            algo_id,
            ticker,
            dataset):
        """process

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param dataset: a dictionary of identifiers (for debugging) and
            multiple pandas ``pd.DataFrame`` objects. Dictionary where keys
            represent a label from one of the data sources (``IEX``,
            ``Yahoo``, ``FinViz`` or other). Here is the supported
            dataset structure for the process method:
        """
        self.latest_report = {
            'id': algo_id,
            'ticker': ticker,
            'buys': [],
            'sells': [],
            'num_indicators': self.num_indicators,
            'date': dataset.get('date', None)
        }
        for idx, ind_id in enumerate(self.ind_dict):
            ind_node = self.ind_dict[ind_id]
            ind_obj = ind_node['obj']
            percent_done = ae_consts.get_percent_done(
                progress=(idx + 1),
                total=self.num_indicators)
            percent_label = (
                f'ticker={self.ticker} {percent_done} '
                f'{idx+1}/{self.num_indicators}')
            ind_obj.reset_internals()
            if self.verbose:
                log.info(
                    f'{self.label} - {ind_obj.get_name()} '
                    f'start {percent_label}')
            # this will throw on errors to help with debugging
            self.last_ind_obj = ind_obj
            ind_obj.handle_subscribed_dataset(
                algo_id=algo_id,
                ticker=ticker,
                dataset=dataset)
            new_report = ind_obj.get_report()
            if self.verbose:
                log.info(
                    f'{self.label} - {ind_obj.get_name()} '
                    f'end {percent_label} '
                    f'report: {ae_consts.ppj(new_report)}')
            self.latest_report.update(new_report)

            is_buy_value = ind_obj.is_buy
            is_sell_value = ind_obj.is_sell

            """"
            v1 indicator type: supported
            binary decision support on buys and sells
            (like an alert threshold that is on or off)

            v2 indicator type: not supported
            support for buy/sell value range
            (like an alert threshold between a lower and upper bound)
            """
            if (hasattr(ind_obj, 'is_buy') and
                    hasattr(ind_obj, 'is_sell')):
                is_buy_value = ind_obj.is_buy
                is_sell_value = ind_obj.is_sell

            if is_buy_value == ae_consts.INDICATOR_BUY:
                self.latest_report['buys'].append({
                    'cell': idx,
                    'name': ind_obj.get_name(),
                    'id': ind_id,
                    'report': new_report})
            elif is_sell_value == ae_consts.INDICATOR_SELL:
                self.latest_report['sells'].append({
                    'cell': idx,
                    'name': ind_obj.get_name(),
                    'id': ind_id,
                    'report': new_report})
        # end of for all indicators

        self.reports.append(self.latest_report)

        # allow derived indicator processors to build custom reports
        return self.get_latest_report(
            algo_id=algo_id,
            ticker=ticker,
            dataset=dataset)
    # end of process

# end of IndicatorProcessor
