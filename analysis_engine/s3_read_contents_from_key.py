"""
Wrapper for downloading an S3 key as a string
"""

import json
import zlib
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def s3_read_contents_from_key(
        s3,
        s3_bucket_name,
        s3_key,
        encoding='utf-8',
        convert_as_json=True,
        compress=False):
    """s3_read_contents_from_key

    Download the S3 key contents as a string. This
    will raise exceptions.

    :param s3: existing S3 object
    :param s3_bucket_name: bucket name
    :param s3_key: S3 key
    :param encoding: utf-8 by default
    :param convert_to_json: auto-convert to a dict
    :param compress: decompress using ``zlib``
    """

    log.debug(
        f'getting s3.Object({s3_bucket_name}, {s3_key})')
    s3_obj = s3.Object(s3_bucket_name, s3_key)

    raw_contents = None
    if compress:
        log.debug(
            f'zlib.decompress('
            f's3_obj.get()["Body"].read()'
            f'.decode({encoding})')
        raw_contents = zlib.decompress(
            s3_obj.get()['Body'].read()).decode(
                encoding)
    else:
        log.debug(
            f's3_obj.get()["Body"].read().decode({encoding})')
        s3_contents = s3_obj.get()['Body'].read()
        raw_contents = s3_contents.decode(encoding)
    # if compressed or not

    data = None
    if convert_as_json:
        data = json.loads(raw_contents)
    else:
        data = raw_contents
    # if convert to json or not
    return data
# end of s3_read_contents_from_key
