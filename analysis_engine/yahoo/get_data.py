"""
Parse data from yahoo
"""

import copy
import datetime
import pinance
import analysis_engine.options_dates
import analysis_engine.get_pricing
import analysis_engine.build_result as build_result
import analysis_engine.work_tasks.publish_pricing_update as \
    publisher
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import TICKER
from analysis_engine.consts import SUCCESS
from analysis_engine.consts import NOT_RUN
from analysis_engine.consts import ERR
from analysis_engine.consts import NOT_SET
from analysis_engine.consts import COMMON_TICK_DATE_FORMAT
from analysis_engine.consts import EMPTY_DF_STR
from analysis_engine.consts import get_status
from analysis_engine.consts import ppj
from analysis_engine.utils import get_last_close_str

log = build_colorized_logger(
    name=__name__)


def get_data_from_yahoo(
        work_dict):
    """get_data_from_yahoo

    Get data from yahoo

    :param work_dict: request dictionary
    """
    label = 'get_data_from_yahoo'

    log.info(
        'task - {} - start '
        'work_dict={}'.format(
            label,
            work_dict))

    num_news_rec = 0
    num_option_calls = 0
    num_option_puts = 0
    cur_high = -1
    cur_low = -1
    cur_open = -1
    cur_close = -1
    cur_volume = -1

    rec = {
        'pricing': None,
        'options': None,
        'calls': None,
        'puts': None,
        'news': None,
        'exp_date': None,
        'publish_pricing_update': None,
        'date': None,
        'updated': None
    }
    res = {
        'status': NOT_RUN,
        'err': None,
        'rec': rec
    }

    try:

        ticker = work_dict.get(
            'ticker',
            TICKER)
        exp_date = work_dict.get(
            'exp_date',
            None)
        cur_strike = work_dict.get(
            'strike',
            None)
        contract_type = str(work_dict.get(
            'contract',
            'C')).upper()
        get_pricing = work_dict.get(
            'get_pricing',
            True)
        get_news = work_dict.get(
            'get_news',
            True)
        get_options = work_dict.get(
            'get_options',
            True)
        orient = work_dict.get(
            'orient',
            'records')
        label = work_dict.get(
            'label',
            label)

        ticker_results = pinance.Pinance(ticker)
        num_news_rec = 0

        use_date = exp_date
        if not exp_date:
            exp_date = analysis_engine.options_dates.option_expiration(
                 date=exp_date)
            use_date = exp_date.strftime('%Y-%m-%d')

        """
        Debug control flags

        Quickly turn specific fetches off:

        get_news = False
        get_pricing = False
        get_options = False

        """
        if get_pricing:
            log.info(
                '{} getting ticker={} pricing'.format(
                    label,
                    ticker))
            ticker_results.get_quotes()
            if ticker_results.quotes_data:
                pricing_dict = ticker_results.quotes_data

                cur_high = pricing_dict.get(
                    'regularMarketDayHigh',
                    None)
                cur_low = pricing_dict.get(
                    'regularMarketDayLow',
                    None)
                cur_open = pricing_dict.get(
                    'regularMarketOpen',
                    None)
                cur_close = pricing_dict.get(
                    'regularMarketPreviousClose',
                    None)
                cur_volume = pricing_dict.get(
                    'regularMarketVolume',
                    None)
                pricing_dict['high'] = cur_high
                pricing_dict['low'] = cur_low
                pricing_dict['open'] = cur_open
                pricing_dict['close'] = cur_close
                pricing_dict['volume'] = cur_volume
                pricing_dict['date'] = get_last_close_str()
                if 'regularMarketTime' in pricing_dict:
                    pricing_dict['market_time'] = \
                        datetime.datetime.fromtimestamp(
                            pricing_dict['regularMarketTime']).strftime(
                                COMMON_TICK_DATE_FORMAT)
                if 'postMarketTime' in pricing_dict:
                    pricing_dict['post_market_time'] = \
                        datetime.datetime.fromtimestamp(
                            pricing_dict['postMarketTime']).strftime(
                                COMMON_TICK_DATE_FORMAT)

                log.info(
                    '{} ticker={} converting pricing to '
                    'df orient={}'.format(
                        label,
                        ticker,
                        orient))

                try:
                    rec['pricing'] = pricing_dict
                except Exception as f:
                    rec['pricing'] = '{}'
                    log.info(
                        '{} ticker={} failed converting pricing '
                        'data={} to df ex={}'.format(
                            label,
                            ticker,
                            ppj(pricing_dict),
                            f))
                # try/ex

                log.info(
                    '{} ticker={} done converting pricing to '
                    'df orient={}'.format(
                        label,
                        ticker,
                        orient))

            else:
                log.error(
                    '{} ticker={} missing quotes_data={}'.format(
                        label,
                        ticker,
                        ticker_results.quotes_data))
            # end of if ticker_results.quotes_data

            log.info(
                '{} ticker={} close={} vol={}'.format(
                    label,
                    ticker,
                    cur_close,
                    cur_volume))
        else:
            log.info(
                '{} skip - getting ticker={} pricing'.format(
                    label,
                    ticker,
                    get_pricing))
        # if get_pricing

        if get_news:
            log.info(
                '{} getting ticker={} news'.format(
                    label,
                    ticker))
            ticker_results.get_news()
            if ticker_results.news_data:
                news_list = None
                try:
                    news_list = ticker_results.news_data
                    log.info(
                        '{} ticker={} converting news to '
                        'df orient={}'.format(
                            label,
                            ticker,
                            orient))

                    num_news_rec = len(news_list)

                    rec['news'] = news_list
                except Exception as f:
                    rec['news'] = '{}'
                    log.info(
                        '{} ticker={} failed converting news '
                        'data={} to df ex={}'.format(
                            label,
                            ticker,
                            news_list,
                            f))
                # try/ex

                log.info(
                    '{} ticker={} done converting news to '
                    'df orient={}'.format(
                        label,
                        ticker,
                        orient))
            else:
                log.info(
                    '{} ticker={} Yahoo NO news={}'.format(
                        label,
                        ticker,
                        ticker_results.news_data))
            # end of if ticker_results.news_data
        else:
            log.info(
                '{} skip - getting ticker={} news'.format(
                    label,
                    ticker))
        # end if get_news

        if get_options:

            get_all_strikes = True
            if get_all_strikes:
                cur_strike = None
            else:
                if cur_close:
                    cur_strike = int(cur_close)
                if not cur_strike:
                    cur_strike = 287

            log.info(
                '{} ticker={} num_news={} get options close={} '
                'exp_date={} contract={} strike={}'.format(
                    label,
                    ticker,
                    num_news_rec,
                    cur_close,
                    use_date,
                    contract_type,
                    cur_strike))

            options_dict = \
                analysis_engine.get_pricing.get_options(
                    ticker=ticker,
                    exp_date_str=use_date,
                    contract_type=contract_type,
                    strike=cur_strike)

            rec['options'] = '{}'

            try:
                log.info(
                    '{} ticker={} converting options to '
                    'df orient={}'.format(
                        label,
                        ticker,
                        orient))

                num_option_calls = options_dict.get(
                    'num_calls',
                    None)
                num_option_puts = options_dict.get(
                    'num_puts',
                    None)
                rec['options'] = {
                    'exp_date': options_dict.get(
                        'exp_date',
                        None),
                    'calls': options_dict.get(
                        'calls',
                        None),
                    'puts': options_dict.get(
                        'puts',
                        None),
                    'num_calls': num_option_calls,
                    'num_puts': num_option_puts
                }
                rec['calls'] = rec['options'].get(
                    'calls',
                    EMPTY_DF_STR)
                rec['puts'] = rec['options'].get(
                    'puts',
                    EMPTY_DF_STR)
            except Exception as f:
                rec['options'] = '{}'
                log.info(
                    '{} ticker={} failed converting options '
                    'data={} to df ex={}'.format(
                        label,
                        ticker,
                        options_dict,
                        f))
            # try/ex

            log.info(
                '{} ticker={} done converting options to '
                'df orient={} num_calls={} num_puts={}'.format(
                    label,
                    ticker,
                    orient,
                    num_option_calls,
                    num_option_puts))

        else:
            log.info(
                '{} skip - getting ticker={} options'.format(
                    label,
                    ticker))
        # end of if get_options

        log.info(
            '{} yahoo pricing for ticker={} close={} '
            'num_calls={} num_puts={} news={}'.format(
                label,
                ticker,
                cur_close,
                num_option_calls,
                num_option_puts,
                num_news_rec))

        fields_to_upload = [
            'pricing',
            'options',
            'calls',
            'puts',
            'news'
        ]

        for field_name in fields_to_upload:
            upload_and_cache_req = copy.deepcopy(work_dict)
            upload_and_cache_req['celery_disabled'] = True
            upload_and_cache_req['data'] = rec[field_name]
            if not upload_and_cache_req['data']:
                upload_and_cache_req['data'] = '{}'

            if 'redis_key' in work_dict:
                upload_and_cache_req['redis_key'] = '{}_{}'.format(
                    work_dict.get(
                        'redis_key',
                        '{}_{}'.format(
                            ticker,
                            field_name)),
                    field_name)
            if 's3_key' in work_dict:
                upload_and_cache_req['s3_key'] = '{}_{}'.format(
                    work_dict.get(
                        's3_key',
                        '{}_{}'.format(
                            ticker,
                            field_name)),
                    field_name)
            try:
                update_res = publisher.run_publish_pricing_update(
                    work_dict=upload_and_cache_req)
                update_status = update_res.get(
                    'status',
                    NOT_SET)
                log.info(
                    '{} publish update status={} data={}'.format(
                        label,
                        get_status(status=update_status),
                        update_res))
            except Exception as f:
                err = (
                    '{} - failed to upload YAHOO data={} to '
                    'to s3_key={} and redis_key={}'.format(
                        label,
                        upload_and_cache_req,
                        upload_and_cache_req['s3_key'],
                        upload_and_cache_req['redis_key']))
                log.error(err)
            # end of try/ex to upload and cache
            if not rec[field_name]:
                log.debug(
                    '{} - ticker={} no data from YAHOO for '
                    'field_name={}'.format(
                        label,
                        ticker,
                        field_name))
        # end of for all fields

        res = build_result.build_result(
            status=SUCCESS,
            err=None,
            rec=rec)
    except Exception as e:
        res = build_result.build_result(
            status=ERR,
            err=(
                'failed - get_data_from_yahoo '
                'dict={} with ex={}').format(
                    work_dict,
                    e),
            rec=rec)
        log.error(
            '{} - {}'.format(
                label,
                res['err']))
    # end of try/ex

    log.info(
        'task - get_data_from_yahoo done - '
        '{} - status={}'.format(
            label,
            get_status(res['status'])))

    return res
# end of get_data_from_yahoo
