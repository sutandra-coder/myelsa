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
from threading import Thread
import time

app = Flask(__name__)
cors = CORS(app)

#----------------------database-connection---------------------#
'''def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_user_library',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection


def mysql_connection_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection'''

#----------------------database-connection-loginDb---------------------#

def mysql_connection():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


def mysql_connection_logindb():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


myelsa_online_test = Blueprint('myelsa_online_test_api', __name__)
api = Api(myelsa_online_test,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaOnlineTest',description='Myelsa Online Test')

online_test_postmodel = api.model('SelectOnlineTest', {
	"institution_id":fields.Integer(required=True),
	"institution_user_id":fields.Integer(required=True),
	"title":fields.String(required=True),
	"total_marks":fields.Integer(required=True),
	"duration":fields.Integer(required=True),
	"subject_id":fields.Integer(required=True),
	"topic_id":fields.Integer(required=True),
	"class":fields.String(required=True),
	"board":fields.String(required=True)
	})

online_test_putmodel = api.model('UpdateOnlineTest', {
	"institution_id":fields.Integer(required=True),
	"institution_user_id":fields.Integer(required=True),
	"title":fields.String(required=True),
	"total_marks":fields.Integer(required=True),
	"duration":fields.Integer(required=True),
	"subject_id":fields.Integer(required=True),
	"topic_id":fields.Integer(required=True),
	"class":fields.String(required=True),
	"board":fields.String(required=True)
	})

online_test_student_model = api.model('SelectOnlineTestStudent', {
	"online_test_id":fields.Integer(required=True),
	"Institution_ID":fields.Integer(required=True),
	"student_id":fields.List(fields.Integer()),
	"group_id":fields.List(fields.Integer()),
	"start_time":fields.String(required=True),
	"end_time":fields.String(required=True),
	"is_group":fields.String(required=True),
	"teacher_id":fields.Integer(required=True)
	})

delete_online_test_student_model = api.model('DeleteOnlineTestStudent', {
	"online_test_id":fields.Integer(required=True),
	"Institution_ID":fields.Integer(required=True),
	"student_id":fields.List(fields.Integer()),
	"group_id":fields.List(fields.Integer()),
	"is_group":fields.String(required=True),
	"teacher_id":fields.Integer(required=True)
	})


# BASE_URL = 'http://127.0.0.1:5000/'

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'

def sendAssignmentNotification(request):
	onlinetest_id,studentList = request

	connection = mysql_connection()
	curLib = connection.cursor()
	conn = mysql_connection_logindb()
	curLog = conn.cursor()

	# url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
	appResponse = []

	url = BASE_URL + 'app_notify/AppCommunicationAPI/appMessage'
	headers = {'Content-type':'application/json', 'Accept':'application/json'}

	curLib.execute("""SELECT `Title` FROM `online_test` WHERE `Online_Test_ID` = %s""",(onlinetest_id))
	testDtls = curLib.fetchone()
	test_name = testDtls.get('Title')

	studentList = list(set(studentList))
	print(studentList)
	for sid in studentList:
		curLog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(sid))
		student = curLog.fetchone()

		
		if student:
			student_name = student['name']
			sdata = {'appParams': {},
					'mailParams': {"studentname":student_name,
									"test_name":test_name},
					'role': 'S1',
					'toMail': '',
					'toNumber': '',
					'userId': sid,
					'sourceapp': 'ONLNTSTS01'
					}
			
			appResponse.append(requests.post(url, data=json.dumps(sdata), headers=headers).json())
			
	curLib.close()
	curLog.close()

	return appResponse


class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'AssignOnlineTest':
			sendAssignmentNotification(self.request)
		else:
			pass

