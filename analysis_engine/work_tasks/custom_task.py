import celery
from spylunking.log.setup_logging import build_colorized_logger


name = 'custom_task'
log = build_colorized_logger(
    name=name)


class CustomTask(celery.Task):

    log_label = 'custom_task'

    def on_success(self, retval, task_id, args, kwargs):
        '''on_success

        http://docs.celeryproject.org/en/latest/reference/celery.app.task.html

        :param retval: return value
        :param task_id: celery task id
        :param args: arguments passed into task
        :param kwargs: keyword arguments passed into task
        '''
        log.info((
            '{} SUCCESS - retval={} task_id={} '
            'args={} kwargs={}').format(
                self.log_label,
                retval,
                task_id,
                args,
                kwargs))
    # end of on_success

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        '''on_failure

        http://docs.celeryproject.org/en/latest/userguide/tasks.html#task-inheritance

        :param exc: exception
        :param task_id: task id
        :param args: arguments passed into task
        :param kwargs: keyword arguments passed into task
        :param einfo: exception info
        '''
        use_exc = str(exc)
        log.error((
            '{} FAIL - exc={} '
            'args={} kwargs={}').format(
                self.log_label,
                use_exc,
                args,
                kwargs))
    # end of on_failure

# end of CustomTask
