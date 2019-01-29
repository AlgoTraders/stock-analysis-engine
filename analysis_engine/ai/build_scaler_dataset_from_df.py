"""
Build a scaler normalized
``pandas.DataFrame`` from an existing ``pandas.DataFrame``
"""

import sklearn.preprocessing as preproc
import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(
    name=__name__)


def build_scaler_dataset_from_df(
        df,
        min_feature=-1,
        max_feature=1):
    """build_scaler_dataset_from_df

    Helper for building scaler datasets from an existing ``pandas.DataFrame``

    returns a dictionary:

    .. code-block:: python

        return {
            'status': status,   # NOT_RUN | SUCCESS | ERR
            'scaler': scaler,   # MinMaxScaler
            'df': df  # scaled df from df arg
        }

    :param df: ``pandas.DataFrame`` to convert to scalers
    :param min_feature: min feature range for scaler normalization
        with default ``-1``
    :param max_feature: max feature range for scaler normalization
        with default ``1``
    """

    status = ae_consts.NOT_RUN
    scaler = None
    output_df = None

    res = {
        'status': status,
        'scaler': scaler,
        'df': output_df
    }

    try:
        log.debug(
            f'building scaler range=[{min_feature}, {max_feature}]')
        scaler = preproc.MinMaxScaler(
            feature_range=(
                min_feature,
                max_feature))

        log.info(
            f'scaler.fit_transform(df) rows={len(df.index)}')
        output_df = scaler.fit_transform(
            df.values)
        status = ae_consts.SUCCESS
    except Exception as e:
        log.error(
            f'failed build_scaler_dataset_from_df '
            f'with ex={e} '
            f'range=[{min_feature}, {max_feature}]')
        status = ae_consts.ERR
    # end of try/ex

    res = {
        'status': status,
        'scaler': scaler,
        'df': output_df
    }
    return res
# end of build_scaler_dataset_from_df
