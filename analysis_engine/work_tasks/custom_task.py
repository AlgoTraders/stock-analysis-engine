"""
Custom Celery task event handling

Debug values with the environment variable:

::

    export DEBUG_TASK=1

"""

import celery
from spylunking.log.setup_logging import build_colorized_logger
from analysis_engine.consts import ev

log = build_colorized_logger(
    name=__name__)


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
            self.log_label = 'label=[{}]'.format(args[0].get(
                'label',
                self.log_label))
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

        http://docs.celeryproject.org/en/latest/reference/celery.app.task.html

        :param retval: return value
        :param task_id: celery task id
        :param args: arguments passed into task
        :param kwargs: keyword arguments passed into task
        """

        self.build_log_label_from_args(
            args=args)

        if ev('DEBUG_TASK', '0') == '1':
            log.info(
                'on_success {} - retval={} task_id={} '
                'args={} kwargs={}'.format(
                    self.log_label,
                    retval,
                    task_id,
                    args,
                    kwargs))
        else:
            log.info(
                'on_success {} - task_id={}'.format(
                    self.log_label,
                    task_id))
    # end of on_success

    def on_failure(
            self,
            exc,
            task_id,
            args,
            kwargs,
            einfo):
        """on_failure

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
        if ev('DEBUG_TASK', '0') == '1':
            log.error(
                'on_failure {} - exc={} '
                'args={} kwargs={}'.format(
                    self.log_label,
                    use_exc,
                    args,
                    kwargs))
        else:
            log.error(
                'on_failure {} - exc={} '.format(
                    self.log_label,
                    use_exc))
    # end of on_failure

# end of CustomTask
