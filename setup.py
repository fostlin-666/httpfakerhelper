#! /usr/bin/env python
# -*- coding: utf-8 -*_
# Author: guolong<565169745@qq.com>
from distutils.core import setup
import setuptools
import os
import codecs
import re

DESCRIPTION = ''
AUTHOR = ''
URL = ''
VERSION = ''
EMAIL_URL = ''

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), encoding='utf-8').read()


def find_config(*file_paths):
    config_file = read(*file_paths)
    global VERSION, DESCRIPTION, URL, AUTHOR, EMAIL_URL
    VERSION = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                        config_file, re.M).group(1)
    DESCRIPTION = re.search(r"^__description__ = ['\"]([^'\"]*)['\"]",
                            config_file, re.M).group(1)
    AUTHOR = re.search(r"^__author__ = ['\"]([^'\"]*)['\"]",
                       config_file, re.M).group(1)
    URL = re.search(r"^__url__ = ['\"]([^'\"]*)['\"]",
                    config_file, re.M).group(1)
    EMAIL_URL = re.search(r"^__author_email__ = ['\"]([^'\"]*)['\"]",
                    config_file, re.M).group(1)


with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

find_config('httpfaker/utils/constant.py')

setup(
    name='httpfaker',
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL_URL,
    url=URL,
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={'console_scripts': [
        'httpfaker = httpfaker.cli:httpfaker',
        'http2api = httpfaker.cli:http2api',
        'swagger2api = httpfaker.cli:swagger2api'
    ]},
    install_requires=[
        'PyMySQL==1.0.2',
        'PyYAML==6.0',
        'pypinyin==0.46.0',
        'Faker==13.15.0',
        'Jinja2==2.11.3',
        'SQLAlchemy==1.4.39',
        'dbutils==3.0.2',
        'flask==1.1.4',
        'requests==2.28.1'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ],
    zip_safe=True,
)
