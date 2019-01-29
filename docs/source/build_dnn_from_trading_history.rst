AI - Building and Tuning Deep Neural Networks for Predicting Future Prices
==========================================================================

.. image:: https://i.imgur.com/tw2wJ6t.png

The following notebooks, script and modules are guides for building **KerasRegressor** models, deep neural networks (dnn), for trying to predict a stock's future closing price from a ``Trading History`` dataset. The tools use a ``Trading History`` dataset that was created and automatically published to S3 after processing a trading algorithm's backtest of custom indicators analyzed intraday minute-by-minute pricing data stored in redis.

If you do not have a ``Trading History`` you can create one with:

::

    ae -t SPY -p s3://algohistory/algo_training_SPY.json

and run it distributed across the engine's workers with ``-w``

::

    ae -w -t SPY -p s3://algohistory/algo_training_SPY.json

Here are examples on training a dnn's using a ``Trading History`` from S3 (Minio or AWS):

- `Comparing 3 Deep Neural Networks Trained to Predict a Stocks Closing Price in a Jupyter Notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Comparing-3-Deep-Neural-Networks-Trained-to-Predict-a-Stocks-Closing-Price-Using-The-Analysis-Engine.ipynb>`__
- `Train a Deep Neural Network For Predicting a Stock's Closing Price in a Jupyter Notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Train-a-Deep-Neural-Network-For-Predicting-a-Stocks-Closing-Price.ipynb>`__
- `train_dnn_from_history.py script <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/train_dnn_from_history.py>`__

AI - Building a Deep Neural Network Helper Module
=================================================

This function is used as a `Keras Scikit-Learn Builder Function <https://keras.io/scikit-learn-api/#wrappers-for-the-scikit-learn-api>`__ for creating a `Keras Sequential deep neural network model (dnn) <https://keras.io/models/sequential/>`__. This function is `passed in as the build_fn argument to create a KerasRegressor (or KerasClassifier) <https://keras.io/scikit-learn-api/#arguments>`__.

.. automodule:: analysis_engine.ai.build_regression_dnn
   :members: build_regression_dnn

AI - Training Dataset Helper Modules
====================================

These modules are included to help build new training datasets. It looks like read the docs does not support keras, sklearn or tensorflow for generating sphinx docs so here are links to the repository's source code:

- `Build Train and Test Datasets using Scaler Normalization <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/ai/build_datasets_using_scalers.py>`__

.. automodule:: analysis_engine.ai.build_datasets_using_scalers
   :members: build_datasets_using_scalers

- `Build a Scaler Normalized Dataset from a pandas DataFrame <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/ai/build_datasets_using_scalers.py>`__

.. automodule:: analysis_engine.ai.build_scaler_dataset_from_df
   :members: build_scaler_dataset_from_df

AI - Plot Deep Neural Network Fit History
=========================================

.. automodule:: analysis_engine.ai.plot_dnn_fit_history
   :members: plot_dnn_fit_history
