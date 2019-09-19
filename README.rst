Berglas Library for Python
==========================

.. image:: https://travis-ci.org/maroux/berglas-python.svg?branch=master
    :target: https://travis-ci.org/maroux/berglas-python

.. image:: https://coveralls.io/repos/github/maroux/berglas-python/badge.svg?branch=master
    :target: https://coveralls.io/github/maroux/berglas-python?branch=master

.. image:: https://img.shields.io/pypi/v/berglas.svg?style=flat-square
    :target: https://pypi.python.org/pypi/berglas

.. image:: https://img.shields.io/pypi/pyversions/berglas.svg?style=flat-square
    :target: https://pypi.python.org/pypi/berglas

.. image:: https://img.shields.io/pypi/implementation/berglas.svg?style=flat-square
    :target: https://pypi.python.org/pypi/berglas

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/ambv/black

This library automatically parses berglas references when imported.

Only Python 3.6+ is supported currently.

You can find the latest, most up to date, documentation on `Github`_.

Quick Start
-----------

Install library:

.. code:: sh

    pip install berglas

Import the module:

.. code:: python

    import berglas.auto  # noqa

When imported, the `berglas` module will:

1. Detect the runtime environment and call the appropriate API to get the list
of environment variables that were set on the resource at deploy time

1. Download and decrypt any secrets that match the `Berglas environment
variable reference syntax`_

1. Replace the value for the environment variable with the decrypted secret

You can also opt out of auto-parsing and call the library yourself instead:

.. code:: python

    import os

    from berglas import resolver

    if __name__ == '__main__':
        client = resolver.Client()
        client.replace("MY_SECRET")
        print(os.environ["MY_SECRET"])

        // alternatively, use resolve method to simply get the value without updating environment:
        my_secret = client.resolve(os.environ["MY_SECRET"])
        print(my_secret)

Release Notes
-------------

v0.1
~~~~

- First version

Development
-----------

Getting Started
~~~~~~~~~~~~~~~
Assuming that you have Python, ``pyenv`` and ``pyenv-virtualenv`` installed, set up your
environment and install the required dependencies like this instead of
the ``pip install berglas`` defined above:

.. code:: sh

    $ git clone https://github.com/maroux/berglas-python.git
    $ cd python
    $ pyenv virtualenv 3.7.2 berglas-3.7
    ...
    $ pyenv shell berglas-3.7
    $ pip install -r requirements/dev-3.7.txt

Running Tests
~~~~~~~~~~~~~
You can run tests in using ``make test``. By default,
it will run all of the unit and functional tests, but you can also specify your own
``py.test`` options.

.. code:: sh

    $ py.test


Getting Help
------------

We use GitHub issues for tracking bugs and feature requests.

* If it turns out that you may have found a bug, please `open an issue <https://github.com/maroux/berglas-python/issues/new>`__

.. _Github: github.com/maroux/berglas-python
.. _Berglas environment variable reference syntax: https://github.com/GoogleCloudPlatform/berglas/blob/master/doc/reference-syntax.md
