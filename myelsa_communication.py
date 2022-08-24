from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
from werkzeug.utils import cached_property
from database_connections import connect_elsalibrary
from database_connections import connect_logindb
import requests
import calendar
import json
from threading import Thread
import time

app = Flask(__name__)
cors = CORS(app)

myelsa_communication = Blueprint('myelsa_communication_api', __name__)
api = Api(myelsa_communication,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaCommunication',description='Myelsa Communication')

base_url = "http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/"

def last_update_ts():
	return (datetime.now() + timedelta(days=0, hours=5, minutes=30)).strftime('%Y-%m-%dT%H:%M:%S')


receiver_group_model = api.model('receiver_group_model', {
	"group_id": fields.Integer()
	})
receiver_students_model = api.model('receiver_students_model', {
	"student_id": fields.Integer()
	})

'''def connect_myelsa_communication():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='myelsa_communication',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def connect_myelsa_communication():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='myelsa_communication',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

appmsgmodel = api.model('appmsgmodel', {
	"title": fields.String(),
	"msg": fields.String(),
	"img": fields.String(),
	"page": fields.String(),
	"page_id": fields.String(),
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer(),
	"receiver_group_model":fields.List(fields.Nested(receiver_group_model)),
	"receiver_students_model":fields.List(fields.Nested(receiver_students_model))
	})

@name_space.route("/sendNotification")
class sendNotification(Resource):
	@api.expect(appmsgmodel)
	def post(self):

		conn = connect_logindb()
		cur = conn.cursor()
		connection = connect_myelsa_communication()
		
		cursor = connection.cursor()
		details = request.get_json()

		title = details['title']
		msg = details['msg']
		img = details['img']
		page = details['page']
		page_id = details['page_id']
		teacher_id = details['teacher_id']
		institution_id = details['institution_id']
		selectedStudents = details['receiver_students_model']
		selectedGroups = details['receiver_group_model']


		cur.execute("SELECT `firebase_key` FROM `institution_firebase_mapping` WHERE `institution_id` = %s",institution_id)
		fcmKeyCur = cur.fetchone()
		if not fcmKeyCur:
			fcmKey = ""
		else:
			fcmKey = fcmKeyCur['firebase_key']
		headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + fcmKey
        }

		if selectedStudents != None:
			for selected in selectedStudents:
				cur.execute("SELECT `Device_id`,`ID` FROM `firebase_link` WHERE `INSTITUTION_USER_ID` = %s ORDER BY `ID` DESC LIMIT 1",selected['student_id'])
				device_id = cur.fetchone()

				if device_id:
					message = {
					'data':{'page': page,'page_id': page_id,'custom-title':title,'custom-body':msg,'custom-image':img},
					'to':device_id['Device_id']}
					r = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(message))
					resp = r.json()
					if resp['failure'] == 1:
						cursor.execute("""INSERT INTO `app_message` (`Title`, `Source_App_ID`, `body`, `User_ID`,
							`Role`, `Device_ID`, `Image_Url`, `page`, `page_id`, `Read_Receipt_Flag`, `Last_Update_ID`, `sent`) 
							VALUES (%s, '', %s, %s, %s, %s, %s, %s, %s, 'N', %s, 'N')""",
							(title,msg,selected['student_id'],"S1",device_id['Device_id'],img,page,page_id,teacher_id))
					else:
						cursor.execute("""INSERT INTO `app_message` (`Title`, `Source_App_ID`, `body`, `User_ID`,
							`Role`, `Device_ID`, `Image_Url`, `page`, `page_id`, `Read_Receipt_Flag`, `Last_Update_ID`, `sent`) 
							VALUES (%s, '', %s, %s, %s, %s, %s, %s, %s, 'N', %s, 'Y')""",
							(title,msg,selected['student_id'],"S1",device_id['Device_id'],img,page,page_id,teacher_id))

		if selectedGroups != None:
			for selected in selectedGroups:
				cur.execute("SELECT `Student_Id` from `group_student_mapping` WHERE `Group_Id` = %s",(selected['group_id']))
				groupStudents = cur.fetchall()
				if groupStudents != None:
					for gs in groupStudents:
						cur.execute("SELECT `Device_id`,`ID` FROM `firebase_link` WHERE `INSTITUTION_USER_ID` = %s ORDER BY `ID` DESC LIMIT 1",gs['Student_Id'])
						device_id = cur.fetchone()

						if device_id:
							message = {
							'data':{'page': page,'page_id': page_id,'custom-title':title,'custom-body':msg,'custom-image':img},
							'to':device_id['Device_id']}
							r = requests.post("https://fcm.googleapis.com/fcm/send",headers = headers, data=json.dumps(message))
							resp = r.json()
							if resp['failure'] == 1:
								cursor.execute("""INSERT INTO `app_message` (`Title`, `Source_App_ID`, `body`, `User_ID`,
									`Role`, `Device_ID`, `Image_Url`, `page`, `page_id`, `Read_Receipt_Flag`, `Last_Update_ID`, `sent`) 
									VALUES (%s, '', %s, %s, %s, %s, %s, %s, %s, 'N', %s, 'N')""",
									(title,msg,selected['student_id'],"S1",device_id['Device_id'],img,page,page_id,teacher_id))
							else:
								cursor.execute("""INSERT INTO `app_message` (`Title`, `Source_App_ID`, `body`, `User_ID`,
									`Role`, `Device_ID`, `Image_Url`, `page`, `page_id`, `Read_Receipt_Flag`, `Last_Update_ID`, `sent`) 
									VALUES (%s, '', %s, %s, %s, %s, %s, %s, %s, 'N', %s, 'Y')""",
									(title,msg,selected['student_id'],"S1",device_id['Device_id'],img,page,page_id,teacher_id))
				else:
					pass

		connection.commit()
		cursor.close()
		cur.close()
		return ({"attributes": {"status_desc": "Notification Details",
								"status": "success"},
				"responseList": ""}), status.HTTP_200_OK

@name_space.route("/markNotificationAsSeen/<int:notification_id>/<int:student_id>")
class markNotificationAsSeen(Resource):
	def put(self, notification_id,student_id):
		connection = connect_myelsa_communication()
		cursor = connection.cursor()
		
		notification_read_query = ("""UPDATE `app_message` SET `Read_Receipt_Flag` = %s WHERE `App_Message_ID` = %s AND `User_ID` = %s""")
		notification_read_data = ('Y',notification_id,student_id)
		
		cursor.execute(notification_read_query,notification_read_data)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Notification Read status",
								"status": "success"},
				"responseList": ''}), status.HTTP_200_OK

@name_space.route("/GetNotificationByStudentId/<int:student_id>",
	doc={'params':{'read':'read_flag: Y or N'}})
class GetNotificationByStudentId(Resource):
	def get(self,student_id):
		connection = connect_myelsa_communication()
		cursor = connection.cursor()
		
		read_flag = str(request.args.get('read','')) # ''-All, 'N'-not read only, 'Y' - read only

		if read_flag == '':
			cursor.execute("""SELECT `User_ID`,`App_Message_ID`,`Title`,`body`,`Image_Url`,`page`,`page_id`,
				`Read_Receipt_Flag`,`Last_Update_TS` FROM `app_message` WHERE `User_ID` = %s ORDER BY `App_Message_ID` DESC""",(student_id))
		else:
			cursor.execute("""SELECT `User_ID`,`App_Message_ID`,`Title`,`body`,`Image_Url`,`page`,`page_id`,
				`Read_Receipt_Flag`,`Last_Update_TS` FROM `app_message` WHERE `User_ID` = %s AND `Read_Receipt_Flag` = %s ORDER BY `App_Message_ID` DESC""",(student_id,read_flag))

		data = cursor.fetchall()

		for x in data:
			x['Last_Update_TS'] = x['Last_Update_TS'].isoformat()

		cursor.close()
		
		return ({"attributes": {"status_desc": "Notification Details",
								"status": "success"},
				"responseList": data}), status.HTTP_200_OK

@name_space.route("/GetUnreadNotificationCountByStudentId/<int:student_id>")
class GetUnreadNotificationCountByStudentId(Resource):
	def get(self,student_id):
		connection = connect_myelsa_communication()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT count(`User_ID`) as 'count' FROM `app_message` WHERE `User_ID` = %s AND `Read_Receipt_Flag` = 'N'""",(student_id))

		data = cursor.fetchone()
		count = data['count']
		

		cursor.close()
		
		return ({"attributes": {"status_desc": "Notification Details",
								"status": "success"},
				"responseList": count}), status.HTTP_200_OK

@name_space.route("/markAllNotificationAsSeen/<int:student_id>")
class markAllNotificationAsSeen(Resource):
	def put(self,student_id):
		connection = connect_myelsa_communication()
		cursor = connection.cursor()
		
		notification_read_query = ("""UPDATE `app_message` SET `Read_Receipt_Flag`=%s WHERE `User_ID` = %s""")
		notification_read_data = ('Y',student_id)
		
		cursor.execute(notification_read_query,notification_read_data)
		connection.commit()
		cursor.close()
		
		return ({"attributes": {"status_desc": "Notification Read status",
								"status": "success"},
				"responseList": ''}), status.HTTP_200_OK