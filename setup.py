#!/usr/bin/env python3
import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "sphinx-xwiki-builder",
    version = "0.1.1",
    author = "Eron Hennessey",
    author_email = "eron@abstrys.com",
    description = "Builds Sphinx documentation source to XWiki-syntax output",
    license = "MIT",
    keywords = "sphinx builder xwiki",
    url = "https://github.com/Abstrys/sphinx-wiki-builder/",
    packages=['abstrys'],
    install_requires=['Sphinx'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
    ],
)
