from pyfcm import FCMNotification
from flask import Flask, request, jsonify, json
from flask_api import status
from flaskext.mysql import MySQL
import datetime
from datetime import datetime,timedelta,date
import time
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
import requests
from pytz import timezone
import pytz

app = Flask(__name__)
mysql = MySQL()
cors = CORS(app)

app.config['MYSQL_DATABASE_USER'] = 'creamson_langlab'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Langlab@123'
app.config['MYSQL_DATABASE_DB'] = 'creamson_lab_lang1'
app.config['MYSQL_DATABASE_HOST'] = 'creamsonservices.com'

mysql.init_app(app)
connection = mysql.connect()
cursor = connection.cursor()

def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='event',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

def connect_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
								cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------Get-Guest-List-For-Ocassion---------------------#

@app.route('/getGuestListForPushNotificationForOcassion')
def getGuestListForPushNotificationForOcassion():
	INSTITUTION_ID = 367

	connection = connect_logindb()
	cursor = connection.cursor()		

	event_connection = mysql_connection()
	event_cursor = event_connection.cursor()

	today = date.today()
	print(today)

	#now = time.time()
	now = datetime.now()
		
	now_utc = datetime.now(timezone('UTC'))
	final_time = now_utc +  timedelta(minutes=30)
	notify_time = final_time.strftime("%I:%M %p")
	notify_date = today.strftime("%d-%m-%Y")
	print(notify_date)
	print(notify_time)

	get_client_data_query = ("""SELECT * FROM `student_dtls` where `INSTITUTION_ID` = %s""")
	get_cleint_data = (INSTITUTION_ID)
	client_count  = cursor.execute(get_client_data_query,get_cleint_data)

	if client_count > 0:
		client_data = cursor.fetchall()
		for ckey,cdata in enumerate(client_data):

			get_occassion_query = ("""SELECT * FROM `occasion` where `occasion_date` = %s and `occasion_time` = %s and `event_manager_id` = %s""")
			get_occassion_data = (notify_date,notify_time,cdata['INSTITUTION_USER_ID_STUDENT'])
			occasion_count = cursor.execute(get_occassion_query,get_occassion_data)
			print(cursor._last_executed)

			if occasion_count > 0:
				occasion_data =  cursor.fetchall()
				for key,data in enumerate(occasion_data):
					occasion_data[key]['last_update_ts'] = str(data['last_update_ts'])

					get_guest_list_query = ("""SELECT iuc.`INSTITUTION_USER_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`INSTITUTION_USER_PASSWORD`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`PRIMARY_CONTACT_NUMBER`
							FROM `guardian_dtls` gd
							INNER JOIN `institution_user_credential` iuc ON iuc.`INSTITUTION_USER_ID` = gd.`INSTITUTION_USER_ID_GUARDIAN`
							WHERE `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID_STUDENT` = %s""")
					get_guest_list_data = (INSTITUTION_ID,cdata['INSTITUTION_USER_ID_STUDENT'])
					guest_list_count = cursor.execute(get_guest_list_query,get_guest_list_data)

					if guest_list_count > 0:
						guest_list =  cursor.fetchall()
						print(guest_list)
						for gkey,gdata in enumerate(guest_list):
							get_device_token_query = ("""SELECT * FROM `devices` where `user_id` = %s""")
							get_device_token_data =(gdata['INSTITUTION_USER_ID'])
							device_token_count = event_cursor.execute(get_device_token_query,get_device_token_data)

							if device_token_count > 0:
								device_details = event_cursor.fetchone()
								print(device_details)									
								data_message = {
									"title" : data['occasion_name'],
									"message":data['occasion_name']+" will be start on "+data['occasion_time']+". Please ready to join here"
								}
								print(data_message)
								api_key = "AAAA66tddZI:APA91bG89PrDCMns8-RSyLHUBiyu8VO1Kj9lchokDygCPg6NeRB59yD0sKXIe2xviw1XGraugdm9T8obOcGwf8tD_fiBVhHzAR_H186SNN88nEtOPxkFt7GQoyXVD91mt_3pVEeVwOb1"
								device_id = device_details['device_token']
								push_service = FCMNotification(api_key=api_key)
								msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = data_message)
								sent = 'N'
								if msgResponse.get('success') == 1:
									sent = 'Y'
								print(msgResponse)

					else:
						guest_list = []
						print(guest_list)



			else:
				occasion_data = []
	else:
		occasion_data = []


	return ({"attributes": {
				    		"status_desc": "ocassion_details",
				    		"status": "success"
				    	},
				    	"responseList":{"occasion_data":occasion_data,"notify_time":notify_time,"notify_date":notify_date}}), status.HTTP_200_OK

