"""
Show an algorithm dataset from file, s3 or redis

Supported Datasets:

- ``SA_DATASET_TYPE_ALGO_READY`` - Algorithm-ready datasets

**Supported environment variables**

::

    # to show debug, trace logging please export ``SHARED_LOG_CFG``
    # to a debug logger json file. To turn on debugging for this
    # library, you can export this variable to the repo's
    # included file with the command:
    export SHARED_LOG_CFG=/opt/sa/analysis_engine/log/debug-logging.json
"""

import analysis_engine.load_dataset as load_dataset
from analysis_engine.consts import DEFAULT_SERIALIZED_DATASETS
from analysis_engine.consts import SA_DATASET_TYPE_ALGO_READY
from analysis_engine.consts import ppj
from spylunking.log.setup_logging import build_colorized_logger

log = build_colorized_logger(
    name=__name__)


def show_dataset(
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
    """show_dataset

    Show a supported dataset's internal structure and preview some
    of the values to debug mapping, serialization issues

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

        if not use_ds:
            log.error(
                'unable to load a dataset from file={} '
                's3={} redis={}'.format(
                    path_to_file,
                    s3_key,
                    redis_key))
            return None
    # load if not created

    if dataset_type == SA_DATASET_TYPE_ALGO_READY:
        print('-----------------------------------')
        print('dates found in dataset')
        root_keys = []
        for root_key in use_ds:
            print(root_key)
            root_keys.append(root_key)
        all_dates = []
        all_ids = []
        for root_key in root_keys:
            second_layer = use_ds[root_key]
            for ds in second_layer:
                if 'date' in ds:
                    if len(all_dates) == 0:
                        print('')
                        print('dates found in dataset')
                    cur_date = ds.get(
                        'date',
                        None)
                    if cur_date:
                        print(cur_date)
                        all_dates.append(cur_date)
        first_node = None
        last_node = None
        end_nodes = []
        for root_key in root_keys:
            second_layer = use_ds[root_key]
            for ds in second_layer:
                if not first_node:
                    first_node = ds
                end_nodes.append(ds)
                last_node = ds
                if 'id' in ds:
                    if len(all_ids) == 0:
                        print('')
                        print('ids in the file')
                    cur_id = ds.get(
                        'id',
                        None)
                    if cur_id:
                        print(cur_id)
                        all_ids.append(cur_id)
        if first_node and last_node:
            show_first = {}
            for ds_key in first_node:
                if ds_key == 'data':
                    show_first[ds_key] = {}
                    for ds_name in first_node[ds_key]:
                        print(
                            'first_node has dataset with name: {}'.format(
                                ds_name))
                        show_first[ds_key][ds_name] = 'EMPTY_DF'
                        if hasattr(
                                first_node[ds_key][ds_name],
                                'index'):
                            show_first[ds_key][ds_name] = (
                                'pd.DataFrame() rows={}'.format(
                                    len(first_node[ds_key][ds_name].index)))
                else:
                    show_first[ds_key] = first_node[ds_key]
            print('')
            print('first node:')
            print(ppj(show_first))

            print('')
            num_records = len(all_ids)
            cur_cell = num_records - 4
            for cur_node in end_nodes[-5:]:
                show_node = {}
                for ds_key in cur_node:
                    if ds_key == 'data':
                        show_node[ds_key] = {}
                        for ds_name in cur_node[ds_key]:
                            show_node[ds_key][ds_name] = 'EMPTY_DF'
                            if hasattr(
                                    cur_node[ds_key][ds_name],
                                    'index'):
                                show_node[ds_key][ds_name] = (
                                    'pd.DataFrame() rows={}'.format(
                                        len(cur_node[ds_key][ds_name].index)))
                    else:
                        show_node[ds_key] = cur_node[ds_key]
                # end of show cur_node
                print(
                    'node={}/{} values:'.format(
                        cur_cell,
                        num_records))
                print(ppj(show_node))
                print('')
                cur_cell += 1
            # end of end_nodes
        else:
            if not first_node:
                print('missing first node in dataset')
            if not last_node:
                print('missing last node in dataset')
        if len(all_dates) > 0:
            print(
                'root_keys={} from {} to {}'.format(
                    root_keys,
                    all_dates[0],
                    all_dates[-1]))
        else:
            print(
                'root_keys={} missing dates'.format(
                    root_keys))

        print('-----------------------------------')

    return use_ds
# end of show_dataset
