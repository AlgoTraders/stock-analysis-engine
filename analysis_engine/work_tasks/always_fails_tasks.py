from celery.task import task
from celery_loaders.log.setup_logging import build_colorized_logger
from celery_loaders.work_tasks.custom_task import CustomTask


name = "always_fails_tasks"
log = build_colorized_logger(name=name)


@task(
    bind=True,
    base=CustomTask,
    queue="always_fails")
def always_fails(
        self,
        work_dict):
    """always_fails

    :param work_dict: dictionary for key/values
    """

    label = "always_fails"

    log.info(("task - {} - start "
              "work_dict={}")
             .format(label,
                     work_dict))

    raise Exception(
            work_dict.get(
                "test_failure",
                "simulating a failure"))

    log.info(("task - {} - done")
             .format(label))

    return True
# end of always_fails
