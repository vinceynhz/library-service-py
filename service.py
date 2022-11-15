"""
:author: vic on 2021-03-13
"""
import logging.config
import os
import sys
import sqlalchemy
from sqlalchemy.exc import IntegrityError

import database.schema as dbschema

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

    @app.route('/contributor/<contributor_id>', methods=['GET', 'PUT'])
    def get_contributor(contributor_id: int):
        if request.method == 'GET':
            found = dbschema.get_contributor(contributor_id)
            return jsonify(found), 200 if found is not None else 404
        data = request.get_json(force=True)
        contributor, updated = dbschema.update_contributor(contributor_id, data)
        return jsonify(contributor), 200 if updated else 304

    @app.route('/contributor', methods=['POST'])
    def add_contributor():
        """
        {
          "first_name": "...",
          "last_names": "...",
          "honorific": "..."
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
        contributor_id = dbschema.add_contributor(new_contributor)
        return link(request.host_url + 'contributor/' + contributor_id), 201

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
        book_id = dbschema.add_book(new_book, data['contributors'])
        return link(request.host_url + 'book/' + book_id), 201

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

    @app.errorhandler(IntegrityError)
    def handle_integrity_error(exception):
        original_exception = exception
        while hasattr(original_exception, 'orig') and original_exception.orig is not None:
            original_exception = original_exception.orig
        detail = str(original_exception)
        return error('Record already present', detail), 409

    return app


def error(message: str, detail: str = None) -> dict:
    return {
        'message': message,
        'detail': detail
    }


def link(resource_link):
    return {
        '_link': resource_link
    }


def fix_data():
    import json
    from collections import OrderedDict
    with open('/home/vic/coding/library-service-py/tests/contributor_data.json', 'r') as infile:
        data = json.load(infile, object_pairs_hook=OrderedDict)

    result = []
    for a in data:
        result.append(fix_entry(a))

    with open('/home/vic/coding/library-service-py/tests/contributor_data.json', 'w') as outfile:
        json.dump(result, outfile, indent=2)


def fix_entry(entry: dict) -> dict:
    import authority
    from collections import OrderedDict
    input_field = entry['input']
    if type(input_field) is OrderedDict:
        return entry
    fields = input_field.split(' ')
    if len(fields) == 2:
        first_name, last_names = fields
        honorific = None
    else:
        first_name, last_names, honorific = fields

    return {
        'input': {
            'first_name': first_name,
            'last_names': last_names,
            'honorific': honorific
        },
        'expected': {
            'first_name': authority.name(first_name),
            'last_names': authority.name(last_names),
            'honorific': authority.name(honorific) if honorific is not None else None,
            'cataloguing': entry['cataloguing'],
            'sha256': entry['sha256']
        }
    }


if __name__ == '__main__':
    if os.path.exists("logging.conf"):
        logging.config.fileConfig("logging.conf")
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s.%(msecs)03d %(levelname)-7s - %(message)s',
                            datefmt='%Y-%m-%dT%H:%M:%S')

    if sys.argv[1] == '--cli':
        import books.cli

        books.cli.run()
    elif sys.argv[1] == '--ui':
        import books.ui

        books.ui.run(sys.argv)
    elif sys.argv[1] == '--db-init':
        import database.init

        database.init.run()
    elif sys.argv[1] == '--fix':
        fix_data()
    elif sys.argv[1] == '--flask':
        app = start()
        app.run()
    else:
        print("Unknown goal: " + sys.argv[1])
