.. mal.py documentation master file, created by
   sphinx-quickstart on Wed Mar 30 17:16:09 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to mal.py's documentation!
==================================

`mal.py <https://github.com/Skylake-dev/mal.py>`_ is an API wrapper for MyAnimeList.net written in Python.

**Features:**

- anime and manga search given a keyword
- fetch details of anime or manga given its id or its url
- accessing public lists of users
- retrieving seasonal anime
- retrieve rankings for anime and manga

Introduction
------------

Start by installing the library on your system, the use of a
virtual environment is recommended (see :doc:`py:tutorial/venv`):

- clone the repository

   .. code-block:: shell

      $ git clone https://github.com/Skylake-dev/mal.py

- install the library

   .. code-block:: shell

      $ pip install /path/to/cloned/repository

- obtain a token for the mal API

  * login on MAL
  * go to account settings -> API -> create id
  * follow the procedure and save your tokens
  * for this library you will need to use the client id

Now you can start using the library

   .. code-block:: python

      from mal import client

      cli = client.Client('your token here')

      anime = cli.get_anime(16498)
      anime.title
      >> Shingeki_no_Kyojin

For more examples you can check the `examples on the repository <https://github.com/Skylake-dev/mal.py/tree/main/examples>`_

Reporting issues
----------------

If you encounter issues using the library you can open an issue or start a discussion
on the project repository. Please note that this is still a work in progress
and there can be bugs. Also The API is not set and could change in later revisions.
Breaking changes may happen at any time before the release of version 1.0 but i
will try not to make them if not necessary.


.. toctree::
   :maxdepth: 2
   :caption: Contents:

Indices and tables
==================

.. toctree::
   api

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
