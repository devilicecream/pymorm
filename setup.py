__author__ = "walter"
try:
    import logging
    import multiprocessing
except:
    pass

import sys
py_version = sys.version_info[:2]

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

dependency_links = []

install_requires = [
    "pymongo",
    "bunch",
]

setup(
    name='pymorm',
    version='0.4.7',
    description='Really simple pymongo-based ODM',
    author='Walter Danilo Galante',
    author_email='walter.galante@proxtome.com',
    classifiers=["Development Status :: 3 - Alpha",
                 "License :: OSI Approved :: MIT License",
                 "Programming Language :: Python",
                 "Topic :: Database :: Front-Ends",
                 "Topic :: Software Development :: Libraries :: Python Modules",
                 "Intended Audience :: Developers"],
    url="https://github.com/devilicecream/pymorm",
    packages=find_packages(),
    keywords='mongodb pymongo simple odm orm mongo database',
    dependency_links=dependency_links,
    install_requires=install_requires,
    entry_points={},
    zip_safe=True
)
