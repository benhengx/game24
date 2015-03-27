
from setuptools import setup

import sys
import game24


if sys.version_info[:2] < (2, 7):
    install_requires = ['argparse']
else:
    install_requires = []

setup(
    name = game24.__title__,
    version = game24.__version__,
    description = game24.__summary__,
    long_description = open('README.rst').read(),
    license = game24.__license__,
    url = game24.__url__,
    author = game24.__author__,
    author_email = game24.__email__,

    packages = ['game24'],

    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: BSD",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        'Topic :: Games/Entertainment :: Puzzle Games',
    ],

    entry_points = {
        'console_scripts': [
            '24gameconsole = game24.24gameconsole:main',
        ],
    },

    install_requires = install_requires
)

