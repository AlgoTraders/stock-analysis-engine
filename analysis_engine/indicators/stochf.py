"""
Custom Stochastics - STOCHF

https://www.investopedia.com/terms/s/stochasticoscillator.asp

Momentum

**Supported environment variables**

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

import analysis_engine.ae_talib as ae_talib
import analysis_engine.consts as ae_consts
import analysis_engine.indicators.base_indicator as base_indicator


class IndicatorSTOCHF(base_indicator.BaseIndicator):
    """IndicatorSTOCHF"""

    def __init__(
            self,
            **kwargs):
        """__init__

        Custom indicator example for showing a
        ``STOCHF``
        within an algo for analyzing intraday minute datasets

        Please refer to the `analysis_engine.indicators.base_indicator.Ba
        seIndicator source code for the latest supported parameters <ht
        tps://github.com/AlgoTraders/stock-analysis-engine/blob/master/
        analysis_engine/indicators/base_indicator.py>`__

        :param kwargs: keyword arguments
        """
        super().__init__(**kwargs)
    # end of __init__

    def get_configurables(
            self,
            **kwargs):
        """get_configurables

        helper for setting up algorithm configs for this indicator
        and programmatically set the values based off the domain
        rules

        .. code-block:: python

            from analysis_engine.indicators.stochf \
                import IndicatorSTOCHF
            ind = IndicatorSTOCHF(config_dict={
                    'verbose': True
                }).get_configurables()

        :param kwargs: keyword args dictionary
        """
        self.ind_confs = []

        # common:
        self.build_base_configurables(
            ind_type='momentum',
            category='technical',
            uses_data=self.config.get(
                'uses_data',
                'minute'),
            version=1)

        # custom:
        self.ind_confs.append(self.build_configurable_node(
            name='num_points',
            conf_type='int',
            max_value=200,
            min_value=2,
            default_value=100,
            inc_interval=1))
        self.ind_confs.append(self.build_configurable_node(
            name='buy_below_percent',
            conf_type='percent',
            min_value=3.0,
            max_value=100.0,
            default_value=5.0,
            inc_interval=1))
        self.ind_confs.append(self.build_configurable_node(
            name='buy_above_percent',
            conf_type='percent',
            min_value=3.0,
            max_value=100.0,
            default_value=5.0,
            inc_interval=1))
        self.ind_confs.append(self.build_configurable_node(
            name='sell_below_percent',
            conf_type='percent',
            min_value=3.0,
            max_value=100.0,
            default_value=5.0,
            inc_interval=1))
        self.ind_confs.append(self.build_configurable_node(
            name='sell_above_percent',
            conf_type='percent',
            min_value=3.0,
            max_value=100.0,
            default_value=5.0,
            inc_interval=1))
        self.ind_confs.append(self.build_configurable_node(
            name='fastk_period',
            conf_type='int',
            min_value=1,
            max_value=40,
            default_value=1,
            inc_interval=2))
        self.ind_confs.append(self.build_configurable_node(
            name='fastd_period',
            conf_type='int',
            min_value=1,
            max_value=40,
            default_value=1,
            inc_interval=2))
        self.ind_confs.append(self.build_configurable_node(
            name='fastd_matype',
            conf_type='int',
            min_value=0,
            max_value=0,
            default_value=0,
            inc_interval=0))

        # output / reporting:
        self.ind_confs.append(self.build_configurable_node(
            name='fastk_value',
            conf_type='float',
            is_output_only=True))
        self.ind_confs.append(self.build_configurable_node(
            name='fastd_value',
            conf_type='float',
            is_output_only=True))
        self.ind_confs.append(self.build_configurable_node(
            name='amount_to_close',
            conf_type='float',
            is_output_only=True))
        self.ind_confs.append(self.build_configurable_node(
            name='close',
            conf_type='float',
            is_output_only=True))
        self.ind_confs.append(self.build_configurable_node(
            name='percent_value',
            conf_type='percent',
            is_output_only=True))

        default_values_dict = {}
        for node in self.ind_confs:
            name = node['name']
            default_value = node.get(
                'default',
                None)
            default_values_dict[name] = default_value

        use_file = None
        try:
            if __file__:
                use_file = __file__
        except Exception:
            use_file = None

        self.starter_dict = {
            'name': self.__class__.__name__.lower().replace(
                'indicator',
                ''),
            'module_path': use_file,
            'category': default_values_dict.get(
                'category',
                'momentum'),
            'type': default_values_dict.get(
                'type',
                'technical'),
            'uses_data': default_values_dict.get(
                'uses_data',
                'minute'),
            'verbose': default_values_dict.get(
                'verbose',
                False)
        }
        self.starter_dict.update(default_values_dict)

        self.lg(
            f'configurables={ae_consts.ppj(self.ind_confs)} for '
            f'class={self.__class__.__name__} in file={use_file} '
            f'starter:\n {ae_consts.ppj(self.starter_dict)}')

        return self.ind_confs
    # end of get_configurables

    def get_starter_dict(
            self):
        if not self.starter_dict:
            self.get_configurables()
        return self.starter_dict
    # end of get_starter_dict

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
        :param dataset: dictionary of ``pandas.DataFrame(s)`` to process
        """

        # set the algo config indicator 'uses_data' to 'day' or 'minute'
        df_status, self.use_df = self.get_subscribed_dataset(
            dataset=dataset)

        if df_status == ae_consts.EMPTY:
            self.lg('process end - no data found')
            return

        # notice the self.num_points is now a member variable
        # because the BaseIndicator class's __init__
        # converts any self.config keys into useable
        # member variables automatically in your derived class
        self.lg(
            f'process - num_points={self.num_points} '
            f'df={len(self.use_df.index)}')
        """
        fastk, fastd = STOCHF(
            high,
            low,
            close,
            fastk_period=5,
            fastd_period=3,
            fastd_matype=0)
        """
        num_records = len(self.use_df.index)
        if num_records > self.num_points:
            cur_value = self.use_df['close'].iloc[-1]
            first_date = self.use_df['date'].iloc[0]
            end_date = self.use_df['date'].iloc[-1]
            start_row = num_records - self.num_points
            self.use_df = self.use_df[start_row:num_records]
            """
            for idx, row in self.use_df[start_row:-1].iterrows():
                high = row['high']
                low = row['low']
                open_val = row['open']
                close = row['close']
                row_date = row['date']
                self.lg(
                    f'{row_date} - high={high}, low={low}, '
                    f'close={close}, period={self.num_points}')
            """
            highs = self.use_df['high'].values
            lows = self.use_df['low'].values
            closes = self.use_df['close'].values

            (self.fastk_value,
             self.fastd_value) = ae_consts.to_f(ae_talib.STOCHF(
                high=highs,
                low=lows,
                close=closes,
                fastk_period=self.fastk_period,
                fastd_period=self.fastd_period,
                fastd_matype=self.fastd_matype)[-1])

            """
            Determine a buy or a sell as a label
            """

            if cur_value <= 0:
                self.lg(f'invalid current_value={cur_value}')
                return

            self.close = cur_value
            self.amount_to_close = ae_consts.to_f(
                cur_value - self.adx_value)
            self.percent_value = ae_consts.to_f(
                self.amount_to_close / cur_value * 100.0)

            self.is_buy = ae_consts.INDICATOR_IGNORE
            self.is_sell = ae_consts.INDICATOR_IGNORE

            if (self.buy_above_percent != -1 and
                    self.percent_value > self.buy_above_percent):
                self.is_buy = ae_consts.INDICATOR_BUY
            elif (self.buy_below_percent != -1 and
                    self.percent_value > self.buy_below_percent):
                self.is_buy = ae_consts.INDICATOR_BUY

            if (self.sell_above_percent != -1 and
                    self.percent_value > self.sell_above_percent):
                self.is_sell = ae_consts.INDICATOR_SELL
            elif (self.sell_below_percent != -1 and
                    self.percent_value > self.sell_below_percent):
                self.is_sell = ae_consts.INDICATOR_SELL

            self.lg(
                f'process end - {first_date} to {end_date} '
                f'buy_below={self.buy_below_percent} '
                f'buy_above={self.buy_above_percent} is_buy={self.is_buy} '
                f'sell_below={self.sell_below_percent} '
                f'sell_above={self.sell_above_percent} is_sell={self.is_sell}')
        else:
            self.lg('process end')
    # end of process

    def reset_internals(
            self):
        """reset_internals"""
        self.is_buy = ae_consts.INDICATOR_RESET
        self.is_sell = ae_consts.INDICATOR_RESET
    # end of reset_internals

# end of IndicatorSTOCHF


def get_indicator(
        **kwargs):
    """get_indicator

    Make sure to define the ``get_indicator`` for your custom
    algorithms to work as a backup with the ``sa.py`` tool...
    Not anticipating issues, but if we do with importlib
    this is the backup plan.

    Please file an issue if you see something weird and would like
    some help:
    https://github.com/AlgoTraders/stock-analysis-engine/issues

    :param kwargs: dictionary of keyword arguments
    """
    print('getting indicator')
    return IndicatorSTOCHF(**kwargs)
# end of get_indicator