#----------------------Post-Online-Test---------------------#
@name_space.route("/OnlineTest")
class OnlineTest(Resource):
	@api.expect(online_test_postmodel)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		institution_id = details['institution_id']
		institution_user_id = details['institution_user_id']
		title = details['title']
		total_marks = details['total_marks']
		duration = details['duration']
		subject_id = details['subject_id']
		topic_id = details['topic_id']
		Class = details['class']
		board = details['board']

		insert_query = ("""INSERT INTO `online_test`(`Institution_ID`,`Institution_user_ID`,`Title`,`Total_Marks`,
		`duration`,`Subject_id`,`Topic_id`,`Class`,`Board`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		data = (institution_id,institution_user_id,title,total_marks,duration,subject_id,topic_id,Class,board)
		cursor.execute(insert_query,data)

		connection.commit()
		cursor.close()
		return ({"attributes": {
	    				"status_desc": "Online Test Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"OnlineTestDtls":details}}), status.HTTP_200_OK

#----------------------Post-Online-Test---------------------#

#----------------------Put-Online-Test---------------------#
@name_space.route("/onlineTestPut/<int:online_test_id>")
class onlineTestPut(Resource):
	@api.expect(online_test_putmodel)
	def put(self, online_test_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		
		institution_id = details['institution_id']
		institution_user_id = details['institution_user_id']
		title = details['title']
		total_marks = details['total_marks']
		duration = details['duration']
		subject_id = details['subject_id']
		topic_id = details['topic_id']
		Class = details['class']
		board = details['board']
		
		online_test_update_query = ("""UPDATE `online_test` SET `Institution_ID` = %s,`Institution_user_ID` = %s,
				`Title` = %s,`Total_Marks` = %s,`duration` = %s,`Subject_id` = %s,`Topic_id` =  %s,`Class` = %s,`Board` = %s
				WHERE `Online_Test_ID` = %s """)
		update_data = (institution_id,institution_user_id,title,total_marks,duration,subject_id,topic_id,Class,board,online_test_id)
		cursor.execute(online_test_update_query,update_data)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Online Test",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK

#----------------------Put-Online-Test---------------------#

#----------------------Delete-Online-Test---------------------#

@name_space.route("/onlineTestDelete/<int:online_test_id>")
class onlineTestDelete(Resource):
	def delete(self, online_test_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		online_test_delete_query = ("""DELETE FROM `online_test` WHERE `Online_Test_ID` = %s """)
		delData = (online_test_id)
		
		cursor.execute(online_test_delete_query,delData)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Delete Online Test",
								"status": "success"},
				"responseList": 'Deleted Successfully'}), status.HTTP_200_OK

#----------------------Delete-Online-Test---------------------#				

#----------------------Get-Online-Test---------------------#		
@name_space.route("/getOnlineTest/<string:key>/<int:key_id>/<int:institution_id>/<int:user_id>")	
class getOnlineTest(Resource):
	def get(self, key,key_id,institution_id,user_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		if key == "a":
			online_test_get_query = ("""SELECT `Online_Test_ID`,`Institution_ID`,`Institution_user_ID`,`Title`,`Total_Marks`,`duration`,
			`Subject_id`,`Topic_id`,`Class`,`Board`
			FROM `online_test` WHERE `institution_id` = %s and `institution_user_id` = %s order by `Last_update_TS` DESC""")
		if key == "su":
			online_test_get_query = ("""SELECT `Online_Test_ID`,`Institution_ID`,`Institution_user_ID`,`Title`,`Total_Marks`,`duration`,
			`Subject_id`,`Topic_id`,`Class`,`Board`
			FROM `online_test` WHERE `Subject_id` = %s and `institution_id` = %s 
			and `institution_user_id` = %s order by `Last_update_TS` DESC""")
		if key == "t":
			online_test_get_query = ("""SELECT `Online_Test_ID`,`Institution_ID`,`Institution_user_ID`,`Title`,`Total_Marks`,`duration`,
			`Subject_id`,`Topic_id`,`Class`,`Board`
			FROM `online_test` WHERE `Topic_id` = %s and `institution_id` = %s 
			and `institution_user_id` = %s order by `Last_update_TS` DESC""")
		if key == "st":
			online_test_get_query = ("""SELECT ot.`Online_Test_ID`,ot.`Institution_ID`,ot.`Institution_user_ID`,ot.`Title`,ot.`Total_Marks`,ot.`duration`,
			ot.`Subject_id`,ot.`Topic_id`,ot.`Class`,ot.`Board`,otsm.`Marks`
			FROM `online_test` ot
			INNER JOIN `online_test_student_mapping` otm ON ot.`Online_Test_ID` = otm.`online_test_id` 
			INNER JOIN `online_test_student_marks` otsm ON ot.`Online_Test_ID` = otsm.`online_test_id` 
			WHERE otm.`Institution_user_ID` = %s and ot.`institution_id` = %s 
			and ot.`Institution_user_ID` = %s and otsm.`Student_ID` = %s order by ot.`Last_update_TS` DESC""")
		if key == "g":
			online_test_get_query = ("""SELECT ot.`Online_Test_ID`,ot.`Institution_ID`,ot.`Institution_user_ID`,ot.`Title`,ot.`Total_Marks`,ot.`duration`,
			ot.`Subject_id`,ot.`Topic_id`,ot.`Class`,ot.`Board`
			FROM `online_test` ot
			LEFT JOIN `online_test_student_mapping` otm ON ot.`Online_Test_ID` = otm.`online_test_id` 
			WHERE otm.`Group_ID` = %s and ot.`institution_id` = %s 
			and ot.`institution_user_id` = %s order by ot.`Last_update_TS` DESC""")
			
		if key == "rp":
			online_test_get_query = ("""SELECT ot.`Online_Test_ID`,ot.`Institution_ID`,ot.`Institution_user_ID`,ot.`Title`,ot.`Total_Marks`,ot.`duration`,
			ot.`Subject_id`,ot.`Topic_id`,ot.`Class`,ot.`Board`
			FROM `online_test` ot
			LEFT JOIN `online_test_student_marks` otm ON ot.`Online_Test_ID` = otm.`Online_Test_ID` 
			WHERE otm.`is_reviwed` = 'n' and ot.`institution_id` = %s 
			and ot.`institution_user_id` = %s group by otm.`Online_Test_ID` order by ot.`Last_update_TS` DESC""")
		
		if key == "ua":
			online_test_get_query = ("""SELECT ot.`Online_Test_ID`,ot.`Institution_ID`,ot.`Institution_user_ID`,ot.`Title`,ot.`Total_Marks`,
			ot.`duration`, ot.`Subject_id`,ot.`Topic_id`,ot.`Class`,ot.`Board` FROM `online_test` ot where ot.`Online_Test_ID` 
			not in (select otm.`Online_Test_ID` from `online_test_student_mapping` otm) and ot.`institution_id` = %s and 
			ot.`institution_user_id` = %s order by ot.`Last_update_TS` DESC""")

		

		if key == "st":
			getData = (key_id,institution_id,user_id,key_id)
		else:
			if key == "a" or key == "rp" or key =="ua":
				getData = (institution_id,user_id)
			else:	
				getData = (key_id,institution_id,user_id)		
		
		rows_count  = cursor.execute(online_test_get_query,getData)

		#print(cursor._last_executed)
		
		online_test_data = cursor.fetchall()


		
		if rows_count>0:
			return ({"attributes": {
		    				"status_desc": "Test_details",
		    				"status": "success"
		    				},
		    				"responseList":online_test_data}), status.HTTP_200_OK
		else:
			return ({"attributes": {
		    				"status_desc": "No_Test",
		    				"status": "success"
		    				},
		    				"responseList":online_test_data}), status.HTTP_200_OK


#----------------------Get-Online-Test---------------------#

#----------------------Dashboard---------------------#	
@name_space.route("/dashboard/<int:institution_id>/<int:user_id>")
class dashboard(Resource):
	def get(self,institution_id,user_id):		
		connection = mysql_connection()
		cursor = connection.cursor()
		
		online_test_dashboard_query_review_pending = ("""SELECT count(otm.`Online_Test_ID`) review_pending_count 
			FROM `online_test` ot
			LEFT JOIN `online_test_student_marks` otm ON ot.`Online_Test_ID` = otm.`Online_Test_ID` 
			WHERE otm.`is_reviwed` = 'n' and ot.`institution_id` = %s and ot.`institution_user_id` = %s group by otm.`Online_Test_ID`""")
		
		online_test_dashboard_query_test_count = ("""SELECT count(`Online_Test_ID`) test_count 
			FROM `online_test` ot			
			WHERE ot.`institution_id` = %s and ot.`institution_user_id` = %s """)
		
		getData = (institution_id,user_id)		
		
		cursor.execute(online_test_dashboard_query_review_pending,getData)		
		online_test_data_review_pending = cursor.fetchone()	
		
		cursor.execute(online_test_dashboard_query_test_count,getData)		
		online_test_data_count = cursor.fetchone()
		
		return ({"attributes": {
	    				"status_desc": "Online Test Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"review_pending_count":online_test_data_review_pending['review_pending_count'],
														  "total_test_count":online_test_data_count['test_count']
						}}), status.HTTP_200_OK
						
#----------------------Dashboard---------------------#

#----------------------Assign-Online-Test---------------------#
@name_space.route("/AssignOnlineTest/")
class AssignOnlineTest(Resource):
	@api.expect(online_test_student_model)
	def post(self):	

		details = request.get_json()

		sconnection = mysql_connection()
		gconnection = mysql_connection_logindb()

		cursor = sconnection.cursor()
		cur = gconnection.cursor()

		online_test_id = details['online_test_id']
		Institution_ID = details['Institution_ID']
		studentList = details.get('student_id',[])
		groupList = details.get('group_id',[])
		is_group = details.get('is_group')
		start_time = details['start_time']
		end_time = details['end_time']
		nstatus = "n"
		No_Of_attempts = 0
		teacher_id = details['teacher_id']

		if is_group == "n":
			insert_query = ("""INSERT INTO `online_test_student_mapping`(`online_test_id`,`Institution_ID`,
					`Institution_user_ID`,`teacher_id`,`status`,`No_Of_attempts`,`start_time`,`end_time`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
			
			for sid in studentList:
				data= (online_test_id,Institution_ID,sid,teacher_id,nstatus,No_Of_attempts,start_time,end_time)

				cursor.execute(insert_query,data)
				
				msg = "Saved Data Successfully"

		else:
			for gid in groupList:
				group_student_get_query = ("""SELECT gsm.`Group_ID`,gsm.`Student_Id`
				FROM `group_student_mapping` gsm
				WHERE gsm.`Group_ID` = %s """)

				getData = (gid)		
			
				cur.execute(group_student_get_query,getData)	

				student_mapping_data = cur.fetchall()
				
				if student_mapping_data != ():
					for data in student_mapping_data:
						Institution_user_ID = data['Student_Id']
						group_ID = data['Group_ID']
						
						studentList.append(Institution_user_ID)
						insert_query = ("""INSERT INTO `online_test_student_mapping`(`online_test_id`,`Institution_ID`,
						`Institution_user_ID`,`Group_ID`,`teacher_id`,`status`,`start_time`,`end_time`) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""")
						data = (online_test_id,Institution_ID,Institution_user_ID,group_ID,teacher_id,nstatus,start_time,end_time)
						cursor.execute(insert_query,data)

						
					insert_query_batch_mapping = ("""INSERT INTO `online_test_batch_mapping`(`online_test_id`,`Institution_ID`,
						`teacher_id`,`Group_ID`) VALUES(%s,%s,%s,%s)""")
					batch_data = (online_test_id,Institution_ID,teacher_id,group_ID)
					cursor.execute(insert_query_batch_mapping,batch_data)
					msg = "Saved Data Successfully"
				else:
					msg = "No student in group"

		sendrReq = (online_test_id,studentList)
		thread_a = Compute(sendrReq,'AssignOnlineTest')
		thread_a.start()
		
		cursor.close()
		cur.close()		

		return ({"atributes": {
	    			"status_desc": "Assign Online Test",
	    			"status": "success"
	    			},
	    			"responseList":msg}), status.HTTP_200_OK

#----------------------Assign-Online-Test---------------------#

#----------------------Online-Test-Student-list---------------------#
@name_space.route("/getOnlineTestAssignList/<string:key>/<int:Institution_ID>/<int:teacher_id>/<int:online_test_id>")	
class getOnlineTestAssignList(Resource):
	def get(self, key,Institution_ID,teacher_id,online_test_id):
		sconnection = mysql_connection()
		gconnection = mysql_connection_logindb()

		cursor = sconnection.cursor()
		cur = gconnection.cursor()

		if key == "s":
			online_test_assign_get_query = ("""SELECT `online_test_id`,`Institution_ID`,`Institution_user_ID`
			FROM `online_test_student_mapping` WHERE `Institution_ID` = %s and `teacher_id` = %s and `online_test_id` = %s""")

			getData = (Institution_ID,teacher_id,online_test_id)

			cursor.execute(online_test_assign_get_query,getData)

			online_test_assign_data = cursor.fetchall()

			for key,data in enumerate(online_test_assign_data):
				get_student_query = ("""SELECT `STUDENT_NAME`,`Image_URL`
				FROM `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` = %s and INSTITUTION_ID =%s""")

				studentData = (data['Institution_user_ID'],Institution_ID)

				row_count_student = cur.execute(get_student_query,studentData)

				if row_count_student>0:
					student_data = cur.fetchone()

					online_test_assign_data[key]['student_name'] = student_data['STUDENT_NAME']
					online_test_assign_data[key]['image_url'] = student_data['Image_URL']
				else:
					online_test_assign_data[key]['student_name'] = ""
					online_test_assign_data[key]['image_url'] = ""
			

		if key == "g":

			online_test_assign_get_query = ("""SELECT `online_test_id`,`Institution_ID`,`teacher_id`,`Group_ID`
			FROM `online_test_batch_mapping` WHERE `Institution_ID` = %s and `teacher_id` = %s and `online_test_id` = %s""")


			getData = (Institution_ID,teacher_id,online_test_id)

			cursor.execute(online_test_assign_get_query,getData)

			online_test_assign_data = cursor.fetchall()

			for key,data in enumerate(online_test_assign_data):
				get_student_query = ("""SELECT `Group_Description`
				FROM `group_master` WHERE `Group_ID` = %s and Institution_ID =%s""")

				studentData = (data['Group_ID'],Institution_ID)

				row_count_student = cur.execute(get_student_query,studentData)

				if row_count_student>0:
					student_data = cur.fetchone()

					online_test_assign_data[key]['Group_Description'] = student_data['Group_Description']					
				else:
					online_test_assign_data[key]['Group_Description'] = ""

		return ({"attributes": {
		    	"status_desc": "Assign List",
		    	"status": "success"
		    	},
		    	"responseList":online_test_assign_data}), status.HTTP_200_OK

#----------------------Online-Test-Student-list---------------------#

#----------------------Delete-Assign-Online-Test---------------------#
@name_space.route("/DeleteAssignOnlineTest/")
class DeleteAssignOnlineTest(Resource):
	@api.expect(delete_online_test_student_model)
	def delete(self):
		details = request.get_json()

		sconnection = mysql_connection()
		gconnection = mysql_connection_logindb()

		cursor = sconnection.cursor()
		cur = gconnection.cursor()

		online_test_id = details['online_test_id']
		Institution_ID = details['Institution_ID']
		studentList = details.get('student_id',[])
		groupList = details.get('group_id',[])
		is_group = details.get('is_group')
		teacher_id = details['teacher_id']

		if is_group == "n":
			delete_query = ("""DELETE FROM `online_test_student_mapping` WHERE `Online_Test_ID` = %s and Institution_ID = %s
				and Institution_user_ID = %s and teacher_id = %s""")
			

			for sid in studentList:
				Data = (online_test_id,Institution_ID,sid,teacher_id)
				cursor.execute(delete_query,Data)

		else:
			delete_query_student_mapping = ("""DELETE FROM `online_test_student_mapping` WHERE `Online_Test_ID` = %s and Institution_ID = %s
				 and teacher_id = %s and Group_ID = %s""")
			delete_query_batch_mapping = ("""DELETE FROM `online_test_batch_mapping` WHERE `online_test_id` = %s and Institution_ID = %s
				 and teacher_id = %s and Group_ID = %s""")

			for gid in groupList:
				student_map_Data = (online_test_id,Institution_ID,teacher_id,gid)
				cursor.execute(delete_query_student_mapping,student_map_Data)	
				cursor.execute(delete_query_batch_mapping,student_map_Data)
				
		return ({"atributes": {
	    			"status_desc": "Delete Assign Online Test",
	    			"status": "success"
	    			},
	    			"responseList":"Deleted Successfully"}), status.HTTP_200_OK		


#----------------------Delete-Assign-Online-Test---------------------#

#----------------------Examination-Details-By-Online-Test-ID---------------------#
@name_space.route("/examinationDetailsByOnlineTestId/<int:online_test_id>/<int:institution_id>")	
class examinationDetailsByOnlineTestId(Resource):
	def get(self, online_test_id,institution_id):

		sconnection = mysql_connection()
		gconnection = mysql_connection_logindb()

		cursor = sconnection.cursor()
		cur = gconnection.cursor()

		get_query = ("""SELECT `Online_Test_ID`,`Student_ID`,`Marks`,`No_Of_attempts`,`is_reviwed`
			FROM `online_test_student_marks` WHERE `Online_Test_ID` = %s""")

		getData = (online_test_id)
		
		rows_count  = cursor.execute(get_query,getData)
		
		online_test_student_marks_data = cursor.fetchall()

		for key,data in enumerate(online_test_student_marks_data):
			get_student_query = ("""SELECT `STUDENT_NAME`,`Image_URL`
			FROM `student_dtls` WHERE `INSTITUTION_USER_ID_STUDENT` = %s""")

			studentData = (data['Student_ID'])

			row_count_student = cur.execute(get_student_query,studentData)

			if row_count_student>0:
				student_data = cur.fetchone()

				online_test_student_marks_data[key]['student_name'] = student_data['STUDENT_NAME']
				online_test_student_marks_data[key]['image_url'] = student_data['Image_URL']
			else:
				online_test_student_marks_data[key]['student_name'] = ""
				online_test_student_marks_data[key]['image_url'] = ""

		if rows_count>0:
			return ({"attributes": {
		    				"status_desc": "Student Marks Detals",
		    				"status": "success"
		    				},
		    				"responseList":online_test_student_marks_data}), status.HTTP_200_OK

#----------------------Examination-Details-By-Online-Test-ID---------------------#
	
if __name__ == '__main__':
	app.run(host='0.0.0.0',debug=True)