from operator import ge
import os
import pdb
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


# ROUTES
@app.route('/drinks')
def drinks():
    """
        it should be a public endpoint
        it should contain only the drink.short() data representation
    """
    drinks_data = Drink.query.all()
    drinks = [drink.short() for drink in drinks_data]
    return jsonify({"success": True, "drinks": drinks})


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def drinks_detail(payload):
    """
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    """
    drinks_data = Drink.query.all()
    drinks = [drink.long() for drink in drinks_data]
    return jsonify({"success": True, "drinks": drinks})


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):
    """
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    """
    try:
        request_data = request.get_json()
        recipe = request_data.get('recipe')
        drink = Drink(title=request_data.get('title'), recipe=json.dumps(recipe))
        drink.insert()

        return jsonify({"success": True, "drinks": [drink.long()]})

    except:
        abort(422)


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    """
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    """
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        request_data = request.get_json()
        if request_data.get('title'):
            drink.title = request_data.get('title')
        if request_data.get('recipe'):
            drink.recipe = request_data.get('recipe')
        
        drink.update()

        return jsonify({"success": True, "drinks": [drink.long()]})

    except:
        abort(422)

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    """
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    """
    try:
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()
        return jsonify({"success": True, "delete": drink_id})
    except:
        abort(422)

# Error Handling

@app.errorhandler(404)
def not_found(error):
    """
    error handler for 404
    """
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(AuthError)
def server_error(error):
    """
    handler for AuthError
    """
    error_payload = error.error
    return jsonify({
        "success": False,
        "error": error_payload.get('code'),
        "message": "authentication error",
        "payload": error_payload.get('description')
    }), error.status_code


# other errors
@app.errorhandler(401)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unathorized",
        "payload": str(error)
    }), 401

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400

@app.errorhandler(405)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed"
    }), 405

@app.errorhandler(Exception)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "something went wrong",
        "payload": str(error)
    }), 500
