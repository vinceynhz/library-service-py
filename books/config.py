"""
 :author: vic on 2022-11-08
"""
import json
import logging

_config = None


def update(new_config: dict):
    global _config
    for k in new_config.keys():
        _config[k] = new_config[k]
    with open('./database/config.json', 'w+') as outfile:
        json.dump(_config, outfile, indent=2, sort_keys=True)


def get(key: str):
    global _config
    if key in _config:
        return _config[key]
    return None


def load(logger: str) -> None:
    global _config
    try:
        with open('./database/config.json', 'r') as infile:
            _config = json.load(infile)
        logging.getLogger(logger).info("Config loaded")
    except FileNotFoundError:
        logging.getLogger(logger).info("Default config not set, creating one")
        _config = {
            'db_file': './database/books.cli.db',
            'language': 'eng',
            'book_format': 'HARDBACK',
            'openlibrary_search_url': 'http://localhost:666',
            'library_service_url': 'http://localhost:666'
        }
        with open('./database/config.json', 'w+') as outfile:
            json.dump(_config, outfile, indent=2)
        logging.getLogger(logger).info("Config created")
