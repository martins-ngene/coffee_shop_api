import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the database
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.all()
    all_drinks = []

    for drink in drinks:
        all_drinks.append(drink.short())

    return jsonify({
        "success": True,
        "drinks": all_drinks
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):
    drinks = Drink.query.all()
    all_drinks = []

    for drink in drinks:
        all_drinks.append(drink.long())

    return jsonify({
        "success": True,
        "drinks": all_drinks
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def post_drinks(payload):

    drinks_body = request.get_json()
    print(drinks_body)

    if drinks_body is None:
        abort(400)
    if 'recipe' not in drinks_body or 'title' not in drinks_body:
        abort(400)

    new_drinks = []

    try:
        drink_recipe = drinks_body.get('recipe', None)
        drink_title = drinks_body.get('title', None)
        drink = Drink(title=drink_title, recipe=json.dumps(drink_recipe))
        drink.insert()

        new_drinks = [drink.long()]

    except:
        abort(422)

    return jsonify({
        "success": True,
        "drinks": new_drinks
    })


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drinks(payload, drink_id):
    if drink_id is None:
        abort(404)

    updated_drink = []
    try:
        drinks_body = request.get_json()
        drink = Drink.query.filter_by(id=drink_id).first_or_404()
        print(drink)
        if 'title' in drinks_body:
            drink.title = drinks_body.get('title')

        if 'recipe' in drinks_body:
            drink.recipe = json.dumps(drinks_body.get('recipe'))
        print(drink)
        drink.update()

        updated_drink = [drink.long()]
    except:
        abort(422)

    return jsonify({
        "success": True,
        "drinks": updated_drink
    })


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<drink_id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    if drink_id is None:
        abort(404)
    drink = Drink.query.get(drink_id)
    if drink is None:
        abort(404)
    print(drink)
    drink.delete()
    return jsonify({
        "success": True,
        "delete": f'drink: {drink_id} deleted'
    })


# Error Handling

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
    }), 400


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Page Not Found"
    }), 404


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500


# AuthError
@app.errorhandler(AuthError)
def unauthorized(error):
    return (jsonify({
        "success": False,
        "error": error.error,
        "message": error.status_code
    }), error.status_code)
