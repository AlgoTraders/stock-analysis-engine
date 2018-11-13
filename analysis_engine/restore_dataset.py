"""
Restore an algorithm dataset from file, s3 or redis to redis
for ensuring all datasets are ready for Algorithmic backtesting

Supported Datasets:

- ``SA_DATASET_TYPE_ALGO_READY`` - Algorithm-ready datasets
"""

import analysis_engine.load_dataset as load_dataset
import analysis_engine.show_dataset as show_dataset
import analysis_engine.get_data_from_redis_key as redis_utils
import analysis_engine.publish as publish
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import REDIS_ADDRESS
from analysis_engine.consts import DEFAULT_SERIALIZED_DATASETS
from analysis_engine.consts import DATASET_COLLECTION_VERSION
from analysis_engine.consts import SA_DATASET_TYPE_ALGO_READY
from analysis_engine.consts import EMPTY_DF_STR
from analysis_engine.consts import get_percent_done
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


def restore_dataset(
        show_summary=True,
        force_restore=False,
        algo_dataset=None,
        dataset_type=SA_DATASET_TYPE_ALGO_READY,
        serialize_datasets=DEFAULT_SERIALIZED_DATASETS,
        path_to_file=None,
        compress=False,
        encoding='utf-8',
        redis_enabled=True,
        redis_key=None,
        redis_address=None,
        redis_db=None,
        redis_password=None,
        redis_expire=None,
        redis_serializer='json',
        redis_encoding='utf-8',
        redis_output_db=None,
        s3_enabled=True,
        s3_key=None,
        s3_address=None,
        s3_bucket=None,
        s3_access_key=None,
        s3_secret_key=None,
        s3_region_name=None,
        s3_secure=False,
        slack_enabled=False,
        slack_code_block=False,
        slack_full_width=False,
        verbose=False):
    """restore_dataset

    Restore missing dataset nodes in redis from an algorithm-ready
    dataset file on disk. Use this to restore redis from scratch.

    :param show_summary: optional - show a summary of the algorithm-ready
        dataset using ``analysis_engine.show_dataset.show_dataset``
        (default is ``True``)
    :param force_restore: optional - boolean - publish whatever is in
        the algorithm-ready dataset into redis. If ``False`` this will
        ensure that datasets are only set in redis if they are not already
        set
    :param algo_dataset: optional - already loaded algorithm-ready dataset
    :param dataset_type: optional - dataset type
        (default is ``SA_DATASET_TYPE_ALGO_READY``)
    :param serialize_datasets: optional - list of dataset names to
        deserialize in the dataset
    :param path_to_file: optional - path to an algorithm-ready dataset
        in a file
    :param compress: optional - boolean flag for decompressing
        the contents of the ``path_to_file`` if necessary
        (default is ``False`` and algorithms
        use ``zlib`` for compression)
    :param encoding: optional - string for data encoding

    **(Optional) Redis connectivity arguments**

    :param redis_enabled: bool - toggle for auto-caching all
        datasets in Redis
        (default is ``True``)
    :param redis_key: string - key to save the data in redis
        (default is ``None``)
    :param redis_address: Redis connection string format: ``host:port``
        (default is ``localhost:6379``)
    :param redis_db: Redis db to use
        (default is ``0``)
    :param redis_password: optional - Redis password
        (default is ``None``)
    :param redis_expire: optional - Redis expire value
        (default is ``None``)
    :param redis_serializer: not used yet - support for future
        pickle objects in redis
    :param redis_encoding: format of the encoded key in redis
    :param redis_output_db: optional - integer publish to a separate
        redis database

    **(Optional) Minio (S3) connectivity arguments**

    :param s3_enabled: bool - toggle for auto-archiving on Minio (S3)
        (default is ``True``)
    :param s3_key: string - key to save the data in redis
        (default is ``None``)
    :param s3_address: Minio S3 connection string format: ``host:port``
        (default is ``localhost:9000``)
    :param s3_bucket: S3 Bucket for storing the artifacts
        (default is ``dev``) which should be viewable on a browser:
        http://localhost:9000/minio/dev/
    :param s3_access_key: S3 Access key
        (default is ``trexaccesskey``)
    :param s3_secret_key: S3 Secret key
        (default is ``trex123321``)
    :param s3_region_name: S3 region name
        (default is ``us-east-1``)
    :param s3_secure: Transmit using tls encryption
        (default is ``False``)

    **(Optional) Slack arguments**

    :param slack_enabled: optional - boolean for
        publishing to slack
    :param slack_code_block: optional - boolean for
        publishing as a code black in slack
    :param slack_full_width: optional - boolean for
        publishing as a to slack using the full
        width allowed

    Additonal arguments

    :param verbose: optional - bool for increasing
        logging
    """

    use_ds = algo_dataset
    redis_host = REDIS_ADDRESS.split(':')[0]
    redis_port = int(REDIS_ADDRESS.split(':')[1])
    if redis_address:
        redis_host = redis_address.split(':')[0]
        redis_port = int(redis_address.split(':')[1])

    if show_summary:
        use_ds = show_dataset.show_dataset(
            dataset_type=dataset_type,
            compress=compress,
            encoding=redis_encoding,
            path_to_file=path_to_file,
            s3_key=s3_key,
            s3_address=s3_address,
            s3_bucket=s3_bucket,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            redis_key=redis_key,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            redis_serializer=redis_serializer,
            serialize_datasets=serialize_datasets)

    # end of if show_summary

    if not use_ds:
        log.info(
            'loading from file={} s3={} redis={}'.format(
                path_to_file,
                s3_key,
                redis_key))
        use_ds = load_dataset.load_dataset(
            dataset_type=dataset_type,
            compress=compress,
            encoding=redis_encoding,
            path_to_file=path_to_file,
            s3_key=s3_key,
            s3_address=s3_address,
            s3_bucket=s3_bucket,
            s3_access_key=s3_access_key,
            s3_secret_key=s3_secret_key,
            s3_region_name=s3_region_name,
            s3_secure=s3_secure,
            redis_key=redis_key,
            redis_address=redis_address,
            redis_db=redis_db,
            redis_password=redis_password,
            redis_expire=redis_expire,
            redis_serializer=redis_serializer,
            serialize_datasets=serialize_datasets)
    # load if not loaded

    if not use_ds:
        log.error(
            'unable to load a dataset from file={} '
            's3={} redis={}'.format(
                path_to_file,
                s3_key,
                redis_key))
        return None

    log.info('restore - start')
    total_to_restore = 0
    for ticker in use_ds:
        for ds_node in use_ds[ticker]:
            for ds_key in ds_node['data']:
                if ds_key in serialize_datasets:
                    total_to_restore += 1
    # end of counting total_to_restore

    log.info('restore - records={}'.format(total_to_restore))
    num_done = 0
    for ticker in use_ds:
        for ds_node in use_ds[ticker]:
            ds_parent_key = ds_node['id']
            log.info(
                'restore - parent_key={} - {} {}/{}'.format(
                    ds_parent_key,
                    get_percent_done(
                        progress=num_done,
                        total=total_to_restore),
                    num_done,
                    total_to_restore))
            if verbose:
                print(ds_parent_key)

            cache_res = redis_utils.get_data_from_redis_key(
                host=redis_host,
                port=redis_port,
                password=redis_password,
                db=redis_db,
                key=ds_parent_key,
                serializer=redis_serializer,
                encoding=redis_encoding,
                expire=redis_expire,
                label='restore-{}'.format(ds_parent_key))
            should_restore = False
            if (not force_restore and
                    cache_res['status'] == SUCCESS and
                    'data' in cache_res['rec'] and
                    cache_res['rec']['data'] and
                    len(cache_res['rec']['data']) > 10):
                should_restore = False
            else:
                should_restore = True
            if should_restore:
                log.info(
                    ' - parent {} restore'.format(
                        ds_parent_key))
                new_parent_rec = {
                    'exp_date': None,
                    'publish_pricing_update': None,
                    'date': ds_node['date'],
                    'updated': None,
                    'version': DATASET_COLLECTION_VERSION
                }
                for sname in serialize_datasets:
                    if sname in ds_node['data']:
                        if hasattr(
                                ds_node['data'][sname],
                                'index'):
                            new_parent_rec[sname] = \
                                ds_node['data'][sname].to_json(
                                    orient='records',
                                    date_format='iso')
                        else:
                            new_parent_rec[sname] = \
                                ds_node['data'][sname]

                publish.publish(
                    data=new_parent_rec,
                    convert_to_json=False,
                    compress=compress,
                    redis_enabled=True,
                    redis_key=ds_parent_key,
                    redis_db=redis_output_db,
                    redis_address=redis_address,
                    redis_password=redis_password,
                    redis_expire=redis_expire,
                    redis_serializer=redis_serializer,
                    redis_encoding=redis_encoding,
                    s3_enabled=False,
                    output_file=None,
                    verbose=verbose)

            for ds_key in ds_node['data']:
                if ds_key in serialize_datasets:
                    new_key = '{}_{}'.format(
                        ds_parent_key,
                        ds_key)
                    if hasattr(
                            ds_node['data'][ds_key],
                            'index'):
                        loaded_df = ds_node['data'][ds_key]
                        if len(loaded_df.index) > 0:
                            if verbose:
                                print(
                                    ' - checking: {}'.format(
                                        new_key))

                            cache_res = redis_utils.get_data_from_redis_key(
                                host=redis_host,
                                port=redis_port,
                                password=redis_password,
                                db=redis_db,
                                key=new_key,
                                serializer=redis_serializer,
                                encoding=redis_encoding,
                                expire=redis_expire,
                                label='restore-{}'.format(new_key))
                            should_restore = False
                            if (not force_restore and
                                    cache_res['status'] == SUCCESS and
                                    'data' in cache_res['rec'] and
                                    cache_res['rec']['data'] and
                                    len(cache_res['rec']['data']) > 10):
                                should_restore = False
                            else:
                                if (str(cache_res['rec']['data']) !=
                                        EMPTY_DF_STR):
                                    should_restore = True
                            if should_restore:
                                log.info(
                                    'restore nested dataset: {}'.format(
                                        ds_parent_key,
                                        new_key))
                                publish.publish(
                                    data=loaded_df,
                                    is_df=True,
                                    compress=compress,
                                    redis_enabled=True,
                                    redis_key=new_key,
                                    redis_db=redis_output_db,
                                    redis_address=redis_address,
                                    redis_password=redis_password,
                                    redis_expire=redis_expire,
                                    redis_serializer=redis_serializer,
                                    redis_encoding=redis_encoding,
                                    s3_enabled=False,
                                    output_file=None,
                                    verbose=verbose)
                            else:
                                if verbose:
                                    print(
                                        ' - checking: {} - SKIP'.format(
                                            new_key))

                        if verbose:
                            print(' - {} - no data to sync'.format(
                                new_key))
                    # end of is a dataframe
                    # else:
                    # end of handling dataframe vs dictionary

                    num_done += 1
        # end of for all datasets
        print('-----------------------------------')
    # end for all dataset to restore

    log.info(
        'restore - done - num_done={} total={}'.format(
            num_done,
            total_to_restore))

    return use_ds
# end of restore_dataset
