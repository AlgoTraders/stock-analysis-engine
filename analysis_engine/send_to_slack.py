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
from analysis_engine.consts import ev
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import FAILED
from analysis_engine.consts import ERR
from spylunking.log.setup_logging import build_colorized_logger


log = build_colorized_logger(
    name=__name__)


def post_success(msg,
                 jupyter=False,
                 block=False,
                 full_width=False):
    """Post a SUCCESS message to slack

    :param msg: A string, list, or dict to send to slack
    """
    result = {'status': FAILED}
    if msg:
        attachments = [{"attachments":
                       [{"color": "good", "title": "SUCCESS"}]}]
        fields = parse_msg(msg, block=block)
        if fields:
            if full_width:
                attachments.append({"text": fields[0].pop("value")})
            else:
                attachments[0]["attachments"][0]["fields"] = fields
            result = post(attachments, jupyter=jupyter)
    return result


def post_failure(msg,
                 jupyter=False,
                 block=False,
                 full_width=False):
    """Post a FAILURE message to slack

    :param msg: A string, list, or dict to send to slack
    """
    result = {'status': FAILED}
    if msg:
        attachments = [{"attachments":
                       [{"color": "danger", "title": "FAILED"}]}]
        fields = parse_msg(msg, block=block)
        if fields:
            if full_width:
                attachments.append({"text": fields[0].pop("value")})
            else:
                attachments[0]["attachments"][0]["fields"] = fields
            result = post(attachments, jupyter=jupyter)
    return result


def post_message(msg,
                 jupyter=False,
                 block=False,
                 full_width=False):
    """Post any message to slack

    :param msg: A string, list, or dict to send to slack
    """
    result = {'status': FAILED}
    if msg:
        attachments = [{"attachments": [{"title": "MESSAGE"}]}]
        fields = parse_msg(msg, block=block)
        if fields:
            if full_width:
                attachments.append({"text": fields[0].pop("value")})
            else:
                attachments[0]["attachments"][0]["fields"] = fields
            result = post(attachments, jupyter=jupyter)
    return result


def parse_msg(msg, block=False):
    """Create an array of fields for slack from the msg type

    :param msg: A string, list, or dict to massage for sending to slack
    """
    if type(msg) is str:
        if block:
            return [{"value": "```{}```".format(msg)}]
        return [{"value": msg}]
    elif type(msg) is list:
        if block:
            string_list = '\n'.join("{}".format(str(x)) for x in msg)
            return [{"value": "```{}```".format(string_list)}]
        return [{"value": str(x)} for x in msg]
    elif type(msg) is dict:
        if block:
            string_dict = '\n'.join(
                "{}: {}".format(str(k), str(v)) for k, v in msg.items())
            return [{"value": "```{}```".format(string_dict)}]
        return [{"value": "{}: {}".format(
            str(k), str(v))} for k, v in msg.items()]
    return None


def post(attachments, jupyter=False):
    """Send created attachments to slack

    :param attachments: Values to post to slack
    """
    SLACK_WEBHOOK = ev('SLACK_WEBHOOK', None)
    result = {'status': FAILED}
    if attachments and SLACK_WEBHOOK:
        try:
            if not jupyter:
                log.info(('Attempting to post attachments={} '
                          'to slack_webhook exists').format(attachments))
            for attachment in attachments:
                r = requests.post(SLACK_WEBHOOK, data=json.dumps(attachment))
                if str(r.status_code) == "200":
                    log.info(('Successful post of attachment={} '
                              'to slack_webhook').format(
                                  attachment if not jupyter else
                                  True if attachment else False))
                    result['status'] = SUCCESS
                else:
                    log.error(('Failed to post attachment={} '
                               'with status_code={}').format(
                                   attachment if not jupyter else
                                   True if attachment else False,
                                   r.status_code))
                    result['status'] = FAILED
                    break
        except Exception as e:
            log.error(('Failed to post attachments={} '
                       'with ex={}').format(
                           attachments if not jupyter else
                           True if attachments else False,
                           e))
            result['status'] = ERR
            result['err'] = e
    else:
        log.info(('Skipping post to slack due to missing '
                  'attachments={} or SLACK_WEBHOOK missing={}').format(
                      attachments if not jupyter else
                      True if attachments else False,
                      False if SLACK_WEBHOOK else True))
    return result
