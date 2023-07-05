import json
from flask import Flask, jsonify, request, Resource
from flask_restful import Resource, Api


class DataResource(Resource):
    def __init__(self, data_path):
        self.data = json.load(open(data_path))
    def get(self):
        return self.data

app = FlaskAPI(Flask(__name__))
app.add_resource(DataResource('dev/example-wiki-export.json'), '/confluence')
app.add_resource(DataResource('dev/example-jira-export.json'), '/jira')

if __name__ == '__main__':
    app.run()
