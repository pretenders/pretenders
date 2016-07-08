#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

from pretenders import __version__


setup(
    name='pretenders',
    version=__version__,
    description='Fake servers for testing',
    long_description=open('README.rst').read(),
    author='Carles Barrobés, Alex Couper',
    author_email='carles@barrobes.com, amcouper@gmail.com',
    url='https://github.com/pretenders/pretenders',
    packages=find_packages(),
    install_requires=['bottle', 'argparse'],
    include_package_data=True,
    #package_data={
    #    '': ['*.txt', '*.rst'],
    #},
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing',
    ],
)
