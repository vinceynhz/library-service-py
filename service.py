"""
:author: vic on 2021-03-13
"""
import sys
import sqlalchemy
from sqlalchemy.exc import IntegrityError

import dbschema

from flask import Flask, request, jsonify


def start():
    import logging

    logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)

    app = Flask(__name__)

    @app.route('/info')
    def info():
        return {
            'version': {
                'python': sys.version,
                'sqlalchemy': sqlalchemy.__version__
            }
        }

    # Contributor API
    @app.route('/contributors', methods=['GET'])
    def get_contributors():
        return jsonify(dbschema.get_contributors())

    @app.route('/contributor/<contributor_id>', methods=['GET'])
    def get_contributor(contributor_id: int):
        found = dbschema.get_contributor(contributor_id)
        return jsonify(found), 200 if found is not None else 404

    @app.route('/contributor', methods=['POST'])
    def add_contributor():
        """
        {
          "name": "..."
        }
        :return: 201 if contributor added, 409 if contributor existed, 400 if incorrect data
        """
        data = request.get_json(force=True)
        for k, v in dbschema.Contributor.required.items():
            if k not in data:
                return error(f"Required attribute '{k}' not defined"), 400
            if type(data[k]) is not v:
                return error(f"Wrong type for attribute '{k}': {type(k)}, expected {v}"), 400

        new_contributor = dbschema.Contributor.maker(data)
        try:
            contributor_id = dbschema.add_contributor(new_contributor)
            return link(request.host_url + 'contributor/' + contributor_id), 201
        except IntegrityError as exception:
            return error(exception), 409

    # Book API
    @app.route('/books', methods=['GET'])
    def get_books():
        return jsonify(dbschema.get_books())

    @app.route('/book/<book_id>', methods=['GET'])
    def get_book(book_id: int):
        found = dbschema.get_book(book_id)
        return jsonify(found), 200 if found is not None else 404

    @app.route('/book', methods=['POST'])
    def add_book():
        """
        {
          "format": "...",
          "title": "...",
          "contributors": {
            "id": "type",
          }
        }
        :return: 201 if book added, 409 if book existed, 400 if incorrect data
        """
        data = request.get_json(force=True)
        for k, v in dbschema.Book.required.items():
            if k not in data:
                return error(f"Required attribute '{k}' not defined"), 400
            if type(data[k]) is not v:
                return error(f"Wrong type for attribute '{k}': {type(k)}, expected {v}"), 400

        new_book = dbschema.Book.maker(data)
        try:
            book_id = dbschema.add_book(new_book, data['contributors'])
            return link(request.host_url + 'book/' + book_id), 201
        except IntegrityError as exception:
            return error(exception), 409

    # Authority API
    @app.route('/authority/contributors/normalize', methods=['POST'])
    def normalize_contributors():
        """
        [
           "...",
           "..."
        ]
        :return: 200 and list of author names in normalized form
        """
        data = request.get_json(force=True)
        result = dbschema.normalize_contributors(data)
        return jsonify(result), 200

    @app.route('/authority/books/normalize', methods=['POST'])
    def normalize_books():
        """
        [
          {
            "title": "...",
            "contributors": [
              "...",
              "..."
            ],
            "format": "...",
            "isbn": [
              "...",
              "..."
            ],
            "year": "...",
            "language": "..."
          },
          ...
        ]
        :return: 200 and list of books in normalized form
        """
        data = request.get_json(force=True)
        result = dbschema.normalize_books(data)
        return jsonify(result), 200

    # Search API
    @app.route('/search/contributors', methods=['POST', 'GET'])
    def search_contributors():
        if request.method == 'GET':
            names = [request.args.get('name')]
            assert names is not None and len(names) > 0
        else:
            names = request.get_json(force=True)
            assert names is not None and type(names) is list and len(names) > 0

        results = dbschema.search_contributors(names)

        return jsonify(results), 200 if results is not None and len(results) > 0 else None, 404

    return app


def error(msg):
    return {
        'error': msg
    }


def link(resource_link):
    return {
        '_link': resource_link
    }
