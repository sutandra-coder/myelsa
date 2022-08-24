from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime
from flask_cors import CORS, cross_origin
from flaskext.mysql import MySQL
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
mysql = MySQL()
coupon_validation = Blueprint('coupon_validation_api', __name__)
api = Api(coupon_validation, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('ValidateCoupon', description='Validate Coupon')

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_logindb'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'
mysql.init_app(app)

app.config['CORS_HEADERS'] = 'Content-Type'

coupon_model = api.model('CouponCode', {
	"Coupon":fields.String(required=True),
	"Institution_user_Id":fields.Integer(required=True),
	"product_code":fields.String(required=True)
	})
@name_space.route("/validateCoupon")
class validateCoupon(Resource):
	@api.expect(coupon_model)
	def post(self):
		details = request.get_json()
		connection = mysql.connect()
		cursor = connection.cursor()
		coupon = details['Coupon']
		product_code = details['product_code']
		coupon_id = None
		used_id = None
		# product_data = []
		try:
			cursor.execute("""SELECT `Product_id` 
				FROM `product` WHERE `Product_CODE` = %s""",(product_code))
			product_id = cursor.fetchone()
			if product_id:
				product_id = product_id[0]
			cursor.execute("""SELECT `Coupon_ID` FROM `event_coupon` 
				WHERE `Coupon` = %s and product_id = %s""",(coupon,product_id))
			coupon_id = cursor.fetchone()[0]
			cursor.execute("""SELECT `FIRST_NAME` FROM `institution_user_credential` 
				WHERE `INSTITUTION_USER_ID` =%s""",(details['Institution_user_Id']))
			username = cursor.fetchone()[0]
			if coupon_id != None:
				cursor.execute("""SELECT `Id` FROM `student_coupon` WHERE `Coupon_ID` = %s""",(coupon_id))
				used_id = cursor.fetchone()[0]
		except:
			pass
		coupon_data = {"coupon":coupon,
						"coupon_id":coupon_id,
						"institution_user_id": details['Institution_user_Id'],
						"product_id":product_id
						}
		if coupon_id != None and used_id == None:
			# cursor.execute("""SELECT `Product_ID` FROM `event_coupon` 
			# 		WHERE `Coupon_ID` = %s""",(coupon_id))
			# product_id = cursor.fetchone()[0]
			cursor.execute("""SELECT `Product_CODE`,`Product_Desc`,`Dashboard_ID`,
				`Activity_ID`,`Activity_Type`,`Product_Image_Path`,`Product_Price`, 
				`GST_Value`,`SGST_Value`,`CGST_Value`,`Delivery_Charges`, 
				`Delivery_Charges_Waived_Flag`,`Period_Type`,`Period_Duration` 
				FROM `product` WHERE `Product_ID` = %s""",(product_id))
			product_desc = cursor.description
			col_names = [col[0] for col in product_desc]
			product_data = [dict(izip(col_names, row)) for row in cursor.fetchall()]
			for i in range(len(product_data)):
				# if product_data[i]['Delivery_Charges']:
				product_data[i]['Delivery_Charges'] = product_data[i].get('Delivery_Charges',0)
			coupon_student_insert_query = ("""INSERT INTO `student_coupon`(`Coupon_ID`, 
				`Institution_user_Id`) VALUES (%s,%s)""")
			coupon_student_data = (coupon_id,details['Institution_user_Id'])
			cursor.execute(coupon_student_insert_query,coupon_student_data)
			coupon_data['message'] = 'valid'
			post_url = 'http://creamsonservices.com:8080/CreamsonWorksheetServices/InsertTransactionPayment'
			post_data = {
					  "addressId": 0,
					  "bankTransactionID": "",
					  "invoiceDetail": {
					    "addressLine1": "Cash Transaction",
					    "addressLine2": "",
					    "addressLine3": "",
					    "amount": product_data[0]['Product_Price'],
					    "amountInwords": "",
					    "buyersAddressLine1": "",
					    "buyersAddressLine2": "",
					    "buyersCode": "",
					    "buyersCompanyName": "",
					    "buyersGstinOrUin": "",
					    "buyersStateName": "",
					    "cgstAmount": product_data[0]['CGST_Value'],
					    "cgstRate": "",
					    "companyCode": "",
					    "companyGstin": "",
					    "companyGstinOrUin": "",
					    "companyName": "myElsa",
					    "companyStatename": "",
					    "companysPan": "",
					    "dated": "",
					    "descriptionOfGoods": product_data[0]['Product_Desc'],
					    "descriptionSerial": "",
					    "invoiceNo": "",
					    "sgstAmount": product_data[0]['SGST_Value'],
					    "sgstRate": "",
					    "supplierRef": "",
					    "taxAmountInWords": "",
					    "total": "",
					    "totalTaxAmount": int(product_data[0]['SGST_Value']) + int(product_data[0]['CGST_Value'])
					  },
					  "paymentMode": "Cash",
					  "productCODE": product_data[0]['Product_CODE'],
					  "productDetails": product_data[0]['Product_Desc'],
					  "transactionAmount": product_data[0]['Product_Price'],
					  "userId": details['Institution_user_Id']
					}
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(post_url, data=json.dumps(post_data), headers=headers)
			r = post_response.json()
			# print(r)
			payment_transaction_id = r['TransactionId']
			order_id = r['OrderId']
			# print(payment_transaction_id,order_id)
			update_url = 'http://creamsonservices.com:8080/CreamsonWorksheetServices/updatePaymentTransaction/{}/{}'.format(payment_transaction_id,order_id)
			update_data = {	  "bankTransactionID": coupon,
							  "remarks": "Txn Success",
							  "transactionStatus": "C"
							}
			update_params = {'paymentTrnsactionId': payment_transaction_id,
							'orderId':order_id}
			update_response = requests.put(update_url,data = json.dumps(update_data),headers = headers)
			r1 = update_response.json()
			print(r1)
			if product_id in [34,35,36,44]:
				insti_post_url = 'http://ec2-18-218-68-83.us-east-2.compute.amazonaws.com/flaskapp/onboarding_teachers/OnboardTeacher/createInstitute'
				insti_post_data = {"institution_user_id":details['Institution_user_Id']}
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				insti_post_res = requests.post(insti_post_url, data=json.dumps(insti_post_data),headers=headers)
				res = insti_post_res.json()

				url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
				data = {
						  'mailDetails': [
						    {
						      'appParams': {},
						      'mailParams': {"username":username},
						      'role': 's1',
						      'toMail': '',
						      'toNumber': '',
						      'userId': details['Institution_user_Id']
						    }
						  ],
						  'sourceApp': 'ELSATUTOR'
						}
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				response = requests.post(url, data=json.dumps(data), headers=headers)

				return ({"attributes": {
		    				"status_desc": "Event Coupon Details.",
		    				"status": "success"
		    				},
		    				"responseList":[{"CouponDtls":coupon_data,
		    								"ProductDtls": product_data,
		    								"InstitutionDtls":res}]}), status.HTTP_200_OK
			else:
				sourceApp = product_code
				url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
				data = {
						  'mailDetails': [
						    {
						      'appParams': {},
						      'mailParams': {"username":username},
						      'role': 's1',
						      'toMail': '',
						      'toNumber': '',
						      'userId': details['Institution_user_Id']
						    }
						  ],
						  'sourceApp': sourceApp
						}
				headers = {'Content-type':'application/json', 'Accept':'application/json'}
				response = requests.post(url, data=json.dumps(data), headers=headers)

				return ({"attributes": {
		    				"status_desc": "Event Coupon Details.",
		    				"status": "success"
		    				},
		    				"responseList":[{"CouponDtls":coupon_data,
		    								"ProductDtls": product_data}]}), status.HTTP_200_OK

		elif coupon_id != None and used_id != None:
			coupon_data['message'] = 'used'
			return ({"attributes": {
	    				"status_desc": "Event Coupon Details.",
	    				"status": "success"
	    				},
	    				"responseList":[{"CouponDtls":coupon_data}]}), status.HTTP_200_OK

		elif coupon_id == None:
			coupon_data['message'] = 'invalid'
			return ({"attributes": {
	    				"status_desc": "Event Coupon Details.",
	    				"status": "success"
	    				},
	    				"responseList":[{"CouponDtls":coupon_data}]}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0')
