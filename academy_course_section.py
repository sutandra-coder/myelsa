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
academy_course_details = Blueprint('academy_course_details_api', __name__)
api = Api(academy_course_details,  title='MyElsa Academy API',description='MyElsa Academy API')
name_space = api.namespace('academyCourseDetails',description='Academy Course Details')


@name_space.route("/getUserEnrolledCourses/<int:user_id>")
class getUserEnrolledCourses(Resource):
	def get(self,user_id):

		courseDtls = [{'course_id':1,
						'course_name':'Teacher Training'}]

		return ({"attributes": {"status_desc": "User Enrolled Course List",
								"status": "success"},
				"responseList":courseDtls})


@name_space.route("/getProgramListByCourseId/<int:user_id>/<int:course_id>")
class getProgramListByCourseId(Resource):
	def get(self,user_id,course_id):

		moduleDtls = [{'module_id':1,
						'module_type':'Module',
						'module_name':'Teacher Training 1',
						'module_no':'Module 1',
						'module_description':'',
						'sequence_id':1
						},
						{'module_id':2,
						'module_type':'Module',
						'module_name':'Teacher Training 2',
						'module_no':'Module 2',
						'module_description':'',
						'sequence_id':2
						},
						{'module_id':3,
						'module_type':'Module',
						'module_name':'Teacher Training 3',
						'module_no':'Module 3',
						'module_description':'',
						'sequence_id':3
						},
						{'module_id':4,
						'module_type':'Case Study',
						'module_name':'Teacher Training 3',
						'module_no':'Case Study 1',
						'module_description':'',
						'sequence_id':4
						}]

		return ({"attributes": {"status_desc": "Module List",
								"status": "success"},
				"responseList":moduleDtls})


@name_space.route("/getSessionListByModuleId/<int:user_id>/<int:module_id>")
class getSessionListByModuleId(Resource):
	def get(self,user_id,module_id):



		sessionDtls = [{'session_id':1,
						'session_name':'Teacher Training 1',
						'session_no':'Session 1',
						'session_description':'',
						'sequence_id':1,
						'segmentDtls':[{'segment_id':1,
										'segment_name':'Teacher Training 1',
										'sequence_id':1}]
						}]

		return ({"attributes": {"status_desc": "Session List",
								"status": "success"},
				"responseList":sessionDtls})