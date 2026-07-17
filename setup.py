#!/usr/bin/env python

# read the contents of your README file
from os import path

from setuptools import setup

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="screenplain",
    version="0.12.0",
    description="Convert text file to viewable screenplay.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Martin Vilcans",
    author_email="screenplain@librador.com",
    url="http://www.screenplain.com/",
    project_urls={
        "Web Page": "http://www.screenplain.com/",
        "Source": "https://github.com/vilcans/screenplain",
    },
    license="MIT",
    install_requires=["reportlab"],
    packages=[
        "screenplain",
        "screenplain.export",
        "screenplain.parsers",
    ],
    package_data={"screenplain.export": ["default.css", "courier_prime/**"]},
    entry_points={"console_scripts": ["screenplain = screenplain.main:cli"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
