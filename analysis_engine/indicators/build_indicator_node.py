"""
Build a single indicator for an algorithm
"""

import uuid
import copy
import analysis_engine.consts as ae_consts
import analysis_engine.utils as ae_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def build_indicator_node(
        node,
        label=None):
    """build_indicator_node

    Parse a dictionary in the algorithm config ``indicators`` list
    and return a dicationry

    Supported values found in:
    `analysis_engine/consts.py <https://github.com/AlgoTraders/sto
    ck-analysis-engine/blob/master/analysis_engine/consts.py>`__

    :param node: single dictionary from the config's ``indicators`` list
    :param label: optional - string log tracking
        this class in the logs (usually just the algo
        name is good enough to help debug issues
        when running distributed)
    :return: dictionary
    """
    if not label:
        label = 'build_indicator_node'

    name = node.get(
        'name',
        None)
    if not name:
        raise Exception(
            '{} - missing "name" in indicator dictionary={}'.format(
                label,
                node))
    # end of name check

    ind_id = str(uuid.uuid4()).replace('-', '')
    uses_dataset_str = node.get(
        'uses_data',
        'daily')
    uses_dataset = ae_consts.get_indicator_uses_data_as_int(
        val=uses_dataset_str)
    if uses_dataset == ae_consts.INDICATOR_USES_DATA_UNSUPPORTED:
        uses_dataset = ae_consts.INDICATOR_USES_DATA_ANY
        log.debug(
            '{} - unsupported indicator '
            'uses_dataset={} defaulting to "daily"'.format(
                label,
                uses_dataset_str))
    # end of supported indicator dataset types

    ind_category_str = node.get(
        'category',
        'momentum')
    ind_category = ae_consts.get_indicator_category_as_int(
        val=ind_category_str)
    if ind_category == ae_consts.INDICATOR_CATEGORY_UNKNOWN:
        ind_category = ae_consts.INDICATOR_CATEGORY_MOMENTUM
        log.debug(
            '{} - unsupported indicator '
            'category={} defaulting to "momentum"'.format(
                label,
                ind_category))
    # end of supported indicator category

    ind_type_str = node.get(
        'type',
        'technical')
    ind_type = ae_consts.get_indicator_type_as_int(
        val=ind_type_str)
    if ind_type == ae_consts.INDICATOR_TYPE_UNKNOWN:
        ind_type = ae_consts.INDICATOR_TYPE_TECHNICAL
        log.debug(
            '{} - unsupported indicator '
            'type={} defaulting to "technical"'.format(
                label,
                ind_type))
    # end of supported indicator type

    # allow easier key discovery
    use_unique_id = node.get(
        'unique_id',
        False)
    ind_name = '{}_{}_{}_{}'.format(
        name,
        ind_category,
        ind_type,
        uses_dataset)
    if use_unique_id:
        ind_name = '{}_{}_{}_{}_{}'.format(
            name,
            ind_category,
            ind_type,
            uses_dataset,
            ind_id)

    use_module_name = None
    use_path_to_module = None

    # none will use the BaseIndicator which does nothing
    use_path_to_module = node.get(
        'module_path',
        ae_consts.INDICATOR_BASE_MODULE_PATH)
    if not use_path_to_module:
        raise Exception(
            'Failed building Indicator node with missing '
            'module_path node={}'.format(
                node))
    use_module_name = node.get(
        'module_name',
        node.get(
            'name',
            ind_id))

    default_report_ignore_keys = \
        ae_consts.INDICATOR_IGNORED_CONIGURABLE_KEYS

    report_dict = {
        'id': ind_id,
        'name': ind_name,
        'created': ae_utils.utc_now_str(),
        'version': 1,
        'module_name': use_module_name,
        'path_to_module': use_path_to_module,
        'report_ignore_keys': default_report_ignore_keys,
        'metrics': {
            'type': ind_type,
            'category': ind_category,
            'uses_data': uses_dataset
        }
    }

    labeled_node = copy.deepcopy(node)

    # allow a node's sub report dir to be patched with this
    # tracking + reporting data
    # the algorithms will flatten:
    #    indicators[ind_name]['report']['metrics']
    # for trading performance report generation
    if 'report' in labeled_node:
        labeled_node['report'].update(report_dict)
    else:
        labeled_node['report'] = report_dict

    return labeled_node
# end of build_indicator_node
