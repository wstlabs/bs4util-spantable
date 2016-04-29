import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "bs4util-spantable",
    version = "0.0.1",
    author = "wstlabs",
    author_email = "wst@pobox.com",
    description = ("A BS4 utility class for parsing complex HTML5 tables"), 
    license = "BSD",
    keywords = "beautiful soup bs4 html5 table colspan rowspan",
    url = "http://packages.python.org/bs4util-spantable",
    packages=['bs4util', 'tests'],
    long_description=read('README.rst'),
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)

