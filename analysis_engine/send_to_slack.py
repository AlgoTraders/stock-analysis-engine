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
import analysis_engine.consts as ae_consts
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def post_success(msg,
                 jupyter=False,
                 block=False,
                 full_width=False):
    """Post a SUCCESS message to slack

    :param msg: A string, list, or dict to send to slack
    """
    result = {'status': ae_consts.FAILED}
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
    result = {'status': ae_consts.FAILED}
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
    result = {'status': ae_consts.FAILED}
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
            return [{"value": f"```{msg}```"}]
        return [{"value": msg}]
    elif type(msg) is list:
        if block:
            string_list = '\n'.join(f"{str(x)}" for x in msg)
            return [{"value": f"```{string_list}```"}]
        return [{"value": str(x)} for x in msg]
    elif type(msg) is dict:
        if block:
            string_dict = '\n'.join(
                f"{str(k)}: {str(v)}" for k, v in msg.items())
            return [{"value": f"```{string_dict}```"}]
        return [{"value": f"{str(k)}: {str(v)}"} for k, v in msg.items()]
    return None


def post(attachments, jupyter=False):
    """Send created attachments to slack

    :param attachments: Values to post to slack
    """
    SLACK_WEBHOOK = ae_consts.ev('SLACK_WEBHOOK', None)
    result = {'status': ae_consts.FAILED}
    if not os.getenv('SLACK_WEBHOOK', False):
        log.info(
            'post - please add a SLACK_WEBHOOK environment '
            'variable to publish messages')
        return result
    if attachments and SLACK_WEBHOOK:
        try:
            # if not jupyter:
            #     log.debug(f'Attempting to post attachments={attachments} '
            #               'to slack_webhook exists')
            for attachment in attachments:
                r = requests.post(SLACK_WEBHOOK, data=json.dumps(attachment))
                if str(r.status_code) == "200":
                    # log.info((
                    #   f'''Successful post of attachment={
                    #       attachment if not jupyter else
                    #       True if attachment else False} '''
                    #   'to slack_webhook'))
                    result['status'] = ae_consts.SUCCESS
                else:
                    log.error(
                        f'''Failed to post attachment={
                            attachment if not jupyter else
                            True if attachment else False} '''
                        f'with status_code={r.status_code}')
                    result['status'] = ae_consts.FAILED
                    break
        except Exception as e:
            log.error(
                f'''Failed to post attachments={
                    attachments if not jupyter else
                    True if attachments else False} '''
                f'with ex={e}')
            result['status'] = ae_consts.ERR
            result['err'] = e
    else:
        log.info(
            'Skipping post to slack due to missing '
            f'''attachments={
                attachments if not jupyter else
                True if attachments else False} or SLACK_WEBHOOK '''
            f'missing={False if SLACK_WEBHOOK else True}')
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

    log.debug(
        f'post_df - df.index={len(df.index)} '
        f'columns={columns} fmt={tablefmt}')

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

    log.debug(f'post_cb - msg={len(msg)} fmt={tablefmt}')

    post_success(
        msg=msg,
        block=block,
        jupyter=jupyter,
        full_width=full_width)
# end of post_cb


def post_plot(plot,
              filename='tmp',
              title=None):
    """post_plot

    Post a matlibplot plot to Slack

    :param plot: matlibplot pyplot figure
    :param filename: filename of plot
    :param title: Title for slack plot postiing
    """

    result = {'status': ae_consts.FAILED}
    if not os.getenv('SLACK_ACCESS_TOKEN', False):
        log.info(
            'post_plot - please add a SLACK_ACCESS_TOKEN environment '
            'variable to publish plots')
        return result
    if not filename:
        log.info(
            'post_plot - no filename provided'
        )
        return result
    url = 'https://slack.com/api/files.upload'
    filename = f'{filename.split(".")[0]}.png'
    channels = [f'#{channel}' for channel in os.getenv(
        'SLACK_PUBLISH_PLOT_CHANNELS',
        'general').split(',')]
    try:
        log.info(f'post_plot - temporarily saving plot: {filename}')
        plot.savefig(filename)
        tmp_file = {
            'file': (filename, open(filename, 'rb'), 'png')
        }
        payload = {
            'channels':        channels,
            'filename':        filename,
            'title':           title if title else filename,
            'token':           os.getenv('SLACK_ACCESS_TOKEN'),
        }
        log.info(f'post_plot - sending payload: {payload} to url: {url}')
        r = requests.post(url,
                          params=payload,
                          files=tmp_file)
        log.info(f'post_plot - removing temporarily saved plot: {filename}')
        os.remove(filename)
        if str(r.status_code) == "200":
            log.info(f'post_plot - posted plot to slack channels: {channels}')
            result['status'] = ae_consts.SUCCESS
    except Exception as e:
        log.info(f'post_plot - failed with Exception: {e}')
        result['status'] = ae_consts.ERR
        result['err'] = e
    return result
# end of post_plot
