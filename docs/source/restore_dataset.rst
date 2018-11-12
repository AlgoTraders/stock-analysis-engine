Dataset Tools - Restore Dataset from an Algorithm-Ready File
============================================================

``analysis_engine.restore_dataset.restore_dataset`` will load a dataset from a file, s3 or redis and merge any missing records back in to redis. Use this to restore missing dataset values after a host goes offline or on a fresh install or redis server restart or redis flush.

.. automodule:: analysis_engine.restore_dataset
   :members: restore_dataset
