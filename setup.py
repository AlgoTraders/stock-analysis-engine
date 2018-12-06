import os
import sys
import warnings
import unittest

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

"""
https://packaging.python.org/guides/making-a-pypi-friendly-readme/
check the README.rst works on pypi as the
long_description with:
twine check dist/*
"""
long_description = open('README.rst').read()

cur_path, cur_script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(cur_path))

requires_that_fail_on_rtd = [
    'awscli',
    'ta-lib'
]

install_requires = []

cur_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(
        cur_dir, 'requirements.txt'), encoding='utf-8') as f:
    install_requires = f.read().split()

# if not on readthedocs.io or travis ci get all the pips:
if (os.getenv('READTHEDOCS', '') == ''
        and os.getenv('TRAVIS', '') == ''):
    install_requires = install_requires + requires_that_fail_on_rtd

if sys.version_info < (3, 5):
    warnings.warn(
        'Less than Python 3.5 is not supported.',
        DeprecationWarning)


def analysis_engine_test_suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('tests', pattern='test_*.py')
    return test_suite


# Don't import analysis_engine module here, since deps may not be installed
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(__file__),
        'analysis_engine'))

setup(
    name='stock-analysis-engine',
    cmdclass={'build_py': build_py},
    version='1.4.10',
    description=(
        'Build and tune your own investment '
        'algorithms using a distributed, scalable '
        'platform capable of '
        'running many backtests and live-trading '
        'algorithms at the same time on publicly '
        'traded companies with automated datafeeds '
        'from: Yahoo, IEX Real-Time Price, and FinViz '
        '(datafeeds include: pricing, options, news, '
        'dividends, daily, intraday, screeners, '
        'statistics, financials, earnings, and more). '
        'Runs on Kubernetes and docker-compose.'
        ''),
    long_description=long_description,
    author='Jay Johnson',
    author_email='jay.p.h.johnson@gmail.com',
    url='https://github.com/AlgoTraders/stock-analysis-engine',
    packages=[
        'analysis_engine',
        'analysis_engine.iex',
        'analysis_engine.finviz',
        'analysis_engine.mocks',
        'analysis_engine.indicators',
        'analysis_engine.log',
        'analysis_engine.scripts',
        'analysis_engine.work_tasks',
        'analysis_engine.yahoo'
    ],
    package_data={},
    install_requires=install_requires,
    test_suite='setup.analysis_engine_test_suite',
    tests_require=[
    ],
    scripts=[
        'analysis_engine/scripts/fetch_new_stock_datasets.py',
        'analysis_engine/scripts/plot_history_from_local_file.py',
        'analysis_engine/scripts/publish_from_s3_to_redis.py',
        'analysis_engine/scripts/publish_ticker_aggregate_from_s3.py',
        'analysis_engine/scripts/run_backtest_and_plot_history.py',
        'analysis_engine/scripts/sa.py',
        'tools/logs-dataset-collection.sh',
        'tools/logs-jupyter.sh',
        'tools/logs-workers.sh',
        'tools/run-algo-history-to-file.sh',
        'tools/run-algo-history-to-s3.sh',
        'tools/run-algo-report-to-file.sh',
        'tools/run-algo-report-to-s3.sh',
        'tools/ssh-jupyter.sh',
        'tools/ssh-workers.sh',
        'tools/update-stack.sh'
    ],
    entry_points={
        'console_scripts': [
            'sa = sa:run_sa_tool',
            (
                'fetch = fetch_new_stock_datasets'
                ':fetch_new_stock_datasets'),
            (
                'plot-history = '
                'plot_history_from_local_file'
                ':plot_local_history_file'),
            (
                'bt = run_backtest_and_plot_history'
                ':start_backtest_with_plot_history'),
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ])
