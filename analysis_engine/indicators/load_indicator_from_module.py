"""
Helper for loading derived Indicators from a local module file
"""

import os
import inspect
import types
import importlib.machinery
import uuid
import analysis_engine.consts as ae_consts
import analysis_engine.indicators.base_indicator as base_indicator
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


def load_indicator_from_module(
        module_name,
        ind_dict,
        path_to_module=None,
        log_label=None,
        base_class_module_name='BaseIndicator',
        verbose=False):
    """load_indicator_from_module

    Load a custom indicator from a file

    :param module_name: string name of the indicator module
        use in to load the module
    :param path_to_module: optional - path to custom indicator file
        (default is to use the
        ``analysis_engine.indicators.base_indicator.BaseIndicator`` or
        if set the ``ind_dict['module_path']`` value)
    :param ind_dict: dictionary of keyword arguments
        to pass to the newly created derived Indicator's
        constructor
    :param log_label: optional - log tracking label
        for helping to find this indicator's logs
        (if not set the default name is the
        ``module_name`` string value)
    :param base_class_module_name: optional - string name
        for using a non-standard indicator base class
    :param verbose: optional - bool for more logging
        (default is ``False``)
    """

    default_base_module_path = ae_consts.INDICATOR_BASE_MODULE_PATH

    # modules need custom names to prevent
    # runtime collisions/module stomping
    # this allows building multiple indicator objects
    # that use the same filename but in different
    # locations on disk
    use_module_name = (
        f'{module_name}_{str(uuid.uuid4())[0:8].replace("-", "")}')

    use_log_label = log_label
    if not use_log_label:
        use_log_label = use_module_name

    if not path_to_module:
        path_to_module = ind_dict.get(
            'module_path',
            None)

    if 'verbose' not in ind_dict:
        ind_dict['verbose'] = verbose

    if not path_to_module:
        return base_indicator.BaseIndicator(
            config_dict=ind_dict,
            name=use_log_label,
            path_to_module=default_base_module_path)

    if not os.path.exists(path_to_module):
        raise Exception(
            f'{use_module_name} - did not find Indicator module at '
            f'path={path_to_module} please confirm the file exists on disk '
            'and if you are using a container, confirm it is '
            'accessible within the container')

    loader = importlib.machinery.SourceFileLoader(
        use_module_name,
        path_to_module)
    custom_indicator_module = types.ModuleType(
        loader.name)
    loader.exec_module(
        custom_indicator_module)

    found_base_object = False
    class_member_in_module = None
    for member in inspect.getmembers(custom_indicator_module):
        if module_name in str(member):
            found_base_object = True
            class_member_in_module = member
            break
    # for all members in this custom module file

    if not found_base_object:
        raise Exception(
            f'{use_module_name} load_indicator_from_module error - '
            f'did not find Indicator with base class={base_class_module_name} '
            f'from module at path={path_to_module} - please confirm '
            'the file has just one class that '
            'inherits from the base Indicator class: '
            'analysis_engine.indicators.base_indicator.BaseIndicator '
            'and try again')

        err = (
            f'{use_module_name} load_indicator_from_module error - '
            'unable to find custom indicator derived from '
            f'module={base_class_module_name} at file path={path_to_module}')
        if path_to_module:
            err = (
                f'{use_module_name} load_indicator_from_module error - '
                'analysis_engine.indicators.base_indicator.BaseIndicator '
                'was unable to find custom Indicator '
                f'module={custom_indicator_module} with provided path to \n '
                f'file: {path_to_module} \n'
                '\n'
                'Please confirm '
                'that the class inherits from the BaseIndicator '
                'class like:\n'
                '\n'
                'import analysis_engine.indicators.base_indicator '
                'as base_ind\n'
                'class MyIndicator(base_ind.BaseIndicator):\n'
                '\n'
                'If it is then please file an issue on github:\n '
                'https://github.com/AlgoTraders/stock-analysis-engine/'
                'issues/new \n\nFor now this error results in a shutdown'
                '\n')
        log.error(err)
        raise Exception(err)
    # end of if did not find the module with the correct Base Class

    if ind_dict.get('verbose', False):
        log.info(
            f'load - custom indicator module={use_module_name} '
            f'from file={path_to_module} member={class_member_in_module}')
    ind = class_member_in_module[1](
        config_dict=ind_dict,
        name=use_log_label,
        path_to_module=path_to_module)
    if ind_dict.get('verbose', False):
        log.info(
            f'ready - custom indicator={ind.__class__.__name__} from '
            f'module={use_module_name} from file={path_to_module} '
            f'member={class_member_in_module}')

    return ind
# end of load_indicator_from_module
