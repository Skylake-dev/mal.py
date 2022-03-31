# mal.py

A [MyAnimeList](https://myanimelist.net) API wrapper written in python.

The objective for now is to cover queries for the publicly available information, support for taking actions on a user list is not planned.

## Features

- anime and mange search given a keyword
- fetch details of anime or manga given its id or its url
- accessing public lists of users

The next features that are planned to be implemented are:

- retrieve more information on recommendations and related entries
- retrieving seasonal anime
- retrieve rankings for anime and manga

## Installation

Python 3.8+ is needed.
To use this library:

- clone the repo
- install requirements `pip install -r requirements.txt`
- to perform requests you need an API token

## Usage

```python
from mal import client

cli = client.Client('your token here')

# see client docstrings for more information on the methods
anime = client.get_anime(16498)
anime.title
>> Shingeki_no_Kyojin
```

Full documentation available [here](https://malpy.readthedocs.io/en/latest/index.html).

This project is still a work in progress, if you have problems or find bugs feel free to open an issue or start a discussion.
