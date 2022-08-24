from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
avatar = Blueprint('avatar_api', __name__)
api = Api(avatar, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('elsaAvatar', description='Avatar')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

avatar_postmodel = api.model('SelectAvatar', {
	"user_id":fields.Integer(required=True),
	"avatar_id":fields.Integer(required=True)
	})

avatar_putmodel = api.model('UpdateAvatar', {
	"avatar_id":fields.Integer(required=True)
	})

@name_space.route("/getAvatarNames")
class getAvatarNames(Resource):
	def get(self):
		connection = mysql.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT `avatar_id`, `avatar_name`, `gender`, `image_path` 
			FROM `avatar_master` limit 6""") 
		desc = cursor.description
		column_names = [col[0] for col in desc]
		avatar_data = [dict(izip(column_names, row)) for row in cursor.fetchall()]
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Avatar Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"AvatarDtls":avatar_data}}), status.HTTP_200_OK

@name_space.route("/selecttUserAvatarUsingPost")
class postUserAvatar(Resource):
	@api.expect(avatar_postmodel)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()

		user_id = details['user_id']
		avatar_id = details['avatar_id']

		user_avatar_insert_query = ("""INSERT INTO `user_avatar_mapping`(`user_id`, `avatar_id`) 
			VALUES(%s,%s)""")
		avatar_data = (user_id,avatar_id)

		cursor.execute(user_avatar_insert_query,avatar_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "User Avatar Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"AvatarDtls":details}}), status.HTTP_200_OK


@name_space.route("/updateUserAvatarUsingPut/<int:user_id>")
class updateUserAvatar(Resource):
	@api.expect(avatar_putmodel)
	def put(self,user_id):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()

		avatar_id = details['avatar_id']

		user_avatar_update_query = ("""UPDATE `user_avatar_mapping` SET `avatar_id`= %s 
			where `user_id` = %s""")
		avatar_data = (avatar_id,user_id)

		cursor.execute(user_avatar_update_query,avatar_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Updated User Avatar Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"AvatarDtls":details}}), status.HTTP_200_OK