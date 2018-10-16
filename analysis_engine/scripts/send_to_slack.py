"""

Send Celery Task Details to Slack Utilities
===========================================

Helper for extracting details from Celery task and
sending it to a slack webhook.

Supported environment variables:

::

    # slack webhook 
    export SLACK_WEBHOOK=https://hooks.slack.com/services/

"""

import json
import requests
from analysis_engine.consts import SLACK_WEBHOOK
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def post_success(msg):
    """Post a SUCCESS message to slack

    :param msg: A string, list, or dict to send to slack
    """
    if msg:
        attachment = {"attachments": [{"color": "good", "title": "SUCCESS"}]}
        fields = parse_msg(msg)
        if fields:
            attachment["attachments"][0]["fields"] = fields
            post(attachment)
    
    

def post_failure(msg):
    """Post a FAILURE message to slack

    :param msg: A string, list, or dict to send to slack
    """
    if msg:
        attachment = {"attachments": [{"color": "danger", "title": "FAILURE"}]}
        fields = parse_msg(msg)
        if fields:
            attachment["attachments"][0]["fields"] = fields
            post(attachment)


def post_message(msg):
    """Post any message to slack

    :param msg: A string, list, or dict to send to slack
    """
    if msg:
        attachment = {"attachments": [{"title": "MESSAGE"}]}
        fields = parse_msg(msg)
        if fields:
            attachment["attachments"][0]["fields"] = fields
            post(attachment)


def parse_msg(msg):
    """Create an array of fields for slack from the msg type
    
    :param msg: A string, list, or dict to massage for sending to slack
    """
    if type(msg) is str:
        return [{"value": msg}]
    elif type(msg) is list:
        return [{"value": x} for x in msg]
    elif type(msg) is dict:
        return [{"value": "{}: {}".format(k, v)} for k, v in msg.items()]
    return None


def post(attachment):
    """Send a created attachment to slack
    
    :param attachment: Values to post to slack
    """
    if attachment and SLACK_WEBHOOK:
        try:
            log.info(('Attempting to post attachment={} '
                      'to slack_webhook={}').format(
                          attachment,
                          SLACK_WEBHOOK))
            r = requests.post(SLACK_WEBHOOK, data=json.dumps(attachment))
            if str(r.status_code) is "200":
                log.info(('Successful post of attachment={} '
                          'to slack_webhook={}').format(
                            attachment,
                            SLACK_WEBHOOK))
            else:
                log.error(('Failed to post attachment={} '
                           'to slack_webhook={} with status_code={}').format(
                               attachment,
                               SLACK_WEBHOOK,
                               r.status_code))
        except Exception as e:
            log.error(('Failed to post attachment={} '
                       'to slack_webhook={} with ex={}').format(
                           attachment,
                           SLACK_WEBHOOK,
                           e))
    else:
        log.info(('Skipping post to slack due to missing '
                  'attachment={} or SLACK_WEBHOOK={}').format(
                      attachment,
                      SLACK_WEBHOOK))
