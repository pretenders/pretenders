#!/usr/bin/env python
# coding: utf-8

from setuptools import setup, find_packages

from pretenders import __version__


setup(
    name='pretenders',
    version=__version__,
    summary='Fake servers for testing',
    description=open('README.rst').read(),
    author='Carles Barrobés',
    author_email='carles@barrobes.com',
    url='https://github.com/txels/pretenders',
    packages=find_packages(),
    install_requires=['bottle'],
    #include_package_data=True,
    #package_data={
    #    '': ['*.txt', '*.rst'],
    #},
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Testing',
    ],
)
