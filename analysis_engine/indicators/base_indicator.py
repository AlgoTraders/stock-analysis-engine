"""
Base Indicator Class for deriving your own indicators
to use within an ``analysis_engine.indicators.in
dicator_processor.IndicatorProcessor``
"""

import uuid
import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


class BaseIndicator:
    """BaseIndicator"""

    def __init__(
            self,
            config_dict,
            path_to_module=None,
            name=None,
            verbose=False):
        """__init__

        Base class for building your own indicators to work
        within an ``IndicatorProcessor``.

        Please derive the ``self.process()`` method as needed

        .. tip:: any keys passed in with ``config_dict`` will
            become class member variables that can be accessed
            and used as normal member variables within the
            derived Indicator class

        :param config_dict:
        :param name:
        :param path_to_module: work in progress -
            this will allow loading indicators from
            outside the repo like the derived algorithm
            classes
            :param verbose:
        """
        self.name = name
        self.config = config_dict
        self.path_to_module = path_to_module
        self.verbose = verbose

        if not self.config:
            raise Exception(
                'please provide a config_dict for loading '
                'the buy and sell rules for this indicator')

        if not self.name:
            self.name = 'ind_{}'.format(
                str(uuid.uuid4()).replace('-', ''))

        self.name_of_df = self.config.get(
            'uses_data',
            None)
        self.report = self.config.get(
            'report',
            {})
        self.ind_id = self.report.get(
            'id',
            self.name)
        self.metrics = self.report.get(
            'metrics',
            {})
        self.ind_type = self.metrics.get(
            'type',
            ae_consts.INDICATOR_TYPE_UNKNOWN)
        self.ind_category = self.metrics.get(
            'category',
            ae_consts.INDICATOR_CATEGORY_UNKNOWN)
        self.dataset_df_str = self.config.get(
            'dataset_df',
            None)

        # allow indicators to state the dataset_df they want
        if self.dataset_df_str:
            self.uses_data = ae_consts.get_indicator_uses_data_as_int(
                val=self.dataset_df_str)
        else:
            self.uses_data = self.metrics.get(
                'uses_data',
                ae_consts.INDICATOR_USES_DATA_UNSUPPORTED)

        if self.uses_data == ae_consts.INDICATOR_USES_DATA_UNSUPPORTED:
            raise Exception(
                'please provide a supported dataset for '
                'for indicator={} current value '
                'uses_data={} as an example the '
                'config_dict argument could be using: '
                '"dataset_df": "daily"'.format(
                    self.path_to_module,
                    self.uses_data))

        self.report_key_prefix = self.report.get(
            'report_key_prefix',
            self.name)

        # this should be mostly numeric values
        # to allow converting to an AI-ready dataset
        # once the algorithm finishes
        self.report_dict = {
            'type': self.ind_type,
            'category': self.ind_category,
            'uses_data': self.uses_data
        }

        self.report_ignore_keys = self.config.get(
            'report_ignore_keys',
            ae_consts.INDICATOR_IGNORED_CONIGURABLE_KEYS)
        self.configurables = {}

        self.convert_config_keys_to_members()
    # end of __init__

    def convert_config_keys_to_members(
            self):
        """convert_config_keys_to_members

        This converts any key in the config to
        a member variable that can be used with the
        your derived indicators like: ``self.<KEY_IN_CONFIG>``
        """
        for k in self.config:
            if k not in self.report_ignore_keys:
                self.__dict__[k] = self.config[k]
    # end of convert_config_keys_to_members

    def get_report_prefix(
            self):
        """get_report_prefix"""
        return self.report_key_prefix
    # end of get_report_prefix

    def set_configurables(
            self,
            config_dict):
        self.configurables = config_dict
        return self.configurables
    # end of set_configurables

    def build_report_key(
            self,
            key,
            prefix_key,
            key_type,
            cur_report_dict):
        """build_report_key

        :param prefix_key:
        """
        report_key = '{}_{}_{}'.format(
            prefix_key,
            key_type,
            key)
        if report_key in cur_report_dict:
            report_key = '{}_{}'.format(
                report_key,
                str(uuid.uuid4()))
        # end of building a key to prevent stomping data

        return report_key
    # end of build_report_key

    def get_report(
            self):
        """get_report

        Get the indicator's current output node
        that is used for the trading performance report
        generated at the end of the algorithm

        .. note:: the report dict should mostly be numeric
            types to enable AI predictions after removing
            non-numeric columns
        """
        cur_report_dict = {}

        # allow derived indicators to build their own report prefix
        report_prefix_key_name = self.get_report_prefix()

        for key in self.report_dict:

            is_valid = True
            if key in self.report_ignore_keys:
                is_valid = False

            if is_valid:
                report_key = self.build_report_key(
                    key,
                    prefix_key=report_prefix_key_name,
                    key_type='report',
                    cur_report_dict=cur_report_dict)
                cur_report_dict[report_key] = self.report_dict[key]
        # for all keys to output into the report

        for key in self.configurables:

            is_valid = True
            if key in self.report_ignore_keys:
                is_valid = False

            if is_valid:
                report_key = self.build_report_key(
                    key,
                    prefix_key=report_prefix_key_name,
                    key_type='conf',
                    cur_report_dict=cur_report_dict)
                cur_report_dict[report_key] = self.configurables[key]
            # if valid

        # end of all configurables for this indicator

        return cur_report_dict
    # end of get_report

    def get_path_to_module(
            self):
        """get_path_to_module"""
        return self.path_to_module
    # end of get_path_to_module

    def get_name(
            self):
        """get_name"""
        return self.name
    # end of get_name

    def handle_subscribed_dataset(
            self,
            algo_id,
            ticker,
            dataset):
        """handle_subscribed_dataset

        Filter the algorithm's ``dataset`` to just the
        dataset the indicator is set up to use as defined by
        the member variable:

        - ``self.name_of_df`` - string value like ``daily``, ``minute``

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param dataset: ``pd.DataFrame`` to process
        """
        if self.name_of_df in dataset['data']:
            found_dataset = dataset['data'].get(
                self.name_of_df,
                ae_consts.EMPTY_DF_STR)

            # call derived class's process()
            self.process(
                algo_id=algo_id,
                ticker=ticker,
                dataset_df=found_dataset)
        # if subscribed dataset is in the dataset
    # end of handle_subscribed_dataset

    def process(
            self,
            algo_id,
            ticker,
            dataset_df):
        """process

        Derive custom indicator processing to determine buy and sell
        conditions before placing orders. Just implement your own
        ``process`` method.

        Please refer to the TA Lib guides for details on building indicators:

        - Overlap Studies
          https://mrjbq7.github.io/ta-lib/func_groups/overlap_studies.html
        - Momentum Indicators
          https://mrjbq7.github.io/ta-lib/func_groups/momentum_indicators.html
        - Volume Indicators
          https://mrjbq7.github.io/ta-lib/func_groups/volume_indicators.html
        - Volatility Indicators
          https://mrjbq7.github.io/ta-lib/func_groups/volatility_indicators.html
        - Price Transform
          https://mrjbq7.github.io/ta-lib/func_groups/price_transform.html
        - Cycle Indicators
          https://mrjbq7.github.io/ta-lib/func_groups/cycle_indicators.html
        - Pattern Recognition
          https://mrjbq7.github.io/ta-lib/func_groups/pattern_recognition.html
        - Statistic Functions
          https://mrjbq7.github.io/ta-lib/func_groups/statistic_functions.html
        - Math Transform
          https://mrjbq7.github.io/ta-lib/func_groups/math_transform.html
        - Math Operators
          https://mrjbq7.github.io/ta-lib/func_groups/math_operators.html

        :param algo_id: string - algo identifier label for debugging datasets
            during specific dates
        :param ticker: string - ticker
        :param dataset_df: ``pd.DataFrame`` to process
        """
        log.info(
            '{} BASE_IND process - start'.format(
                self.name))
        log.info(
            '{} BASE_IND process - end'.format(
                self.name))
    # end of process

# end of BaseIndicator
