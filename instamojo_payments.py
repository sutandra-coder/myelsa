import pymysql
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import os
import utils
from instamojoConfig import CLIENT_ID,CLIENT_SECRET,referrer

app = Flask(__name__)
cors = CORS(app)
instamojo_payments = Blueprint('instamojo_payments_api', __name__)
api = Api(instamojo_payments,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('paymentController',description='Instamojo')

# CLIENT_ID = os.getenv('INSTAMOJO_CLIENT_ID')
# CLIENT_SECRET = os.getenv('INSTAMOJO_CLIENT_SECRET')


'''def connect_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


def connect_userLib():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_user_library',
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


def connect_userLib():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

create_payment_link_model = api.model('create_payment_link_model', {
	"amount":fields.Integer(),
	"purpose":fields.String(),
	"buyer_name":fields.String(),
	"email":fields.String(),
	"phone":fields.String(),
	"user_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"transaction_id":fields.Integer()
	})


signup_model = api.model('signup_model', {
	"email":fields.String(),
	"password":fields.String(),
	"phone":fields.String(),
	"userId":fields.Integer(),
	"institutionId":fields.Integer(),
	})

update_bank_dtls_model = api.model('update_bank_dtls_model', {
	"account_holder_name":fields.String(),
	"account_number":fields.String(),
	"ifsc_code":fields.String(),
	"user_id":fields.Integer()
	})

ask_for_fees_model = api.model('ask_for_fees_model', {
	"amount":fields.Integer(),
	"purpose":fields.String(),
	"teacher_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"student_id":fields.List(fields.Integer()),
	"group_id":fields.List(fields.Integer()),
	"is_group":fields.Integer(required=True),
	})

settlement_model = api.model('settlement_model', {
	"payment_id":fields.String(),
	"request_id":fields.Integer(),
	"user_id":fields.Integer(),
	"settlement_type":fields.String(),
	"amount":fields.String(),
	"institution_id":fields.Integer()
	})

MOJO_TEST_URL = 'https://test.instamojo.com/'

MOJO_BASE_URL = 'https://api.instamojo.com/'

BASE_URL = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"

@name_space.route("/createPaymentRequest")
class createPaymentRequest(Resource):
	@api.expect(create_payment_link_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		payload = {"grant_type": "client_credentials",
					"client_id": CLIENT_ID,
					"client_secret": CLIENT_SECRET}

		authResponse = requests.post(MOJO_BASE_URL+"oauth2/token/",
			data=payload).json()

		accesstoken = authResponse.get('access_token')

		headers = {"Authorization": "Bearer "+accesstoken}

		details = request.get_json()

		details['redirect_url'] = 'http://creamsonservices.com/instamojo2.php'
		details['allow_repeated_payments'] = False
		details['send_email'] = False
		details['send_sms'] = True
		userId = details.get('user_id',None)
		details.pop('user_id',None)
		institutionId = details.get('institution_id',None)
		details.pop('institution_id',None)
		transactionId = details.get('transaction_id',None)
		details.pop('transaction_id',None)
		mojoResponse = requests.post(MOJO_BASE_URL+"v2/payment_requests/",
			data=details, headers=headers)

		statusCode = mojoResponse.status_code
		print(statusCode)

		response = mojoResponse.json()
		print(response)

		if statusCode == 201:

			mojoResInsertQuery = ("""INSERT INTO `instamojo_payment_request`(`instamojo_request_id`, 
				`phone`, `email`, `buyer_name`, `amount`, `purpose`, `status`, `send_sms`, 
				`send_email`, `sms_status`, `email_status`, `shorturl`, `longurl`, 
				`redirect_url`, `webhook`, `scheduled_at`, `expires_at`, `allow_repeated_payments`, 
				`mark_fulfilled`, `customer_id`, `created_at`, `modified_at`, `resource_uri`, 
				`remarks`, `user_id`,`institution_id`,`transaction_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
				%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

			created_at = datetime.strptime(response.get('created_at'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
			modified_at = datetime.strptime(response.get('modified_at'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')

			mojoData = (response.get('id'),details.get('phone'),response.get('email'),
				response.get('buyer_name'),response.get('amount'),response.get('purpose'),
				response.get('status'),response.get('send_sms'),response.get('send_email'),
				response.get('sms_status'),response.get('email_status'),response.get('shorturl'),
				response.get('longurl'),response.get('redirect_url'),response.get('webhook'),
				response.get('scheduled_at'),response.get('expires_at'),response.get('allow_repeated_payments'),
				response.get('mark_fulfilled'),response.get('customer_id'),
				created_at,modified_at,response.get('resource_uri'),response.get('remarks'),userId,institutionId,transactionId)
			curlog.execute(mojoResInsertQuery,mojoData)

			requestId = curlog.lastrowid
			response['paymentRequestId'] = requestId

			connection.commit()

			msg = 'Payment Link Created'
		else:
			response = {}
			msg = 'No matching credentials'
		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo payment request Details",
								"status": "success",
								"msg":msg},
				"responseList": response}), status.HTTP_200_OK


@name_space.route("/createSubAccounts")
class createSubAccounts(Resource):
	@api.expect(signup_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()

		# referrer = 'sanjoy'
		details['referrer'] = referrer

		payload = {"grant_type": "client_credentials",
					"client_id": CLIENT_ID,
					"client_secret": CLIENT_SECRET}

		authResponse = requests.post(MOJO_BASE_URL+"oauth2/token/",
			data=payload).json()

		accesstoken = authResponse.get('access_token')
		headers = {"Authorization": "Bearer "+accesstoken}

		mojoResponse = requests.post(MOJO_BASE_URL+"v2/users/",
			data=details, headers=headers)

		statusCode = mojoResponse.status_code
		# print(statusCode)

		response = mojoResponse.json()
		# print(response)

		if statusCode == 201:
			mojoId = response.get('id')
			resource_uri = response.get('resource_uri')
			username = response.get('username')
			curtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			mojoInsertQuery = ("""INSERT INTO `instamojo_user_dtls`(`user_id`, `instamojo_id`, `mail_id`, 
				`username`, `password`, `phoneno`, `resource_uri`, 
				`date_joined`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")

			userMojoDtls = (details.get('userId'),mojoId,details.get('email'),username,
				details.get('password'),details.get('phone'),resource_uri,curtime)
			curlog.execute(mojoInsertQuery,userMojoDtls)
			connection.commit()

			msg = 'Account Created'
			error = {}
		else:
			msg = 'Unable to create Account'
			error = response
			response = {}

		connection.commit()
		curlog.close()

		return ({"attributes": {"status_desc": "Instamojo payment request Details",
								"status": "success",
								"msg":msg,
								"error":error},
				"responseList": response}), status.HTTP_200_OK


@name_space.route("/updateBankDetails")
class updateBankDetails(Resource):
	@api.expect(update_bank_dtls_model)
	def put(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()

		curlog.execute("""SELECT `instamojo_id`,`username`,`password` FROM `instamojo_user_dtls` 
			WHERE `user_id` = %s""",(details.get('user_id')))

		userDtls = curlog.fetchone()

		if userDtls:
			username = userDtls.get('username')
			password = userDtls.get('password')
			mojoId = userDtls.get('instamojo_id')
			payload = {"grant_type": "password",
						"client_id": CLIENT_ID,
						"client_secret": CLIENT_SECRET,
						'username': username,
						'password': password}

			authResponse = requests.post(MOJO_BASE_URL+"oauth2/token/",
				data=payload).json()

			accesstoken = authResponse.get('access_token')
			headers = {"Authorization": "Bearer "+accesstoken}

			userId = details.get('user_id',None)
			details.pop('user_id',None)
			mojoResponse = requests.put(MOJO_BASE_URL+"v2/users/{}/inrbankaccount/".format(mojoId),
			data=details, headers=headers)

			statusCode = mojoResponse.status_code
			print(statusCode)

			response = mojoResponse.json()
			print(response)
			if statusCode in (201,200):
				updateBankQuery = ("""UPDATE `instamojo_user_dtls` SET `account_holder_name` = %s,
					`account_number` = %s,`ifsc_code` = %s WHERE `user_id` = %s""")

				bankData = (details.get('account_holder_name'),details.get('account_number'),
					details.get('ifsc_code'),userId)

				curlog.execute(updateBankQuery,bankData)

				connection.commit()

				sendRes = response
				msg = 'Bank Details Updated'
				error = {}
			else:
				msg = 'Unable to Update Bank Details'
				error = response
				sendRes = {}
		else:
			msg = 'Unable to Update Bank Details'
			error = {'user_id':['Account Not Found!']}
			sendRes = {}

		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo Bank Update Details",
							"status": "success",
							"msg":msg,
							"error":error},
			"responseList": sendRes}), status.HTTP_200_OK



@name_space.route("/getInstamojoAccountDetailsByUserId/<int:user_id>")
class getInstamojoAccountDetailsByUserId(Resource):
	def get(self,user_id):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		curlog.execute("""SELECT `instamojo_id`,`mail_id`,`username`,`phoneno`,`date_joined`,
			`account_holder_name`,`account_number`,`ifsc_code` FROM `instamojo_user_dtls` 
			WHERE `user_id` = %s""",(user_id))

		accountDtls = curlog.fetchone()
		account_created = 'n'
		bankDtls = 'n'
		if accountDtls:
			accountDtls['date_joined'] = accountDtls.get('date_joined').isoformat()
			account_created = 'y'
			if accountDtls.get('account_number') != None:
				bankDtls = 'y'
		else:
			accountDtls = {}
		# accountDtls['is_account_created'] = account_created
		# accountDtls['is_bank_details'] = bankDtls


		return ({"attributes": {"status_desc": "Instamojo Account Details",
							"status": "success",
							"is_account":account_created,
							"is_bank_details":bankDtls},
			"responseList": accountDtls}), status.HTTP_200_OK



@name_space.route("/askForFessByTeacher")
class askForFessByTeacher(Resource):
	@api.expect(ask_for_fees_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()


		URL = BASE_URL + "instamojo_payments/paymentController/createPaymentRequest"

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		amount = details.get('amount')
		purpose = details.get('purpose')
		teacher_id = details.get('teacher_id')
		institution_id = details.get('institution_id')
		student_id = details.get('student_id')
		group_id = details.get('group_id')
		is_group = details.get('is_group')
		studentList = []

		initiatePaymentQuery = ("""INSERT INTO `instamojo_initiate_payment`(`user_id`, 
			`institution_id`,`initiated_for`) VALUES (%s,%s,%s)""")
		if is_group == 0:
			initiated_for = 'I'
		elif is_group == 1:
			initiated_for = 'G'
		initiateData = (teacher_id,institution_id,initiated_for)

		curlog.execute(initiatePaymentQuery,initiateData)

		transaction_id = curlog.lastrowid

		if is_group:
			studentList = utils.getStudentListFromGroupid(group_id)
			groupMapInsertQuery = ("""INSERT INTO `instamojo_payment_batch_mapping`(`transaction_id`, 
				`group_id`, `teacher_id`) VALUES (%s,%s,%s)""")
			for gid in group_id:
				groupData = (transaction_id,gid,teacher_id)
				curlog.execute(groupMapInsertQuery,groupData)
		else:
			studentList = student_id
			
		for sid in studentList:
			curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name,`PRIMARY_CONTACT_NUMBER` as phone 
				FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(sid))

			student = curlog.fetchone()

			if student:
				student_name = student['name']
				student_phone = student['phone']

				payload = {"amount":amount,
							"purpose":purpose,
							"buyer_name":student_name,
							"phone":student_phone,
							"user_id":teacher_id,
							"institution_id":institution_id,
							"transaction_id":transaction_id}

				mojoResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()

				print(mojoResponse)
				if mojoResponse.get('attributes').get('msg') == 'Payment Link Created':

					paymentStudentMapQuery = ("""INSERT INTO `instamojo_payment_student_mapping`(
						`request_id`, `student_id`, `status`) VALUES (%s,%s,%s)""")
					responseList = mojoResponse.get('responseList')
					mapData = (responseList.get('paymentRequestId'),sid,responseList.get('status'))

					curlog.execute(paymentStudentMapQuery,mapData)

		transRes = {"transaction_id":transaction_id,
					"initiated_for":initiated_for}
		connection.commit()
		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo Payment Initiation Details",
							"status": "success"},
			"responseList": transRes}), status.HTTP_200_OK


@name_space.route("/updatePaymentDetails/<string:payment_id>/<string:payment_status>/<string:payment_request_id>")
class updatePaymentDetails(Resource):
	def put(self,payment_id,payment_status,payment_request_id):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		conn = connect_userLib()
		curlab = conn.cursor()

		details = request.get_json()

		settlementURL = BASE_URL + "instamojo_payments/paymentController/createSettlementByPaymentId"

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		
		update_status = 'Complete'
		
		updatePaymentQuery = ("""UPDATE `instamojo_payment_request` SET  
			`payment_status` = %s,`payment_id`= %s, `status` = %s WHERE `instamojo_request_id`= %s""")

		paymentData = (payment_status,payment_id,update_status,payment_request_id)

		curlog.execute(updatePaymentQuery,paymentData)

		curlog.execute("""SELECT `request_id`,`user_id`,`institution_id`,`amount`,`purpose` FROM `instamojo_payment_request` 
			WHERE `instamojo_request_id` = %s""",(payment_request_id))

		reqDtls = curlog.fetchone()

		reqId = reqDtls.get('request_id')	
		userId = reqDtls.get('user_id')
		amount = reqDtls.get('amount')	
		purpose = reqDtls.get('purpose')
		institutionId = reqDtls.get('institution_id')

		updateStudentStatus = ("""UPDATE `instamojo_payment_student_mapping` SET `status` = %s 
			where `request_id` = %s""")

		curlog.execute(updateStudentStatus,(update_status,reqId))


		if payment_status == 'Credit':
			payload = {"payment_id":payment_id,
						"request_id":reqId,
						"user_id":userId,
						"settlement_type":'CREDIT',
						"amount":amount}

			settleRes = requests.post(settlementURL,data=json.dumps(payload), headers=headers).json()
			print(settleRes)

			if purpose.startswith('Course-'):
				updateStudentCourse = ("""UPDATE `student_coursefee_payment_details` SET `is_pending` = 'n',
					paid_on = %s WHERE `transaction_id` = %s""")
				paid_on = datetime.now().strftime('%Y-%m-%d')
				curlab.execute(updateStudentCourse,(paid_on,payment_request_id))

				curlab.execute("""SELECT scpd.`coursefee_id`,scpd.`student_id`,`course_id` FROM `student_coursefee_payment_details` scpd 
					INNER JOIN `student_coursefee_mapping` sm on scpd.`coursefee_id` = sm.`coursefee_id`
					WHERE `transaction_id` = %s""",(payment_request_id))

				courseDtls = curlab.fetchone()
				student_id = courseDtls.get('student_id')
				coursefee_id = courseDtls.get('coursefee_id')
				course_id = courseDtls.get('course_id')
				studentcourseMap = ("""INSERT INTO `student_course_master`(`student_id`, `course_id`, 
					`teacher_id`, `coursefee_id`, `Institution_ID`) VALUES (%s,%s,%s,%s,%s)""")

				curlab.execute(studentcourseMap,(student_id,course_id,userId,coursefee_id,institutionId))

		else:
			if purpose.startswith('Course-'):
				updateStudentCourse = ("""UPDATE `student_coursefee_payment_details` SET `is_pending` = 'f',
					paid_on = %s WHERE `transaction_id` = %s""")
				paid_on = datetime.now().strftime('%Y-%m-%d')
				curlab.execute(updateStudentCourse,(paid_on,payment_request_id))
		
		connection.commit()
		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo Payment Details",
							"status": "success"},
			"responseList": 'Payment Details Updated'}), status.HTTP_200_OK

@name_space.route("/getInstamojoTransactionDetailsByTeacherId/<int:teacher_id>")
class getInstamojoTransactionDetailsByTeacherId(Resource):
	def get(self,teacher_id):

		connection = connect_logindb()
		curlog = connection.cursor()
		pendingAmount = 0
		settledAmount = 0
		totalAmount = 0

		curlog.execute("""SELECT sum(`amount`) as 'pendingAmount' FROM `instamojo_payment_request` WHERE 
			`payment_status` is Null and `user_id` = %s""",(teacher_id))

		pendingDtls = curlog.fetchone()
		if pendingDtls:
			pendingAmount = pendingDtls.get('pendingAmount')
		else:
			pendingAmount = 0

		curlog.execute("""SELECT sum(`amount`) as 'settledAmount' FROM `instamojo_settlement_details` 
			WHERE `user_id` = %s""",(teacher_id))
		settleDtls = curlog.fetchone()
		if settleDtls.get('settledAmount'):
			settledAmount = settleDtls.get('settledAmount',0)
		else:
			settledAmount = 0
			
		totalAmount = pendingAmount + settledAmount
		curlog.execute("""SELECT ipr.`request_id`,`student_id`,`buyer_name`,`phone`,`email`,
			`purpose`,`amount`,`payment_status`,ipr.`status`,`payment_id`,`longurl` as 'paymentLink',
			`created_at` FROM `instamojo_payment_request` ipr INNER JOIN 
			instamojo_payment_student_mapping ipsm on ipr.`request_id` = ipsm.`request_id` 
			WHERE `user_id` = %s""",(teacher_id))

		transactionDtls = curlog.fetchall()

		for tid, tran in enumerate(transactionDtls):
			tran['created_at'] = tran.get('created_at').isoformat()
		return ({"attributes": {"status_desc": "Instamojo Transaction Details",
							"status": "success",
							"pendingAmount":pendingAmount,
							"settledAmount":settledAmount,
							"totalAmount":totalAmount},
			"responseList": transactionDtls}), status.HTTP_200_OK


@name_space.route("/getInstamojoTransactionDetailsByStudentIdAndStatus/<int:student_id>/<string:payment_status>")
class getInstamojoTransactionDetailsByStudentIdAndStatus(Resource):
	def get(self,student_id,payment_status):

		connection = connect_logindb()
		curlog = connection.cursor()

		if payment_status.lower() == 'pending':
			curlog.execute("""SELECT ipsm.`request_id`,`phone`,`email`,`buyer_name`,`amount`,`purpose`,
				`payment_status`,`payment_id`,ipr.`status`,`longurl` as 'paymentLink',`created_at`,`user_id` as 'teacher_id' FROM 
				`instamojo_payment_student_mapping` ipsm INNER JOIN `instamojo_payment_request` ipr 
				ON ipsm.`request_id` = ipr.`request_id` WHERE `student_id` = %s 
				AND ipsm.`status` = %s""",(student_id,payment_status))


			transactionDtls = curlog.fetchall()
			if transactionDtls:
				for tid, tran in enumerate(transactionDtls):
					tran['created_at'] = tran.get('created_at').isoformat()

					curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name,`PRIMARY_CONTACT_NUMBER` as phone 
						FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(tran.get('teacher_id')))
					teacherDtls = curlog.fetchone()
					teachername = teacherDtls.get('name')
					teacher_num = teacherDtls.get('phone')

					tran['teacherName'] = teachername
					tran['teacherPhoneNo'] = teacher_num


		elif payment_status.lower() == 'complete':

			curlog.execute("""SELECT ipsm.`request_id`,`phone`,`email`,`buyer_name`,`amount`,`purpose`,
				`payment_status`,`payment_id`,ipr.`status`,`longurl` as 'paymentLink',`created_at`,`user_id` as 'teacher_id' FROM 
				`instamojo_payment_student_mapping` ipsm INNER JOIN `instamojo_payment_request` ipr 
				ON ipsm.`request_id` = ipr.`request_id` WHERE `student_id` = %s 
				AND ipsm.`status` = %s""",(student_id,payment_status))


			transactionDtls = curlog.fetchall()
			if transactionDtls:
				for tid, tran in enumerate(transactionDtls):
					tran['created_at'] = tran.get('created_at').isoformat()

					curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name,`PRIMARY_CONTACT_NUMBER` as phone 
						FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(tran.get('teacher_id')))
					teacherDtls = curlog.fetchone()
					teachername = teacherDtls.get('name')
					teacher_num = teacherDtls.get('phone')

					tran['teacherName'] = teachername
					tran['teacherPhoneNo'] = teacher_num
		else:
			transactionDtls = 'Payment Status should be pending or complete'
		
		return ({"attributes": {"status_desc": "Instamojo Transaction Details",
							"status": "success"},
			"responseList": transactionDtls}), status.HTTP_200_OK

@name_space.route("/createSettlementByPaymentId")
class createSettlementByPaymentId(Resource):
	@api.expect(settlement_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()


		payload = {"grant_type": "client_credentials",
					"client_id": CLIENT_ID,
					"client_secret": CLIENT_SECRET}

		authResponse = requests.post(MOJO_BASE_URL+"oauth2/token/",
			data=payload).json()

		accesstoken = authResponse.get('access_token')

		headers = {"Authorization": "Bearer "+accesstoken}

		details = request.get_json()

		payment_id = details.get('payment_id')
		request_id = details.get('request_id')
		user_id = details.get('user_id')
		settlement_type = details.get('settlement_type')
		amount = details.get('amount')

		curlog.execute("""SELECT `instamojo_id`,`username`,`password` FROM `instamojo_user_dtls` 
			WHERE `user_id` = %s""",(user_id))
		
		mojoUserDtls = curlog.fetchone()
		mojoID = mojoUserDtls.get('instamojo_id')
		username = mojoUserDtls.get('username')
		password = mojoUserDtls.get('password')

		settleInsertQuery = ("""INSERT INTO `instamojo_settlement_details`(`request_id`, 
			`payment_id`, `settlement_type`, `user_id`, `amount`) VALUES (%s,%s,%s,%s,%s)""")

		settleData = (request_id,payment_id,'CREDIT',user_id,amount)

		curlog.execute(settleInsertQuery,settleData)

		settlementId = curlog.lastrowid

		payload = {"settlement_id":str(settlementId),
				  "submerchant":mojoID,
				  "amount":amount,
				  "type":settlement_type}
		
		mojoResponse = requests.post(MOJO_BASE_URL+"v2/payments/{}/settlements/".format(payment_id),
			data=payload, headers=headers)

		statusCode = mojoResponse.status_code
		print(statusCode)

		response = mojoResponse.json()
		print(response)

		if statusCode == 201:

			updateSettlementQuery = ("""UPDATE `instamojo_settlement_details` SET `created_at` = %s,
				`message` = %s WHERE `settlement_id` = %s""")
			created_at = datetime.strptime(response.get('created'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
			updateData = (created_at,response.get('message'),settlementId)

			curlog.execute(updateSettlementQuery,updateData)
		else:
			updateSettlementQuery = ("""UPDATE `instamojo_settlement_details` SET `created_at` = %s,
				`message` = %s WHERE `settlement_id` = %s""")
			created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			updateData = (created_at,response.get('message'),settlementId)

			curlog.execute(updateSettlementQuery,updateData)

		# mojoResponse = requests.get(MOJO_BASE_URL+"v2/payments/{}/settlements/".format(payment_id),
		# 	headers=headers)

		# statusCode = mojoResponse.status_code
		# print(statusCode)

		# response = mojoResponse.json()
		# print(response)

		return ({"attributes": {"status_desc": "Instamojo Settlement Details",
							"status": "success"},
			"responseList": response}), status.HTTP_200_OK


@name_space.route("/getInstamojoAccountDetailsByUserId/v2/<int:user_id>/<int:institution_id>")
class getInstamojoAccountDetailsByUserIdV2(Resource):
	def get(self,user_id,institution_id):
		
		connection = connect_logindb()
		curlog = connection.cursor()
		accountDtls = {}
		account_created = 'n'
		bankDtls = 'n'
		merchantDtls = {}
		curlog.execute("""SELECT `client_id`,`client_secret`,`referrer` FROM 
			`instamojo_merchant_accounts` WHERE `Institution_Id` = %s""",(institution_id))
		merchantDtls = curlog.fetchone()

		if merchantDtls:
			account_created = 'y'
			bankDtls = 'y'
		else:
			curlog.execute("""SELECT `instamojo_id`,`mail_id`,`username`,`phoneno`,`date_joined`,
				`account_holder_name`,`account_number`,`ifsc_code` FROM `instamojo_user_dtls` 
				WHERE `user_id` = %s and institution_id = %s""",(user_id,institution_id))

			accountDtls = curlog.fetchone()
			account_created = 'n'
			bankDtls = 'n'
			if accountDtls:
				accountDtls['date_joined'] = accountDtls.get('date_joined').isoformat()
				account_created = 'y'
				if accountDtls.get('account_number') != None:
					bankDtls = 'y'
			else:
				accountDtls = {}

		return ({"attributes": {"status_desc": "Instamojo Account Details",
							"status": "success",
							"is_account":account_created,
							"is_bank_details":bankDtls},
			"responseList": accountDtls}), status.HTTP_200_OK



@name_space.route("/createPaymentRequestV2")
class createPaymentRequestV2(Resource):
	@api.expect(create_payment_link_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()

		# client_id = CLIENT_ID
		# client_secret = CLIENT_SECRET
		# referrer_id = referrer

		curlog.execute("""SELECT `client_id`,`client_secret`,`referrer` FROM 
			`instamojo_merchant_accounts` WHERE `Institution_Id` = 1""")
		defaultMerchantDtls = curlog.fetchone()
		
		client_id = defaultMerchantDtls.get('client_id')
		client_secret = defaultMerchantDtls.get('client_secret')
		referrer_id = defaultMerchantDtls.get('referrer')

		curlog.execute("""SELECT `client_id`,`client_secret`,`referrer` FROM 
			`instamojo_merchant_accounts` WHERE `Institution_Id` = %s""",(details.get('institution_id')))
		merchantDtls = curlog.fetchone()
		if merchantDtls:
			client_id = merchantDtls.get('client_id')
			client_secret = merchantDtls.get('client_secret')
			referrer_id = merchantDtls.get('referrer')

		payload = {"grant_type": "client_credentials",
					"client_id": client_id,
					"client_secret": client_secret}
		print(payload)

		authResponse = requests.post(MOJO_BASE_URL+"oauth2/token/",
			data=payload).json()

		print(authResponse)

		accesstoken = authResponse.get('access_token')

		headers = {"Authorization": "Bearer "+accesstoken}

		details['redirect_url'] = 'http://visuable.in/instamojo_test.php'
		details['allow_repeated_payments'] = False
		details['send_email'] = False
		details['send_sms'] = True
		userId = details.get('user_id',None)
		details.pop('user_id',None)
		institutionId = details.get('institution_id',None)
		details.pop('institution_id',None)
		transactionId = details.get('transaction_id',None)
		details.pop('transaction_id',None)
		mojoResponse = requests.post(MOJO_BASE_URL+"v2/payment_requests/",
			data=details, headers=headers)

		statusCode = mojoResponse.status_code
		print(statusCode)

		response = mojoResponse.json()
		print(response)

		if statusCode == 201:

			mojoResInsertQuery = ("""INSERT INTO `instamojo_payment_request`(`instamojo_request_id`, 
				`phone`, `email`, `buyer_name`, `amount`, `purpose`, `status`, `send_sms`, 
				`send_email`, `sms_status`, `email_status`, `shorturl`, `longurl`, 
				`redirect_url`, `webhook`, `scheduled_at`, `expires_at`, `allow_repeated_payments`, 
				`mark_fulfilled`, `customer_id`, `created_at`, `modified_at`, `resource_uri`, 
				`remarks`, `user_id`,`institution_id`,`transaction_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
				%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

			created_at = datetime.strptime(response.get('created_at'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
			modified_at = datetime.strptime(response.get('modified_at'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')

			mojoData = (response.get('id'),details.get('phone'),response.get('email'),
				response.get('buyer_name'),response.get('amount'),response.get('purpose'),
				response.get('status'),response.get('send_sms'),response.get('send_email'),
				response.get('sms_status'),response.get('email_status'),response.get('shorturl'),
				response.get('longurl'),response.get('redirect_url'),response.get('webhook'),
				response.get('scheduled_at'),response.get('expires_at'),response.get('allow_repeated_payments'),
				response.get('mark_fulfilled'),response.get('customer_id'),
				created_at,modified_at,response.get('resource_uri'),response.get('remarks'),userId,institutionId,transactionId)
			curlog.execute(mojoResInsertQuery,mojoData)

			requestId = curlog.lastrowid
			response['paymentRequestId'] = requestId

			connection.commit()

			msg = 'Payment Link Created'
		else:
			response = {}
			msg = 'No matching credentials'
		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo payment request Details",
								"status": "success",
								"msg":msg},
				"responseList": response}), status.HTTP_200_OK


@name_space.route("/askForFessByTeacherV2")
class askForFessByTeacherV2(Resource):
	@api.expect(ask_for_fees_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()


		# URL = BASE_URL + "instamojo_payments/paymentController/createPaymentRequest"
		URL = BASE_URL + "instamojo_payments/paymentController/createPaymentRequestV2"

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		amount = details.get('amount')
		purpose = details.get('purpose')
		teacher_id = details.get('teacher_id')
		institution_id = details.get('institution_id')
		student_id = details.get('student_id')
		group_id = details.get('group_id')
		is_group = details.get('is_group')
		studentList = []

		initiatePaymentQuery = ("""INSERT INTO `instamojo_initiate_payment`(`user_id`, 
			`institution_id`,`initiated_for`) VALUES (%s,%s,%s)""")
		if is_group == 0:
			initiated_for = 'I'
		elif is_group == 1:
			initiated_for = 'G'
		initiateData = (teacher_id,institution_id,initiated_for)

		curlog.execute(initiatePaymentQuery,initiateData)

		transaction_id = curlog.lastrowid

		if is_group:
			studentList = utils.getStudentListFromGroupid(group_id)
			groupMapInsertQuery = ("""INSERT INTO `instamojo_payment_batch_mapping`(`transaction_id`, 
				`group_id`, `teacher_id`) VALUES (%s,%s,%s)""")
			for gid in group_id:
				groupData = (transaction_id,gid,teacher_id)
				curlog.execute(groupMapInsertQuery,groupData)
		else:
			studentList = student_id
			
		for sid in studentList:
			curlog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name,`PRIMARY_CONTACT_NUMBER` as phone 
				FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(sid))

			student = curlog.fetchone()

			if student:
				student_name = student['name']
				student_phone = student['phone']

				payload = {"amount":amount,
							"purpose":purpose,
							"buyer_name":student_name,
							"phone":student_phone,
							"user_id":teacher_id,
							"institution_id":institution_id,
							"transaction_id":transaction_id}

				mojoResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()

				print(mojoResponse)
				if mojoResponse.get('attributes').get('msg') == 'Payment Link Created':

					paymentStudentMapQuery = ("""INSERT INTO `instamojo_payment_student_mapping`(
						`request_id`, `student_id`, `status`) VALUES (%s,%s,%s)""")
					responseList = mojoResponse.get('responseList')
					mapData = (responseList.get('paymentRequestId'),sid,responseList.get('status'))

					curlog.execute(paymentStudentMapQuery,mapData)

		transRes = {"transaction_id":transaction_id,
					"initiated_for":initiated_for}
		connection.commit()
		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo Payment Initiation Details",
							"status": "success"},
			"responseList": transRes}), status.HTTP_200_OK


@name_space.route("/createSubAccountsV2")
class createSubAccountsV2(Resource):
	@api.expect(signup_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()
		# referrer = 'sanjoy'

		curlog.execute("""SELECT `client_id`,`client_secret`,`referrer` FROM 
			`instamojo_merchant_accounts` WHERE `Institution_Id` = 1""")
		defaultMerchantDtls = curlog.fetchone()

		client_id = defaultMerchantDtls.get('client_id')
		client_secret = defaultMerchantDtls.get('client_secret')
		referrer_id = defaultMerchantDtls.get('referrer')

		if not details.get('institutionId'):

			curlog.execute("""SELECT icm.`INSTITUTION_ID` FROM `institution_user_credential_master` icm
				WHERE icm.`INSTITUTION_USER_ID` = %s""",(details.get('userId')))

			instiDtls = curlog.fetchone()

			institutionId = instiDtls.get('INSTITUTION_ID')
		else:
			institutionId = details.get('institutionId')

		curlog.execute("""SELECT `client_id`,`client_secret`,`referrer` FROM 
			`instamojo_merchant_accounts` WHERE `Institution_Id` = %s""",(institutionId))
		
		merchantDtls = curlog.fetchone()
		
		if merchantDtls:
			client_id = merchantDtls.get('client_id')
			client_secret = merchantDtls.get('client_secret')
			referrer_id = merchantDtls.get('referrer')

		details['referrer'] = referrer_id

		payload = {"grant_type": "client_credentials",
					"client_id": client_id,
					"client_secret": client_secret}

		print(payload)

		authResponse = requests.post(MOJO_TEST_URL+"oauth2/token/",
			data=payload).json()

		accesstoken = authResponse.get('access_token')
		headers = {"Authorization": "Bearer "+accesstoken}

		mojoResponse = requests.post(MOJO_TEST_URL+"v2/users/",
			data=details, headers=headers)

		statusCode = mojoResponse.status_code
		print(statusCode)

		response = mojoResponse.json()
		print(response)

		if statusCode == 201:
			mojoId = response.get('id')
			resource_uri = response.get('resource_uri')
			username = response.get('username')
			curtime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			mojoInsertQuery = ("""INSERT INTO `instamojo_user_dtls`(`user_id`, `instamojo_id`, `mail_id`, 
				`username`, `password`, `phoneno`, `resource_uri`, 
				`date_joined`,`institution_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

			userMojoDtls = (details.get('userId'),mojoId,details.get('email'),username,
				details.get('password'),details.get('phone'),resource_uri,curtime,institutionId)
			curlog.execute(mojoInsertQuery,userMojoDtls)
			connection.commit()

			msg = 'Account Created'
			error = {}
		else:
			msg = 'Unable to create Account'
			error = response
			response = {}

		connection.commit()
		curlog.close()

		return ({"attributes": {"status_desc": "Instamojo payment request Details",
								"status": "success",
								"msg":msg,
								"error":error},
				"responseList": response}), status.HTTP_200_OK


@name_space.route("/updateBankDetailsV2")
class updateBankDetailsV2(Resource):
	@api.expect(update_bank_dtls_model)
	def put(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()

		curlog.execute("""SELECT `client_id`,`client_secret`,`referrer` FROM 
			`instamojo_merchant_accounts` WHERE `Institution_Id` = 1""")
		defaultMerchantDtls = curlog.fetchone()

		client_id = defaultMerchantDtls.get('client_id')
		client_secret = defaultMerchantDtls.get('client_secret')
		referrer_id = defaultMerchantDtls.get('referrer')

		curlog.execute("""SELECT `institution_id`,`instamojo_id`,`username`,`password` FROM `instamojo_user_dtls` 
			WHERE `user_id` = %s""",(details.get('user_id')))

		userDtls = curlog.fetchone()

		if userDtls:
			print(userDtls.get('institution_id'))
			curlog.execute("""SELECT `client_id`,`client_secret`,`referrer` FROM 
			`instamojo_merchant_accounts` WHERE `Institution_Id` = %s""",(userDtls.get('institution_id')))
		
			merchantDtls = curlog.fetchone()
			
			if merchantDtls:
				client_id = merchantDtls.get('client_id')
				client_secret = merchantDtls.get('client_secret')
				referrer_id = merchantDtls.get('referrer')
			username = userDtls.get('username')
			password = userDtls.get('password')
			mojoId = userDtls.get('instamojo_id')
			payload = {"grant_type": "password",
						"client_id": client_id,
						"client_secret": client_secret,
						'username': username,
						'password': password}

			authResponse = requests.post(MOJO_TEST_URL+"oauth2/token/",
				data=payload).json()

			accesstoken = authResponse.get('access_token')
			headers = {"Authorization": "Bearer "+accesstoken}

			userId = details.get('user_id',None)
			details.pop('user_id',None)
			mojoResponse = requests.put(MOJO_TEST_URL+"v2/users/{}/inrbankaccount/".format(mojoId),
			data=details, headers=headers)

			statusCode = mojoResponse.status_code
			print(statusCode)

			response = mojoResponse.json()
			print(response)
			if statusCode in (201,200):
				updateBankQuery = ("""UPDATE `instamojo_user_dtls` SET `account_holder_name` = %s,
					`account_number` = %s,`ifsc_code` = %s WHERE `user_id` = %s""")

				bankData = (details.get('account_holder_name'),details.get('account_number'),
					details.get('ifsc_code'),userId)

				curlog.execute(updateBankQuery,bankData)

				connection.commit()

				sendRes = response
				msg = 'Bank Details Updated'
				error = {}
			else:
				msg = 'Unable to Update Bank Details'
				error = response
				sendRes = {}
		else:
			msg = 'Unable to Update Bank Details'
			error = {'user_id':['Account Not Found!']}
			sendRes = {}

		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo Bank Update Details",
							"status": "success",
							"msg":msg,
							"error":error},
			"responseList": sendRes}), status.HTTP_200_OK



@name_space.route("/updatePaymentDetails/v2/<string:payment_id>/<string:payment_status>/<string:payment_request_id>")
class updatePaymentDetailsV2(Resource):
	def put(self,payment_id,payment_status,payment_request_id):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		conn = connect_userLib()
		curlab = conn.cursor()

		details = request.get_json()

		settlementURL = BASE_URL + "instamojo_payments/paymentController/createSettlementByPaymentIdV2"

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		update_status = 'Complete'
		
		updatePaymentQuery = ("""UPDATE `instamojo_payment_request` SET  
			`payment_status` = %s,`payment_id`= %s, `status` = %s WHERE `instamojo_request_id`= %s""")

		paymentData = (payment_status,payment_id,update_status,payment_request_id)

		curlog.execute(updatePaymentQuery,paymentData)

		curlog.execute("""SELECT `request_id`,`user_id`,`institution_id`,`amount`,`purpose` FROM `instamojo_payment_request` 
			WHERE `instamojo_request_id` = %s""",(payment_request_id))

		reqDtls = curlog.fetchone()

		reqId = reqDtls.get('request_id')	
		userId = reqDtls.get('user_id')
		amount = reqDtls.get('amount')	
		purpose = reqDtls.get('purpose')
		institutionId = reqDtls.get('institution_id')

		updateStudentStatus = ("""UPDATE `instamojo_payment_student_mapping` SET `status` = %s 
			where `request_id` = %s""")

		curlog.execute(updateStudentStatus,(update_status,reqId))

		if payment_status == 'Credit':
			payload = {"payment_id":payment_id,
						"request_id":reqId,
						"user_id":userId,
						"settlement_type":'CREDIT',
						"amount":amount,
						"institution_id":institutionId}

			settleRes = requests.post(settlementURL,data=json.dumps(payload), headers=headers).json()
			print(settleRes)

			if purpose.startswith('Course-'):
				updateStudentCourse = ("""UPDATE `student_coursefee_payment_details` SET `is_pending` = 'n',
					paid_on = %s WHERE `transaction_id` = %s""")
				paid_on = datetime.now().strftime('%Y-%m-%d')
				curlab.execute(updateStudentCourse,(paid_on,payment_request_id))

				curlab.execute("""SELECT scpd.`coursefee_id`,scpd.`student_id`,`course_id` FROM `student_coursefee_payment_details` scpd 
					INNER JOIN `student_coursefee_mapping` sm on scpd.`coursefee_id` = sm.`coursefee_id`
					WHERE `transaction_id` = %s""",(payment_request_id))

				courseDtls = curlab.fetchone()
				student_id = courseDtls.get('student_id')
				coursefee_id = courseDtls.get('coursefee_id')
				course_id = courseDtls.get('course_id')
				studentcourseMap = ("""INSERT INTO `student_course_master`(`student_id`, `course_id`, 
					`teacher_id`, `coursefee_id`, `Institution_ID`) VALUES (%s,%s,%s,%s,%s)""")

				curlab.execute(studentcourseMap,(student_id,course_id,userId,coursefee_id,institutionId))

			elif purpose.startswith('ComboCourse-'):
				updateStudentCourse = ("""UPDATE `student_coursefee_payment_details` SET `is_pending` = 'n',
					paid_on = %s WHERE `transaction_id` = %s""")
				paid_on = datetime.now().strftime('%Y-%m-%d')
				curlab.execute(updateStudentCourse,(paid_on,payment_request_id))

				curlab.execute("""SELECT scpd.`coursefee_id`,scpd.`student_id`,`combo_id` FROM `student_coursefee_payment_details` scpd 
					INNER JOIN `student_coursefee_mapping` sm on scpd.`coursefee_id` = sm.`coursefee_id`
					WHERE `transaction_id` = %s""",(payment_request_id))

				courseDtls = curlab.fetchone()
				student_id = courseDtls.get('student_id')
				coursefee_id = courseDtls.get('coursefee_id')

				curlab.execute("""SELECT `course_id` FROM `student_combo_mapping` WHERE 
					`coursefee_id` = %s and `student_id` = %s""",(coursefee_id,student_id))

				courseIdList = curlab.fetchall()
				studentcourseMap = ("""INSERT INTO `student_course_master`(`student_id`, `course_id`, 
						`teacher_id`, `coursefee_id`, `Institution_ID`) VALUES (%s,%s,%s,%s,%s)""")
				for cid, course in enumerate(courseIdList):
					course_id = course.get('course_id')
					curlab.execute(studentcourseMap,(student_id,course_id,userId,coursefee_id,institutionId))
		else:
			if purpose.startswith('Course-') or purpose.startswith('ComboCourse-'):
				updateStudentCourse = ("""UPDATE `student_coursefee_payment_details` SET `is_pending` = 'f',
					paid_on = %s WHERE `transaction_id` = %s""")
				paid_on = datetime.now().strftime('%Y-%m-%d')
				curlab.execute(updateStudentCourse,(paid_on,payment_request_id))
		
		connection.commit()
		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo Payment Details",
							"status": "success"},
			"responseList": 'Payment Details Updated'}), status.HTTP_200_OK

@name_space.route("/createSettlementByPaymentIdV2")
class createSettlementByPaymentIdV2(Resource):
	@api.expect(settlement_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()
		response = {}
		curlog.execute("""SELECT `client_id`,`client_secret`,`referrer` FROM 
			`instamojo_merchant_accounts` WHERE `Institution_Id` = 1""")
		defaultMerchantDtls = curlog.fetchone()

		client_id = defaultMerchantDtls.get('client_id')
		client_secret = defaultMerchantDtls.get('client_secret')
		referrer_id = defaultMerchantDtls.get('referrer')

		details = request.get_json()

		payment_id = details.get('payment_id')
		request_id = details.get('request_id')
		user_id = details.get('user_id')
		settlement_type = details.get('settlement_type')
		amount = details.get('amount')
		institutionId = details.get('institution_id')

		settleInsertQuery = ("""INSERT INTO `instamojo_settlement_details`(`request_id`, 
			`payment_id`, `settlement_type`, `user_id`, `amount`) VALUES (%s,%s,%s,%s,%s)""")

		settleData = (request_id,payment_id,'CREDIT',user_id,amount)

		curlog.execute(settleInsertQuery,settleData)

		settlementId = curlog.lastrowid

		curlog.execute("""SELECT `client_id`,`client_secret`,`referrer` FROM 
			`instamojo_merchant_accounts` WHERE `Institution_Id` = %s""",(institutionId))
		
		merchantDtls = curlog.fetchone()

		updateSettlementQuery = ("""UPDATE `instamojo_settlement_details` SET `created_at` = %s,
			`message` = %s WHERE `settlement_id` = %s""")		
		
		if merchantDtls:
			client_id = merchantDtls.get('client_id')
			client_secret = merchantDtls.get('client_secret')
			referrer_id = merchantDtls.get('referrer')
			created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
			updateData = (created_at,'Settlement created',settlementId)
			curlog.execute(updateSettlementQuery,updateData)
		else:
			payload = {"grant_type": "client_credentials",
						"client_id": client_id,
						"client_secret": client_secret}

			authResponse = requests.post(MOJO_BASE_URL+"oauth2/token/",
				data=payload).json()

			accesstoken = authResponse.get('access_token')

			headers = {"Authorization": "Bearer "+accesstoken}

			curlog.execute("""SELECT `institution_id`,`instamojo_id`,`username`,`password` FROM `instamojo_user_dtls` 
				WHERE `user_id` = %s and `institution_id` = %s""",(user_id,institutionId))
			
			mojoUserDtls = curlog.fetchone()
			if mojoUserDtls:

				mojoID = mojoUserDtls.get('instamojo_id')
				username = mojoUserDtls.get('username')
				password = mojoUserDtls.get('password')

				
				payload = {"settlement_id":str(settlementId),
						  "submerchant":mojoID,
						  "amount":amount,
						  "type":settlement_type}
				
				mojoResponse = requests.post(MOJO_BASE_URL+"v2/payments/{}/settlements/".format(payment_id),
					data=payload, headers=headers)

				statusCode = mojoResponse.status_code
				print(statusCode)

				response = mojoResponse.json()
				print(response)

				if statusCode == 201:

					created_at = datetime.strptime(response.get('created'),'%Y-%m-%dT%H:%M:%S.%fZ').strftime('%Y-%m-%d %H:%M:%S')
					updateData = (created_at,response.get('message'),settlementId)

					curlog.execute(updateSettlementQuery,updateData)
				else:
					
					created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
					updateData = (created_at,response.get('message'),settlementId)
					curlog.execute(updateSettlementQuery,updateData)
			else:
				created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				updateData = (created_at,'Sub account not found',settlementId)
				curlog.execute(updateSettlementQuery,updateData)

		# mojoResponse = requests.get(MOJO_BASE_URL+"v2/payments/{}/settlements/".format(payment_id),
		# 	headers=headers)

		# statusCode = mojoResponse.status_code
		# print(statusCode)

		# response = mojoResponse.json()
		# print(response)


		return ({"attributes": {"status_desc": "Instamojo Settlement Details",
							"status": "success"},
			"responseList": response}), status.HTTP_200_OK


@name_space.route("/skywalkupdatePaymentDetails/v2/<string:payment_id>/<string:payment_status>/<string:payment_request_id>")
class skywalkupdatePaymentDetailsV2(Resource):
	def put(self,payment_id,payment_status,payment_request_id):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		conn = connect_userLib()
		curlab = conn.cursor()

		details = request.get_json()

		# settlementURL = BASE_URL + "instamojo_payments/paymentController/createSettlementByPaymentIdV2"

		# headers = {'Content-type':'application/json', 'Accept':'application/json'}

		update_status = 'Complete'
		
		updatePaymentQuery = ("""UPDATE `instamojo_payment_request` SET  
			`payment_status` = %s,`payment_id`= %s, `status` = %s WHERE `instamojo_request_id`= %s""")

		paymentData = (payment_status,payment_id,update_status,payment_request_id)

		curlog.execute(updatePaymentQuery,paymentData)

		curlog.execute("""SELECT `request_id`,`user_id`,`institution_id`,`amount`,`purpose` FROM `instamojo_payment_request` 
			WHERE `instamojo_request_id` = %s""",(payment_request_id))

		reqDtls = curlog.fetchone()

		reqId = reqDtls.get('request_id')	
		userId = reqDtls.get('user_id')
		amount = reqDtls.get('amount')	
		purpose = reqDtls.get('purpose')
		institutionId = reqDtls.get('institution_id')

		updateStudentStatus = ("""UPDATE `instamojo_payment_student_mapping` SET `status` = %s 
			where `request_id` = %s""")

		curlog.execute(updateStudentStatus,(update_status,reqId))

		if payment_status == 'Credit':
			# payload = {"payment_id":payment_id,
			# 			"request_id":reqId,
			# 			"user_id":userId,
			# 			"settlement_type":'CREDIT',
			# 			"amount":amount,
			# 			"institution_id":institutionId}

			# settleRes = requests.post(settlementURL,data=json.dumps(payload), headers=headers).json()
			# print(settleRes)

			if purpose.startswith('Course-'):
				updateStudentCourse = ("""UPDATE `student_coursefee_payment_details` SET `is_pending` = 'n',
					paid_on = %s WHERE `transaction_id` = %s""")
				paid_on = datetime.now().strftime('%Y-%m-%d')
				curlab.execute(updateStudentCourse,(paid_on,payment_request_id))

				curlab.execute("""SELECT scpd.`coursefee_id`,scpd.`student_id`,`course_id` FROM `student_coursefee_payment_details` scpd 
					INNER JOIN `student_coursefee_mapping` sm on scpd.`coursefee_id` = sm.`coursefee_id`
					WHERE `transaction_id` = %s""",(payment_request_id))

				courseDtls = curlab.fetchone()
				student_id = courseDtls.get('student_id')
				coursefee_id = courseDtls.get('coursefee_id')
				course_id = courseDtls.get('course_id')
				studentcourseMap = ("""INSERT INTO `student_course_master`(`student_id`, `course_id`, 
					`teacher_id`, `coursefee_id`, `Institution_ID`) VALUES (%s,%s,%s,%s,%s)""")

				curlab.execute(studentcourseMap,(student_id,course_id,userId,coursefee_id,institutionId))

			elif purpose.startswith('ComboCourse-'):
				updateStudentCourse = ("""UPDATE `student_coursefee_payment_details` SET `is_pending` = 'n',
					paid_on = %s WHERE `transaction_id` = %s""")
				paid_on = datetime.now().strftime('%Y-%m-%d')
				curlab.execute(updateStudentCourse,(paid_on,payment_request_id))

				curlab.execute("""SELECT scpd.`coursefee_id`,scpd.`student_id`,`combo_id` FROM `student_coursefee_payment_details` scpd 
					INNER JOIN `student_coursefee_mapping` sm on scpd.`coursefee_id` = sm.`coursefee_id`
					WHERE `transaction_id` = %s""",(payment_request_id))

				courseDtls = curlab.fetchone()
				student_id = courseDtls.get('student_id')
				coursefee_id = courseDtls.get('coursefee_id')

				curlab.execute("""SELECT `course_id` FROM `student_combo_mapping` WHERE 
					`coursefee_id` = %s and `student_id` = %s""",(coursefee_id,student_id))

				courseIdList = curlab.fetchall()
				studentcourseMap = ("""INSERT INTO `student_course_master`(`student_id`, `course_id`, 
						`teacher_id`, `coursefee_id`, `Institution_ID`) VALUES (%s,%s,%s,%s,%s)""")
				for cid, course in enumerate(courseIdList):
					course_id = course.get('course_id')
					curlab.execute(studentcourseMap,(student_id,course_id,userId,coursefee_id,institutionId))
		else:
			if purpose.startswith('Course-') or purpose.startswith('ComboCourse-'):
				updateStudentCourse = ("""UPDATE `student_coursefee_payment_details` SET `is_pending` = 'f',
					paid_on = %s WHERE `transaction_id` = %s""")
				paid_on = datetime.now().strftime('%Y-%m-%d')
				curlab.execute(updateStudentCourse,(paid_on,payment_request_id))
		
		connection.commit()
		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo Payment Details",
							"status": "success"},
			"responseList": 'Payment Details Updated'}), status.HTTP_200_OK

if __name__ == '__main__':
	# app.register_blueprint(instamojo_payments, url_prefix='/instamojo_payments')
	app.run(host='0.0.0.0',debug=True)