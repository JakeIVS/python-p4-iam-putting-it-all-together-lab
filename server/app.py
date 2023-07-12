#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            new_user = User(
                username = data['username'],
                image_url = data['image_url'],
                bio = data['bio']
            )
            new_user.password_hash = data['password']
            db.session.add(new_user)
            db.session.commit()
            session['user_id'] = new_user.id
            return new_user.to_dict(), 201
        except:
            return {'error': 'invalid user information'}, 422

class CheckSession(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            user = User.query.filter(User.id == user_id).first()
            return user.to_dict(), 200
        else:
            return {'error': "No user currently logged in"}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter(User.username == data['username']).first()
        if user:
            if user.authenticate(data['password']):
                session['user_id'] = user.id
                return user.to_dict(), 201
            else:
                return {"error": "Invalid Password"}, 401
        else:
            return {"error": "Invalid Username"}, 401

class Logout(Resource):
    def delete(self):
        user_id = session['user_id']
        if user_id:
            session['user_id'] = None
            return {}, 204
        else:
            return {"error": "No user logged in currently"}, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session['user_id']
        if user_id:
            recipe_list = [recipe.to_dict() for recipe in Recipe.query.filter(Recipe.user_id == user_id).all()]
            return recipe_list, 200
        else:
            return {"error": "No user logged in"}, 401
    def post(self):
        user_id = session['user_id']
        if user_id:
            try:
                data = request.get_json()
                new_recipe = Recipe(
                    title = data['title'],
                    instructions = data['instructions'],
                    minutes_to_complete = data['minutes_to_complete'],
                    user_id = user_id
                )
                print(new_recipe)
                db.session.add(new_recipe)
                db.session.commit()
                return new_recipe.to_dict(), 201
            except:
                return {"errors": ["Validation errors"]}, 422
        else:
            return {"error": "No user logged in"}, 401
        

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)
