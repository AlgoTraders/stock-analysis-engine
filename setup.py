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

long_description = ''
try:
    import pypandoc
    long_description = pypandoc.convert(
        'README.rst',
        'rst')
except(IOError, ImportError):
    long_description = open('README.rst').read()

cur_path, cur_script = os.path.split(sys.argv[0])
os.chdir(os.path.abspath(cur_path))

requires_that_fail_on_rtd = [
    'awscli'
]

install_requires = [
    'antinex-client',
    'celery-connectors',
    'celery-loaders',
    'colorlog',
    'coverage',
    'flake8<=3.4.1',
    'future',
    'mock',
    'pandas',
    'pep8>=1.7.1',
    'pinance',
    'pypandoc',
    'pycodestyle<=2.3.1',
    'pylint',
    'recommonmark',
    'redis',
    'sphinx',
    'sphinx-autobuild',
    'sphinx_rtd_theme',
    'spylunking',
    'unittest2'
]

# if not on readthedocs.io get all the pips:
if os.getenv("READTHEDOCS", "") == "":
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
    version='1.0.5',
    description=(
        'Stock Analysis Engine - '
        'Use this to get pricing data for tickers '
        '(news, quotes and options right now) and '
        'archive it in s3 (using minio) and cache '
        'it in redis. Analysis tasks coming soon!'),
    long_description=long_description,
    author='Jay Johnson',
    author_email='jay.p.h.johnson@gmail.com',
    url='https://github.com/AlgoTraders/stock-analysis-engine',
    packages=[
        'analysis_engine',
        'analysis_engine.log',
        'analysis_engine.scripts',
        'analysis_engine.work_tasks',
    ],
    package_data={},
    install_requires=install_requires,
    test_suite='setup.analysis_engine_test_suite',
    tests_require=[
    ],
    scripts=[
        'analysis_engine/scripts/publish_from_s3_to_redis.py',
        'analysis_engine/scripts/run_ticker_analysis.py',
        'analysis_engine/scripts/sa.py'
    ],
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
