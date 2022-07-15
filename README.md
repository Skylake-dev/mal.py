# mal.py

[![Downloads](https://pepy.tech/badge/mal-api-py)](https://pepy.tech/project/mal-api-py)

A [MyAnimeList](https://myanimelist.net) API wrapper written in Python.

The objective for now is to cover queries for the publicly available information, support for taking actions on a user list is not planned.

## Features

- anime and manga search given a keyword
- fetch details of anime or manga given its id or its url
- accessing public lists of users
- retrieving seasonal anime
- retrieve rankings for anime and manga
- retrieve forum boards and discussions

The next features that are planned to be implemented are:

- retrieve more information on recommendations and related entries

## Installation

Python 3.8+ is needed.

To use this library:

- (optional) create a virtual environment `python -m venv .venv` and activate it
- install with `pip install mal-api.py`
- to perform requests you need an API token
  log in on MAL -> account settings -> API -> create ID

## Usage

```python
from mal import client

cli = client.Client('your token here')

anime = cli.get_anime(16498)
anime.title
>> Shingeki_no_Kyojin
```

Full documentation available [here](https://malpy.readthedocs.io/en/latest/index.html).

Code samples can be found in the examples folder.

## Logging

This library uses the logging module to keep track of configuration changes and possible
network errors. If you want to see the logs you need to configure the logging module yourself, for example:

```python
import logging

logging.basicConfig(logging.level=INFO)
```

For more information on how to use logging refer to the documentation of python:

- [documentation of logging module](https://docs.python.org/3/library/logging.html)
- [logging HOWTO guide](https://docs.python.org/3/howto/logging.html)

This project is still a work in progress, if you have problems or find bugs feel free to open an issue or start a discussion.
