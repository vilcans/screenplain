#!/usr/bin/env python

from setuptools import setup

setup(
    name='screenplain',
    version='0.8.0',
    description='Convert text file to viewable screenplay.',
    author='Martin Vilcans',
    author_email='screenplain@librador.com',
    url='http://www.screenplain.com/',
    project_urls={
        'Web Page': 'http://www.screenplain.com/',
        'Source': 'https://github.com/vilcans/screenplain',
    },
    license='MIT',
    install_requires=[
    ],
    extras_require={
        'PDF': 'reportlab'
    },
    packages=[
        'screenplain',
        'screenplain.export',
        'screenplain.parsers',
    ],
    package_data={
        'screenplain.export': ['default.css']
    },
    scripts=[
        'bin/screenplain'
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
