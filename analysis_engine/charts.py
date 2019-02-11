"""
Charting functions with matplotlib, numpy, pandas, and seaborn

Change the footnote with:

::

    export PLOT_FOOTNOTE="custom footnote on images"

.. note: most of these functions were ported from
         the repo: https://github.com/jay-johnson/scipype

"""

import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import analysis_engine.consts as ae_consts
import analysis_engine.build_result as build_result
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def add_footnote(
        fig=None,
        xpos=0.90,
        ypos=0.01,
        text=None,
        color='#888888',
        fontsize=8):
    """add_footnote

    Add a footnote based off the environment key:
    ``PLOT_FOOTNOTE``

    :param fig: add the footnote to this figure object
    :param xpos: x-axes position
    :param ypos: y-axis position
    :param text: text in the footnote
    :param color: font color
    :param fontsize: text size for the footnote text
    """
    if not fig:
        return

    use_footnote = text
    if not use_footnote:
        use_footnote = ae_consts.ev(
            'PLOT_FOOTNOTE',
            'algotraders')

    fig.text(
        xpos,
        ypos,
        use_footnote,
        va='bottom',
        fontsize=fontsize,
        color=color)
# end of add_footnote


def set_common_seaborn_fonts():
    """set_common_seaborn_fonts

    Set the font and text style
    """
    sns.set(font='serif')
    sns.set_context(
        'paper',
        rc={
            'font.size': 12,
            'axes.titlesize': 12,
            'axes.labelsize': 10
        }
    )
# end of set_common_seaborn_fonts


def send_final_log(
        log_label,
        fn_name,
        result):
    """send_final_log

    :param log_label: log identifier
    :param fn_name: function name
    :param result: dictionary result
    """

    if not fn_name:
        log.error(
            f'{log_label} missing fn_name parameter for send_final_log')
        return

    if not result:
        log.error(
            f'{log_label} missing result parameter for send_final_log')
        return

    str_result = (
        f'{log_label} - {fn_name} - done '
        f'status={ae_consts.get_status(result["status"])} '
        f'err={result["err"]}')

    if result['status'] == ae_consts.ERR:
        log.error(str_result)
    else:
        log.info(str_result)
    # handle log based off status

# end of send_final_log


def show_with_entities(
        log_label,
        xlabel,
        ylabel,
        title,
        ax,
        fig,
        legend_list=None,
        show_plot=True):
    """show_with_entities

    Helper for showing a plot with a legend and a
    footnoe

    :param log_label: log identifier
    :param xlabel: x-axis label
    :param ylabel: y-axis label
    :param title: title of the plot
    :param ax: axes
    :param fig: figure
    :param legend_list: list of legend items to show
    :param show_plot: bool to show the plot
    """

    log.debug(
        f'{log_label} - '
        'show_with_entities'
        ' - start')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    ax.set_title(title)

    if not legend_list:
        ax.legend(
            loc="best",
            prop={
                "size": "medium"
            }
        )
    else:
        ax.legend(
            legend_list,
            loc="best",
            prop={
                "size": "medium"
            }
        )
    # end of if/else legend entries

    add_footnote(fig)
    plt.tight_layout()

    if show_plot:
        plt.show()
    else:
        plt.plot()
# end of show_with_entities


