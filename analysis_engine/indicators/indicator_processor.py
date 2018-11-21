"""
"""

import os
import json
import analysis_engine.indicators.build_indicator_node as build_indicator
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


class IndicatorProcessor:
    """IndicatorProcessor"""

    def __init__(
            self,
            config_dict,
            config_file=None,
            ticker=None,
            label=None):
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
        """

        self.config_dict = config_dict
        if not self.config_dict:
            if config_file:
                if not os.path.exists(config_file):
                    raise Exception(
                        'Unable to find config_file: {}'.format(
                            config_file))
                # end of if file does not exist on the disk
                self.config_dict = json.loads(
                    open(config_file, 'r').read())
        # end of trying to ensure the config_dict is ready

        if not self.config_dict:
            raise Exception(
                'Missing either a config_dict or a config_file to '
                'create the IndicatorProcessor')

        self.ticker = ticker
        self.ind_dict = {}
        self.num_indicators = len(self.config_dict.get(
            'indicators',
            []))
        self.label = label
        if not self.label:
            self.label = 'idprc'

        self.build_indicators_for_config(
            config_dict=self.config_dict)
    # end of __init__

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

        log.info(
            '{} start - building indicators={}'.format(
                self.label,
                self.num_indicators))

        for idx, node in enumerate(config_dict['indicators']):
            # this will throw on errors parsing to make
            # it easeir to debug
            # before starting the algo and waiting for an error
            # in the middle of a backtest
            new_node = build_indicator.build_indicator_node(
                node=node)
            if new_node:
                self.ind_dict[new_node['name']] = new_node
            else:
                raise Exception(
                    '{} - failed creating indicator {} node={}'.format(
                        self.label,
                        idx,
                        node))
        # end for all indicators in the config

        log.info(
            '{} done - built={} from indicators={}'.format(
                self.label,
                len(self.ind_dict),
                self.num_indicators))
    # end of build_indicators_for_config

# end of IndicatorProcessor
