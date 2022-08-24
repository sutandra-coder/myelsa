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
app = Flask(__name__)
cors = CORS(app)

'''def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def mysql_connection():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

student_subscription = Blueprint('student_subscription_api', __name__)
api = Api(student_subscription,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('student_subscription',description='Student Subscription')

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'


def sendAddStudentNoification(student_id, teacherList):

	connection = mysql_connection()
	cursor = connection.cursor()

	url = BASE_URL + 'app_notify/AppCommunicationAPI/appMessage'
	headers = {'Content-type':'application/json', 'Accept':'application/json'}

	cursor.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(student_id))
	student = cursor.fetchone()

		
	if student:
		student_name = student['name']
		for tid in teacherList:
			sdata = {'appParams': {},
					'mailParams': {"student":student_name},
					'role': 'T1',
					'toMail': '',
					'toNumber': '',
					'userId': tid,
					'sourceapp': 'StudentAdded'
					}
			requests.post(url, data=json.dumps(sdata), headers=headers).json()
	cursor.close()


class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'studentSubcription':
			student_id = self.request[0]
			teacherList = []
			for tid,teacher in enumerate(self.request[1]):
				teacherList.append(teacher.get('INSTITUTION_USER_ID'))
			sendAddStudentNoification(student_id,teacherList)
		elif self.funcname == 'studentRegisteredNotification':
			student_id = self.request[0]
			teacherList = self.request[1]
			sendAddStudentNoification(student_id,teacherList)
		else:
			pass


@name_space.route("/studentSubcription/<int:otp>/<int:student_id>")
class studentSubcription(Resource):
	def post(self,otp,student_id):

		connection = mysql_connection()
		cursor = connection.cursor()
		productCodes = []
		resp = []
		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential_master` 
			WHERE `INSTITUTION_ID` in (SELECT `INSTITUTION_ID` FROM `institution_user_otp` 
			WHERE `OTP` = %s) and `INSTITUTION_USER_ROLE` = 'TA' and `INSTITUTION_ID` <> 1""",(otp))

		userID = cursor.fetchall()
		if userID:
			teacherID = userID[0].get('INSTITUTION_USER_ID')
			
			cursor.execute("""SELECT `Product_CODE` FROM `user_subscription` WHERE `User_Id` = %s 
				and `Product_CODE` not in('MEI3','MEI6','MEI12')""",(teacherID))


			teacherSubDtls = cursor.fetchall()
			# print(teacherSubDtls)
			
			if teacherSubDtls:
				productCodes = [code.get('Product_CODE') for code in teacherSubDtls]

				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				for code in productCodes:
					subUrl = BASE_URL+'cash_transaction/cashTransactionController/cashTransactionsForProducts/{}/{}'.format(student_id,code)


					subResponse = requests.post(subUrl, headers=headers).json()
					subResponse['responseList']['productCode'] = code 
					resp.append(subResponse.get('responseList'))
			sendReq = (student_id,userID)
			thread_a = Compute(sendReq,'studentSubcription')
			thread_a.start()
		cursor.close()

		return ({"attributes": {"status_desc": "Cash Transaction Details.",
									"status": "success"
									},
					"responseList":resp}), status.HTTP_200_OK


@name_space.route("/studentRegisteredNotification/<int:institution_id>/<int:student_id>")
class studentRegisteredNotification(Resource):
	def post(self,institution_id,student_id):

		connection = mysql_connection()
		cursor = connection.cursor()


		cursor.execute("""SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential_master` 
			WHERE `INSTITUTION_ID` = %s and `INSTITUTION_USER_ROLE` = 'TA'""",(institution_id))

		teacherListDtls = cursor.fetchall()
		teacherList = []
		if teacherListDtls:
			for tid, teach in enumerate(teacherListDtls):
				teacherList.append(teach.get('INSTITUTION_USER_ID'))
			sendReq = (student_id,teacherList)
			thread_a = Compute(sendReq,'studentRegisteredNotification')
			thread_a.start()

		return ({"attributes": {"status_desc": "Student Registered Notification",
								"status": "success"},
				"responseList":'Notification sent to teachers'}), status.HTTP_200_OK



if __name__ == '__main__':
	app.run(host='0.0.0.0')