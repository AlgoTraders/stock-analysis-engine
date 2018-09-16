broker_url = "redis://localhost:6379/9"
result_backend = "redis://localhost:6379/10"

# http://docs.celeryproject.org/en/latest/userguide/optimizing.html

# these are targeted at optimizing processing
# on long-running tasks
# while increasing reliability

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-worker_prefetch_multiplier  # noqa
worker_prefetch_multiplier = 1

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_heartbeat  # noqa
broker_heartbeat = 240  # seconds

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_connection_max_retries  # noqa
broker_connection_max_retries = None

# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-task_acks_late  # noqa
task_acks_late = True

# http://docs.celeryproject.org/en/latest/userguide/calling.html#calling-retry
task_publish_retry_policy = {
    "interval_max": 1,
    "max_retries": 120,     # None = forever
    "interval_start": 0.1,
    "interval_step": 0.2}

task_serializer = "json"
result_serializer = "json"
accept_content = ["json"]
timezone = "America/Los_Angeles"

task_routes = {
    "run.check_values": "low-priority",
    "run.calculate_results": "high-priority"}