#----------------------Get-Guest-List-For-Ocassion---------------------#	

#----------------------Get-Guest-List-For-Food---------------------#

@app.route('/getGuestListForPushNotificationForFood')
def getGuestListForPushNotificationForFood():
	INSTITUTION_ID = 367
	connection = connect_logindb()
	cursor = connection.cursor()		

	event_connection = mysql_connection()
	event_cursor = event_connection.cursor()

	today = date.today()
	print(today)

	#now = time.time()
	now = datetime.now()
		
	now_utc = datetime.now(timezone('UTC'))
	final_time = now_utc +  timedelta(minutes=30)
	notify_time = final_time.strftime("%I:%M %p")
	notify_date = today.strftime("%d-%m-%Y")
	print(notify_date)
	print(notify_time)

	get_client_data_query = ("""SELECT * FROM `student_dtls` where `INSTITUTION_ID` = %s""")
	get_cleint_data = (INSTITUTION_ID)
	client_count  = cursor.execute(get_client_data_query,get_cleint_data)

	if client_count > 0:
		client_data = cursor.fetchall()
		for ckey,cdata in enumerate(client_data):
			get_food_query = ("""SELECT * FROM `food` where `date` = %s and `time` = %s and `event_manager_id` = %s""")
			get_food_data = (notify_date,notify_time,cdata['INSTITUTION_USER_ID_STUDENT'])
			food_count = event_cursor.execute(get_food_query,get_food_data)
			print(event_cursor._last_executed)

			if food_count > 0:
				food_data =  event_cursor.fetchall()
				for fkey,fdata in enumerate(food_data):
					food_data[fkey]['last_update_ts'] = str(fdata['last_update_ts'])
					get_guest_list_query = ("""SELECT iuc.`INSTITUTION_USER_ID`,iuc.`INSTITUTION_USER_NAME`,iuc.`INSTITUTION_USER_PASSWORD`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`PRIMARY_CONTACT_NUMBER`
						FROM `guardian_dtls` gd
						INNER JOIN `institution_user_credential` iuc ON iuc.`INSTITUTION_USER_ID` = gd.`INSTITUTION_USER_ID_GUARDIAN`
						WHERE `INSTITUTION_ID` = %s and `INSTITUTION_USER_ID_STUDENT` = %s""")
					get_guest_list_data = (INSTITUTION_ID,cdata['INSTITUTION_USER_ID_STUDENT'])
					guest_list_count = cursor.execute(get_guest_list_query,get_guest_list_data)

					if guest_list_count > 0:
						guest_list =  cursor.fetchall()
						print(guest_list)
						for gkey,gdata in enumerate(guest_list):
							get_device_token_query = ("""SELECT * FROM `devices` where `user_id` = %s""")
							get_device_token_data =(gdata['INSTITUTION_USER_ID'])
							device_token_count = event_cursor.execute(get_device_token_query,get_device_token_data)

							if device_token_count > 0:
								device_details = event_cursor.fetchone()
								print(device_details)
									
								food_data_message = {
									"title" : fdata['food_name'],
									"message":fdata['food_name']+" will be start on "+fdata['time']+". Please ready to join here"
								}
								api_key = "AAAA66tddZI:APA91bG89PrDCMns8-RSyLHUBiyu8VO1Kj9lchokDygCPg6NeRB59yD0sKXIe2xviw1XGraugdm9T8obOcGwf8tD_fiBVhHzAR_H186SNN88nEtOPxkFt7GQoyXVD91mt_3pVEeVwOb1"
								device_id = device_details['device_token']
								push_service = FCMNotification(api_key=api_key)
								msgResponse = push_service.notify_single_device(registration_id=device_id,data_message = food_data_message)
								sent = 'N'
								if msgResponse.get('success') == 1:
									sent = 'Y'

					else:
						guest_list = []
						print(guest_list)

			else:
				food_data = []
	else:
		food_data = []

	return ({"attributes": {
				    		"status_desc": "ocassion_details",
				    		"status": "success"
				    	},
				    	"responseList":{"food_data":food_data,"notify_time":notify_time,"notify_date":notify_date}}), status.HTTP_200_OK

#----------------------Get-Guest-List-For-Food---------------------#

@app.route('/')
def hello_world():
	return 'Hello, World!!!'


if __name__ == '__main__':
	app.run()