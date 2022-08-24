from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
from threading import Thread
import time
from itertools import groupby

app = Flask(__name__)
cors = CORS(app)

def connect_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


myelsa_helpsection = Blueprint('myelsa_helpsection_api', __name__)
api = Api(myelsa_helpsection,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('myelsaHelpController',description='myelsaHelp Controller')


content_upload_model = api.model('content_upload_model', {
	"dashboard_desc":fields.String(),
	"dashboard_desc_id":fields.Integer(),
	"help_content_filepath":fields.String(),
	"filetype":fields.String(),
	"user_role":fields.String(),
	"sequence_id":fields.Integer()
	})


@name_space.route("/getDashboardMasterDetails")
class getDashboardMasterDetails(Resource):
	def get(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT `dashboard_master_id`,`dashboard_desc` FROM `dashboard_master`""")
		dashboardDtls = cursor.fetchall()

		cursor.close()
		return ({"attributes": {"status_desc": "Dashboard Details.",
								"status": "success"
								},
				"responseList": dashboardDtls}), status.HTTP_200_OK



@name_space.route("/postDashboardContentDetails")
class postDashboardContentDetails(Resource):
	@api.expect(content_upload_model)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		details = request.get_json()

		dashboard_desc = details.get('dashboard_desc')
		dashboard_desc_id = details.get('dashboard_desc_id')
		help_content_filepath = details.get('help_content_filepath')
		filetype = details.get('filetype')
		user_role = details.get('user_role')
		sequence_id = details.get('sequence_id')

		contentInsertQuery =("""INSERT INTO `help_section`(`sequence_id`,`dashboard_desc`, `dashboard_desc_id`, 
			`help_content_filepath`, `filetype`, `institution_user_role`) VALUES (%s,%s,%s,%s,%s,%s)""")

		contentData = (sequence_id,dashboard_desc,dashboard_desc_id,help_content_filepath,filetype,user_role)

		cursor.execute(contentInsertQuery,contentData)

		connection.commit()

		cursor.close()

		return ({"attributes": {"status_desc": "Dashboard Details.",
								"status": "success"
								},
				"responseList":details}), status.HTTP_200_OK


@name_space.route("/getDashboardContentDetails")
class getDashboardContentDetails(Resource):
	def get(self):

		connection = connect_logindb()
		cursor = connection.cursor()
		studentList= []
		teacherList = []
		adminList = []
		parentList = [] 
		cursor.execute("""SELECT `help_id`, `dashboard_desc`, `dashboard_desc_id`, `sequence_id`, 
			`help_content_filepath`, `filetype`, `institution_user_role` FROM `help_section`""")


		dashboardDtls = cursor.fetchall()

		studentList = list(filter(lambda a: (a.get('institution_user_role') == 'S1'),dashboardDtls))
		dashboardDescList = list(set([j.get('dashboard_desc') for i,j in enumerate(studentList)]))
		studentDashboard = [{'dashboard_desc':i,'dashboard_content':[]} for i in dashboardDescList]
		for did, dash in enumerate(studentList):
			for sid, item in enumerate(studentDashboard):
				if dash.get('dashboard_desc') == item.get('dashboard_desc'):
					studentDashboard[sid]['dashboard_content'].append(dash)

		teacherList = list(filter(lambda a: (a.get('institution_user_role') == 'TA'),dashboardDtls))
		dashboardDescList = list(set([j.get('dashboard_desc') for i,j in enumerate(teacherList)]))
		teacherDashboard = [{'dashboard_desc':i,'dashboard_content':[]} for i in dashboardDescList]
		for did, dash in enumerate(teacherList):
			for sid, item in enumerate(teacherDashboard):
				if dash.get('dashboard_desc') == item.get('dashboard_desc'):
					teacherDashboard[sid]['dashboard_content'].append(dash)

		adminList = list(filter(lambda a: (a.get('institution_user_role') == 'A1'),dashboardDtls))
		dashboardDescList = list(set([j.get('dashboard_desc') for i,j in enumerate(adminList)]))
		adminDashboard = [{'dashboard_desc':i,'dashboard_content':[]} for i in dashboardDescList]
		for did, dash in enumerate(adminList):
			for sid, item in enumerate(adminDashboard):
				if dash.get('dashboard_desc') == item.get('dashboard_desc'):
					adminDashboard[sid]['dashboard_content'].append(dash)

		parentList = list(filter(lambda a: (a.get('institution_user_role') == 'G1'),dashboardDtls))
		dashboardDescList = list(set([j.get('dashboard_desc') for i,j in enumerate(parentList)]))
		parentDashboard = [{'dashboard_desc':i,'dashboard_content':[]} for i in dashboardDescList]
		for did, dash in enumerate(parentList):
			for sid, item in enumerate(parentDashboard):
				if dash.get('dashboard_desc') == item.get('dashboard_desc'):
					parentDashboard[sid]['dashboard_content'].append(dash)

		details = {"studentDashboard":studentDashboard,
					"teacherDashboard":teacherDashboard,
					"adminDashboard":adminDashboard,
					"parentDashboard":parentDashboard}
		cursor.close()
		return ({"attributes": {"status_desc": "Dashboard Details.",
								"status": "success"
								},
				"responseList":details}), status.HTTP_200_OK

@name_space.route("/getDashboardHelpContentByDescIdAndUserRole/<int:dashboard_desc_id>/<string:user_role>")
class getDashboardHelpContentByDescIdAndUserRole(Resource):
	def get(self,dashboard_desc_id,user_role):

		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT `help_id`, `dashboard_desc`, `dashboard_desc_id`, `sequence_id`, 
			`help_content_filepath`, `filetype`, `institution_user_role` FROM `help_section` 
			WHERE `dashboard_desc_id` = %s 
			and `institution_user_role` = %s ORDER BY `sequence_id`""",(dashboard_desc_id,user_role))

		dashboardDtls = cursor.fetchall()

		cursor.close()
		return ({"attributes": {"status_desc": "Dashboard Details.",
								"status": "success"
								},
				"responseList":dashboardDtls}), status.HTTP_200_OK 


@name_space.route("/getDashboardHelpContentByUserRole/<string:user_role>")
class getDashboardHelpContentByUserRole(Resource):
	def get(self,user_role):

		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT `help_id`, `dashboard_desc`, `dashboard_desc_id`, `sequence_id`, 
			`help_content_filepath`, `filetype`, `institution_user_role` FROM `help_section` 
			WHERE `institution_user_role` = %s ORDER BY `sequence_id`""",(user_role))

		dashboardDtls = cursor.fetchall()
		dashboardDescList = list(set([j.get('dashboard_desc') for i,j in enumerate(dashboardDtls)]))
		userDashboard = [{'dashboard_desc':i,'dashboard_content':[]} for i in dashboardDescList]
		for did, dash in enumerate(dashboardDtls):
			for sid, item in enumerate(userDashboard):
				if dash.get('dashboard_desc') == item.get('dashboard_desc'):
					userDashboard[sid]['dashboard_content'].append(dash)

		cursor.close()
		return ({"attributes": {"status_desc": "Dashboard Details.",
								"status": "success"
								},
				"responseList":userDashboard}), status.HTTP_200_OK 