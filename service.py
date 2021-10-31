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

    @app.route('/contributors', methods=['GET'])
    def get_contributors():
        return jsonify(dbschema.get_contributors())

    @app.route('/contributor/<contributor_id>', methods=['GET'])
    def get_contributor(contributor_id: int):
        found = dbschema.get_contributor(contributor_id)
        return jsonify(found), 200 if found is not None else 404

    @app.route('/contributor', methods=['POST'])
    def add_contributor():
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

    @app.route('/books', methods=['GET'])
    def get_books():
        return jsonify(dbschema.get_books())

    @app.route('/book', methods=['POST'])
    def add_book():
        data = request.get_json(force=True)
        for k, v in dbschema.Book.required.items():
            if k not in data:
                return error(f"Required attribute '{k}' not defined"), 400
            if type(data[k]) is not v:
                return error(f"Wrong type for attribute '{k}': {type(k)}, expected {v}"), 400

        new_book = dbschema.Book.maker(data)
        book_id = dbschema.add_book(new_book, data['contributors'])
        return link(request.host_url + 'book/' + book_id), 201

    return app


def error(msg):
    return {
        'error': msg
    }


def link(resource_link):
    return {
        '_link': resource_link
    }
