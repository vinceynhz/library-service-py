"""
 :author: vic on 2022-11-11
"""
import requests
import books.config

from typing import Union

from contextlib import contextmanager


class LibraryClientException(Exception):
    """ For errors interacting with the library service"""
    status_code: int
    message: str
    detail: str

    def __init__(self, message: str, detail: str = None, status_code: int = 0):
        self.status_code = status_code
        self.message = message
        self.detail = detail

    def __str__(self):
        return f"{self.status_code} {self.message} - {self.detail}"


def add_contributor(contributor: dict) -> dict:
    url = books.config.get('library_service_url') + '/contributor'
    with _handled_request(contributor):
        result = requests.post(
            url,
            json=contributor,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
        )
    return _get_response(result)


def update_contributor(contributor: dict) -> Union[dict, None]:
    url = books.config.get('library_service_url') + '/contributor/' + str(contributor['id'])
    with _handled_request():
        result = requests.put(
            url,
            json=contributor,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
        )
    return _get_response(result)


def get_contributors() -> list:
    url = books.config.get('library_service_url') + '/contributors'
    with _handled_request():
        result = requests.get(
            url,
            headers={'Accept': 'application/json'}
        )
    return _get_response(result)


@contextmanager
def _handled_request(payload=None):
    try:
        yield
    except requests.exceptions.ConnectionError as error:
        if hasattr(error, 'message'):
            raise LibraryClientException(error.message, f"payload: {str(payload)}")
        else:
            raise LibraryClientException(str(error), f"payload: {str(payload)}")


def _get_response(source, payload=None):
    try:
        response = source.json()
    except requests.exceptions.JSONDecodeError as error:
        if hasattr(error, 'message'):
            raise LibraryClientException(error.message)
        else:
            raise LibraryClientException(str(error))
    if source.status_code == requests.codes.not_modified:
        return None
    if source.status_code not in (requests.codes.ok, requests.codes.created, requests.codes.accepted):
        raise LibraryClientException(
            response['message'],
            response['detail'] + (f" - payload: {str(payload)}" if payload is not None else ''),
            source.status_code
        )

    return response
