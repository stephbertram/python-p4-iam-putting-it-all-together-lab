#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):

    def post(self):
        try:
            json = request.get_json()
            user = User(
                username = json.get('username'),
                image_url = json.get('image_url'),
                bio = json.get('bio')
            )
            # Use setter to set password
            user.password_hash = json.get('password')
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return {'message': 'Invalid user'}, 422

        session['user_id'] = user.id
        return user.to_dict(), 201

class CheckSession(Resource):
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        if user:
            return user.to_dict(), 200
        else:
            return {'message': '401: Not Authorized'}, 401

class Login(Resource):
    def post(self):
        username = request.get_json()['username']
        user = User.query.filter(User.username == username).first()

        password = request.get_json()['password']

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {"message": "401 Unauthorized"}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session['user_id'] = None
            return {'message': '204: No content'}, 204
        
        return {'message': '401: Unauthorized'}, 401
    
class RecipeIndex(Resource):
    def get(self):
        if session.get('user_id'):
            all_recipes = [recipe.to_dict() for recipe in Recipe.query]
            return all_recipes, 200
        
        return {'message': '401: Unauthorized'}, 401

    def post(self):
        if session.get('user_id'):
            try: 
                data = request.json
                
                new_recipe = Recipe(**data)
                new_recipe.user_id = session['user_id']
                db.session.add(new_recipe)
                db.session.commit()
                return new_recipe.to_dict(), 201
            except Exception as e:
                db.session.rollback()
                return {"errors": str(e)}, 422 
        
        return {'message': '401: Unauthorized'}, 401
    
    # def post(self):
    #     if session.get('user_id'):
    #         try:
    #             data = request.json
    #             new_recipe = Recipe(
    #                 title = data.get('title'),
    #                 instructions = data.get('instructions'),
    #                 minutes_to_complete = data.get('minutes_to_complete'),
    #                 user_id = session['user_id']
    #             )
    #             db.session.add(new_recipe)
    #             db.session.commit()
    #             return new_recipe.to_dict(), 201
    #         except Exception as e:
    #             db.session.rollback()
    #             return {"errors": str(e)}, 422 
    
    #     return {'message': '401: Unauthorized'}, 401


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)