"""
:author: vic on 2021-03-13
"""
import sys
import sqlalchemy
import dbschema

from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/info')
def info():
    return {
        'version': {
            'python': sys.version,
            'sqlalchemy': sqlalchemy.__version__
        }
    }


@app.route('/contributor', methods=['GET', 'POST'])
def add_contributor():
    if request.method == 'GET':
        return jsonify(dbschema.all_contributors())

    data = request.get_json(force=True)
    if 'name' not in data:
        return error("Required attribute 'name' not defined"), 400

    new_contributor = dbschema.Contributor.maker(data)
    dbschema.add_contributor(new_contributor)
    return link(request.host_url + '/' + new_contributor.id), 201


def error(msg):
    return {
        'error': msg
    }


def link(resource_link):
    return {
        '_link': resource_link
    }
