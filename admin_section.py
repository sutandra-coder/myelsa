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
admin_section = Blueprint('teacher_list', __name__)
api = Api(admin_section,  title='MyElsa API',
          description='MyElsa API')
name_space = api.namespace('admin_section', description='admin_section')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)
connection = mysql.connect()


@name_space.route("/getTeacherListByAdminUserId/<int:user_id>")
class getTeacherListByAdminUserId(Resource):
    def get(self, user_id):
        connection = mysql.connect()
        cursor = connection.cursor()
        teacher_list = []
        cursor.execute("""SELECT CONCAT(`FIRST_NAME`," ",`LAST_NAME`) teacher_name,
						`IMAGE_URL` image_url FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` IN
						(SELECT `INSTITUTION_USER_ID_TEACHER` FROM `teacher_dtls` WHERE `INSTITUTION_ID` IN
						(SELECT `INSTITUTION_ID` FROM `admin_dtls` WHERE `INSTITUTION_USER_ID_ADMIN` = %s))""", (user_id))
        
        getteacher = cursor.fetchall()
        if getteacher:
            desc = cursor.description
            col_names = [col[0] for col in desc]
            teacher_list = [dict(izip(col_names, row)) for row in getteacher]

        return ({"attributes": {
                    "status_desc": "Student Voting Details.",
                    "status": "success"
                },
                "responseList": teacher_list}), status.HTTP_200_OK
