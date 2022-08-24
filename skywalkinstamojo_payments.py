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
from instamojo_wrapper import Instamojo


app = Flask(__name__)
cors = CORS(app)
skywalkinstamojo_payments = Blueprint('skywalkinstamojo_payments_api', __name__)
api = Api(skywalkinstamojo_payments,  title='MyElsa API',description='MyElsa API')
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



ask_for_fees_model = api.model('ask_for_fees_model', {
	"amount":fields.Integer(),
	"purpose":fields.String(),
	"teacher_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"student_id":fields.List(fields.Integer()),
	"group_id":fields.List(fields.Integer()),
	"is_group":fields.Integer(required=True),
	})

create_payment_dtls_model = api.model('create_payment_dtls_model', {
	"student_id":fields.Integer(),
	"course_id":fields.Integer(),
	"payment_mode":fields.String(),
	"payment_type":fields.String(),
	"no_of_installment":fields.Integer(),
	"discount_given":fields.String(),
	"discount":fields.Float(),
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"total_amount":fields.String(),
	})

MOJO_TEST_URL = 'https://test.instamojo.com/'

MOJO_BASE_URL = 'https://api.instamojo.com/'

BASE_URL = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"
# BASE_URL = "http://127.0.0.1:5000/"


@name_space.route("/createPaymentRequestV2")
class createPaymentRequestV2(Resource):
	@api.expect(create_payment_link_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()

		API_KEY = 'test_c3611ee30020e5ec32db9a9c709'
		AUTH_TOKEN = 'test_acfacf68eb5b439ae305f1f34cc'
		
		api = Instamojo(api_key=API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/');

		userId = details.get('user_id',None)
		institutionId = 2226
		transactionId = details.get('transaction_id',None)

		redirect_url = 'http://visuable.in/instamojo_test.php'
		response = api.payment_request_create(
		    amount='10',
		    purpose='Course-Test',
		    send_email=True,
		    email="shantikyna@gmail.com",
		    redirect_url=redirect_url
		    )
		# response = {}
		# print the long URL of the payment request.
		# response = response['payment_request'] 
		# print(response)
		# print the unique ID(or payment request ID)
		# print(response['payment_request']['id'])
		mojoResInsertQuery = ("""INSERT INTO `instamojo_payment_request`(`instamojo_request_id`, 
			`phone`, `buyer_name`, `amount`, `purpose`,`status`, `shorturl`, `longurl`, 
			`redirect_url`, `webhook`, 
			 `user_id`,`institution_id`,`transaction_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		created_at = datetime.now()
		modified_at = datetime.now()

		mojoData = (response['payment_request']['id'],details.get('phone'),
			'skywalk test',response['payment_request']['amount'],response['payment_request']['purpose'],
			response['payment_request']['status'],response['payment_request']['shorturl'],
			response['payment_request']['longurl'],response['payment_request']['redirect_url'],response['payment_request']['webhook'],
			userId,institutionId,transactionId)
		curlog.execute(mojoResInsertQuery,mojoData)

		requestId = curlog.lastrowid
		response['paymentRequestId'] = requestId

		connection.commit()

		msg = 'Payment Link Created'
	
		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo payment request Details",
								"status": "success",
								"msg":msg},
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


@name_space.route("/askForFessByTeacherV2")
class askForFessByTeacherV2(Resource):
	@api.expect(ask_for_fees_model)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		details = request.get_json()


		# URL = BASE_URL + "instamojo_payments/paymentController/createPaymentRequest"
		URL = BASE_URL + "skywalk_payments/paymentController/createPaymentRequestV2"

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

				# print(mojoResponse)
				if mojoResponse.get('attributes').get('msg') == 'Payment Link Created':

					paymentStudentMapQuery = ("""INSERT INTO `instamojo_payment_student_mapping`(
						`request_id`, `student_id`, `status`) VALUES (%s,%s,%s)""")
					responseList = mojoResponse.get('responseList')
					mapData = (responseList.get('paymentRequestId'),sid,responseList['payment_request']['status'])

					curlog.execute(paymentStudentMapQuery,mapData)

		transRes = {"transaction_id":transaction_id,
					"initiated_for":initiated_for}
		connection.commit()
		curlog.close()
		return ({"attributes": {"status_desc": "Instamojo Payment Initiation Details",
							"status": "success"},
			"responseList": transRes}), status.HTTP_200_OK


@name_space.route("/createPaymentDetails")	
class createPaymentDetails(Resource):
	@api.expect(create_payment_dtls_model)
	def post(self):

		connection = connect_userLib()
		curlab = connection.cursor()

		conn = connect_logindb()
		curlog = conn.cursor()

		details = request.get_json()

		student_id = details.get('student_id')
		course_id = details.get('course_id')
		payment_mode = details.get('payment_mode')
		payment_type = details.get('payment_type')
		no_of_installment = details.get('no_of_installment')
		discount_given = details.get('discount_given')
		discount = details.get('discount')
		institution_id = details.get('institution_id')
		teacher_id = details.get('teacher_id')
		total_amount = details.get('total_amount')
		curdate = datetime.now().strftime('%Y-%m-%d')

		courseFeeInsertQuery = ("""INSERT INTO `student_coursefee_mapping`(`purchase_type`,`student_id`, `course_id`, 
			`payment_mode`, `payment_type`, `no_of_installment`, `total_amount`, `actual_amount`,
			`purchased_on`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		courseFeeData = ('course',student_id,course_id,payment_mode,payment_type,no_of_installment,
			total_amount,total_amount,curdate)


		curlab.execute(courseFeeInsertQuery,courseFeeData)

		courseFeeId = curlab.lastrowid

		studentPaymentDetailsInsert = ("""INSERT INTO `student_coursefee_payment_details`(`student_id`,
			`payment_amount`,`payment_duedate`,`is_pending`,
			`coursefee_id`) VALUES(%s,%s,%s,%s,%s)""")

		if no_of_installment > 1:

			installment_amount = float(total_amount)/no_of_installment

			for x in range(no_of_installment):
					payment_due_date = curdate
					# print(payment_due_date)
					paymentDtlsData = (student_id,installment_amount,payment_due_date,'y',courseFeeId)

					curlab.execute(studentPaymentDetailsInsert,paymentDtlsData)
					curdate = later_date(curdate)
		else:

			paymentDtlsData = (student_id,total_amount,curdate,'y',courseFeeId)

			curlab.execute(studentPaymentDetailsInsert,paymentDtlsData)

		connection.commit()
		curlab.close()

		getURL = BASE_URL + "myelsa_course/MyelsaCourse/getCourseFeesByStudentId/{}/{}".format(student_id,course_id)

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		getResponse = requests.get(getURL, headers=headers).json()

		return getResponse

@name_space.route("/createPaymentLinkByPaymentId/<int:payment_id>")	
class createPaymentLinkByPaymentId(Resource):
	def put(self,payment_id):

		connection = connect_userLib()
		curlab = connection.cursor()

		conn = connect_logindb()
		curlog = conn.cursor()
		
		linkDtls = {}

		URL = BASE_URL + "skywalk_payments/paymentController/askForFessByTeacherV2"

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		curlab.execute("""SELECT scpd.`student_id`,`payment_amount`,`payment_duedate`,
			scpd.`coursefee_id`,icm.`teacher_id`,icm.`Institution_ID`,sm.`course_id` ,`course_title`
			FROM `student_coursefee_payment_details` scpd
			INNER JOIN `student_coursefee_mapping` sm on 
			scpd.`coursefee_id` = sm.`coursefee_id`
			INNER JOIN `instituition_course_master` icm on sm.`course_id` = icm.`course_id`
			WHERE `payment_id` = %s""",(payment_id))

		paymentDtls = curlab.fetchone()
		# print(paymentDtls)
		if paymentDtls:

			payload = {"amount":int(paymentDtls.get('payment_amount')),
						"purpose":"Course-"+str(paymentDtls.get('course_title')),
						"teacher_id":paymentDtls.get('teacher_id'),
						"institution_id":paymentDtls.get('Institution_ID'),
						"student_id":[paymentDtls.get('student_id')],
						"group_id":[],
						"is_group":0}
			# print(payload)
			mojoResponse = requests.post(URL,data=json.dumps(payload), headers=headers).json()
			# print(mojoResponse)
			transId = mojoResponse.get('responseList').get('transaction_id')
			curlog.execute("""SELECT `phone`,`buyer_name`,`amount`,`purpose`,`longurl`as 'payment_link',ipr.`instamojo_request_id`
				FROM `instamojo_payment_request` ipr 
				INNER JOIN `instamojo_payment_student_mapping` ipsm 
				on ipr.`request_id` = ipsm.`request_id` WHERE `transaction_id` = %s 
				and `student_id` = %s""",(transId,paymentDtls.get('student_id')))

			linkDtls = curlog.fetchone()
			# print(linkDtls)
			if linkDtls:
				updateTran = ("""UPDATE `student_coursefee_payment_details` SET `transaction_id` = %s 
					WHERE `payment_id` = %s""")
				updateData = (linkDtls.get('instamojo_request_id'),payment_id)
				curlab.execute(updateTran,updateData)
				
		connection.commit()
		curlab.close()
		conn.commit()
		curlog.close()
		return ({"attributes": {"status_desc": "Student Payment Link Details",
								"status": "success"},
				"responseList": linkDtls}), status.HTTP_200_OK



if __name__ == '__main__':
	# app.register_blueprint(instamojo_payments, url_prefix='/instamojo_payments')
	app.run(host='0.0.0.0',debug=True)