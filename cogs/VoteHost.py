from flask import Flask, request
from flask_restful import Api, Resource, reqparse

app = Flask(__name__)
api = Api(app)



class Vote(Resource):
    def post(self):
        print(request.headers)
        pass

api.add_resource(Vote, "/")

app.run("0.0.0.0", "50505")
print("h")