def plot_overlay_pricing_and_volume(
        log_label,
        ticker,
        df,
        xlabel=None,
        ylabel=None,
        high_color=ae_consts.PLOT_COLORS['high'],
        close_color=ae_consts.PLOT_COLORS['blue'],
        volume_color=ae_consts.PLOT_COLORS['green'],
        date_format=ae_consts.IEX_MINUTE_DATE_FORMAT,
        show_plot=True,
        dropna_for_all=True):
    """plot_overlay_pricing_and_volume

    Plot pricing (high, low, open, close) and volume as
    an overlay off the x-axis

    Here is a sample chart from the
    `Stock Analysis Jupyter Intro Notebook <https://github.com/Al
    goTraders/stock-analysis-engine/blob/master/co
    mpose/docker/notebooks/Stock-Analysis-Intro.ipynb>`__

    .. image:: https://i.imgur.com/pH368gy.png

    :param log_label: log identifier
    :param ticker: ticker name
    :param df: timeseries ``pandas.DateFrame``
    :param xlabel: x-axis label
    :param ylabel: y-axis label
    :param high_color: optional - high plot color
    :param close_color: optional - close plot color
    :param volume_color: optional - volume color
    :param data_format: optional - date format string this must
        be a valid value for the ``df['date']`` column
        that would work with:
        ``datetime.datetime.stftime(date_format)``
    :param show_plot: optional - bool to show the plot
    :param dropna_for_all: optional - bool to toggle keep None's in
        the plot ``df`` (default is drop them
        for display purposes)
    """

    rec = {
        'fig': None,
        'ax': None,
        'ax2': None
    }
    result = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=rec)

    try:

        log.info(
            f'{log_label} - '
            'plot_overlay_pricing_and_volume'
            ' - start')

        set_common_seaborn_fonts()

        use_df = df
        if dropna_for_all:
            log.info(
                f'{log_label} - '
                'plot_overlay_pricing_and_volume'
                ' - dropna_for_all')
            use_df = df.dropna(axis=0, how='any')
        # end of pre-plot dataframe scrubbing

        fig, ax = plt.subplots(
            sharex=True,
            sharey=True,
            figsize=(15.0, 10.0))
        ax.plot(
            use_df['date'],
            use_df['close'],
            color=close_color)
        ax.plot(
            use_df['date'],
            use_df['high'],
            color=high_color)

        # use a second axis to display the
        # volume since it is in a different range
        # this will fill under the
        # volume's y values as well
        ax2 = ax.twinx()
        ax2.plot(
            use_df['date'],
            use_df['volume'],
            linestyle='-',
            color=volume_color,
            alpha=0.6)
        ax2.fill_between(
            use_df['date'].values,
            0,
            use_df['volume'].values,
            color=volume_color,
            alpha=0.5)
        # setup the second plot for volume
        ax2.set_ylim([0, ax2.get_ylim()[1] * 3])

        plt.grid(True)
        use_xlabel = xlabel
        use_ylabel = ylabel
        if not use_xlabel:
            xlabel = 'Minute Dates'
        if not use_ylabel:
            ylabel = f'{ticker} High and Close Prices'
        plt.xlabel(use_xlabel)
        plt.ylabel(use_ylabel)

        # Build a date vs Close DataFrame
        start_date = ''
        end_date = ''
        try:
            start_date = str(use_df.iloc[0]['date'].strftime(date_format))
            end_date = str(use_df.iloc[-1]['date'].strftime(date_format))
        except Exception:
            date_format = '%Y-%m-%d'
            start_date = str(use_df.iloc[0]['date'].strftime(date_format))
            end_date = str(use_df.iloc[-1]['date'].strftime(date_format))

        use_title = (
            f'{ticker} Pricing from: {start_date} to {end_date}')
        ax.set_title(use_title)

        # Merge in the second axis (volume) Legend
        handles, labels = plt.gca().get_legend_handles_labels()
        newLabels, newHandles = [], []
        for handle, label in zip(handles, labels):
            if label not in newLabels:
                newLabels.append(label)
                newHandles.append(handle)
        lines = ax.get_lines() + ax2.get_lines() + newHandles
        ax.legend(
            lines,
            [l.get_label() for l in lines],
            loc='best',
            shadow=True)

        # Build out the xtick chart by the dates
        ax.xaxis.grid(True, which='minor')
        ax.fmt_xdata = mdates.DateFormatter(date_format)
        ax.xaxis.set_major_formatter(ax.fmt_xdata)
        ax.xaxis.set_minor_formatter(ax.fmt_xdata)

        # turn off the grids on volume
        ax2.fmt_xdata = mdates.DateFormatter(date_format)
        ax2.xaxis.grid(False)
        ax2.yaxis.grid(False)
        ax2.yaxis.set_ticklabels([])

        fig.autofmt_xdate()

        show_with_entities(
            log_label=log_label,
            xlabel=xlabel,
            ylabel=ylabel,
            title=use_title,
            ax=ax,
            fig=fig,
            show_plot=show_plot)

        rec['fig'] = fig
        rec['ax'] = ax
        rec['ax2'] = ax2

        result = build_result.build_result(
            status=ae_consts.SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        err = (
            'failed plot_overlay_pricing_and_volume '
            f'and volume with ex={e}')
        result = build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=rec)
    # end of try/ex

    send_final_log(
        log_label=log_label,
        fn_name='plot_overlay_pricing_and_volume',
        result=result)

    return result
