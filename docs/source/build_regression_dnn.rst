Build a Deep Neural Network for Predicting Future Prices
========================================================

You can use a **KerasRegressor** to build a deep neural network (dnn) for trying to predict a future closing price from a ``Trading History dataset`` (jupyter notebook coming soon).

This function is used as a `Keras Scikit-Learn Builder Function <https://keras.io/scikit-learn-api/#wrappers-for-the-scikit-learn-api>`__ for creating a `Keras Sequential deep neural network model (dnn) <https://keras.io/models/sequential/>`__. This function is `used as an argument (build_fn) for creating a KerasRegressor or KerasClassifier <https://keras.io/scikit-learn-api/#arguments>`__.

For how to use this module please refer to:

- `Train a Deep Neural Network For Predicting a Stock's Closing Price in a Jupyter Notebook <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/compose/docker/notebooks/Train-a-Deep-Neural-Network-For-Predicting-a-Stocks-Closing-Price.ipynb.ipynb>`__
- `train_dnn_from_history.py script <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/scripts/train_dnn_from_history.py>`__

Until ``tensorflow`` and ``keras`` work on Read the Docs, please refer to the `build_regression_dnn.py source code <https://github.com/AlgoTraders/stock-analysis-engine/blob/master/analysis_engine/ai/build_regression_dnn.py>`__

.. automodule:: analysis_engine.ai.build_regression_dnn
   :members: build_regression_dnn
