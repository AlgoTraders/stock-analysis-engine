"""
Plot a ``Trading History`` dataset using seaborn and matplotlib
"""

import datetime
import matplotlib.pyplot as plt
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import analysis_engine.charts as ae_charts
import analysis_engine.build_result as build_result
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def plot_trading_history(
        title,
        df,
        red,
        red_color=None,
        red_label=None,
        blue=None,
        blue_color=None,
        blue_label=None,
        green=None,
        green_color=None,
        green_label=None,
        orange=None,
        orange_color=None,
        orange_label=None,
        date_col='date',
        xlabel='Date',
        ylabel='Algo Values',
        linestyle='-',
        width=15.0,
        height=15.0,
        date_format='%d\n%b',
        df_filter=None,
        start_date=None,
        footnote_text=None,
        footnote_xpos=0.70,
        footnote_ypos=0.01,
        footnote_color='#888888',
        footnote_fontsize=8,
        scale_y=False,
        show_plot=True,
        dropna_for_all=False,
        verbose=False):
    """plot_trading_history

    Plot columns up to 4 lines from the ``Trading History`` dataset

    :param title: title of the plot
    :param df: dataset which is ``pandas.DataFrame``
    :param red: string - column name to plot in
        ``red_color`` (or default ``ae_consts.PLOT_COLORS[red]``)
        where the column is in the ``df`` and
        accessible with:``df[red]``
    :param red_color: hex color code to plot the data in the
        ``df[red]``  (default is ``ae_consts.PLOT_COLORS['red']``)
    :param red_label: optional - string for the label used
        to identify the ``red`` line in the legend
    :param blue: string - column name to plot in
        ``blue_color`` (or default ``ae_consts.PLOT_COLORS['blue']``)
        where the column is in the ``df`` and
        accessible with:``df[blue]``
    :param blue_color: hex color code to plot the data in the
        ``df[blue]``  (default is ``ae_consts.PLOT_COLORS['blue']``)
    :param blue_label: optional - string for the label used
        to identify the ``blue`` line in the legend
    :param green: string - column name to plot in
        ``green_color`` (or default ``ae_consts.PLOT_COLORS['darkgreen']``)
        where the column is in the ``df`` and
        accessible with:``df[green]``
    :param green_color: hex color code to plot the data in the
        ``df[green]``  (default is ``ae_consts.PLOT_COLORS['darkgreen']``)
    :param green_label: optional - string for the label used
        to identify the ``green`` line in the legend
    :param orange: string - column name to plot in
        ``orange_color`` (or default ``ae_consts.PLOT_COLORS['orange']``)
        where the column is in the ``df`` and
        accessible with:``df[orange]``
    :param orange_color: hex color code to plot the data in the
        ``df[orange]``  (default is ``ae_consts.PLOT_COLORS['orange']``)
    :param orange_label: optional - string for the label used
        to identify the ``orange`` line in the legend
    :param date_col: string - date column name
        (default is ``date``)
    :param xlabel: x-axis label
    :param ylabel: y-axis label
    :param linestyle: style of the plot line
    :param width: float - width of the image
    :param height: float - height of the image
    :param date_format: string - format for dates
    :param df_filter: optional - initialized ``pandas.DataFrame`` query
        for reducing the ``df`` records before plotting. As an eaxmple
        ``df_filter=(df['close'] > 0.01)`` would find only records in
        the ``df`` with a ``close`` value greater than ``0.01``
    :param start_date: optional - string ``datetime``
        for plotting only from a date formatted as
        ``YYYY-MM-DD HH\:MM\:SS``
    :param footnote_text: optional - string footnote text
        (default is ``algotraders <DATE>``)
    :param footnote_xpos: optional - float for footnote position
        on the x-axies
        (default is ``0.75``)
    :param footnote_ypos: optional - float for footnote position
        on the y-axies
        (default is ``0.01``)
    :param footnote_color: optional - string hex color code for
        the footnote text
        (default is ``#888888``)
    :param footnote_fontsize: optional - float footnote font size
        (default is ``8``)
    :param scale_y: optional - bool to scale the y-axis with
        .. code-block:: python

            use_ax.set_ylim(
                [0, use_ax.get_ylim()[1] * 3])
    :param show_plot: bool to show the plot
    :param dropna_for_all: optional - bool to toggle keep None's in
        the plot ``df`` (default is drop them for display purposes)
    :param verbose: optional - bool to show logs for debugging
        a dataset
    """

    rec = {
        'ax1': None,
        'ax2': None,
        'ax3': None,
        'ax4': None,
        'fig': None
    }
    result = build_result.build_result(
        status=ae_consts.NOT_RUN,
        err=None,
        rec=rec)

    if verbose:
        log.info('plot_trading_history - start')

    use_red = red_color
    use_blue = blue_color
    use_green = green_color
    use_orange = orange_color

    if not use_red:
        use_red = ae_consts.PLOT_COLORS['red']
    if not use_blue:
        use_blue = ae_consts.PLOT_COLORS['blue']
    if not use_green:
        use_green = ae_consts.PLOT_COLORS['darkgreen']
    if not use_orange:
        use_orange = ae_consts.PLOT_COLORS['orange']

    use_footnote = footnote_text
    if not use_footnote:
        use_footnote = (
            'algotraders - {}'.format(
                datetime.datetime.now().strftime(
                    ae_consts.COMMON_TICK_DATE_FORMAT)))

    column_list = [
        date_col
    ]
    all_plots = []
    if red:
        column_list.append(red)
        all_plots.append({
            'column': red,
            'color': use_red})
    if blue:
        column_list.append(blue)
        all_plots.append({
            'column': blue,
            'color': use_blue})
    if green:
        column_list.append(green)
        all_plots.append({
            'column': green,
            'color': use_green})
    if orange:
        column_list.append(orange)
        all_plots.append({
            'column': orange,
            'color': use_orange})

    use_df = df
    if start_date:
        start_date_value = datetime.datetime.strptime(
            start_date,
            ae_consts.COMMON_TICK_DATE_FORMAT)
        use_df = df[(df[date_col] >= start_date_value)][column_list]
    # end of filtering by start date

    if verbose:
        log.info(
            'plot_history_df start_date={} df.index={} column_list={}'.format(
                start_date,
                len(use_df.index),
                column_list))

    if hasattr(df_filter, 'to_json'):
        # Was seeing this warning below in Jupyter:
        # UserWarning: Boolean Series key
        # will be reindexed to match DataFrame index
        # use_df = use_df[df_filter][column_list]
        # now using:
        use_df = use_df.loc[df_filter, column_list]

    if verbose:
        log.info(
            'plot_history_df filter df.index={} column_list={}'.format(
                start_date,
                len(use_df.index),
                column_list))

    if dropna_for_all:
        use_df = use_df.dropna(axis=0, how='any')
        if verbose:
            log.info('plot_history_df dropna_for_all')
    # end of pre-plot dataframe scrubbing

    ae_charts.set_common_seaborn_fonts()

    hex_color = ae_consts.PLOT_COLORS['blue']
    fig, ax = plt.subplots(
        sharex=True,
        sharey=True,
        figsize=(
            width,
            height))

    # Convert matplotlib date numbers to strings for dates to
    # avoid dealing with weekend date gaps in plots
    date_strings, date_labels = \
        ae_utils.get_trade_open_xticks_from_date_col(
            use_df[date_col])

    """
    hit the slice warning with this approach before
    and one trying df[date_col] = df[date_col].dt.strftime

    SettingWithCopyWarning
    Try using .loc[row_indexer,col_indexer] = value instead

    use_df[date_col].replace(
        use_df[date_col].dt.strftime(
            ae_consts.COMMON_TICK_DATE_FORMAT),
        inplace=True)
    trying this:
    https://stackoverflow.com/questions/19738169/
    convert-column-of-date-objects-in-pandas-dataframe-to-strings
    """
    use_df[date_col] = use_df[date_col].apply(lambda x: x.strftime(
        ae_consts.COMMON_TICK_DATE_FORMAT))

    all_axes = []
    num_plots = len(all_plots)
    for idx, node in enumerate(all_plots):
        column_name = node['column']
        hex_color = node['color']

        use_ax = ax
        if idx > 0:
            use_ax = ax.twinx()

        if verbose:
            log.info(
                'plot_history_df - {}/{} - {} in {} - ax={}'.format(
                    (idx + 1),
                    num_plots,
                    column_name,
                    hex_color,
                    use_ax))

        all_axes.append(use_ax)
        use_ax.plot(
            use_df[date_col],
            use_df[column_name],
            linestyle=linestyle,
            color=hex_color)
        if idx > 0:
            if scale_y:
                use_ax.set_ylim(
                    [0, use_ax.get_ylim()[1] * 3])
            use_ax.yaxis.set_ticklabels([])
            use_ax.yaxis.set_ticks([])
            use_ax.xaxis.grid(False)
            use_ax.yaxis.grid(False)
        # end if this is not the fist axis

        use_ax.set_xticks(date_strings)
        use_ax.set_xticklabels(date_labels, rotation=45, ha='right')
    # end of for all plots

    lines = []
    for idx, cur_ax in enumerate(all_axes):
        ax_lines = cur_ax.get_lines()
        for line in ax_lines:
            label_name = str(line.get_label())
            use_label = label_name
            if idx == 0:
                if red_label:
                    use_label = red_label
            elif idx == 1:
                if blue_label:
                    use_label = blue_label
            elif idx == 2:
                use_label = label_name[-20:]
                if green_label:
                    use_label = green_label
            elif idx == 3:
                use_label = label_name[-20:]
                if orange_label:
                    use_label = orange_label
            else:
                if len(label_name) > 10:
                    use_label = label_name[-20:]
            # end of fixing the labels in the legend
            line.set_label(use_label)
            if line.get_label() not in lines:
                lines.append(line)
        rec['ax{}'.format(idx + 1)] = cur_ax
    # end of compiling a new-shortened legend while removing dupes

    for idx, cur_ax in enumerate(all_axes):
        if cur_ax:
            if cur_ax.get_legend():
                cur_ax.get_legend().remove()
    # end of removing all previous legends

    if verbose:
        log.info(
            'legend lines={}'.format(
                [l.get_label() for l in lines]))
    # log what's going to be in the legend

    ax.legend(
        lines,
        [l.get_label() for l in lines],
        loc='best',
        shadow=True)

    fig.autofmt_xdate()

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    ax.set_title(title)
    ae_charts.add_footnote(
        fig=fig,
        xpos=footnote_xpos,
        ypos=footnote_ypos,
        text=use_footnote,
        color=footnote_color,
        fontsize=footnote_fontsize)
    plt.tight_layout()

    plt.show()
    if show_plot:
        plt.show()
    else:
        plt.plot()

    rec['fig'] = fig

    result = build_result.build_result(
        status=ae_consts.SUCCESS,
        err=None,
        rec=rec)

    return result
# end of plot_history_df
