TA-Lib Wrappers
===============

The analysis engine includes a wrapper for `talib <https://github.com/mrjbq7/ta-lib>`__. This wrapper imports with:

::

    from analysis_engine.talib import talib
    
Use this wrapper if you want to run unittests that need to access talib functions. This approach is required because not all testing platforms support installing talib. If ``import talib`` fails, then ``import analysis_engine.mocks.mock_talib as talib`` module is loaded instead. This wrapper provides lightweight functions that are compatible with python mocks and replicate the functionality of ``talib``.

.. automodule:: analysis_engine.talib
   :members: BBANDS,EMA,WMA,ADX,MACD,MFI,MOM,ROC,RSI,STOCH,STOCHF,WILLR,Chaikin,ChaikinADOSC,OBV,ATR,NATR,TRANGE
