"""
Helper for extracting details from Celery task and
sending it to a slack webhook.

Supported environment variables:

::

    # slack webhook
    export SLACK_WEBHOOK=https://hooks.slack.com/services/

"""

import os
import json
import requests
import tabulate as tb
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
    if not os.getenv('SLACK_WEBHOOK', False):
        log.info(
            'post_success - please add a SLACK_WEBHOOK environment '
            'variable to publish messages')
        return result
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
    if not os.getenv('SLACK_WEBHOOK', False):
        log.info(
            'post_failure - please add a SLACK_WEBHOOK environment '
            'variable to publish messages')
        return result
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
    if not os.getenv('SLACK_WEBHOOK', False):
        log.info(
            'post_message - please add a SLACK_WEBHOOK environment '
            'variable to publish messages')
        return result
    if not os.getenv('SLACK_WEBHOOK', False):
        log.info(
            'post_message - please add a SLACK_WEBHOOK environment '
            'variable for to work')
        return result
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
    if not os.getenv('SLACK_WEBHOOK', False):
        log.info(
            'post - please add a SLACK_WEBHOOK environment '
            'variable to publish messages')
        return result
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


def post_df(
        df,
        columns=None,
        block=True,
        jupyter=True,
        full_width=True,
        tablefmt='github'):
    """post_df

    Post a ``pandas.DataFrame`` to Slack

    :param df: ``pandas.DataFrame`` object
    :param columns: ordered list of columns to for the table
                    header row
                    (``None`` by default)
    :param block: bool for
                  post as a Slack-formatted block ```like this```
                  (``True`` by default)
    :param jupyter: bool for
                    jupyter attachment handling
                    (``True`` by default)
    :param full_width: bool to ensure the width is preserved
                       the Slack message  (``True`` by default)
    :param tablefmt: string for table format (``github`` by default).
                     Additional format values can be found on:
                     https://bitbucket.org/astanin/python-tabulate
    """

    if not os.getenv('SLACK_WEBHOOK', False):
        log.info(
            'post_df - please add a SLACK_WEBHOOK environment '
            'variable to publish messages')
        return
    if not hasattr(df, 'index'):
        log.debug('post_df - no df ')
        return

    log.debug('post_df - df.index={} columns={} fmt={}'.format(
        len(df.index),
        columns,
        tablefmt))

    msg = None
    if columns:
        msg = tb.tabulate(
            df[columns],
            headers=columns,
            tablefmt=tablefmt)
    else:
        msg = tb.tabulate(
            df,
            tablefmt=tablefmt)
    # end of if/else

    post_success(
        msg=msg,
        block=block,
        jupyter=jupyter,
        full_width=full_width)
# end of post_df


def post_cb(
        msg,
        block=True,
        jupyter=True,
        full_width=True,
        tablefmt='github'):
    """post_cb

    Post a text messsage as a code block to Slack

    :param msg: text message (pre-formatting is not necessary)
    :param block: bool for
                  post as a Slack-formatted block ```like this```
                  (``True`` by default)
    :param jupyter: bool for
                    jupyter attachment handling
                    (``True`` by default)
    :param full_width: bool to ensure the width is preserved
                       the Slack message  (``True`` by default)
    :param tablefmt: string for table format (``github`` by default).
                     Additional format values can be found on:
                     https://bitbucket.org/astanin/python-tabulate
    """

    if not os.getenv('SLACK_WEBHOOK', False):
        log.info(
            'post_cb - please add a SLACK_WEBHOOK environment '
            'variable to publish messages')
        return
    if not msg:
        log.debug('post_cb - no msg')
        return

    log.debug('post_cb - msg={} fmt={}'.format(
        len(msg),
        tablefmt))

    post_success(
        msg=msg,
        block=block,
        jupyter=jupyter,
        full_width=full_width)
# end of post_cb
