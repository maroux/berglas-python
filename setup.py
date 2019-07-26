"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import ast
from codecs import open
from os import path
import re
from setuptools import setup, find_packages


cwd = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(cwd, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

_version_re = re.compile(r"VERSION\s+=\s+(.*)")

with open("berglas/__init__.py", "rb") as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1)))

tests_require = ["pytest", "flake8", "mypy", "ipdb", "coverage", "coveralls", "pytest-cov", "black"]

setup(
    name="berglas",
    version=version,
    description="Berglas Python Library",
    long_description=long_description,
    url="https://github.com/maroux/berglas-python",
    author="Aniruddha Maru",
    license="Apache Software License (Apache License 2.0)",
    maintainer="Aniruddha Maru",
    maintainer_email="aniruddhamaru@gmail.com",
    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Natural Language :: English",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires=">=3.6",
    keywords="secrets gcs gcp",
    # https://mypy.readthedocs.io/en/latest/installed_packages.html
    package_data={"berglas": ["py.typed"]},
    packages=find_packages(exclude=["tests", "tests.*"]),
    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=["pycryptodome", "google-api-python-client", "google-cloud-storage", "google-cloud-kms"],
    tests_require=tests_require,
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={"dev": ["flake8"], "test": tests_require, "publish": ["twine", "wheel"]},
    include_package_data=True,
)
