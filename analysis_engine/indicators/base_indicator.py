"""
Base Indicator Class for deriving your own indicators
to use within an ``analysis_engine.indicators.in
dicator_processor.IndicatorProcessor``
"""

import uuid
import pandas as pd
import logging
import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils


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

        :param config_dict: dictionary for this indicator
        :param name: name of the indicator
        :param path_to_module: work in progress -
            this will allow loading indicators from
            outside the repo like the derived algorithm
            classes
        :param verbose: optional - bool for toggling more logs
        """
        self.name = name
        self.log = log_utils.build_colorized_logger(
            name=name)

        self.config = config_dict
        self.path_to_module = path_to_module
        self.verbose = verbose

        if not self.config:
            raise Exception(
                'please provide a config_dict for loading '
                'the buy and sell rules for this indicator')

        if not self.verbose:
            self.verbose = self.config.get(
                'verbose',
                False)

        if not self.name:
            self.name = 'ind_{}'.format(
                str(uuid.uuid4()).replace('-', ''))

        self.starter_dict = None
        self.previous_df = self.config.get(
            'previous_df',
            None)
        self.name_of_df = self.config.get(
            'uses_data',
            None)
        self.uses_data = self.name_of_df
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
        self.ind_uses_data = self.metrics.get(
            'ind_uses_data',
            ae_consts.INDICATOR_USES_DATA_ANY)
        self.dataset_df_str = self.config.get(
            'dataset_df',
            None)

        self.report_key_prefix = self.report.get(
            'report_key_prefix',
            self.name)

        # this should be mostly numeric values
        # to allow converting to an AI-ready dataset
        # once the algorithm finishes
        self.report_dict = {
            'type': self.ind_type,
            'category': self.ind_category,
            'uses_data': self.ind_uses_data
        }

        self.report_ignore_keys = self.config.get(
            'report_ignore_keys',
            ae_consts.INDICATOR_IGNORED_CONIGURABLE_KEYS)
        self.use_df = pd.DataFrame(
            ae_consts.EMPTY_DF_LIST)
        self.configurables = self.config
        self.ind_confs = []
        self.convert_config_keys_to_members()
    # end of __init__

    def get_config(
            self):
        """get_config"""
        pruned_config = {}

        # remove the obj
        remove_keys = [
            'obj'
        ]
        for k in self.config:
            if k not in remove_keys:
                pruned_config[k] = self.config[k]
        return pruned_config
    # end of get_config

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

    def build_configurable_node(
            self,
            name,
            conf_type,
            current_value=None,
            default_value=None,
            max_value=None,
            min_value=None,
            is_output_only=False,
            inc_interval=None,
            notes=None,
            **kwargs):
        """build_configurable_node

        Helper for building a single configurable type
        node for programmatically creating algo configs

        :param name: name of the member configurable
        :param conf_type: string - configurable type
        :param current_value: optional - current value
        :param default_value: optional - default value
        :param max_value: optional - maximum value
        :param min_value: optional - minimum value
        :param is_output_only: optional - bool for setting
            the input parameter as an output-only value
            (default is ``False``)
        :param inc_interval: optional - float value
            for controlling how the tests should increment
            while walking between the ``min_value`` and the
            ``max_value``
        :param notes: optional - string notes
        :param kwargs: optional - derived keyword args dictionary
        """
        node = {
            'name': name,
            'type': conf_type,
            'value': current_value,
            'default': default_value,
            'max': max_value,
            'min': min_value,
            'is_output_only': is_output_only,
            'inc_interval': inc_interval,
            'notes': notes
        }
        for k in kwargs:
            node[k] = kwargs[k]
        return node
    # end of build_configurable_node

    def build_base_configurables(
            self,
            ind_type='momentum',
            category='technical',
            uses_data='minute',
            version=1):
        """build_base_configurables

        :param ind_type: string indicator type
        :param category: string indicator category
        :param uses_data: string indicator
            usess this type of data
        :param version: integer for building
            configurables for the testing
            generation version
        """
        self.ind_confs = []
        self.ind_confs.append(self.build_configurable_node(
            name='category',
            conf_type='str',
            default_value=category,
            is_output_only=True))
        self.ind_confs.append(self.build_configurable_node(
            name='type',
            conf_type='str',
            default_value=ind_type,
            is_output_only=True))
        self.ind_confs.append(self.build_configurable_node(
            name='uses_data',
            conf_type='str',
            default_value=self.config.get(
                'uses_data',
                uses_data),
            is_output_only=True))

        if version == 1:
            self.ind_confs.append(self.build_configurable_node(
                name='is_buy',
                conf_type='int',
                is_output_only=True))
            self.ind_confs.append(self.build_configurable_node(
                name='is_sell',
                conf_type='int',
                is_output_only=True))
    # end of build_base_configurables

    def get_configurables(
            self,
            **kwargs):
        """get_configurables

        **Derive this in your indicators**

        This is used as a helper for setting up algorithm
        configs for this indicator and to programmatically set
        the values based off the domain rules

        :param kwargs: optional keyword args
        """
        self.ind_confs = []

        self.lg(
            'configurables={} for class={}'.format(
                ae_consts.ppj(self.ind_confs),
                self.__class__.__name__))

        return self.ind_confs
    # end of get_configurables

    def set_configurables(
            self,
            config_dict):
        """set_configurables

        :param config_dict: indicator config dictionary
        """
        self.configurables = config_dict
        return self.configurables
    # end of set_configurables

    def lg(
            self,
            msg,
            level=logging.INFO):
        """lg

        Log only if the indicator has ``self.verbose``
        set to ``True`` or if the ``level == logging.CRITICAL`` or
        ``level = logging.ERROR`` otherwise no logs

        :param msg: string message to log
        :param level: set the logging level
            (default is ``logging.INFO``)
        """
        if self.verbose:
            if level == logging.INFO:
                self.log.info(msg)
                return
            elif level == logging.ERROR:
                self.log.error(msg)
                return
            elif level == logging.DEBUG:
                self.log.debug(msg)
                return
            elif level == logging.WARN:
                self.log.warn(msg)
                return
            elif level == logging.CRITICAL:
                self.log.critical(msg)
                return
        else:
            if level == logging.ERROR:
                self.log.error(msg)
                return
            elif level == logging.CRITICAL:
                self.log.critical(msg)
                return
    # end lg

    def get_report_prefix(
            self):
        """get_report_prefix"""
        return self.report_key_prefix
    # end of get_report_prefix

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
                str(uuid.uuid4()).replace('-', ''))
        # end of building a key to prevent stomping data

        return report_key
    # end of build_report_key

    def get_report(
            self,
            verbose=False):
        """get_report

        Get the indicator's current output node
        that is used for the trading performance report
        generated at the end of the algorithm

        .. note:: the report dict should mostly be numeric
            types to enable AI predictions after removing
            non-numeric columns

        :param verbose: optional - boolean for toggling
            to show the report
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

        buy_value = None
        sell_value = None

        for key in self.configurables:

            is_valid = True
            if key in self.report_ignore_keys:
                is_valid = False
            elif key not in self.__dict__:
                is_valid = False

            if is_valid:
                report_key = self.build_report_key(
                    key,
                    prefix_key=report_prefix_key_name,
                    key_type='conf',
                    cur_report_dict=cur_report_dict)

                use_value = None
                if key == 'is_buy':
                    buy_value = self.__dict__[key]
                    if buy_value:
                        use_value = \
                            ae_consts.INDICATOR_ACTIONS[buy_value]
                    else:
                        use_value = \
                            ae_consts.INT_INDICATOR_NOT_PROCESSED
                elif key == 'is_sell':
                    sell_value = self.__dict__[key]
                    if sell_value:
                        use_value = \
                            ae_consts.INDICATOR_ACTIONS[sell_value]
                    else:
                        use_value = \
                            ae_consts.INT_INDICATOR_NOT_PROCESSED
                else:
                    use_value = self.__dict__[key]
                # end of deciding value

                cur_report_dict[report_key] = use_value
            # if valid

        # end of all configurables for this indicator

        if verbose or self.verbose:
            self.lg(
                'indicator={} '
                'report={} '
                'buy={} sell={}'.format(
                    self.name,
                    ae_consts.ppj(cur_report_dict),
                    buy_value,
                    sell_value))

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

    def get_dataset_by_name(
            self,
            dataset,
            dataset_name):
        """get_dataset_by_name

        Method for getting just a dataset
        by the dataset_name`` inside the cached
        ``dataset['data']`` dictionary of ``pd.Dataframe(s)``

        :param dataset: cached dataset value
            that holds the dictionaries: ``dataset['data']``
        :param dataset_name: optional - name of the
            supported ``pd.DataFrame`` that is in the
            cached ``dataset['data']`` dictionary
            of dataframes
        """
        return dataset['data'].get(
            dataset_name,
            pd.DataFrame(ae_consts.EMPTY_DF_LIST))
    # end of get_dataset_by_name

    def get_subscribed_dataset(
            self,
            dataset,
            dataset_name=None):
        """get_subscribed_dataset

        Method for getting just the subscribed dataset
        else use the ``dataset_name`` argument dataset

        :param dataset: cached dataset value
            that holds the dictionaries: ``dataset['data']``
        :param dataset_name: optional - name of the
            supported ``pd.DataFrame`` that is in the
            cached ``dataset['data']`` dictionary
            of dataframes
        """
        ret_df = None
        if dataset_name:
            ret_df = dataset['data'].get(
                dataset_name,
                pd.DataFrame(ae_consts.EMPTY_DF_LIST))
        else:
            ret_df = dataset['data'].get(
                self.name_of_df,
                pd.DataFrame(ae_consts.EMPTY_DF_LIST))

        if hasattr(ret_df, 'index'):
            return ae_consts.SUCCESS, ret_df
        else:
            return ae_consts.EMPTY, ret_df
    # end of get_subscribed_dataset

    def reset_internals(
            self,
            **kwargs):
        """reset_internals

        Support a cleanup action before indicators
        run between datasets. Derived classes can
        implement custom cleanup actions that need
        to run before each ``IndicatorProcessor.process()``
        call is run on the next cached dataset

        :param kwargs: keyword args dictionary
        """
        return ae_consts.SUCCESS
    # end of reset_internals

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
        :param dataset: dictionary of ``pd.DataFrame(s)`` to process
        """

        # certain datasets like minutes or options may
        # want to refer to the previous dataset
        self.previous_df = dataset

        # call derived class's process()
        self.process(
            algo_id=algo_id,
            ticker=ticker,
            dataset=dataset)
    # end of handle_subscribed_dataset

    def process(
            self,
            algo_id,
            ticker,
            dataset):
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
        :param dataset: dictionary of ``pd.DataFrame(s)`` to process
        """
        self.lg(
            '{} BASE_IND process - start'.format(
                self.name))
        self.lg(
            '{} BASE_IND process - end'.format(
                self.name))
    # end of process

# end of BaseIndicator
