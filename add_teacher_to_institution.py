import pymysql
from datetime import datetime,timedelta,date
import requests
import json
from flask import Flask, request, jsonify, json
from flask_api import status
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields



app = Flask(__name__)
cors = CORS(app)

teacher_to_institution = Blueprint('add_teacher_to_institution_api', __name__)
api = Api(teacher_to_institution,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('AddTeacherToInstitutionController',description='AddTeacherToInstitution')

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


@name_space.route("/addTeacher/<string:firstname>/<string:lastname>/<int:phone_no>/<string:institution_name>/<int:institution_id>")
class cashTransactionsForProducts(Resource):
	def post(self,firstname,lastname,phone_no,institution_name,institution_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		pass

		city = 'Kolkata'
		role = 'TA'
		licenseKey = 'ELSA'
		current_date = date.today()
		userEnrollDate = str(current_date)
		nextyear_date = current_date.replace(year=current_date.year + 1)
		userEndDate = str(nextyear_date)

		middlename = None

		add_user = {"city": city,
		"dateOfBirth": "",
		"emailId": "",
		"firstName": firstname,
		"gender": "",
		"institutionUserName": phone_no,
		"institutionUserPassword": phone_no,
		"institutionUserRole": role,
		"institutionUserStatus": "",
		"lastName": lastname,
		"middleName": middlename,
		"pincode": "",
		"primaryContactNumber": phone_no,
		"secondaryContactNumber": "",
		"state": "",
		"streetAddress": "",
		"userEndDate": userEndDate,
		"userEnrollDate": userEnrollDate,
		"userTaxId": "",
		"userUniqueId": "",
		"board": "",
		"studentname": "",
		"class": "",
		"institutionName": institution_name,
		"institutionId": institution_id,
		"licenseKey": licenseKey
		}
		post_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/myelsa_registration/myELSARegistration/registration'
		payload = json.dumps(add_user)
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		post_response = requests.post(post_url, data=payload, headers=headers)
		r = post_response.json()
		print(r)
		return r
		# # res_status = r['responseList']['STATUS']
		# res_user_id = r['responseList']['user_id']
		# # print(r,res_user_id)
		# if res_user_id > 0:
		# 	# print('line 91')
		# 	cursor.execute("""SELECT `User_Subscription_Id` FROM `user_subscription` 
		# 		WHERE `Product_CODE` in ('MEI3','MEI6','MEI12') and `User_Id` = %s""",(res_user_id))

		# 	user_sub = cursor.fetchall()

		# 	print(user_sub)
		# 	if user_sub:
		# 		sub_status = 'User Already Subscribed'

		# 	else:
		# 		post_url = 'http://creamsonservices.com:8080/CreamsonWorksheetServices/InsertTransactionPayment'
		# 		post_data = {
		# 				  "addressId": 0,
		# 				  "bankTransactionID": "",
		# 				  "invoiceDetail": {
		# 				    "addressLine1": "Cash Transaction",
		# 				    "addressLine2": "",
		# 				    "addressLine3": "",
		# 				    "amount": '1800',
		# 				    "amountInwords": "",
		# 				    "buyersAddressLine1": "",
		# 				    "buyersAddressLine2": "",
		# 				    "buyersCode": "",
		# 				    "buyersCompanyName": "",
		# 				    "buyersGstinOrUin": "",
		# 				    "buyersStateName": "",
		# 				    "cgstAmount": 0,
		# 				    "cgstRate": "",
		# 				    "companyCode": "",
		# 				    "companyGstin": "",
		# 				    "companyGstinOrUin": "",
		# 				    "companyName": "myElsa",
		# 				    "companyStatename": "",
		# 				    "companysPan": "",
		# 				    "dated": '2019-12-22',
		# 				    "descriptionOfGoods": 'Tutor Intelli',
		# 				    "descriptionSerial": "",
		# 				    "invoiceNo": "",
		# 				    "sgstAmount": 0,
		# 				    "sgstRate": "",
		# 				    "supplierRef": "",
		# 				    "taxAmountInWords": "",
		# 				    "total": "",
		# 				    "totalTaxAmount": 0
		# 				  },
		# 				  "paymentMode": "Cash",
		# 				  "productCODE": 'MEI12',
		# 				  "productDetails": 'Tutor Intelli',
		# 				  "transactionAmount": float(1800),
		# 				  "userId": res_user_id
		# 				}
		# 		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		# 		post_response = requests.post(post_url, data=json.dumps(post_data), headers=headers)
		# 		paymentDtls = post_response.json()
		# 		# print(paymentDtls)

		# 		payment_transaction_id = paymentDtls['TransactionId']
		# 		order_id = paymentDtls['OrderId']
		# 		# print(payment_transaction_id,order_id)
		# 		# print(paymentDtls.get('STATUS'))
		# 		if paymentDtls.get('STATUS') == 'SUCCESS':
		# 			# print('payment_success')
		# 			update_url = 'http://creamsonservices.com:8080/CreamsonWorksheetServices/updatePaymentTransaction/{}/{}'.format(payment_transaction_id,order_id)
		# 			update_data = {	  "bankTransactionID": 'Cash',
		# 							  "remarks": "Txn Success",
		# 							  "transactionStatus": "C"
		# 							}
		# 			update_params = {'paymentTrnsactionId': payment_transaction_id,
		# 							'orderId':order_id}
		# 			update_response = requests.put(update_url,data = json.dumps(update_data),headers = headers)
		# 			updatePaymentRes = update_response.json()

		# 			sub_status = 'User Subscribed'

		# 			url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/myelsa_communication/CommunicationAPI/postCommunication'
		# 			data = {
		# 					  "appParams": {},
		# 					  "userId": res_user_id,
		# 					  "sourceapp": "ELSATUTOR",
		# 					  "toMail": "",
		# 					  "role": "",
		# 					  "toNumber": "",
		# 					  "mailParams": {}
		# 					}
		# 			headers = {'Content-type':'application/json', 'Accept':'application/json'}
		# 			response = requests.post(url, data=json.dumps(data), headers=headers)
		# print(sub_status)