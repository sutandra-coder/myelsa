import pymysql
from datetime import datetime,timedelta,date
import requests
import json
import time
from threading import Thread
from flask import Flask, request, jsonify, json
from flask_api import status
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields

app = Flask(__name__)
cors = CORS(app)
demo_onboarding = Blueprint('demo_onboarding_api', __name__)
api = Api(demo_onboarding,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('demoOnboardingController',description='Demo Oboarding')

'''def connect_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def connect_logindb():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


def createGroup(institutionId, teacherId):
	connection = connect_logindb()
	cursor = connection.cursor()
	current_date = datetime.now()

	lastUpdateTimestamp = int(str(int(time.time()))+'000')
	groupList = ['WB Class 9', 'WB Class 10']
	gidList = []
	# dt_object = datetime.fromtimestamp(1588928098)
	# print(dt_object)
	for gid in range(len(groupList)):
		create_group = {"groupDescription": groupList[gid],
						"groupID": 0,
						"institutionID": institutionId,
						"lASTUPDATEID": str(teacherId),
						"lASTUPDATETIMESTAMP": lastUpdateTimestamp,
						"teacherId": teacherId}

		post_url = 'http://creamsonservices.com:8080/GroupsAndMarksServicesUpdate/createGroup'
		payload = json.dumps(create_group)
		# print(payload)
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		post_response = requests.post(post_url, data=payload, headers=headers)
		post_res_status = post_response.status_code
		groupId = post_response.json().get('GROUP_ID')

		gidList.append(groupId)
	cursor.close()
	
	return gidList
	

def addStudentToGroup(studentId,groupId,groupDesc,institutionId,teacherId):
	connection = connect_logindb()
	cursor = connection.cursor()
	current_date = datetime.now()

	lastUpdateTimestamp = int(str(int(time.time()))+'000')
	add_student = [
					{
					"groupDescription": groupDesc,
					"groupID": groupId,
					"lASTUPDATEID": str(teacherId),
					"lASTUPDATETIMESTAMP": lastUpdateTimestamp,
					"mappingID": 0,
					"studentId": studentId,
					"teacherId": teacherId 
						}
					]
	post_url = 'http://creamsonservices.com:8080/GroupsAndMarksServicesUpdate/MapStudentGroup'
	payload = json.dumps(add_student)
	# print(payload)
	headers = {'Content-type':'application/json', 'Accept':'application/json'}
	post_response = requests.post(post_url, data=payload, headers=headers)
	post_res_status = post_response.status_code
	cursor.close()
	return 'success'


def createAssignment(teacherId):
	connection = connect_logindb()
	cursor = connection.cursor()
	current_date = datetime.now()
	lastUpdateTimestamp = int(str(int(time.time()))+'000')
	# print(lastUpdateTimestamp)
	aidList = []
	create_assignment = {
							"assignmentID": 0,
							"assignmentType": "video",
							"contentFileType": "video",
							"contentPath": "http://creamsonservices.com/Video/The_Adventurous_Clown.mp4",
							"lASTUPDATEID": str(teacherId),
							"lASTUPDATETIMESTAMP": lastUpdateTimestamp,
							"teacherId": str(teacherId),
							"remarks": 0,
							"title": "Demo assignment One"
						}

	post_url = 'http://creamsonservices.com:8080/StudentAssignmentServices_base64/createAssignment'
	payload = json.dumps(create_assignment)
	# print(payload)
	headers = {'Content-type':'application/json', 'Accept':'application/json'}
	post_response = requests.post(post_url, data=payload, headers=headers)
	assignmentId = post_response.json().get('AssignmentId')
	aidList.append(assignmentId)
	create_assignment = {
							"assignmentID": 0,
							"assignmentType": "image",
							"contentFileType": "image",
							"contentPath": "http://creamsonservices.com/Image/Asleep_In_The_Valley.jpg",
							"lASTUPDATEID": str(teacherId),
							"lASTUPDATETIMESTAMP": lastUpdateTimestamp,
							"teacherId": str(teacherId),
							"remarks": 0,
							"title": "Demo assignment Two"
						}
	payload = json.dumps(create_assignment)
	post_response = requests.post(post_url, data=payload, headers=headers)
	assignmentId = post_response.json().get('AssignmentId')

	aidList.append(assignmentId)
	# print(aidList)
	post_res_status = post_response.status_code
	cursor.close()
	return aidList



def assignStudent(teacherId,studentId,groupId,assignmentDesc,assignmentId):
	connection = connect_logindb()
	cursor = connection.cursor()
	current_date = datetime.now()
	lastUpdateTimestamp = int(str(int(time.time()))+'000')
	# print(lastUpdateTimestamp)
	aidList = []

	assign_student = [
							{
							"assignmentDescription": assignmentDesc,
							"assignmentId": assignmentId,
							"clas": "",
							"dUEDATE": "2020-12-31",
							"groupID": groupId,
							"iD": 0,
							"lastUpdateTs": lastUpdateTimestamp,
							"status": "w",
							"studentUserId": studentId,
							"teacherId": teacherId
							}
						]

	post_url = 'http://creamsonservices.com:8080/StudentAssignmentServices_base64/AssignStudents'
	payload = json.dumps(assign_student)
	# print(payload)
	headers = {'Content-type':'application/json', 'Accept':'application/json'}
	post_response = requests.post(post_url, data=payload, headers=headers)
	cursor.close()
	return 'success'


def assignmentGroupMapping(teacherId,groupId,assignmentId):

	connection = connect_logindb()
	cursor = connection.cursor()
	# current_date = datetime.now()
	# lastUpdateTimestamp = int(str(int(datetime.timestamp(current_date)))+'000')
	# print(lastUpdateTimestamp)
	aidList = []

	assign_student = {
						"assigngroup": [
										{
										"assignment_id": assignmentId,
										"last_update_id": str(teacherId),
										"group_id": groupId
										}
									]
					}

	post_url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/my_Library/myLibrary/groupAssignmentMapping'
	payload = json.dumps(assign_student)
	# print(payload)
	headers = {'Content-type':'application/json', 'Accept':'application/json'}
	post_response = requests.post(post_url, data=payload, headers=headers)

	cursor.close()
	return 'success'


def createDemoStudents(institutionId, teacherId):

	connection = connect_logindb()
	cursor = connection.cursor()
	post_res_status = 0

	studentList = [193,194,195,1771,3572,4611]
	current_date = date.today()
	userEnrollDate = str(current_date)
	nextyear_date = current_date.replace(year=current_date.year + 1)
	userEndDate = str(nextyear_date)
	lastUpdateTimestamp = int(str(int(time.time()))+'000')
	gidlist = createGroup(institutionId, teacherId)
	aidList = createAssignment(teacherId)
	for sid in studentList:
		cursor.execute("""SELECT `Board`,`CLASS`,`Fathers_Name`,`STUDENT_NAME` FROM `student_dtls` 
			WHERE `INSTITUTION_USER_ID_STUDENT` = %s and `INSTITUTION_ID` = 1""",(sid))

		studentDtls = cursor.fetchone()

		add_user = {"board": studentDtls.get('Board'),
					"clazz": studentDtls.get('CLASS'),
					"fathersName": studentDtls.get('Fathers_Name'),
					"institutionId": institutionId,
					"institutionName": "Elsa Demo Academy",
					"institutionUserId": sid,
					"institutionUserIdStudent": sid,
					"institutionUserIdTeacher": 0,
					"institutionUserRole": "S1",
					"institutionUserStatus": "",
					"lastUpdateId": str(institutionId),
					"lastUpdateTimestamp": lastUpdateTimestamp,
					"studentName": studentDtls.get('STUDENT_NAME'),
					"userEndDate": userEndDate,
					"userEnrollDate": userEnrollDate
				}
		post_url = 'http://creamsonservices.com:8080/NewSignUpService/addStudentDetailsAndInstitutionCreadentialmaster'
		payload = json.dumps(add_user)
		# print(payload)
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		post_response = requests.post(post_url, data=payload, headers=headers)
		post_res_status = post_response.status_code
	cursor.close()
	str_studentList = ['193','194','195','1771','3572','4611']
	if post_res_status == 200:
		for sid in range(0,3):
			addStudentToGroup(studentList[sid],gidlist[0],'WB Class 9',institutionId,teacherId)
		groupId = ','.join(str_studentList[0:3])
		assignStudent(teacherId,groupId,"",'Demo Assignment One',aidList[0])
		assignmentGroupMapping(teacherId,gidlist[0],aidList[0])
		for sid in range(3,6):
			addStudentToGroup(studentList[sid],gidlist[1],'WB Class 10',institutionId,teacherId)
		groupId = ','.join(str_studentList[3:6])
		assignStudent(teacherId,groupId,"",'Demo Assignment Two',aidList[1])
		assignmentGroupMapping(teacherId,gidlist[1],aidList[1])
		return 'success'
	else:
		return 'Try Again'



class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'createDemoOnboardingData':
			institutionId,teacherId = self.request
			createDemoStudents(institutionId,teacherId)
		else:
			pass

@name_space.route("/createDemoOnboardingData/<int:institutionId>/<int:teacherId>")
class createDemoOnboardingData(Resource):
	def get(self,institutionId,teacherId):

		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT `INSTITUTION_ID` FROM `institution_user_credential_master` 
			WHERE `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID` = %s""",(institutionId, teacherId))
		instiDtls = cursor.fetchone()

		if instiDtls:
			# reqRes = createDemoStudents(institutionId,teacherId)
			# if reqRes == 'success':
			sendrReq = (institutionId,teacherId)
			thread_a = Compute(sendrReq,'createDemoOnboardingData')
			thread_a.start()
			res = 'Demo Onboarding Data is being created in background'
			# else:
			# 	res = 'Demo Onboarding Data not being created in background'
		else:
			res = 'Invalid institutionId or TeacherId'

		cursor.close()
		return ({"attributes": {"status_desc": "Demo Onboarding Data Details",
									"status": "success",
										},
					"responseList":res}), status.HTTP_200_OK


# createGroup(6,5376)

# createAssignment()
