from flaskapi import FlaskAPI, Resource, Fields
from flask import Flask, request
from json import loads

data_confluence = loads('dev/example-wiki-export.json')
data_jira = loads('dev/example-jira-export.json')

class ConfluenceResource(Resource):
    def get(self):
        return data_confluence

class JiraResource(Resource):
    def get(self):
        return data_jira

class ApiApp(FlaskAPI):
    def __init__(self):
        super().__init__('api', Flask(__name__))
        self.add_resource(ConfluenceResource, '/confluence')
        self.add_resource(JiraResource, /'jira')

app = ApiApp()

if __name__ == '__main__':
    app.run()