# end of plot_overlay_pricing_and_volume


def plot_hloc_pricing(
        log_label,
        ticker,
        df,
        title,
        show_plot=True,
        dropna_for_all=True):
    """plot_hloc_pricing

    Plot the high, low, open and close columns together on a chart

    :param log_label: log identifier
    :param ticker: ticker
    :param df: initialized ``pandas.DataFrame``
    :param title: title for the chart
    :param show_plot: bool to show the plot
    :param dropna_for_all: optional - bool to toggle keep None's in
                           the plot ``df`` (default is drop them
                           for display purposes)
    """

    rec = {
        'ax': None,
        'fig': None
    }
    result = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=rec)

    try:

        log.info(
            f'{log_label} - '
            'plot_hloc_pricing'
            ' - start')

        set_common_seaborn_fonts()

        fig, ax = plt.subplots(
            figsize=(15.0, 10.0))

        use_df = df
        if dropna_for_all:
            log.info(
                f'{log_label} - '
                'plot_hloc_pricing'
                ' - dropna_for_all')
            use_df = df.dropna(axis=0, how='any')
        # end of pre-plot dataframe scrubbing

        plt.plot(
            use_df['date'],
            use_df['high'],
            label='High',
            color=ae_consts.PLOT_COLORS['high'],
            alpha=0.4)
        plt.plot(
            use_df['date'],
            use_df['low'],
            label='Low',
            color=ae_consts.PLOT_COLORS['low'],
            alpha=0.4)
        plt.plot(
            use_df['date'],
            use_df['close'],
            label='Close',
            color=ae_consts.PLOT_COLORS['close'],
            alpha=0.4)
        plt.plot(
            use_df['date'],
            use_df['open'],
            label='Open',
            color=ae_consts.PLOT_COLORS['open'],
            alpha=0.4)

        xlabel = 'Dates'
        ylabel = 'Prices'

        plt.grid(True)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        # Build a date vs Close DataFrame
        start_date = str(use_df.iloc[0]['date'].strftime('%Y-%m-%d'))
        end_date = str(use_df.iloc[-1]['date'].strftime('%Y-%m-%d'))
        if not title:
            title = (
                f'{ticker} Pricing from: {start_date} to {end_date}')
        ax.set_title(title)

        # Build out the xtick chart by the dates
        ax.xaxis.grid(True, which='minor')

        legend_list = [
            'high',
            'low',
            'close',
            'open'
        ]

        fig.autofmt_xdate()
        show_with_entities(
            log_label=log_label,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            ax=ax,
            fig=fig,
            legend_list=legend_list,
            show_plot=show_plot)

        rec['ax'] = ax
        rec['fig'] = fig

        result = build_result.build_result(
            status=ae_consts.SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        err = (
            f'failed plot_hloc_pricing with ex={e}')
        log.error(err)
        result = build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=rec)
    # end of try/ex

    send_final_log(
        log_label=log_label,
        fn_name='plot_hloc_pricing',
        result=result)

    return result
# end of plot_hloc_pricing


