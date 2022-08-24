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
avatar_polls = Blueprint('avatarPolls_api', __name__)
api = Api(avatar_polls, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('AvatarPoll', description='Avatar Poll')

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

@name_space.route("/getVoterList")
class getVoterList(Resource):
	def get(self):
		connection = mysql.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT DISTINCT `avatar_id`,user_id FROM `avatar_poll` 
			order by `last_updated_ts` desc limit 20""") 
		desc = cursor.description
		column_names = [col[0] for col in desc]
		avatar_data = [dict(izip(column_names, row)) for row in cursor.fetchall()]
		for i in avatar_data:
			cursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`) FROM 
				`institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(i['user_id']))
			user_name = cursor.fetchone()
			if user_name:
				user_name = user_name[0]
			i['user_name'] = user_name
			cursor.execute("""SELECT `avatar_name` FROM `avatar_master` 
				where avatar_id = %s""",(i['avatar_id']))
			avatar_name = cursor.fetchone()
			if avatar_name:
				avatar_name = avatar_name[0]
			i['avatar_name'] = avatar_name
			i['desc'] = 'voted for'
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Avatar Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"AvatarDtls":avatar_data}}), status.HTTP_200_OK


@name_space.route("/getVoteCount")
class getAvatarNamesAndVoteCount(Resource):
	def get(self):
		connection = mysql.connect()
		cursor = connection.cursor()

		cursor.execute("""SELECT am.`avatar_id`, am.`avatar_name`, am.`gender`,am.`image_path`, 
			COUNT(ap.`avatar_id`) AS TotalVotes FROM avatar_poll ap 
			RIGHT JOIN `avatar_master` am ON ap.`avatar_id` = am.`avatar_id` 
			GROUP BY am.`avatar_id`""")

		desc = cursor.description
		column_names = [col[0] for col in desc]
		avatar_data = [dict(izip(column_names, row)) for row in cursor.fetchall()]

		cursor.execute("""SELECT count(`id`) as TotalVotes FROM `avatar_poll`""")
		totalvote = cursor.fetchone()
		if totalvote:
			totalvote = totalvote[0]
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Avatar Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"AvatarDtls":avatar_data,
	    								"OverallVotes":totalvote}}), status.HTTP_200_OK



@name_space.route("/getUserVoteDetails/<int:user_id>")
class getUserVoteDetails(Resource):
	def get(self,user_id):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = {"voted_id":"",
				   "avatar_id":"",
				   "avatar_name":""}

		cursor.execute("""SELECT `id`,`avatar_id` FROM `avatar_poll` WHERE `user_id` = %s""",(user_id))
		selected_id = cursor.fetchall()
		print(selected_id)
		if selected_id: 
			vote_id = selected_id[0][0]
			avatar_id = selected_id[0][1]
			details['voted_id'] = vote_id
			details['avatar_id'] = avatar_id
			print(vote_id,avatar_id)
			cursor.execute("""SELECT `avatar_name` FROM `avatar_master` 
				where avatar_id = %s""",(avatar_id))
			avatar_details = cursor.fetchone()
			avatar_name = avatar_details[0]
			details['avatar_name'] = avatar_name

			return ({"attributes": {
	    				"status_desc": "User Avatar Details.",
	    				"status": "success",
	    				"message": "You have already voted once.",
	    				"voted_for":avatar_name
	    				},
	    				"responseList":{"AvatarDtls":[]}}), status.HTTP_200_OK
		else:
			cursor.execute("""SELECT am.`avatar_id`, am.`avatar_name`, am.`gender`,am.`image_path`, 
			COUNT(ap.`avatar_id`) AS TotalVotes FROM avatar_poll ap 
			RIGHT JOIN `avatar_master` am ON ap.`avatar_id` = am.`avatar_id` 
			GROUP BY am.`avatar_id`""")

			desc = cursor.description
			column_names = [col[0] for col in desc]
			avatar_data = [dict(izip(column_names, row)) for row in cursor.fetchall()]
			cursor.execute("""SELECT count(`id`) FROM `avatar_poll`""")
			totalvote = cursor.fetchone()
			if totalvote:
				totalvote = totalvote[0]
			cursor.close()

			return ({"attributes": {
	    				"status_desc": "User Avatar Details.",
	    				"status": "success",
	    				"message": "You can Vote For an Avatar.",
	    				"voted_for":""
	    				},
	    				"responseList":{"AvatarDtls":avatar_data,
	    								"OverallVotes":totalvote}}), status.HTTP_200_OK
		


@name_space.route("/voteAvatarUsingPost")
class voteAvatarUsingPost(Resource):
	@api.expect(avatar_postmodel)
	def post(self):
		connection = mysql.connect()
		cursor = connection.cursor()
		details = request.get_json()

		user_id = details['user_id']
		avatar_id = details['avatar_id']

		user_avatar_insert_query = ("""INSERT INTO `avatar_poll`(`user_id`,`avatar_id`) 
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


if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)