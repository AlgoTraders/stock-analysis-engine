"""
Wrapper for downloading an S3 key as a string
"""

import json
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def s3_read_contents_from_key(
        s3,
        s3_bucket_name,
        s3_key,
        encoding='utf-8',
        convert_as_json=True):
    """s3_read_contents_from_key

    Download the S3 key contents as a string. This
    will raise exceptions.

    :param s3: existing S3 object
    :param s3_bucket_name: bucket name
    :param s3_key: S3 key
    :param encoding: utf-8 by default
    :param convert_to_json: auto-convert to a dict
    """

    log.debug(
        'getting s3.Object({}, {})'.format(
            s3_bucket_name,
            s3_key))
    s3_obj = s3.Object(s3_bucket_name, s3_key)
    log.debug(
        's3_obj.get()["Body"].read().decode({})'.format(
            encoding))
    raw_contents = s3_obj.get()['Body'].read().decode(encoding)
    data = None
    if convert_as_json:
        data = json.loads(raw_contents)
    else:
        data = raw_contents
    return data
# end of s3_read_contents_from_key
