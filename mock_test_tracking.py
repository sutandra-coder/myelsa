from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
mock_test_tracking = Blueprint('mock_test_tracking', __name__)
api = Api(mock_test_tracking,  title='MyElsa API',
          description='MyElsa API')
name_space = api.namespace(
    'mock_test_tracking', description='Mock Test Download History By User Id')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_lab_lang1'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)
connection = mysql.connect()


@name_space.route("/getTeacherListByInstitutionId/<int:user_id>")
class getTeacherListByInstitutionId(Resource):
    def get(self, user_id):
        connection = mysql.connect()
        cursor = connection.cursor()
        conn = mysql.connect()
        cur = conn.cursor()
        content_filepath_list = []
        cursor.execute("""SELECT `content_filepath` FROM `mock_test_download_history` WHERE `user_id` = %s""", (user_id))
        getdownloadhistory = cursor.fetchall()
        if getdownloadhistory:
            desc = cursor.description
            print(desc)
            col_names = [col[0] for col in desc]
            content_filepath_list = [dict(izip(col_names, row))
                            for row in getdownloadhistory]
            print(content_filepath_list)

        return ({"attributes": {
            "status_desc": "Student Voting Details.",
            "status": "success"
        },
            "responseList": content_filepath_list}), status.HTTP_200_OK
        
