from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import pymysql

app = Flask(__name__)
cors = CORS(app)

myelsa_app_notify = Blueprint('myelsa_app_notify_api', __name__)
api = Api(myelsa_app_notify, version='1.0', title='MyElsa API',
    description='MyElsa API')
name_space = api.namespace('AppCommunicationAPI', description='App Notification')

def mysql_connection():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_communication',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def mysql_connection1():
    connection = pymysql.connect(host='creamsonservices.com',
                                 user='creamson_langlab',
                                 password='Langlab@123',
                                 db='creamson_logindb',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

app.config['CORS_HEADERS'] = 'Content-Type'


# BASE_URL = 'http://127.0.0.1:5000/'
BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'

class DictModel(fields.Raw):
	def format(self, value):
		dictmodel = {}
		return dictmodel

communication_model = api.model('communication_model', {
	"sourceapp":fields.String(),
	"appParams": DictModel(),
	"mailParams":DictModel(),
	"role":fields.String(),
	"toMail":fields.String(),
	"toNumber":fields.String(),
	"userId": fields.Integer(),
		})

data_message_model = api.model('data_message_model',{
						"image-url" : fields.String(),
						"userId" : fields.Integer(),
						"sourceAppId" : fields.String(), 
						"title" : fields.String(),
						"AppMessageId" : fields.Integer(),
						"message":fields.String(),
						"dashboard_id":fields.Integer()
						})

appmsg_model = api.model('appmsg_model', {
	"data_message":fields.Nested(data_message_model),
	"firebase_key":fields.String(),
	"device_id":fields.String()
		})

def get_apiKey(user_id):

	conn = mysql_connection1()
	cur = conn.cursor()

	cur.execute("""SELECT `INSTITUTION_ID`,`Device_id` FROM `institution_user_credential_master` icm 
		INNER JOIN `firebase_link` fl ON icm.`INSTITUTION_USER_ID` = fl.`INSTITUTION_USER_ID`
		WHERE icm.`INSTITUTION_ID` <> 1 and fl.`INSTITUTION_USER_ID` = %s 
		ORDER BY fl.`ID` desc limit 1""",(user_id))

	userDtls = cur.fetchone()

	if userDtls:
		institution_id = userDtls.get('INSTITUTION_ID')
		device_id = userDtls.get('Device_id')
		 
		cur.execute("""SELECT `firebase_key` FROM `institution_firebase_mapping` 
			WHERE `institution_id` = %s""",(institution_id))

		firebaseDtls = cur.fetchone()

		if firebaseDtls:
			firebaseKey = firebaseDtls.get('firebase_key')
		else:
			cur.execute("""SELECT `firebase_key` FROM `institution_firebase_mapping` 
			WHERE `institution_id` = 1""")

			firebaseDtls = cur.fetchone()
			firebaseKey = firebaseDtls.get('firebase_key')
	else:
		institution_id = 1
		device_id = None
		firebaseKey = None

	return (institution_id,device_id,firebaseKey)


@name_space.route("/appMessage")
class appMessage(Resource):
	@api.expect(communication_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = mysql_connection1()
		cur = conn.cursor()

		details = request.get_json()

		sourceapp = details['sourceapp']
		appParams = details['appParams']
		mailParams = details['mailParams']
		role = details['role']
		toMail = details['toMail']
		toNumber = details['toNumber']
		userId = details['userId']
		body_text = ''
		sms_body_text = ''
		cursor.execute("""SELECT `application_name`,`Recipient`,`title`,`app`,`App_Body`,
			`App_Description`,`Dashboard_Id` FROM `configuration` 
			WHERE `application_name` =  %s""",(sourceapp))


		config_info = cursor.fetchone()
		app_body = config_info.get('App_Body')
		title = config_info.get('App_Description')
		recipient = config_info.get('Recipient')
		dashboard_id = config_info.get('Dashboard_Id')
		if userId > 0:
			cur.execute("""SELECT `FIRST_NAME`,`LAST_NAME`,`PRIMARY_CONTACT_NUMBER` as 'phone_no' FROM 
				`institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(userId))

			user_info = cur.fetchone()
			FIRST_NAME = user_info['FIRST_NAME']
			LAST_NAME = user_info['LAST_NAME']
			phoneno = user_info['phone_no']
			fullName = FIRST_NAME + ' ' + LAST_NAME
			
			
			app_text = app_body
			for k,v in mailParams.items():
				app_text = app_text.replace('{{'+k+'}}',v)

			config_info['App_Body'] = app_text
			imageurl =  appParams.get('image-url','')
		
			response = get_apiKey(userId)
			print(response)
			appMsgInsertQuery = ("""INSERT INTO `app_massage`(`Source_App_ID`, `body`, `User_ID`, 
				`Role`, `Device_ID`, `Image_Url`, 
				`Read_Receipt_Flag`, `sent`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")
			appMsgData = (sourceapp,app_text,userId,recipient,response[1],imageurl,'N','N')
			cursor.execute(appMsgInsertQuery,appMsgData)
			msgID = cursor.lastrowid
			data_message = {"image-url" : imageurl,
							"userId" : userId,
							"sourceAppId" : sourceapp, 
							"title" : title,
							"AppMessageId" : msgID,
							"message":app_text,
							"dashboard_id":dashboard_id
							}
			posturl = BASE_URL + 'app_notify/AppCommunicationAPI/sendAppPushNotifications'
			payload = {"data_message":data_message ,
						"firebase_key": response[2],
						"device_id": response[1]}

			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			post_response = requests.post(posturl, data=json.dumps(payload), headers=headers).json()
		else:
			post_response = {}
		cursor.close()
		cur.close()
		return post_response
		

@name_space.route("/sendAppPushNotifications")
class sendAppPushNotifications(Resource):
	@api.expect(appmsg_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		details = request.get_json()
		data_message = details.get('data_message')
		api_key = details.get('firebase_key')
		device_id = details.get('device_id')
		push_service = FCMNotification(api_key=api_key)
		msgResponse = push_service.notify_single_device(registration_id=device_id,
			data_message = data_message)
		sent = 'N'
		if msgResponse.get('success') == 1:
			sent = 'Y'
		
		msgStatusUpdateQuery = ("""UPDATE `app_massage` SET `sent` = %s 
			where `App_Massage_ID` = %s""")
		statusData = (sent,data_message.get('AppMessageId'))

		cursor.execute(msgStatusUpdateQuery,statusData)
		connection.commit()
		cursor.close()
		return msgResponse


if __name__ == '__main__':
	app.run(host='0.0.0.0')