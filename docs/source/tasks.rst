Celery Worker Tasks
===================

Celery tasks are automatically processed by the workers. You can turn off celery task publishing by setting the environment variable ``CELERY_DISABLED`` is set to ``1`` (by default celery is enabled for task publishing).

.. tip:: all tasks share the `analysis_engine.work_tasks.custom_task.CustomTask class <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/work_tasks/custom_task.py>`__ for customizing event handling.

.. automodule:: analysis_engine.work_tasks.handle_pricing_update_task
    :members: run_handle_pricing_update_task,handle_pricing_update_task

.. automodule:: analysis_engine.work_tasks.get_new_pricing_data
    :members: run_get_new_pricing_data,get_new_pricing_data

.. automodule:: analysis_engine.work_tasks.publish_pricing_update
    :members: run_publish_pricing_update,publish_pricing_update

.. automodule:: analysis_engine.work_tasks.publish_from_s3_to_redis
    :members: run_publish_from_s3_to_redis,publish_from_s3_to_redis

.. automodule:: analysis_engine.work_tasks.prepare_pricing_dataset
    :members: run_prepare_pricing_dataset,prepare_pricing_dataset

.. automodule:: analysis_engine.work_tasks.custom_task
    :members: CustomTask
