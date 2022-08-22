from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from database_connections import connect_elsalibrary,connect_logindb
import requests
import calendar
import json
from threading import Thread
import time

app = Flask(__name__)
cors = CORS(app)

myelsa_leaderboard = Blueprint('myelsa_leaderboard_api', __name__)
api = Api(myelsa_leaderboard,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaLeaderboard',description='Myelsa Leaderboard')

base_url = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"

def last_update_ts():
	return (datetime.now() + timedelta(days=0, hours=5, minutes=30)).strftime('%Y-%m-%dT%H:%M:%S')

@name_space.route("/get_quiz_leaderboard/<exam_id>")
class get_quiz_leaderboard(Resource):
	def get(self,exam_id):
		
		loginconnection = connect_logindb()
		logincursor = loginconnection.cursor()
		connection = connect_elsalibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `student_id`,`total_marks` FROM `publish_exam_results` WHERE `exam_id` = %s ORDER BY `total_marks` DESC""",(exam_id))

		student_dtls = cursor.fetchall()
		for student in student_dtls:

			logincursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`) as 'student_name',`IMAGE_URL` FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(student['student_id']))

			temp = logincursor.fetchone()
			if temp:
				student['student_name'] = temp['student_name']
				student['IMAGE_URL'] = temp['IMAGE_URL']
			else:
				student['student_name'] = ""
				student['IMAGE_URL'] = ""

		index = 0
		prevRank = -1
		prevPoints = -1
		for student in student_dtls:
			if student['total_marks'] == prevPoints:
				student['rank'] = prevRank
			else:
				student['rank'] = index+1
				prevRank = index + 1
				prevPoints = student['total_marks']
			index = index + 1

		return ({"attributes": {"status_desc": "Quiz Leaderboard Details",
			"status": "success"},
			"responseList": student_dtls}), status.HTTP_200_OK

def myFunc(e):
	return e['points']

@name_space.route("/get_course_leaderboard/<course_id>/<institution_id>")
class get_course_leaderboard(Resource):
	def get(self,course_id,institution_id):

		connection = connect_elsalibrary()
		cursor = connection.cursor()
		loginconnection = connect_logindb()
		logincursor=loginconnection.cursor()

		cursor.execute("""SELECT `student_id` FROM `student_course_master` WHERE `course_id` = %s""",(course_id))

		student_dtls = cursor.fetchall()
		for student in student_dtls:

			cursor.execute("""SELECT COUNT(`course_content_id`) as 'count' FROM `user_course_content_tracking` WHERE `course_id` = %s AND `user_id` = %s""",(course_id,student['student_id']))
			student['points'] = cursor.fetchone()['count']
			logincursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`) as 'student_name',`IMAGE_URL` FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(student['student_id']))

			temp = logincursor.fetchone()
			if temp:
				student['student_name'] = temp['student_name']
				student['IMAGE_URL'] = temp['IMAGE_URL']
			else:
				student['student_name'] = ""
				student['IMAGE_URL'] = ""

		student_dtls.sort(key=myFunc,reverse=True)
		index = 0
		prevRank = -1
		prevPoints = -1
		for student in student_dtls:
			if student['points'] == prevPoints:
				student['rank'] = prevRank
			else:
				student['rank'] = index+1
				prevRank = index + 1
				prevPoints = student['points']
			index = index + 1

		return ({"attributes": {"status_desc": "Quiz Leaderboard Details",
			"status": "success"},
			"responseList": student_dtls}), status.HTTP_200_OK

publish_exam_section=api.model('publish_exam_section',{
	"exam_id":fields.Integer(),
	"student_id":fields.Integer(),
	"total_marks":fields.Integer(),
	"last_update_id":fields.Integer()
	})

@name_space.route("/Publishexamresult")
class Publishexamresult(Resource):
	@api.expect(publish_exam_section)
	def post(self):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		details = request.get_json()

		exam_id=details["exam_id"]
		student_id=details["student_id"]
		total_marks=details["total_marks"]
		last_update_id=details["last_update_id"]

		exam_query=("""INSERT INTO `publish_exam_results`(`exam_id`,`student_id`,`total_marks`,`last_update_id`) VALUES(%s,%s,%s,%s)""")
		exam_data=(exam_id,student_id,total_marks,last_update_id)

		publishexam=cursor.execute(exam_query,exam_data)
		msg=""

		if publishexam:
			msg="inserted"
		else:
			msg="not inserted"

		return ({"attributes": {"status_desc": "Exam Section",
                                "status": "success",
                                "msg": msg
                                },
	             "responseList": details}), status.HTTP_200_OK

#----------------------------------------------get api for marks------------------------------------------------------#
@name_space.route("/get_quizzes_by_course_id/<int:course_id>/<int:student_id>")
class get_quizzes_by_course_id(Resource):
	def get(self,course_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		test_query=("""SELECT `exam_id`,`name`,`duration`,`fullmarks` FROM `exam_master` WHERE `course_id`=%s""")
		test_data=(course_id)
		test_details_count=cursor.execute(test_query,test_data)
		test_details=cursor.fetchall()
		if test_details:
			for key,data in enumerate(test_details):
				marks_query=("""SELECT `total_marks` FROM `publish_exam_results` WHERE `exam_id`=%s AND `student_id`=%s""")
				marks_data=(data["exam_id"],student_id)
				marks_count=cursor.execute(marks_query,marks_data)
				if marks_count>0:
					marks=cursor.fetchone()
					test_details[key]["total_marks"]=marks["total_marks"]
				else:
					test_details[key]["total_marks"]=-1


		return ({"attributes": {"status_desc": "Test List",
	                            "status": "success",
	                            
	                            },
	             "responseList": test_details}), status.HTTP_200_OK

#---------------------------------------------------------option check api----------------------------------------------------------#

@name_space.route("/get_students_marks/<int:exam_id>/<int:student_id>")
class get_students_marks(Resource):
	def get(self,exam_id,student_id):
		connection = connect_elsalibrary()
		cursor = connection.cursor()
		total=0
		details=[]

		question_query=("""SELECT `question_id`,`answer` FROM `student_question_mapping` WHERE `exam_id`=%s AND `student_id`=%s AND `question_status`="answered" """)
		question_data=(exam_id,student_id)
		question_count=cursor.execute(question_query,question_data)

		if question_count>0:
			questions=cursor.fetchall()
			for key,data in enumerate(questions):
				solution_query=("""SELECT `marks`,`solution` FROM `question` WHERE `question_id`=%s""")
				solution_data=(data["question_id"])
				solution_count=cursor.execute(solution_query,solution_data)
				if solution_count>0:
					solutions=cursor.fetchone()
					details.append(solutions)


			for key,data in enumerate(details):
				if data["solution"]==questions[key]["answer"]:
					total+=data["marks"]
				else:
					total+=0

			return ({"attributes": {"status_desc": "Correct Option Check",
	                            "status": "success",
	                            
	                            },
	             "responseList": total}), status.HTTP_200_OK