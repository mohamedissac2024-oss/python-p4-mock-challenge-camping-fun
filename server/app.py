from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)


@app.route('/')
def home():
    return ''


# API Setup
api = Api(app)


# Helper function to handle validation errors
def handle_validation_error(error):
    response = make_response(jsonify({"errors": ["validation errors"]}), 400)
    return response


# Resource for Campers List
class CampersResource(Resource):
    def get(self):
        campers = Camper.query.all()
        return [camper.to_dict(only=('id', 'name', 'age')) for camper in campers]
    
    def post(self):
        data = request.get_json()
        try:
            camper = Camper(name=data['name'], age=data['age'])
            db.session.add(camper)
            db.session.commit()
            return camper.to_dict(only=('id', 'name', 'age')), 201
        except (ValueError, KeyError) as e:
            return handle_validation_error(e)


# Resource for Single Camper
class CamperResource(Resource):
    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response(jsonify({"error": "Camper not found"}), 404)
        return camper.to_dict(rules=('signups', '-signups.camper'))
    
    def patch(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if not camper:
            return make_response(jsonify({"error": "Camper not found"}), 404)
        
        data = request.get_json()
        try:
            if 'name' in data:
                camper.name = data['name']
            if 'age' in data:
                camper.age = data['age']
            db.session.commit()
            return camper.to_dict(only=('id', 'name', 'age')), 202
        except ValueError as e:
            return handle_validation_error(e)


# Resource for Activities List
class ActivitiesResource(Resource):
    def get(self):
        activities = Activity.query.all()
        return [activity.to_dict(only=('id', 'name', 'difficulty')) for activity in activities]


# Resource for Single Activity
class ActivityResource(Resource):
    def delete(self, id):
        activity = Activity.query.filter_by(id=id).first()
        if not activity:
            return make_response(jsonify({"error": "Activity not found"}), 404)
        db.session.delete(activity)
        db.session.commit()
        return '', 204


# Resource for Signups
class SignupsResource(Resource):
    def post(self):
        data = request.get_json()
        try:
            signup = Signup(
                camper_id=data['camper_id'],
                activity_id=data['activity_id'],
                time=data['time']
            )
            db.session.add(signup)
            db.session.commit()
            return signup.to_dict(rules=('activity', 'camper'))
        except (ValueError, KeyError) as e:
            return handle_validation_error(e)


# Add routes to API
api.add_resource(CampersResource, '/campers')
api.add_resource(CamperResource, '/campers/<int:id>')
api.add_resource(ActivitiesResource, '/activities')
api.add_resource(ActivityResource, '/activities/<int:id>')
api.add_resource(SignupsResource, '/signups')


if __name__ == '__main__':
    app.run(port=5555, debug=True)

