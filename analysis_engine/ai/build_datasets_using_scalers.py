"""
Build scaler normalized train and test datasets
from a ``pandas.DataFrame`` (like a ``Trading History`` stored in s3)

.. note:: This function will create multiple copies of the data so
    this is a memory intensive call which may overflow the
    available memory on a machine if there are many rows
"""

import analysis_engine.consts as ae_consts
import analysis_engine.ai.build_scaler_dataset_from_df as scaler_utils
import spylunking.log.setup_logging as log_utils
import sklearn.model_selection as tt_split

log = log_utils.build_colorized_logger(
    name=__name__)


def build_datasets_using_scalers(
        train_features,
        test_feature,
        df,
        test_size,
        seed,
        min_feature=-1,
        max_feature=1):
    """build_datasets_using_scalers

    Build train and test datasets using a
    `MinMaxScaler <https://scikit-learn.org/stable/
    modules/generated/
    sklearn.preprocessing.MinMaxScaler.html>`__ for normalizing a dataset
    before training a deep neural network.

    Here's the returned dictionary:

    .. code-block:: python

        res = {
            'status': status,
            'scaled_train_df': scaled_train_df,
            'scaled_test_df': scaled_test_df,
            'scaler_train': scaler_train,
            'scaler_test': scaler_test,
            'x_train': x_train,
            'y_train': y_train,
            'x_test': x_test,
            'y_test': y_test,
        }

    :param train_features: list of strings with all columns (features)
        to train
    :param test_feature: string name of the column to predict.
        This is a single column name in the``df``
        (which is a ``pandas.DataFrame``).
    :param df: dataframe to build scaler test and train datasets
    :param test_size: percent of test to train rows
    :param min_feature: min scaler range
        with default ``-1``
    :param max_feature: max scaler range
        with default ``1``
    """

    status = ae_consts.NOT_RUN
    scaled_train_df = None
    scaled_test_df = None
    scaler_train = None
    scaler_test = None
    x_train = None
    y_train = None
    x_test = None
    y_test = None

    res = {
        'status': status,
        'scaled_train_df': scaled_train_df,
        'scaled_test_df': scaled_test_df,
        'scaler_train': scaler_train,
        'scaler_test': scaler_test,
        'x_train': x_train,
        'y_train': y_train,
        'x_test': x_test,
        'y_test': y_test,
    }

    try:
        log.info(
            f'building scalers '
            f'df.rows={len(df.index)} '
            f'columns={len(list(df.columns.values))} '
            f'train_features={len(train_features)} '
            f'test_feature={test_feature}')

        if test_feature not in df:
            log.error(
                f'did not find test_feature={test_feature} in '
                f'df columns={df.columns.values}')
            status = ae_consts.FAILED
            res['status'] = status
            return res
        for single_train_feature in train_features:
            if single_train_feature not in df:
                log.error(
                    f'did not find '
                    f'train_feature={single_train_feature} in '
                    f'df columns={df.columns.values}')
                status = ae_consts.FAILED
                res['status'] = status
                return res

        train_df = df[train_features]
        test_df = df[[test_feature]]

        log.info(
            f'building scaled train df')
        scaled_train_res = scaler_utils.build_scaler_dataset_from_df(
            df=train_df,
            min_feature=min_feature,
            max_feature=max_feature)

        log.info(
            f'building scaled test df')
        scaled_test_res = scaler_utils.build_scaler_dataset_from_df(
            df=test_df,
            min_feature=min_feature,
            max_feature=max_feature)

        log.info(
            f'scaled df transform '
            f'train_status={scaled_train_res["status"] == ae_consts.SUCCESS} '
            f'test_status={scaled_test_res["status"] == ae_consts.SUCCESS}')

        if scaled_train_res['status'] == ae_consts.SUCCESS \
           and scaled_test_res['status'] == ae_consts.SUCCESS:
            log.info(
                f'scaled train_rows={len(scaled_train_res["df"])} '
                f'test_rows={len(scaled_test_res["df"])}')

            scaler_train = scaled_train_res['scaler']
            scaler_test = scaled_test_res['scaler']
            scaled_train_df = scaled_train_res['df']
            scaled_test_df = scaled_test_res['df']
            (x_train,
             x_test,
             y_train,
             y_test) = tt_split.train_test_split(
                scaled_train_df,
                scaled_test_df,
                test_size=test_size,
                random_state=seed)
        else:
            log.error(
                f'failed df transform '
                f'train_status={scaled_train_res["status"]} '
                f'test_status={scaled_test_res["status"]}')
            status = ae_consts.FAILED
            res['status'] = status
            return res
        # if built both train and test successfully

        log.info(
            f'train_rows={len(train_df.index)} '
            f'test_rows={len(test_df.index)} '
            f'x_train={len(x_train)} '
            f'x_test={len(x_test)} '
            f'y_train={len(y_train)} '
            f'y_test={len(y_test)}')

        res['scaled_train_df'] = scaled_train_df
        res['scaled_test_df'] = scaled_test_df
        res['scaler_train'] = scaler_train
        res['scaler_test'] = scaler_test
        res['x_train'] = x_train
        res['y_train'] = y_train
        res['x_test'] = x_test
        res['y_test'] = y_test

        status = ae_consts.SUCCESS

    except Exception as e:
        log.error(
            f'failed with ex={e} '
            f'building scalers '
            f'df.rows={len(df.index)} '
            f'columns={list(df.columns.values)} '
            f'train_features={train_features} '
            f'test_feature={test_feature}')
        status = ae_consts.ERR
    # try/ex

    res['status'] = status
    return res
# end of build_datasets_using_scalers
