import pymysql
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
from database_connections import creamson_academy_connection

app = Flask(__name__)
cors = CORS(app)
academy_signin = Blueprint('academy_signin_api', __name__)
api = Api(academy_signin,  title='MyElsa Academy API',description='MyElsa Academy API')
name_space = api.namespace('academy_signin',description='Academy Signin')


@name_space.route("/authenticateUserCredentials/<string:username>/<string:password>")
class authenticateUserCredentials(Resource):
	def get(self,username,password):

		connection = creamson_academy_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `academy_user_id`,`email_id`,`first_name`, IFNULL(`middle_name`,'') as 'middle_name',
			`last_name`,`gender`,`date_of_birth`,`country`,`state`,`city`,`address`,`zipcode`,
			`phone_no`,`created_at` FROM `academy_user_master` 
			WHERE `username` = %s and `password` = %s""",(username,password))

		userDtls = cursor.fetchone()
		msg = 'Incorrect Username or Password'
		if userDtls:
			msg = 'User Authentication Successful'
			userDtls['created_at'] = userDtls.get('created_at').isoformat()
		else:
			userDtls = {}
		cursor.close()
		return ({"attributes": {"status_desc": "User Details",
								"status": "success",
								"message":msg},
				"responseList":userDtls})


@name_space.route("/updatePassword/<string:username>/<string:password>")
class updatePassword(Resource):
	def put(self,username,password):

		connection = creamson_academy_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `academy_user_id` FROM `academy_user_master` 
			WHERE `username` = %s""",(username))

		userDtls = cursor.fetchone()
		msg = 'Username not found'
		if userDtls:
			user_id = userDtls.get('academy_user_id')
			updateQuery = ("""UPDATE `academy_user_master` SET `password` = %s WHERE `academy_user_id` = %s""")

			cursor.execute(updateQuery,(password,user_id))

			connection.commit()
			msg = 'Password updated successfully'
		cursor.close()
		return ({"attributes": {"status_desc": "User Details",
								"status": "success",},
				"responseList":msg})