def plot_df(
        log_label,
        title,
        column_list,
        df,
        xcol='date',
        xlabel='Date',
        ylabel='Pricing',
        linestyle='-',
        color='blue',
        show_plot=True,
        dropna_for_all=True):
    """plot_df
    :param log_label: log identifier
    :param title: title of the plot
    :param column_list: list of columns in the df to show
    :param df: initialized ``pandas.DataFrame``
    :param xcol: x-axis column in the initialized ``pandas.DataFrame``
    :param xlabel: x-axis label
    :param ylabel: y-axis label
    :param linestyle: style of the plot line
    :param color: color to use
    :param show_plot: bool to show the plot
    :param dropna_for_all: optional - bool to toggle keep None's in
                           the plot ``df`` (default is drop them
                           for display purposes)
    """

    rec = {
        'ax': None,
        'fig': None
    }
    result = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=rec)

    try:

        log.info(
            f'{log_label} - '
            'plot_df'
            ' - start')

        use_df = df
        if dropna_for_all:
            log.info(
                f'{log_label} - '
                'plot_df'
                ' - dropna_for_all')
            use_df = df.dropna(axis=0, how='any')
        # end of pre-plot dataframe scrubbing

        set_common_seaborn_fonts()

        hex_color = ae_consts.PLOT_COLORS['blue']
        fig, ax = plt.subplots(figsize=(15.0, 10.0))

        if linestyle == '-':
            use_df[column_list].plot(
                x=xcol,
                linestyle=linestyle,
                ax=ax,
                color=hex_color,
                rot=0)
        else:
            use_df[column_list].plot(
                kind='bar',
                x=xcol,
                ax=ax,
                color=hex_color,
                rot=0)

        if 'date' in str(xcol).lower():
            # plot the column
            min_date = use_df.iloc[0][xcol]
            max_date = use_df.iloc[-1][xcol]

            # give a bit of space at each end of the plot - aesthetics
            span = max_date - min_date
            extra = int(span.days * 0.03) * datetime.timedelta(days=1)
            ax.set_xlim([min_date - extra, max_date + extra])

            # format the x tick marks
            ax.xaxis.set_minor_formatter(mdates.DateFormatter('%b\n%Y'))
            ax.xaxis.set_major_locator(plt.NullLocator())
            ax.xaxis.set_minor_locator(
                mdates.MonthLocator(
                    bymonthday=1,
                    interval=1))

            # grid, legend and yLabel
            ax.xaxis.grid(True, which='minor')

        # end of date formatting

        show_with_entities(
            log_label=log_label,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            ax=ax,
            fig=fig,
            show_plot=show_plot)

        rec['ax'] = ax
        rec['fig'] = fig

        result = build_result.build_result(
            status=ae_consts.SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        err = (
            f'failed plot_df title={title} with ex={e}')
        result = build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=rec)
    # end of try/ex

    send_final_log(
        log_label=log_label,
        fn_name='plot_df',
        result=result)

    return result
# end of plot_df


def dist_plot(
        log_label,
        df,
        width=10.0,
        height=10.0,
        title='Distribution Plot',
        style='default',
        xlabel='',
        ylabel='',
        show_plot=True,
        dropna_for_all=True):
    """dist_plot

    Show a distribution plot for the passed in dataframe: ``df``

    :param log_label: log identifier
    :param df: initialized ``pandas.DataFrame``
    :param width: width of figure
    :param height: height of figure
    :param style: style to use
    :param xlabel: x-axis label
    :param ylabel: y-axis label
    :param show_plot: bool to show plot or not
    :param dropna_for_all: optional - bool to toggle keep None's in
                           the plot ``df`` (default is drop them
                           for display purposes)
    """

    rec = {}
    result = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=rec)

    try:

        log.info(
            f'{log_label} - '
            'dist_plot'
            ' - start')

        set_common_seaborn_fonts()

        fig, ax = plt.subplots(
            figsize=(width, height))

        if style == 'default':
            sns.set_context('poster')
            sns.axes_style('darkgrid')

        use_df = df
        if dropna_for_all:
            log.info(
                f'{log_label} - '
                'dist_plot'
                ' - dropna_for_all')
            use_df = df.dropna(axis=0, how='any')
        # end of pre-plot dataframe scrubbing

        sns.distplot(
            use_df,
            color=ae_consts.PLOT_COLORS['blue'],
            ax=ax)

        if xlabel != '':
            ax.set_xlabel(xlabel)
        if ylabel != '':
            ax.set_ylabel(ylabel)

        plt.tight_layout()
        plt.subplots_adjust(top=0.9)
        fig.suptitle(title)

        show_with_entities(
            log_label=log_label,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            ax=ax,
            fig=fig,
            show_plot=show_plot)

        rec['ax'] = ax
        rec['fig'] = fig

        result = build_result.build_result(
            status=ae_consts.SUCCESS,
            err=None,
            rec=rec)

    except Exception as e:
        err = (
            f'failed dist_plot title={title} with ex={e}')
        log.error(err)
        result = build_result.build_result(
            status=ae_consts.ERR,
            err=err,
            rec=rec)
    # end of try/ex

    send_final_log(
        log_label=log_label,
        fn_name='dist_plot',
        result=result)

    return result
# end of dist_plot
