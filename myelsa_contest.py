from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
import requests
import calendar
import json

app = Flask(__name__)
cors = CORS(app)

#----------------------database-connection-loginDb---------------------#
def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection-loginDb---------------------#

myelsa_contest = Blueprint('myelsa_contest_api', __name__)
api = Api(myelsa_contest,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaContest',description='Myelsa Contest')

usercontest_postmodel = api.model('userContest',{
	"contest_id":fields.Integer(required=True),
	"student_id":fields.Integer(required=True),
	"content":fields.String(required=True),
	"file_type":fields.String(required=True)
})

student_contest_enquiery_postmodel = api.model('studentContestEnquiery',{
	"contest_id":fields.Integer(required=True),
	"student_id":fields.Integer(required=True),
	"text":fields.String(required=True),
	"title":fields.String
})

#-----------------------Get-Contest-List----------------------#

@name_space.route("/getContestList/<int:dashboard_id>/<int:student_id>")	
class getContestList(Resource):
	def get(self,dashboard_id,student_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `contest`			
			WHERE `dashboard_id` = %s""")

		get_data = (dashboard_id)
		cursor.execute(get_query,get_data)

		contest_data = cursor.fetchall()

		for key,data in enumerate(contest_data):

			get_student_submission = ("""SELECT *
				FROM `user_contest`			
				WHERE `contest_id` = %s and `student_id` = %s""")
			get_student_submission_data = (data['contest_id'],student_id)
			student_submission_count = cursor.execute(get_student_submission,get_student_submission_data)

			if student_submission_count > 0:
				contest_data[key]['is_submission'] = 1
			else:
				contest_data[key]['is_submission'] = 0

			contest_data[key]['payment_status'] = 0
			contest_data[key]['Last_Update_TS'] = str(data['Last_Update_TS'])

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "contest_details",
		    		"status": "success"
		    	},
		    	"responseList":contest_data}), status.HTTP_200_OK

#-----------------------Get-Contest-List----------------------#

#----------------------Save-User-Contest---------------------#

@name_space.route("/saveUserContest")	
class saveUserContest(Resource):
	@api.expect(usercontest_postmodel)
	def put(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		contest_id = details['contest_id']
		student_id = details['student_id']
		content = details['content']
		file_type = details['file_type']

		get_query = ("""SELECT *
			FROM `user_contest` WHERE `contest_id` = %s and `student_id` = %s""")

		getData = (contest_id,student_id)

		count_user_contest = cursor.execute(get_query,getData)

		if count_user_contest >0 :
			update_query = ("""UPDATE `user_contest` SET `content` = %s , `file_type` = %s
								WHERE `contest_id` = %s and `student_id` = %s""")
			update_data = (content,file_type,contest_id,student_id)
			cursor.execute(update_query,update_data)
		else:
			insert_query = ("""INSERT INTO `user_contest`(`contest_id`,`student_id`,`content`,`file_type`) 
					VALUES(%s,%s,%s,%s)""")

			data = (contest_id,student_id,content,file_type)
			cursor.execute(insert_query,data)			

		connection.commit()
		cursor.close()

		return ({"attributes": {
			    		"status_desc": "user_contest_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK


#----------------------Save-User-Contest---------------------#

#-----------------------Get-Student-Submission----------------------#

@name_space.route("/getMySubmission/<int:student_id>/<int:contest_id>")	
class getMySubmission(Resource):
	def get(self,student_id,contest_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT uc.`content`,c.`contest_name`,uc.`Last_Update_TS`
			FROM `user_contest` uc
			INNER JOIN `contest` c ON c.`contest_id` = uc.`contest_id`			
			WHERE uc.`student_id` = %s and uc.`contest_id` = %s ORDER BY uc.`mapping_id` DESC""")

		get_data = (student_id,contest_id)
		cursor.execute(get_query,get_data)

		my_submission_data = cursor.fetchall()

		for key,data in enumerate(my_submission_data):
			my_submission_data[key]['Last_Update_TS'] = str(data['Last_Update_TS'])

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "submission_details",
		    		"status": "success"
		    	},
		    	"responseList":my_submission_data}), status.HTTP_200_OK

#-----------------------Get-Student-Submission----------------------#

#-----------------------Student-Contest-Enquiery----------------------#

@name_space.route("/saveStudentContestEnquiery")	
class saveStudentContestEnquiery(Resource):
	@api.expect(student_contest_enquiery_postmodel)
	def post(self):		
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		contest_id = details['contest_id']
		student_id = details['student_id']
		text = details['text']
		title = details['title']

		insert_query = ("""INSERT INTO `contest_enquiry`(`contest_id`,`student_id`,`text`,`title`) 
				VALUES(%s,%s,%s,%s)""")

		data = (contest_id,student_id,text,title)
		cursor.execute(insert_query,data)

		details['enquiery_id'] = cursor.lastrowid

		return ({"attributes": {
			    		"status_desc": "contest_enquiery_details",
			    		"status": "success"
			    	},
			    	"responseList":details}), status.HTTP_200_OK

#-----------------------Student-Contest-Enquiery----------------------#

#-----------------------Get-Contest-Resource-List----------------------#

@name_space.route("/getContestResources/<int:contest_id>/<int:resource_type>")	
class getContestResourcesList(Resource):
	def get(self,contest_id,resource_type):
		connection = mysql_connection()
		cursor = connection.cursor()

		get_query = ("""SELECT *
			FROM `contest_resources`			
			WHERE `contest_id` = %s and `resource_type` = %s""")

		get_data = (contest_id,resource_type)
		cursor.execute(get_query,get_data)

		contest_data = cursor.fetchall()

		for key,data in enumerate(contest_data):
			contest_data[key]['Last_Update_TS'] = str(data['Last_Update_TS'])

		connection.commit()
		cursor.close()
				
		return ({"attributes": {
		    		"status_desc": "contest_details",
		    		"status": "success"
		    	},
		    	"responseList":contest_data}), status.HTTP_200_OK

#-----------------------Get-Contest-Resource-List----------------------#

