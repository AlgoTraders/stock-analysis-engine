"""
Custom Celery Task Handling
===========================

Define your own ``on_failure`` and ``on_success``
with the ``analysis_engine.work_tasks.custom_task.CustomTask`` custom
class object.

Debug values with the environment variable:

::

    export DEBUG_TASK=1

"""

import celery
import analysis_engine.consts as ae_consts
import analysis_engine.send_to_slack as slack_utils
import spylunking.log.setup_logging as log_utils

log = log_utils.build_colorized_logger(name=__name__)


class CustomTask(celery.Task):
    """CustomTask"""

    log_label = 'custom_task'

    def build_log_label_from_args(
            self,
            args):
        """build_log_label_from_args

        :param args: list of celery args
        """
        if not args:
            return
        if len(args) > 0:
            self.log_label = f'''label=[{args[0].get(
                'label',
                args[0].get(
                    'name',
                    self.name))}]'''
        else:
            return
    # end of build_log_label_from_args

    def on_success(
            self,
            retval,
            task_id,
            args,
            kwargs):
        """on_success

        Handle custom actions when a task completes
        successfully.

        http://docs.celeryproject.org/en/latest/reference/celery.app.task.html

        :param retval: return value
        :param task_id: celery task id
        :param args: arguments passed into task
        :param kwargs: keyword arguments passed into task
        """

        self.build_log_label_from_args(
            args=args)

        if ae_consts.ev('DEBUG_TASK', '0') == '1':
            log.info(
                f'on_success {self.log_label} - retval={retval} '
                f'task_id={task_id} args={args} kwargs={kwargs}')
        else:
            log.info(f'on_success {self.log_label} - task_id={task_id}')
    # end of on_success

    def on_failure(
            self,
            exc,
            task_id,
            args,
            kwargs,
            einfo):
        """on_failure

        Handle custom actions when a task completes
        not successfully. As an example, if the task throws an
        exception, then this ``on_failure`` method can
        customize how to handle **exceptional** cases.

        http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-inheritance

        :param exc: exception
        :param task_id: task id
        :param args: arguments passed into task
        :param kwargs: keyword arguments passed into task
        :param einfo: exception info
        """

        self.build_log_label_from_args(
            args=args)

        use_exc = str(exc)
        if ae_consts.ev('DEBUG_TASK', '0') == '1':
            log.error(
                f'on_failure {self.log_label} - exc={use_exc} '
                f'args={args} kwargs={kwargs}')
        else:
            log.error(f'on_failure {self.log_label} - exc={use_exc}')
        if ae_consts.ev('PROD_SLACK_ALERTS', '0') == '1':
            slack_utils.post_failure([f'on_failure {self.log_label}',
                                      f'exc={use_exc}'])
    # end of on_failure

# end of CustomTask
