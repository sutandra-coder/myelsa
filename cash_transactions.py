from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

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

cash_transaction = Blueprint('cash_transaction_api', __name__)
api = Api(cash_transaction,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('cashTransactionController',description='Cash Transaction')

BASE_URL_JAVA = 'http://creamsonservices.com:8080/'
@name_space.route("/cashTransactionsForProducts/<int:user_id>/<string:product_code>")
class cashTransactionsForProducts(Resource):
	def post(self,user_id,product_code):
		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Product_CODE`,`Product_Desc`,`Dashboard_ID`,
				`Activity_ID`,`Activity_Type`,`Product_Image_Path`,`Product_Price`, 
				`GST_Value`,`SGST_Value`,`CGST_Value`,`Delivery_Charges`, 
				`Delivery_Charges_Waived_Flag`,`Period_Type`,`Period_Duration` 
				FROM `product` WHERE `Product_CODE` = %s""",(product_code))

		productDtls = cursor.fetchone()
		# print(productDtls)
		if productDtls:

			cursor.execute("""SELECT `FIRST_NAME` FROM `institution_user_credential` 
				WHERE `INSTITUTION_USER_ID` =%s""",(user_id))
			username = cursor.fetchone()

			productDtls['Delivery_Charges'] = productDtls.get('Delivery_Charges',0)
			# print(productDtls['Delivery_Charges'])

			post_url = BASE_URL_JAVA+'CreamsonWorksheetServices/InsertTransactionPayment'
			post_data = {
					  "addressId": 0,
					  "bankTransactionID": "",
					  "invoiceDetail": {
					    "addressLine1": "Cash Transaction",
					    "addressLine2": "",
					    "addressLine3": "",
					    "amount": productDtls.get('Product_Price',0),
					    "amountInwords": "",
					    "buyersAddressLine1": "",
					    "buyersAddressLine2": "",
					    "buyersCode": "",
					    "buyersCompanyName": "",
					    "buyersGstinOrUin": "",
					    "buyersStateName": "",
					    "cgstAmount": productDtls.get('CGST_Value',0),
					    "cgstRate": "",
					    "companyCode": "",
					    "companyGstin": "",
					    "companyGstinOrUin": "",
					    "companyName": "myElsa",
					    "companyStatename": "",
					    "companysPan": "",
					    "dated": "",
					    "descriptionOfGoods": productDtls.get('Product_Desc'),
					    "descriptionSerial": "",
					    "invoiceNo": "",
					    "sgstAmount": productDtls.get('SGST_Value',0),
					    "sgstRate": "",
					    "supplierRef": "",
					    "taxAmountInWords": "",
					    "total": "",
					    "totalTaxAmount": int(productDtls.get('SGST_Value')) + int(productDtls.get('CGST_Value'))
					  },
					  "paymentMode": "Cash",
					  "productCODE": productDtls.get('Product_CODE'),
					  "productDetails": productDtls.get('Product_Desc'),
					  "transactionAmount": productDtls.get('Product_Price'),
					  "userId": user_id
					}
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(post_url, data=json.dumps(post_data), headers=headers)
			r = post_response.json()
			print(r)
			payment_transaction_id = r['TransactionId']
			order_id = r['OrderId']
			# print(payment_transaction_id,order_id)
			update_url = BASE_URL_JAVA+'CreamsonWorksheetServices/updatePaymentTransaction/{}/{}'.format(payment_transaction_id,order_id)
			update_data = {"bankTransactionID": 'Cash',
							"remarks": "Txn Success",
							"transactionStatus": "C"
							}
			update_params = {'paymentTrnsactionId': payment_transaction_id,
							'orderId':order_id}
			update_response = requests.put(update_url,data = json.dumps(update_data),headers = headers)
			r1 = update_response.json()
			print(r1)
			if r1.get('attributes').get('status') == "success":
				try:
					sourceApp = product_code
					url = BASE_URL_JAVA+'CommunicationModule2/sendMailMessage'
					msgdata = {
							  'mailDetails': [
							    {
							      'appParams': {},
							      'mailParams': {"username":username.get('FIRST_NAME')},
							      'role': 's1',
							      'toMail': '',
							      'toNumber': '',
							      'userId': user_id
							    }
							  ],
							  'sourceApp': sourceApp
							}
					response = requests.post(url, data=json.dumps(msgdata), headers=headers)
				except:
					pass
				return ({"attributes": {"status_desc": "Cash Transaction Details.",
										"status": "success"
										},
						"responseList":r}), status.HTTP_200_OK
			else:
				return ({"attributes": {"status_desc": "Cash Transaction Details.",
										"status": "failure"
										},
						"responseList":'Transaction Unsuccessful'}), status.HTTP_200_OK
		else:
			return ({"attributes": {"status_desc": "Cash Transaction Details.",
									"status": "failure"
									},
					"responseList":'Invalid userID or Product Code'}), status.HTTP_200_OK

if __name__ == '__main__':
	app.run(host='0.0.0.0')