"""
Wrapper for downloading an S3 key as a string
"""

import json
import zlib
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


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
        'getting s3.Object({}, {})'.format(
            s3_bucket_name,
            s3_key))
    s3_obj = s3.Object(s3_bucket_name, s3_key)

    raw_contents = None
    if compress:
        log.debug(
            'zlib.decompress('
            's3_obj.get()["Body"].read()'
            '.decode({})'
            ''.format(
                encoding))
        raw_contents = zlib.decompress(
            s3_obj.get()['Body'].read()).decode(
                encoding)
    else:
        log.debug(
            's3_obj.get()["Body"].read().decode({})'.format(
                encoding))
        raw_contents = s3_obj.get()['Body'].read().decode(encoding)
    # if compressed or not

    data = None
    if convert_as_json:
        data = json.loads(raw_contents)
    else:
        data = raw_contents
    return data
# end of s3_read_contents_from_key
