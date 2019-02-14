Slack Publish API
=================

Want to publish alerts to Slack?

The source code reference guide is below and here is `the intro to publishing alerts to Slack as a Jupyter Notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Stock-Analysis-Intro-Publishing-to-Slack.ipynb>`__.

Send Celery Task Details to Slack Utilities
===========================================

.. automodule:: analysis_engine.send_to_slack
   :members: post_df,post_success,post_failure,post_message,parse_msg,post
