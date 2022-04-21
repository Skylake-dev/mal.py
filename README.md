# mal.py

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

- clone the repo
- (optional) create a virtual environment `python -m venv .venv` and activate it
- install with `pip install full/path/to/cloned/repo`
  installation from pypi will be available once [this](https://github.com/pypa/pypi-support/issues/1800) is solved
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

This project is still a work in progress, if you have problems or find bugs feel free to open an issue or start a discussion.
