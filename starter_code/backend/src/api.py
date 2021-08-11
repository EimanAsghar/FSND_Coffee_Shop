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


db_drop_and_create_all()

# ROUTES

@app.route('/drinks', methods=['GET'])
def get_drinks(): 

    # get all drinks from database
    all_drinks =  [drinks.short() for drinks in Drink.query.all()]
    
    # send error if it does not exist
    if all_drinks is None:
        abort(404, description='Not Found')

    return jsonify({
    'success': True,
    'drinks': all_drinks
    }), 200


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details(payload):  

    # get drinks with details
    drinks_details =  [drinks.long() for drinks in Drink.query.all()]

    # send error if it not found
    if drinks_details is None:
        abort(404, description='Not Found') 

    return jsonify({
        'success': True,
        'drinks': drinks_details
        }), 200


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def create_drink(payload):

    # create drink object
    drink = Drink(
        title=request.get_json().get('title'),
        recipe=json.dumps([request.get_json().get('recipe')])
        )


    try:
        drink.insert()

    except:
        # send error 
        abort(400, description='title must be not empty ')

    return jsonify({'success': True, 'drinks': [drink.long()]}), 200



@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(payload, drink_id):

        #get spacifi drink by id
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        body = request.get_json()

        # send error if it not found
        if drink is None:
            abort(404, description='Not Found')
        
        # check if recipe and title in request
        if 'title' in body:
            # then get the new value and update
            drink.title = request.get_json().get('title')
        elif 'recipe' in body:
            # then get the new value and update
            drink.recipe = [json.dumps(request.get_json().get('recipe'))]
        else:
            abort(400, description='fill the required')

        drink.update()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(payload, drink_id):
    # get spacific drink with id
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

    # check if it exist or not
    if drink is None:
        abort(404, description='drink id not Found')
    
    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink_id
    }), 200

# Error Handling


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": error.description
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": error.description
    }), 404


@app.errorhandler(AuthError)
def authentication_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': error.error.get('description')
    }), error.status_code

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": error.description
    }), 400
