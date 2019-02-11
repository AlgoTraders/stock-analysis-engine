"""
Algo data helper for mapping indicator category
to an integer label value for downstream dataset predictions
"""

import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def get_category_as_int(
        node,
        label=None):
    """get_category_as_int

    Helper for converting feature labels to numeric values

    :param node: convert the dictionary's ``category``
        string to the integer mapped value
    """
    if not label:
        label = 'get_category_as_int'
    ind_category_str = node.get(
        'category',
        'momentum')
    if not ind_category_str:
        return ae_consts.INDICATOR_CATEGORY_UNKNOWN
    elif ind_category_str == 'momentum':
        return ae_consts.INDICATOR_CATEGORY_MOMENTUM
    elif ind_category_str == 'overlap':
        return ae_consts.INDICATOR_CATEGORY_OVERLAP
    elif ind_category_str == 'price':
        return ae_consts.INDICATOR_CATEGORY_PRICE
    elif ind_category_str == 'volume':
        return ae_consts.INDICATOR_CATEGORY_VOLUME
    elif ind_category_str == 'volatility':
        return ae_consts.INDICATOR_CATEGORY_VOLATILITY
    elif ind_category_str == 'single_call':
        return ae_consts.INDICATOR_CATEGORY_SINGLE_CALL
    elif ind_category_str == 'single_put':
        return ae_consts.INDICATOR_CATEGORY_SINGLE_PUT
    elif ind_category_str == 'bull_call':
        return ae_consts.INDICATOR_CATEGORY_BULL_CALL
    elif ind_category_str == 'bear_put':
        return ae_consts.INDICATOR_CATEGORY_BEAR_PUT
    elif ind_category_str == 'quarterly':
        return ae_consts.INDICATOR_CATEGORY_QUARTERLY
    elif ind_category_str == 'yearly':
        return ae_consts.INDICATOR_CATEGORY_YEARLY
    elif ind_category_str == 'income_statement':
        return ae_consts.INDICATOR_CATEGORY_INCOME_STMT
    elif ind_category_str == 'cash_flow':
        return ae_consts.INDICATOR_CATEGORY_CASH_FLOW
    elif ind_category_str == 'balance_sheet':
        return ae_consts.INDICATOR_CATEGORY_BALANCE_SHEET
    elif ind_category_str == 'press_release':
        return ae_consts.INDICATOR_CATEGORY_PRESS_RELEASE
    elif ind_category_str == 'news':
        return ae_consts.INDICATOR_CATEGORY_NEWS
    elif ind_category_str == 'earnings':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'splits':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'reverse_splits':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'distributions':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'spinoffs':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'merger_acq':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'exchange_inclusion':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'exchange_exclusion':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'clinical_trial_positive':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'clinical_trial_negative':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'short_sellers':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'custom':
        return ae_consts.INDICATOR_CATEGORY_CUSTOM
    elif ind_category_str == 'news':
        return ae_consts.INDICATOR_CATEGORY_NEWS
    elif ind_category_str == 'earnings':
        return ae_consts.INDICATOR_CATEGORY_EARNINGS
    elif ind_category_str == 'csuite':
        return ae_consts.INDICATOR_CATEGORY_CSUITE
    elif ind_category_str == 'splits':
        return ae_consts.INDICATOR_CATEGORY_SPLITS
    elif ind_category_str == 'reverse_splits':
        return ae_consts.INDICATOR_CATEGORY_REVERSE_SPLITS
    elif ind_category_str == 'distributions':
        return ae_consts.INDICATOR_CATEGORY_DISTRIBUTIONS
    elif ind_category_str == 'spinoffs':
        return ae_consts.INDICATOR_CATEGORY_SPINOFFS
    elif ind_category_str == 'merger_acq':
        return ae_consts.INDICATOR_CATEGORY_MERGER_ACQ
    elif ind_category_str == 'exchange_inclusion':
        return ae_consts.INDICATOR_CATEGORY_EXCHANGE_INCLUSION
    elif ind_category_str == 'exchange_exclusion':
        return ae_consts.INDICATOR_CATEGORY_EXCHANGE_EXCLUSION
    elif ind_category_str == 'trial_positive':
        return ae_consts.INDICATOR_CATEGORY_TRIAL_POSITIVE
    elif ind_category_str == 'trial_negative':
        return ae_consts.INDICATOR_CATEGORY_TRIAL_NEGATIVE
    elif ind_category_str == 'short_sellers':
        return ae_consts.INDICATOR_CATEGORY_SHORT_SELLERS
    elif ind_category_str == 'real_estate':
        return ae_consts.INDICATOR_CATEGORY_REAL_ESTATE
    elif ind_category_str == 'housing':
        return ae_consts.INDICATOR_CATEGORY_HOUSING
    elif ind_category_str == 'pipeline':
        return ae_consts.INDICATOR_CATEGORY_PIPELINE
    elif ind_category_str == 'construction':
        return ae_consts.INDICATOR_CATEGORY_CONSTRUCTION
    elif ind_category_str == 'fed':
        return ae_consts.INDICATOR_CATEGORY_FED
    else:
        if label:
            log.error(
                f'{label} - unsupported indicator '
                f'uses_dataset={ind_category_str} defaulting to "unknown"')
        else:
            log.error(
                'unsupported indicator '
                f'uses_dataset={ind_category_str} defaulting to "unknown"')
        return ae_consts.INDICATOR_CATEGORY_UNKNOWN
    # end of supported indicator dataset types
# end of get_category_as_int
