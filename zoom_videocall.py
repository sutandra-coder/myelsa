import requests
import pymysql
import time
from lxml import etree
from threading import Thread
from utils import getStudentListFromGroupid
import configparser
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import webinar_qrcode


app = Flask(__name__)
cors = CORS(app)
live_classes = Blueprint('live_classes_api', __name__)
api = Api(live_classes,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('liveClassesController',description='Live Classes')


BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'
'''def connnect_userLibrary():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_user_library',
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
	return connection'''

def connnect_userLibrary():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_user_library',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection


def connect_logindb():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
									user='admin',
									password='cbdHoRPQPRfTdC0uSPLt',
									db='creamson_logindb',
									charset='utf8mb4',
									cursorclass=pymysql.cursors.DictCursor)
	return connection

create_meeting = api.model('create_meeting', {
	"meeting_id":fields.Integer(required=True),
	"google_meet_url":fields.String(),
	"is_webinar":fields.Integer()
	})

update_meeting = api.model('update_meeting', {
	"zoom_meeting_id":fields.Integer(required=True),
	"meeting_id":fields.Integer(required=True),
	"teacher_id":fields.Integer(required=True),
	"start_time":fields.String(),
	"end_time":fields.String(),
	"description":fields.String(),
	"subject":fields.String(),
	})

def sendMeetingInvite(request):
	meeting_id,meetingDtls,liveclass_id,platform = request

	connection = connnect_userLibrary()
	curLib = connection.cursor()
	conn = connect_logindb()
	curLog = conn.cursor()

	
	# url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
	url = BASE_URL + 'app_notify/AppCommunicationAPI/appMessage'
	headers = {'Content-type':'application/json', 'Accept':'application/json'}

	curLog.execute("""SELECT `MEETING_GROUP` FROM `notification_tracking_dtls` 
		WHERE `MEETING_ID` = %s limit 1""",(meeting_id))

	assignedTo = curLog.fetchone()
	studentList = []
	appResponse = []
	classStudentMapInsertQuery = ("""INSERT INTO `liveclass_student_mapping`(`liveclass_id`, 
		`student_id`,`platform`) VALUES (%s,%s,%s)""")

	if assignedTo.get('MEETING_GROUP') == 'I':
		curLog.execute("""SELECT `MEETING_GROUP_ID` FROM `notification_tracking_dtls` 
			WHERE `MEETING_ID` = %s""",(meeting_id))

		studentDtls = curLog.fetchall()

		studentList = [x['MEETING_GROUP_ID'] for i, x in enumerate(studentDtls)]
	else:
		curLog.execute("""SELECT `MEETING_GROUP_ID` FROM `notification_tracking_dtls` 
			WHERE `MEETING_ID` = %s""",(meeting_id))

		groupDtls = curLog.fetchall()

		groupList = [x['MEETING_GROUP_ID'] for i, x in enumerate(groupDtls)]

		studentList = getStudentListFromGroupid(groupList)
	curLog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
		`image_url` as teacher_image FROM `institution_user_credential` 
		WHERE `INSTITUTION_USER_ID` = %s""",(meetingDtls.get('TEACHER_ID')))
	teacher = curLog.fetchone()

	if teacher:
		teacher_name = teacher['name']
	else:
		teacher_name = 'ELSA'
	studentList = list(set(studentList))
	for sid in studentList:
		curLog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
			FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(sid))
		student = curLog.fetchone()
		if student:
			student_name = student['name']
			sdata = {'appParams': {},
					'mailParams': {"student":student_name,
										"liveclass":meetingDtls.get('DESCRIPTION'),
										"startdate":meetingDtls.get('START_DATE').isoformat().replace('T',' '),
										"teacher":teacher_name},
					'role': 'S1',
					'toMail': '',
					'toNumber': '',
					'userId': sid,
					'sourceapp': 'LCS001'
					}
			
			appResponse.append(requests.post(url, data=json.dumps(sdata), headers=headers).json())
			classStudentData = (liveclass_id,sid,platform)
			curLib.execute(classStudentMapInsertQuery,classStudentData)
	curLib.close()
	curLog.close()

class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'createZoomMeeting' or self.funcname == 'createZoomMeeting' or self.funcname == 'createGoogleMeeting' or self.funcname == 'createSafeMeeting':
			sendMeetingInvite(self.request)
		else:
			pass

@name_space.route("/createZoomMeeting")
class createZoomMeeting(Resource):
	@api.expect(create_meeting)
	def post(self):

		details = request.get_json()
		meeting_id = details.get('meeting_id')
		is_webinar = details.get('is_webinar',0)
		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()
		res = {}
		url = 'http://creamsonservices.com:8080/CommunicationModule2/sendMailMessage'
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		curLog.execute("""SELECT `INSTITUTION_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,`LOCATION`,
			`SUBJECT`,`DESCRIPTION` FROM `meeting_dtls` WHERE `meeting_id` = %s""",(meeting_id))

		meetingDtls = curLog.fetchone()
		message = 'Invalid MeetingID'

		if meetingDtls:
			curLog.execute("""SELECT `user_mailid`,`zoom_api_key` FROM `zoom_user_details` 
				WHERE `user_id` = %s""",(meetingDtls.get('TEACHER_ID')))

			teacherDtls = curLog.fetchone()
			if teacherDtls:

				mailId = teacherDtls.get('user_mailid')
				apiKey = teacherDtls.get('zoom_api_key')

				start_time = meetingDtls.get('START_DATE').isoformat()
				print(start_time)
				headers = {'Content-Type':'application/json','authorization': 'Bearer ' + apiKey}
				createUrl = 'https://api.zoom.us/v2/users/{userId}/meetings'.format(userId=mailId)
				zoom_payload = {"topic": meetingDtls.get('SUBJECT'),
								"type": 2,
								"start_time": start_time,
								"duration": 40,
								"timezone": "Asia/Calcutta",
								"password": "",
								"agenda": meetingDtls.get('DESCRIPTION'),
								"settings": {
									"host_video": "true",
									"participant_video": "false",
									"join_before_host": "true",
									"mute_upon_entry": "true",
									"watermark": "true",
									"use_pmi": "false",
									"approval_type": "2",
									"registration_type": "1",
									"audio": "both",
									"auto_recording": "local"
									}
								}

				postRequest = requests.post(createUrl, data=json.dumps(zoom_payload), headers=headers)
				postStatus = postRequest.status_code
				print(postStatus)
				
				if postStatus == 201:
					postRes = postRequest.json()
					zoom_meeting_id = postRes.get('id')
					zoom_uuid = postRes.get('uuid')
					zoom_join_url = postRes.get('join_url')

					createMeetingQuery = ("""INSERT INTO `liveclass_mapping`(`meeting_id`, 
						`zoom_meeting_id`, `zoom_uuid`, `zoom_join_url`, `teacher_id`, 
						`institution_id`,`platform`, `start_date`,`end_date`,`location`,
						`subject`,`description`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

					meetingData = (meeting_id,zoom_meeting_id,zoom_uuid,zoom_join_url,
						meetingDtls.get('TEACHER_ID'),meetingDtls.get('INSTITUTION_ID'),'zoom',
						meetingDtls.get('START_DATE'),meetingDtls.get('END_DATE'),
						meetingDtls.get('LOCATION'),meetingDtls.get('SUBJECT'),
						meetingDtls.get('DESCRIPTION'))

					curLib.execute(createMeetingQuery,meetingData)
					liveclass_id = curLib.lastrowid

					liveclass_tracking_query = ("""INSERT INTO `student_liveclass_tracking`(
						`Student_ID`, `liveclass_id`,`Status`) VALUES (%s,%s,%s)""")

					liveclass_tracking_data = (meetingDtls.get('TEACHER_ID'),liveclass_id,'scheduled')

					curLib.execute(liveclass_tracking_query,liveclass_tracking_data)
					if is_webinar:
						qrCodeURL = webinar_qrcode.generateQRCode(liveclass_id,zoom_join_url,meetingDtls.get('TEACHER_ID'))
					else:
						qrCodeURL = ''
					res = {'zoom_meeting_id':zoom_meeting_id,
							'zoom_uuid':zoom_uuid,
							'zoom_join_url':zoom_join_url,
							'qrCodeURL':qrCodeURL}
					message = 'Zoom Meeting Scheduled Successfully'
					sendrReq = (meeting_id,meetingDtls,liveclass_id,'zoom')
					thread_a = Compute(sendrReq,'createZoomMeeting')
					thread_a.start()
				else:
					message = 'Failed to Schedule Zoom Meeting Scheduled.'
		connection.commit()
		curLib.close()
		curLog.close()

		
		return ({"attributes": {"status_desc": "Meeting Details",
								"status": "success",
								"message":message,
								"platform":'zoom',
								"is_webinar":is_webinar
									},
				"responseList":res}), status.HTTP_200_OK



@name_space.route("/getLiveClassScheduleforTeacher/<int:teacher_id>")
class getScheduleLiveClassforTeacher(Resource):
	def get(self,teacher_id):

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()
		platform = None
		zoomDtls = []
		curLog.execute("""SELECT `platform` FROM `zoom_user_details` 
				WHERE `user_id` = %s""",(teacher_id))

		platformDtls = curLog.fetchone()

		if platformDtls:
			platform = platformDtls.get('platform')

			if platform == 'zoom':

				curLib.execute("""SELECT `liveclass_id`,`meeting_id`,`zoom_join_url`,`zoom_meeting_id`, 
					`platform`,is_webinar,webinar_qrcode FROM `liveclass_mapping` WHERE `teacher_id` = %s 
					and `meeting_status` = 'created'""",(teacher_id))

				zoomDtls = curLib.fetchall()

				if zoomDtls:
					for mid,meet in enumerate(zoomDtls):
						curLog.execute("""SELECT `TEACHER_ID`,`START_DATE`,`END_DATE`,`LOCATION`,
							`SUBJECT` as 'Topic',`DESCRIPTION` FROM `meeting_dtls` 
							WHERE `meeting_id` = %s""",(meet.get('meeting_id')))

						meetingDtls = curLog.fetchone()

						if meetingDtls:
							curLib.execute("""SELECT `Student_ID`,`liveclass_id`,`Status` 
								FROM `student_liveclass_tracking` WHERE `Student_ID`=%s
								and liveclass_id=%s""",
								(teacher_id,meet.get('liveclass_id')))

							teacherclassDtls = curLib.fetchone()
							if teacherclassDtls:
								meet['class_start'] = teacherclassDtls.get('Status')
							else:
								meet['class_start'] = 'scheduled'
							# meet['zoom_join_url'] = meetingDtls.get('zoom_join_url')
							meet['START_DATE'] = meetingDtls.get('START_DATE').isoformat()
							meet['END_DATE'] = meetingDtls.get('END_DATE').isoformat()
							meet['LOCATION'] = meetingDtls.get('LOCATION')
							meet['Topic'] = meetingDtls.get('Topic')
							meet['Description'] = meetingDtls.get('DESCRIPTION')
							meet['teacher_id'] = teacher_id

			elif platform == 'webex':

				curLib.execute("""SELECT `liveclass_id`,`meeting_id`,`webex_meetingkey`,
					`webex_hosturl`,`webex_attendeeurl`,`webex_meeting_pwd`,`platform`,is_webinar,webinar_qrcode 
					FROM `liveclass_mapping` WHERE `teacher_id`  = %s
					and `meeting_status` = 'created'""",(teacher_id))

				zoomDtls = curLib.fetchall()

				if zoomDtls:
					for mid,meet in enumerate(zoomDtls):
						curLog.execute("""SELECT `TEACHER_ID`,`START_DATE`,`END_DATE`,`LOCATION`,
							`SUBJECT` as 'Topic',`DESCRIPTION` FROM `meeting_dtls` 
							WHERE `meeting_id` = %s""",(meet.get('meeting_id')))

						meetingDtls = curLog.fetchone()

						if meetingDtls:
							curLib.execute("""SELECT `Student_ID`,`liveclass_id`,`Status` 
								FROM `student_liveclass_tracking` WHERE `Student_ID`=%s
								and liveclass_id=%s""",
								(teacher_id,meet.get('liveclass_id')))

							teacherclassDtls = curLib.fetchone()
							if teacherclassDtls:
								meet['class_start'] = teacherclassDtls.get('Status')
							else:
								meet['class_start'] = 'scheduled'
							meet['zoom_join_url'] = meet.get('webex_hosturl')
							meet['zoom_meeting_id'] = meet.get('webex_meetingkey')
							meet['START_DATE'] = meetingDtls.get('START_DATE').isoformat()
							meet['END_DATE'] = meetingDtls.get('END_DATE').isoformat()
							meet['LOCATION'] = meetingDtls.get('LOCATION')
							meet['Topic'] = meetingDtls.get('Topic')
							meet['Description'] = meetingDtls.get('DESCRIPTION')
							meet['teacher_id'] = teacher_id
							meet.pop('webex_meetingkey')
							meet.pop('webex_hosturl')

			elif platform == 'google':

				curLib.execute("""SELECT `liveclass_id`,`meeting_id`,`google_meet_url`,`platform`,is_webinar,webinar_qrcode 
					FROM `liveclass_mapping` WHERE `teacher_id`  = %s
					and `meeting_status` = 'created'""",(teacher_id))

				zoomDtls = curLib.fetchall()
				if zoomDtls:
					for mid,meet in enumerate(zoomDtls):
						curLog.execute("""SELECT `TEACHER_ID`,`START_DATE`,`END_DATE`,`LOCATION`,
							`SUBJECT` as 'Topic',`DESCRIPTION` FROM `meeting_dtls` 
							WHERE `meeting_id` = %s""",(meet.get('meeting_id')))

						meetingDtls = curLog.fetchone()

						if meetingDtls:
							curLib.execute("""SELECT `Student_ID`,`liveclass_id`,`Status` 
								FROM `student_liveclass_tracking` WHERE `Student_ID`=%s
								and liveclass_id=%s""",
								(teacher_id,meet.get('liveclass_id')))

							teacherclassDtls = curLib.fetchone()
							if teacherclassDtls:
								meet['class_start'] = teacherclassDtls.get('Status')
							else:
								meet['class_start'] = 'scheduled'
							meet['zoom_join_url'] = meet.get('google_meet_url')
							meet['zoom_meeting_id'] = ""
							meet['START_DATE'] = meetingDtls.get('START_DATE').isoformat()
							meet['END_DATE'] = meetingDtls.get('END_DATE').isoformat()
							meet['LOCATION'] = meetingDtls.get('LOCATION')
							meet['Topic'] = meetingDtls.get('Topic')
							meet['Description'] = meetingDtls.get('DESCRIPTION')
							meet['teacher_id'] = teacher_id
							meet.pop('google_meet_url')

		curLib.close()
		curLog.close()

		return ({"attributes": {"status_desc": "Meeting Schedule Details",
								"status": "success",
								"platform":platform
									},
				"responseList":zoomDtls}), status.HTTP_200_OK


@name_space.route("/getLiveClassScheduleforStudents/<int:institution_id>/<int:student_id>")
class getLiveClassScheduleforStudents(Resource):
	def get(self,institution_id,student_id):

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()
		meetList = []
		curLib.execute("""SELECT `liveclass_id`,`platform` FROM `liveclass_student_mapping` 
			WHERE `student_id` = %s""",(student_id))


		classList = curLib.fetchall()

		if classList:
			for cid, clas in enumerate(classList):
				curLib.execute("""SELECT `content_id` FROM `content_library` WHERE 
					`content_id` in(SELECT `content_id` FROM `content_liveclass_mapping` 
					WHERE `liveclass_id` = %s) and `content_name` in 
					('prelive-Dummy','postlive-Dummy') limit 1""",(clas['liveclass_id']))

				assessmentDtls = curLib.fetchone()
				assessmentFlag = 'N'
				if assessmentDtls:
					assessmentFlag = 'Y'

				curLib.execute("""SELECT `content_id` FROM `content_library` WHERE 
					`content_id` in(SELECT `content_id` FROM `content_liveclass_mapping` 
					WHERE `liveclass_id` = %s) and `content_name` not in 
					('prelive-Dummy','postlive-Dummy') limit 1""",(clas['liveclass_id']))

				contentDtls = curLib.fetchone()
				contentFlag = 'N'
				if contentDtls:
					contentFlag = 'Y'
				if clas.get('platform') == 'zoom':
					curLib.execute("""SELECT `meeting_id`,`zoom_meeting_id`,`zoom_uuid`,
						`zoom_join_url`	FROM `liveclass_mapping` 
						WHERE `liveclass_id` = %s and `meeting_status` = 'created'""",(clas.get('liveclass_id')))

					classDtls = curLib.fetchone()
					if classDtls:
						curLog.execute("""SELECT md.`MEETING_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,
							`LOCATION`,`SUBJECT`,`DESCRIPTION` FROM `meeting_dtls` md 
							WHERE md.`MEETING_ID` = %s""",(classDtls.get('meeting_id')))

						meetingDtls = curLog.fetchone()

						curLog.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as name
						 FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`=%s""",
						 (meetingDtls.get('TEACHER_ID')))

						teachername = curLog.fetchone()
						if teachername:
							meetingDtls['Teachername'] = teachername.get('name')
						else:
							meetingDtls['Teachername'] = 'elsa'

						curLib.execute("""SELECT `Student_ID`,`liveclass_id`,`Status` 
							FROM `student_liveclass_tracking` WHERE `Student_ID`=%s
							and liveclass_id=%s""",
							(meetingDtls.get('TEACHER_ID'),clas.get('liveclass_id')))

						teacherclassDtls = curLib.fetchone()
						if teacherclassDtls:
							meetingDtls['class_start'] = teacherclassDtls.get('Status')
						else:
							meetingDtls['class_start'] = 'n'

						if meetingDtls:
							meetingDtls['START_DATE'] = meetingDtls['START_DATE'].isoformat()
							meetingDtls['END_DATE'] = meetingDtls['END_DATE'].isoformat()
							meetingDtls['assessmentFlag'] = assessmentFlag
							meetingDtls['contentFlag'] = contentFlag
							meetingDtls['liveclass_id'] = clas.get('liveclass_id')
							meetingDtls['platform'] = clas.get('platform')
							meetingDtls['zoom_meeting_id'] = classDtls.get('zoom_meeting_id')
							meetingDtls['zoom_uuid'] = classDtls.get('zoom_uuid')
							meetingDtls['zoom_join_url'] = classDtls.get('zoom_join_url')
							meetList.append(meetingDtls)
				elif clas.get('platform') == 'webex':
					curLib.execute("""SELECT `meeting_id`,`webex_attendeeurl`,`webex_meeting_pwd`,
						`webex_meetingkey` FROM `liveclass_mapping` 
						WHERE `liveclass_id` = %s and `meeting_status` = 'created'""",(clas.get('liveclass_id')))

					classDtls = curLib.fetchone()
					if classDtls:
						curLog.execute("""SELECT md.`MEETING_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,
							`LOCATION`,`SUBJECT`,`DESCRIPTION` FROM `meeting_dtls` md 
							WHERE md.`MEETING_ID` = %s""",(classDtls.get('meeting_id')))

						meetingDtls = curLog.fetchone()

						curLog.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as name
						 FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`=%s""",
						 (meetingDtls.get('TEACHER_ID')))

						teachername = curLog.fetchone()
						if teachername:
							meetingDtls['Teachername'] = teachername.get('name')
						else:
							meetingDtls['Teachername'] = 'elsa'

						curLib.execute("""SELECT `Student_ID`,`liveclass_id`,`Status` 
							FROM `student_liveclass_tracking` WHERE `Student_ID`=%s
							and liveclass_id=%s""",
							(meetingDtls.get('TEACHER_ID'),clas.get('liveclass_id')))

						teacherclassDtls = curLib.fetchone()
						if teacherclassDtls:
							meetingDtls['class_start'] = teacherclassDtls.get('Status')
						else:
							meetingDtls['class_start'] = 'n'
							
						if meetingDtls:
							meetingDtls['START_DATE'] = meetingDtls['START_DATE'].isoformat()
							meetingDtls['END_DATE'] = meetingDtls['END_DATE'].isoformat()
							meetingDtls['assessmentFlag'] = assessmentFlag
							meetingDtls['contentFlag'] = contentFlag
							meetingDtls['liveclass_id'] = clas.get('liveclass_id')
							meetingDtls['platform'] = clas.get('platform')
							meetingDtls['zoom_meeting_id'] = classDtls.get('webex_meetingkey')
							meetingDtls['webex_meeting_pwd'] = classDtls.get('webex_meeting_pwd')
							meetingDtls['zoom_join_url'] = classDtls.get('webex_attendeeurl')
							meetingDtls['webex_attendeeurl'] = classDtls.get('webex_attendeeurl')
							meetList.append(meetingDtls)

				elif clas.get('platform') == 'google':
					curLib.execute("""SELECT `meeting_id`,`google_meet_url`	FROM `liveclass_mapping` 
						WHERE `liveclass_id` = %s and `meeting_status` = 'created'""",(clas.get('liveclass_id')))

					classDtls = curLib.fetchone()
					if classDtls:
						curLog.execute("""SELECT md.`MEETING_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,
							`LOCATION`,`SUBJECT`,`DESCRIPTION` FROM `meeting_dtls` md 
							WHERE md.`MEETING_ID` = %s""",(classDtls.get('meeting_id')))

						meetingDtls = curLog.fetchone()

						curLog.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as name
						 FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`=%s""",
						 (meetingDtls.get('TEACHER_ID')))

						teachername = curLog.fetchone()
						if teachername:
							meetingDtls['Teachername'] = teachername.get('name')
						else:
							meetingDtls['Teachername'] = 'elsa'

						curLib.execute("""SELECT `Student_ID`,`liveclass_id`,`Status` 
							FROM `student_liveclass_tracking` WHERE `Student_ID`=%s
							and liveclass_id=%s""",
							(meetingDtls.get('TEACHER_ID'),clas.get('liveclass_id')))

						teacherclassDtls = curLib.fetchone()
						if teacherclassDtls:
							meetingDtls['class_start'] = teacherclassDtls.get('Status')
						else:
							meetingDtls['class_start'] = 'n'

						if meetingDtls:
							meetingDtls['START_DATE'] = meetingDtls['START_DATE'].isoformat()
							meetingDtls['END_DATE'] = meetingDtls['END_DATE'].isoformat()
							meetingDtls['assessmentFlag'] = assessmentFlag
							meetingDtls['contentFlag'] = contentFlag
							meetingDtls['liveclass_id'] = clas.get('liveclass_id')
							meetingDtls['platform'] = clas.get('platform')
							meetingDtls['zoom_meeting_id'] = ""
							meetingDtls['zoom_uuid'] = ""
							meetingDtls['zoom_join_url'] = classDtls.get('google_meet_url')
							meetList.append(meetingDtls)

		meetList = sorted(meetList, key = lambda i: i['START_DATE']) 
		return ({"attributes": {"status_desc": "Meeting Schedule Details",
								"status": "success"
									},
				"responseList":meetList}), status.HTTP_200_OK


@name_space.route("/getZoomAccountDetails/<int:user_id>")
class getZoomAccountDetails(Resource):
	def get(self,user_id):

		conn = connect_logindb()
		curLog = conn.cursor()
		userDtls = {"user_mailid":"",
					"zoom_password":""}
		curLog.execute("""SELECT `user_mailid`,`zoom_password`,`webex_pwd`,`platform` 
			FROM `zoom_user_details` WHERE `user_id` = %s""",(user_id))

		userDtls = curLog.fetchone()

		if not userDtls:
			userDtls = {}
			userDtls['user_mailid'] = ""
			userDtls['zoom_password'] = ""
			userDtls['platform'] = 'google'
		else:
			if userDtls.get('platform') == 'zoom':
				userDtls.pop('webex_pwd',None)
			elif userDtls.get('platform') == 'webex':
				userDtls.pop('zoom_password',None)
				userDtls['zoom_password'] = userDtls.get('webex_pwd')
				userDtls.pop('webex_pwd',None)
			elif userDtls.get('platform') == 'google':
				userDtls.pop('webex_pwd',None)
				userDtls.pop('zoom_password',None)
				userDtls['zoom_password'] = ""
			elif userDtls.get('platform') == None:
				userDtls['platform'] = 'google'

		curLog.close()

		return ({"attributes": {"status_desc": "User Details",
								"status": "success"
									},
				"responseList":userDtls}), status.HTTP_200_OK



@name_space.route("/updateScheduledLiveClass")
class updateScheduledLiveClass(Resource):
	@api.expect(update_meeting)
	def put(self):

		details = request.get_json()
		zoom_meeting_id = details.get('zoom_meeting_id')
		meeting_id = details.get('meeting_id')
		teacher_id = details.get('teacher_id')
		start_time = details.get('start_time')
		end_time = details.get('end_time')
		description = details.get('description')
		subject = details.get('subject')

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()

		curLog.execute("""SELECT `START_DATE`,`END_DATE`,`SUBJECT`,`DESCRIPTION` 
			FROM `meeting_dtls` WHERE `meeting_id` = %s""",(meeting_id))

		meetingDtls = curLog.fetchone()
		message = 'Invalid MeetingID'
		meetingTime = 'Meeting Updated'
		result = ''
		postStatus = 0
		if meetingDtls:


			if not description:
				description = meetingDtls.get('DESCRIPTION')

			if not subject:
				subject = meetingDtls.get('SUBJECT')

			if not end_time:
				end_time = meetingDtls.get('END_DATE')

			if not start_time:
				start_time = meetingDtls.get('START_DATE')

			else:
				start_date = start_time.replace(' ','T')
				curLog.execute("""SELECT `user_mailid`,`zoom_api_key`,`webex_pwd`,`webex_sitename`, 
					`platform` FROM `zoom_user_details` WHERE `user_id` = %s""",(teacher_id))

				teacherDtls = curLog.fetchone()
				if teacherDtls:
					if teacherDtls.get('platform') == 'zoom':
						mailId = teacherDtls.get('user_mailid')
						apiKey = teacherDtls.get('zoom_api_key')
						headers = {'Content-Type':'application/json','authorization': 'Bearer ' + apiKey}
						createUrl = 'https://api.zoom.us/v2/meetings/{meetingId}'.format(meetingId=zoom_meeting_id)
						zoom_payload = {"topic": subject,
										"type": 2,
										"start_time": start_date,
										"duration": 40,
										"timezone": "Asia/Calcutta",
										"password": "",
										"agenda": description,
										"settings": {
											"host_video": "true",
											"participant_video": "false",
											"join_before_host": "true",
											"mute_upon_entry": "true",
											"watermark": "true",
											"use_pmi": "false",
											"approval_type": "2",
											"registration_type": "1",
											"audio": "both",
											"auto_recording": "local"
											}
										}

						postRequest = requests.patch(createUrl, data=json.dumps(zoom_payload), headers=headers)
						postStatus = postRequest.status_code
						# print(postRequest.content)
					elif teacherDtls.get('platform') == 'webex':
						# startDate = start_time.strftime('%m/%d/%Y %H:%M:%S')
						startDate = datetime.strptime(start_time,'%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %H:%M:%S')
						# startDate = '04/30/2020 12:00:00'
						webexId = teacherDtls.get('user_mailid')
						webexPwd = teacherDtls.get('webex_pwd')
						siteName = teacherDtls.get('webex_sitename')
						requestXML = '''<?xml version="1.0" encoding="UTF-8"?>
										<serv:message
											xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
											xmlns:serv="http://www.webex.com/schemas/2002/06/service">
											<header>
												<securityContext>
													<siteName>{siteName}</siteName>
													<webExID>{webexId}</webExID>
													<password>{webexPwd}</password>
												</securityContext>
											</header>
											<body>
												<bodyContent
													xsi:type="java:com.webex.service.binding.meeting.SetMeeting">
													<metaData>
														<confName>{subject}</confName>
														<!--<meetingType>-1</meetingType>-->
														<agenda>{description}</agenda>
													</metaData>
													<enableOptions>
														<chat>true</chat>
														<poll>true</poll>
														<audioVideo>true</audioVideo>
														<supportE2E>TRUE</supportE2E>
														<autoRecord>TRUE</autoRecord>
													</enableOptions>
													<schedule>
														<startDate>{startDate}</startDate>
														<joinTeleconfBeforeHost>false</joinTeleconfBeforeHost>
														<duration>40</duration>
														<timeZoneID>41</timeZoneID>
													</schedule>
													<telephony>
														<telephonySupport>CALLIN</telephonySupport>
														<extTelephonyDescription>
															Call 1-800-555-1234, Passcode 98765
														</extTelephonyDescription>
													</telephony>
													<meetingkey>{meetingKey}</meetingkey>
												</bodyContent>
											</body>
										</serv:message>'''.format(siteName=siteName,webexId=webexId,
											 webexPwd=webexPwd,subject=subject,description=description,
											 startDate=startDate,meetingKey=zoom_meeting_id)
						result, reason, response = sendRequest(requestXML)
						if result == 'SUCCESS':
							updateLiveClass = ("""UPDATE `liveclass_mapping` SET `webex_hosturl` = %s,
								`webex_attendeeurl` = %s WHERE `webex_meetingkey` = %s""")
							liveData = (response.get('zoom_join_url'),response.get('attendeeURL'),zoom_meeting_id)

							curLib.execute(updateLiveClass,liveData)

					if postStatus == 204 or result == 'SUCCESS':
						meetingTime = 'Meeting Schedule changed'


			meetingUpdateQuery = ("""UPDATE `meeting_dtls` SET `START_DATE` = %s, `END_DATE` = %s,
				`SUBJECT`= %s, `DESCRIPTION` = %s where `MEETING_ID` = %s""")
			liveClassUpdate = ("""UPDATE `liveclass_mapping` SET `start_date` = %s,`end_date` = %s,
				`subject` = %s,`description` = %s where `meeting_id` = %s""")
			updateData = (start_time,end_time,subject,description,meeting_id)
			curLog.execute(meetingUpdateQuery,updateData)
			curLib.execute(liveClassUpdate,updateData)

			message = 'Meeting Updated'
		connection.commit()
		conn.commit()
		curLib.close()
		curLog.close()

		return ({"attributes": {"status_desc": "Meeting Details",
								"status": "success",
								"message":message
									},
				"responseList":meetingTime}), status.HTTP_200_OK

def read_ical(hostiCal,attendeeiCal):
	from icalendar import Calendar, Event
	host = hostiCal
	attendee = attendeeiCal
	hostURL = ''
	attendeeURL = ''
	try:
		read_host = requests.get(host, stream=True)
		read_attendee = requests.get(attendee, stream=True)
		hostcal = Calendar.from_ical(read_host.raw.read())
		attendeeCal = Calendar.from_ical(read_attendee.raw.read())
		
		for component in hostcal.walk():
			if component.name == "VEVENT":
				hostURL = component.get('location')
		for component in attendeeCal.walk():
			if component.name == "VEVENT":
				attendeeURL = component.get('location')
	except:
		pass

	return hostURL, attendeeURL


def sendRequest(envelope):

	headers = { 'Content-Type': 'application/xml'}
	response = requests.post( 'https://api.webex.com/WBXService/XMLService', envelope )
	meetingRes = {}

	message = etree.fromstring( response.content )
	print(message)
	if message.find( '{*}header/{*}response/{*}result').text != 'SUCCESS':

		result = message.find( '{*}header/{*}response/{*}result').text
		reason = message.find( '{*}header/{*}response/{*}reason').text

	else:
		result = message.find( '{*}header/{*}response/{*}result').text
		reason = ''
		if message.find( '{*}body/{*}bodyContent/{*}meetingkey') is not None:
			meetingkey = message.find( '{*}body/{*}bodyContent/{*}meetingkey').text
		else:
			meetingkey = ''
		if message.find( '{*}body/{*}bodyContent/{*}meetingPassword') is not None:
			meetingPassword = message.find( '{*}body/{*}bodyContent/{*}meetingPassword').text
		else:
			meetingPassword = ''
		if message.find( '{*}body/{*}bodyContent/{*}iCalendarURL/{*}host') is not None:
			hostiCal = message.find( '{*}body/{*}bodyContent/{*}iCalendarURL/{*}host').text
		else:
			hostiCal = None
		if message.find( '{*}body/{*}bodyContent/{*}iCalendarURL/{*}attendee') is not None:
			attendeeiCal = message.find( '{*}body/{*}bodyContent/{*}iCalendarURL/{*}attendee').text
		else:
			attendeeiCal = None
		
		if hostiCal and attendeeiCal:
			hostURL, attendeeURL = read_ical(hostiCal,attendeeiCal)
		else:
			hostURL, attendeeURL = ('','')
		# meetingRes = {"meetingkey":meetingkey,
		# 				"meetingPassword":meetingPassword,
		# 				"hostURL":hostURL,
		# 				"attendeeURL":attendeeURL
		# 				}

		meetingRes = {"zoom_meeting_id":meetingkey,
						"zoom_uuid":meetingPassword,
						"zoom_join_url":hostURL,
						"attendeeURL":attendeeURL
						}
	return (result,reason,meetingRes)


@name_space.route("/createWebexMeeting")
class createWebexMeeting(Resource):
	@api.expect(create_meeting)
	def post(self):

		details = request.get_json()
		meeting_id = details.get('meeting_id')
		is_webinar = details.get('is_webinar',0)
		connection = connnect_userLibrary()
		curLib = connection.cursor()
		response = {}
		result = 'failure'
		reason = ''
		conn = connect_logindb()
		curLog = conn.cursor()

		curLog.execute("""SELECT `INSTITUTION_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,`LOCATION`,
			`SUBJECT`,`DESCRIPTION` FROM `meeting_dtls` WHERE `meeting_id` = %s""",(meeting_id))

		meetingDtls = curLog.fetchone()
		message = 'Invalid MeetingID'

		if meetingDtls:
			institution_id = meetingDtls.get('INSTITUTION_ID')
			teacher_id = meetingDtls.get('TEACHER_ID')
			start_time = meetingDtls.get('START_DATE')
			end_time = meetingDtls.get('END_DATE')
			description = meetingDtls.get('DESCRIPTION')
			subject = meetingDtls.get('SUBJECT')
			startDate = start_time.strftime('%m/%d/%Y %H:%M:%S')
			# startDate = '04/17/2020 17:00:00'
			# print(startDate)
			curLog.execute("""SELECT `user_mailid`,`webex_pwd`,`webex_sitename` 
				FROM `zoom_user_details` WHERE `user_id` =  %s""",(teacher_id))

			teacherDtls = curLog.fetchone()
			if teacherDtls:

				webexId = teacherDtls.get('user_mailid')
				webexPwd = teacherDtls.get('webex_pwd')
				siteName = teacherDtls.get('webex_sitename')

				requestXML = '''<?xml version="1.0" encoding="UTF-8"?>
						        <serv:message xmlns:serv="http://www.webex.com/schemas/2002/06/service"
						            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
						            <header>
						                <securityContext>
						                    <siteName>{siteName}</siteName>
						                    <webExID>{webexId}</webExID>
						                    <password>{webexPwd}</password>  
						                </securityContext>
						            </header>
						            <body>
						                <bodyContent
						                    xsi:type="java:com.webex.service.binding.meeting.CreateMeeting">
						                    <accessControl>
						                        <meetingPassword></meetingPassword>
						                    </accessControl>
						                    <metaData>
						                        <confName>{subject}</confName>
						                        <meetingType>0</meetingType>
						                        <agenda>{description}</agenda>
						                    </metaData>
						                    <enableOptions>
						                        <chat>true</chat>
						                        <poll>true</poll>
						                        <audioVideo>true</audioVideo>
						                        <supportE2E>TRUE</supportE2E>
						                        <autoRecord>TRUE</autoRecord>
						                    </enableOptions>
						                    <schedule>
						                        <startDate>{startDate}</startDate>
						                        <joinTeleconfBeforeHost>false</joinTeleconfBeforeHost>
						                        <duration>40</duration>
						                        <timeZoneID>41</timeZoneID>
						                    </schedule>
						                    <telephony>
						                        <telephonySupport>CALLIN</telephonySupport>
						                        <extTelephonyDescription>
						                            Call 1-800-555-1234, Passcode 98765
						                        </extTelephonyDescription>
						                    </telephony>
						                </bodyContent>
						            </body>
						        </serv:message>'''.format(siteName=siteName,webexId=webexId,webexPwd=webexPwd,
						        	subject=subject,description=description,startDate=startDate)
				result, reason, response = sendRequest(requestXML)

				if result == 'SUCCESS':

					webexInsertQuery = ("""INSERT INTO `liveclass_mapping`( `meeting_id`, `webex_meetingkey`, 
						`webex_hosturl`, `webex_attendeeurl`, `webex_meeting_pwd`, `teacher_id`, 
						`institution_id`, `platform`, `start_date`,`end_date`,`location`,
						`subject`,`description`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

					webexData = (meeting_id,response.get('zoom_meeting_id'),response.get('zoom_join_url'),
						response.get('attendeeURL'),response.get('zoom_uuid'),teacher_id,
						institution_id,'webex',meetingDtls.get('START_DATE'),meetingDtls.get('END_DATE'),
						meetingDtls.get('LOCATION'),meetingDtls.get('SUBJECT'),
						meetingDtls.get('DESCRIPTION'))

					curLib.execute(webexInsertQuery,webexData)
					liveclass_id = curLib.lastrowid

					liveclass_tracking_query = ("""INSERT INTO `student_liveclass_tracking`(
						`Student_ID`, `liveclass_id`,`Status`) VALUES (%s,%s,%s)""")

					liveclass_tracking_data = (teacher_id,liveclass_id,'scheduled')

					curLib.execute(liveclass_tracking_query,liveclass_tracking_data)
					if is_webinar:
						qrCodeURL = webinar_qrcode.generateQRCode(liveclass_id,response.get('attendeeURL'),teacher_id)
					else:
						qrCodeURL = ''
					response['qrCodeURL'] = qrCodeURL
					sendrReq = (meeting_id,meetingDtls,liveclass_id,'webex')
					thread_a = Compute(sendrReq,'createZoomMeeting')
					thread_a.start()

				response.pop('attendeeURL',None)
		connection.commit()
		conn.commit()
		curLib.close()
		curLog.close()

		return ({"attributes": {"status_desc": "Meeting Details",
								"status": "success",
								"message":result + ' in creating webex meeeting. ' + reason,
								"platform":'webex',
								"is_webinar":is_webinar
									},
				"responseList":response}), status.HTTP_200_OK


@name_space.route("/scheduleLiveClass")
class scheduleLiveClass(Resource):
	@api.expect(create_meeting)
	def post(self):

		details = request.get_json()
		meeting_id = details.get('meeting_id')

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()

		meetingRes = {}
		curLog.execute("""SELECT `INSTITUTION_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,`LOCATION`,
			`SUBJECT`,`DESCRIPTION` FROM `meeting_dtls` WHERE `meeting_id` = %s""",(meeting_id))

		meetingDtls = curLog.fetchone()
		message = 'Invalid MeetingID'
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		if meetingDtls:
			curLog.execute("""SELECT `platform` FROM `zoom_user_details` 
				WHERE `user_id` = %s""",(meetingDtls.get('TEACHER_ID')))

			platformDtls = curLog.fetchone()

			if platformDtls:
				platform = platformDtls.get('platform')

				if platform == 'zoom':

					createZoomURL = BASE_URL + 'live_classes/liveClassesController/createZoomMeeting'
					
					meetingRes = requests.post(createZoomURL, data = json.dumps(details), headers = headers).json()

				elif platform == 'webex':

					createWebexURL = BASE_URL + 'live_classes/liveClassesController/createWebexMeeting'

					meetingRes = requests.post(createWebexURL, data = json.dumps(details), headers = headers).json()
			
				elif platform == 'google':

					createGoogleURL = BASE_URL + 'live_classes/liveClassesController/createGoogleMeeting'

					meetingRes = requests.post(createGoogleURL, data = json.dumps(details), headers = headers).json()

				elif platform == 'safemeet':

					createSafemeetURL = BASE_URL + 'live_classes/liveClassesController/createSafeMeeting'

					meetingRes = requests.post(createSafemeetURL, data = json.dumps(details), headers = headers).json()

			else:
				platformInsert = ("""INSERT INTO `zoom_user_details`(`user_id`, `platform`) VALUES (%s,%s)""")
				platformData = (meetingDtls.get('TEACHER_ID'),'google')
				curLog.execute(platformInsert,platformData)
				conn.commit()

				createGoogleURL = BASE_URL + 'live_classes/liveClassesController/createGoogleMeeting'

				meetingRes = requests.post(createGoogleURL, data = json.dumps(details), headers = headers).json()
			curLib.close()
			curLog.close()
			return meetingRes
		else:
			curLib.close()
			curLog.close()
			return ({"attributes": {"status_desc": "Meeting Details",
									"status": "success",
									"message":message,
										},
						"responseList":response}), status.HTTP_200_OK


@name_space.route("/getLiveClassDownloadListforStudents/<int:institution_id>/<int:student_id>")
class getLiveClassDownloadListforStudents(Resource):
	def get(self,institution_id,student_id):

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()

		curLib.execute("""SELECT `liveclass_id`,`meeting_id`,`zoom_meeting_id`,`zoom_uuid`,`zoom_join_url` 
			FROM `liveclass_mapping` WHERE `institution_id` = %s and `meeting_status` = 'created'""",(institution_id))

		zoomDtls = curLib.fetchall()
		meetList = []
		if zoomDtls:
			for zid, zoom in enumerate(zoomDtls):
				curLog.execute("""SELECT md.`MEETING_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,`LOCATION`,
					`SUBJECT`,`DESCRIPTION`,`MEETING_GROUP`,`MEETING_GROUP_ID` FROM 
					`meeting_dtls` md INNER JOIN `notification_tracking_dtls` ntd 
					on md.`MEETING_ID` = ntd.`MEETING_ID` WHERE `INSTITUTION_ID` = %s 
					and md.`MEETING_ID` = %s and date(`START_DATE`) = CURRENT_DATE""",(institution_id,zoom['meeting_id']))


				meetingDtls = curLog.fetchall()

				
				if meetingDtls:

					curLib.execute("""SELECT `content_id`,`content_name`,`content_filepath`,`content_filename`,
						`content_filetype` FROM `content_library` WHERE 
						`content_id` in(SELECT `content_id` FROM `content_liveclass_mapping` 
						WHERE `liveclass_id` = %s) and `content_name` not 
						in ('prelive-Dummy','postlive-Dummy')""",(zoom['liveclass_id']))

					contentDtls = curLib.fetchall()
					contentFlag = 'N'
					if contentDtls:
						contentFlag = 'Y'

					for mid,meet in enumerate(meetingDtls):
						if meet['MEETING_GROUP'] == 'I':
							if meet['MEETING_GROUP_ID'] == student_id:
								meet.pop('MEETING_GROUP')
								meet.pop('MEETING_GROUP_ID')
								meet['START_DATE'] = meet.get('START_DATE').isoformat()
								meet['END_DATE'] = meet.get('END_DATE').isoformat()
								meet['zoom_meeting_id'] = zoom.get('zoom_meeting_id')
								meet['zoom_uuid'] = zoom.get('zoom_uuid')
								meet['zoom_join_url'] = zoom.get('zoom_join_url')
								meet['contentDtls'] = contentDtls
								meet['liveclass_id'] = zoom['liveclass_id']
								meetList.append(meet)
						else:
							curLog.execute("""SELECT `Student_Id` FROM `group_student_mapping`
							WHERE `Group_ID` = %s""",(meet['MEETING_GROUP_ID']))

							grpDtls = curLog.fetchall()

							for sid in grpDtls:
								if sid['Student_Id'] == student_id:
									meet.pop('MEETING_GROUP')
									meet.pop('MEETING_GROUP_ID')
									meet['START_DATE'] = meet.get('START_DATE').isoformat()
									meet['END_DATE'] = meet.get('END_DATE').isoformat()
									meet['zoom_meeting_id'] = zoom.get('zoom_meeting_id')
									meet['zoom_uuid'] = zoom.get('zoom_uuid')
									meet['zoom_join_url'] = zoom.get('zoom_join_url')
									meet['contentDtls'] = contentDtls
									meet['liveclass_id'] = zoom['liveclass_id']
									meetList.append(meet)

		meetList = sorted(meetList, key = lambda i: i['START_DATE']) 
		return ({"attributes": {"status_desc": "Meeting Schedule Details",
								"status": "success"
									},
				"responseList":meetList}), status.HTTP_200_OK


@name_space.route("/deleteLiveClass/<int:meeting_id>/<int:teacher_id>")
class deleteLiveClass(Resource):
	def put(self,meeting_id,teacher_id):

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()
		msg = 'Class could not be cancelled'
		
		curLib.execute("""SELECT `liveclass_id`,`zoom_meeting_id`,`webex_meetingkey`,`platform` 
			FROM `liveclass_mapping` WHERE `meeting_id` = %s and `meeting_status` = 'created'""",(meeting_id))

		curLog.execute("""SELECT `user_mailid`,`zoom_api_key`,`webex_pwd`,`webex_sitename` 
			FROM `zoom_user_details` WHERE `user_id` = %s""",(teacher_id))

		teacherDtls = curLog.fetchone()

		meetingDtls = curLib.fetchone()
		if meetingDtls:
			postStatus = 0
			result = ''
			if meetingDtls.get('platform') == 'zoom':
				meet_id = meetingDtls.get('zoom_meeting_id')
				if teacherDtls:
					mailId = teacherDtls.get('user_mailid')
					apiKey = teacherDtls.get('zoom_api_key')
					headers = {'Content-Type':'application/json','authorization': 'Bearer ' + apiKey}
					deleteUrl = 'https://api.zoom.us/v2/meetings/{meetingId}'.format(meetingId=meet_id)
					postRequest = requests.delete(deleteUrl, headers=headers)
					postStatus = postRequest.status_code
					# print(postStatus)
					# print(postRequest.content)
					
			elif meetingDtls.get('platform') == 'webex':
				meet_id = meetingDtls.get('webex_meetingkey')
				if teacherDtls:
					webexId = teacherDtls.get('user_mailid')
					webexPwd = teacherDtls.get('webex_pwd')
					siteName = teacherDtls.get('webex_sitename')
					requestXML = '''<?xml version="1.0" encoding="UTF-8"?>
									<serv:message 
										xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
										<header>
											<securityContext>
												<siteName>{siteName}</siteName>
												<webExID>{webexId}</webExID>
												<password>{webexPwd}</password>  
											</securityContext>
										</header>
										<body>
											<bodyContent
												xsi:type="java:com.webex.service.binding.meeting.DelMeeting">
												<meetingKey>{meet_id}</meetingKey>
											</bodyContent>
										</body>
									</serv:message>'''.format(siteName=siteName,webexId=webexId,
										 webexPwd=webexPwd,meet_id=meet_id)
					result, reason, response = sendRequest(requestXML)
					print(result)
			if postStatus == 204 or result == 'SUCCESS':
				delLiveClassQuery = ("""UPDATE `liveclass_mapping` SET `meeting_status` = %s 
					where `liveclass_id` = %s""")

				delData = ('deleted',meetingDtls.get('liveclass_id'))
				curLib.execute(delLiveClassQuery,delData)
				msg = 'Class Cancelled'
		connection.commit()
		curLib.close()
		curLog.close()
		return ({"attributes": {"status_desc": "Meeting Details",
								"status": "success"
									},
				"responseList":msg}), status.HTTP_200_OK


@name_space.route("/createGoogleMeeting")
class createGoogleMeeting(Resource):
	@api.expect(create_meeting)
	def post(self):
		details = request.get_json()
		meeting_id = details.get('meeting_id')
		google_meet_url = details.get('google_meet_url')
		is_webinar = details.get('is_webinar',0)
		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()
		res = {}
		
		curLog.execute("""SELECT `INSTITUTION_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,`LOCATION`,
			`SUBJECT`,`DESCRIPTION` FROM `meeting_dtls` WHERE `meeting_id` = %s""",(meeting_id))

		meetingDtls = curLog.fetchone()
		message = 'Invalid MeetingID'
		createMeetingQuery = ("""INSERT INTO `liveclass_mapping`(`meeting_id`, 
				`google_meet_url`,`teacher_id`,`institution_id`,
				`platform`, `start_date`,`end_date`,`location`,
				`subject`,`description`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		meetingData = (meeting_id,google_meet_url,meetingDtls.get('TEACHER_ID'),
			meetingDtls.get('INSTITUTION_ID'),'google',meetingDtls.get('START_DATE'),meetingDtls.get('END_DATE'),
			meetingDtls.get('LOCATION'),meetingDtls.get('SUBJECT'),
			meetingDtls.get('DESCRIPTION'))

		curLib.execute(createMeetingQuery,meetingData)
		liveclass_id = curLib.lastrowid

		liveclass_tracking_query = ("""INSERT INTO `student_liveclass_tracking`(
						`Student_ID`, `liveclass_id`,`Status`) VALUES (%s,%s,%s)""")

		liveclass_tracking_data = (meetingDtls.get('TEACHER_ID'),liveclass_id,'scheduled')

		curLib.execute(liveclass_tracking_query,liveclass_tracking_data)
		
		if is_webinar:
			qrCodeURL = webinar_qrcode.generateQRCode(liveclass_id,google_meet_url,meetingDtls.get('TEACHER_ID'))
		else:
			qrCodeURL = ''
		res = {'zoom_meeting_id':0,
				'zoom_uuid':"",
				'zoom_join_url':google_meet_url,
				'qrCodeURL':qrCodeURL}
		message = 'Google Meeting Scheduled Successfully'
		sendrReq = (meeting_id,meetingDtls,liveclass_id,'google')
		thread_a = Compute(sendrReq,'createGoogleMeeting')
		thread_a.start()
		
		connection.commit()
		curLib.close()
		curLog.close()

		
		return ({"attributes": {"status_desc": "Meeting Details",
								"status": "success",
								"message":message,
								"platform":'google',
								"is_webinar":is_webinar
									},
				"responseList":res}), status.HTTP_200_OK

#----------------------Create-Safe-Meeting---------------------#

@name_space.route("/createSafeMeeting")
class createSafeMeeting(Resource):
	@api.expect(create_meeting)
	def post(self):
		details = request.get_json()
		meeting_id = details.get('meeting_id')
		google_meet_url = details.get('google_meet_url')
		is_webinar = details.get('is_webinar',0)
		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()
		res = {}
		
		curLog.execute("""SELECT `INSTITUTION_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,`LOCATION`,
			`SUBJECT`,`DESCRIPTION` FROM `meeting_dtls` WHERE `meeting_id` = %s""",(meeting_id))

		meetingDtls = curLog.fetchone()
		message = 'Invalid MeetingID'
		createMeetingQuery = ("""INSERT INTO `liveclass_mapping`(`meeting_id`, 
				`safemeet_url`,`teacher_id`,`institution_id`,
				`platform`, `start_date`,`end_date`,`location`,
				`subject`,`description`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		meetingData = (meeting_id,google_meet_url,meetingDtls.get('TEACHER_ID'),
			meetingDtls.get('INSTITUTION_ID'),'safemeet',meetingDtls.get('START_DATE'),meetingDtls.get('END_DATE'),
			meetingDtls.get('LOCATION'),meetingDtls.get('SUBJECT'),
			meetingDtls.get('DESCRIPTION'))

		curLib.execute(createMeetingQuery,meetingData)
		liveclass_id = curLib.lastrowid

		liveclass_tracking_query = ("""INSERT INTO `student_liveclass_tracking`(
						`Student_ID`, `liveclass_id`,`Status`) VALUES (%s,%s,%s)""")

		liveclass_tracking_data = (meetingDtls.get('TEACHER_ID'),liveclass_id,'scheduled')

		curLib.execute(liveclass_tracking_query,liveclass_tracking_data)
		
		if is_webinar:
			qrCodeURL = webinar_qrcode.generateQRCode(liveclass_id,google_meet_url,meetingDtls.get('TEACHER_ID'))
		else:
			qrCodeURL = ''
		res = {'zoom_meeting_id':0,
				'zoom_uuid':"",
				'zoom_join_url':google_meet_url,
				'qrCodeURL':qrCodeURL}
		message = 'Safe Meeting Scheduled Successfully'
		sendrReq = (meeting_id,meetingDtls,liveclass_id,'safemeet')
		thread_a = Compute(sendrReq,'createSafeMeeting')
		thread_a.start()
		
		connection.commit()
		curLib.close()
		curLog.close()

		
		return ({"attributes": {"status_desc": "Meeting Details",
								"status": "success",
								"message":message,
								"platform":'safemeet',
								"is_webinar":is_webinar
									},
				"responseList":res}), status.HTTP_200_OK

#----------------------Create-Safe-Meeting---------------------#

@name_space.route("/getLiveClassScheduleVersion2forStudents/<int:institution_id>/<int:student_id>/<string:liveclass_status>")
class getLiveClassScheduleVersion2forStudents(Resource):
	def get(self,institution_id,student_id,liveclass_status):

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()
		meetList = []
		
		if liveclass_status.lower() == 'today':

			curLib.execute("""SELECT lsm.`liveclass_id`, lsm.`platform`, `zoom_meeting_id`, `zoom_uuid`, 
				`zoom_join_url`, `webex_meetingkey`, `webex_hosturl`, `webex_attendeeurl`, `meeting_id`,
				`webex_meeting_pwd`, `google_meet_url`, `safemeet_url`,`start_date`, `end_date`, `location`, `subject`, 
				`description`, `teacher_id`, `institution_id` FROM `liveclass_student_mapping` lsm 
				INNER JOIN `liveclass_mapping` lm ON lsm.`liveclass_id` = lm.`liveclass_id` 
				WHERE `student_id` = %s and lm.`meeting_status` = 'created'
				and date(`start_date`) = CURRENT_DATE""",(student_id))

			classList = curLib.fetchall()
		elif liveclass_status.lower() == 'upcoming':

			curLib.execute("""SELECT lsm.`liveclass_id`, lsm.`platform`, `zoom_meeting_id`, `zoom_uuid`, 
				`zoom_join_url`, `webex_meetingkey`, `webex_hosturl`, `webex_attendeeurl`, `meeting_id`,
				`webex_meeting_pwd`, `google_meet_url`, `safemeet_url`,`start_date`, `end_date`, `location`, `subject`, 
				`description`, `teacher_id`, `institution_id` FROM `liveclass_student_mapping` lsm 
				INNER JOIN `liveclass_mapping` lm ON lsm.`liveclass_id` = lm.`liveclass_id` 
				WHERE `student_id` = %s and lm.`meeting_status` = 'created'
				and date(`start_date`) > CURRENT_DATE""",(student_id))

			classList = curLib.fetchall()
		elif liveclass_status.lower() == 'completed':

			curLib.execute("""SELECT lsm.`liveclass_id`, lsm.`platform`, `zoom_meeting_id`, `zoom_uuid`, 
				`zoom_join_url`, `webex_meetingkey`, `webex_hosturl`, `webex_attendeeurl`, `meeting_id`,
				`webex_meeting_pwd`, `google_meet_url`,`safemeet_url`,`start_date`, `end_date`, `location`, `subject`, 
				`description`, `teacher_id`, `institution_id` FROM `liveclass_student_mapping` lsm 
				INNER JOIN `liveclass_mapping` lm ON lsm.`liveclass_id` = lm.`liveclass_id` 
				WHERE `student_id` = %s and lm.`meeting_status` = 'created'
				and date(`start_date`) < CURRENT_DATE""",(student_id))

			classList = curLib.fetchall()
		else:
			curLib.execute("""SELECT lsm.`liveclass_id`, lsm.`platform`, `zoom_meeting_id`, `zoom_uuid`, 
				`zoom_join_url`, `webex_meetingkey`, `webex_hosturl`, `webex_attendeeurl`, `meeting_id`,
				`webex_meeting_pwd`, `google_meet_url`, `safemeet_url`, `start_date`, `end_date`, `location`, `subject`, 
				`description`, `teacher_id`, `institution_id` FROM `liveclass_student_mapping` lsm 
				INNER JOIN `liveclass_mapping` lm ON lsm.`liveclass_id` = lm.`liveclass_id` 
				WHERE `student_id` = %s and lm.`meeting_status` = 'created'""",(student_id))

			classList = curLib.fetchall()
		

		if classList:
			for cid, clas in enumerate(classList):
				curLib.execute("""SELECT `content_id` FROM `content_library` WHERE 
					`content_id` in(SELECT `content_id` FROM `content_liveclass_mapping` 
					WHERE `liveclass_id` = %s) and `content_name` in 
					('prelive-Dummy','postlive-Dummy') limit 1""",(clas['liveclass_id']))

				assessmentDtls = curLib.fetchone()
				assessmentFlag = 'N'
				if assessmentDtls:
					assessmentFlag = 'Y'

				curLib.execute("""SELECT `content_id` FROM `content_library` WHERE 
					`content_id` in(SELECT `content_id` FROM `content_liveclass_mapping` 
					WHERE `liveclass_id` = %s) and `content_name` not in 
					('prelive-Dummy','postlive-Dummy') limit 1""",(clas['liveclass_id']))

				contentDtls = curLib.fetchone()
				contentFlag = 'N'
				if contentDtls:
					contentFlag = 'Y'
				meetingDtls = {}
				curLog.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as name
					FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID`=%s""",
					(clas.get('teacher_id')))

				teachername = curLog.fetchone()
				meetingDtls['Teachername'] = teachername.get('name')

				curLib.execute("""SELECT `Student_ID`,`liveclass_id`,`Status` 
					FROM `student_liveclass_tracking` WHERE `Student_ID`=%s
					and liveclass_id=%s""",
					(meetingDtls.get('teacher_id'),clas.get('liveclass_id')))

				teacherclassDtls = curLib.fetchone()
				if teacherclassDtls:
					meetingDtls['class_start'] = teacherclassDtls.get('Status')
				else:
					meetingDtls['class_start'] = 'scheduled'

				meetingDtls['TEACHER_ID'] = clas.get('teacher_id')
				meetingDtls['DESCRIPTION'] = clas.get('description')
				meetingDtls['MEETING_ID'] = clas.get('meeting_id')
				meetingDtls['LOCATION'] = clas.get('location')
				meetingDtls['SUBJECT'] = clas.get('subject')
				meetingDtls['START_DATE'] = clas['start_date'].isoformat()
				meetingDtls['END_DATE'] = clas['end_date'].isoformat()
				meetingDtls['assessmentFlag'] = assessmentFlag
				meetingDtls['contentFlag'] = contentFlag
				meetingDtls['liveclass_id'] = clas.get('liveclass_id')
				meetingDtls['platform'] = clas.get('platform')

				if clas.get('platform') == 'zoom':
					
					
					meetingDtls['zoom_meeting_id'] = clas.get('zoom_meeting_id')
					meetingDtls['zoom_uuid'] = clas.get('zoom_uuid')
					meetingDtls['zoom_join_url'] = clas.get('zoom_join_url')
					meetList.append(meetingDtls)

				elif clas.get('platform') == 'webex':
					
					meetingDtls['zoom_meeting_id'] = clas.get('webex_meetingkey')
					meetingDtls['webex_meeting_pwd'] = clas.get('webex_meeting_pwd')
					meetingDtls['zoom_join_url'] = clas.get('webex_attendeeurl')
					meetingDtls['webex_attendeeurl'] = clas.get('webex_attendeeurl')
					meetList.append(meetingDtls)

				elif clas.get('platform') == 'google':
	
					meetingDtls['zoom_meeting_id'] = ""
					meetingDtls['zoom_uuid'] = ""
					meetingDtls['zoom_join_url'] = clas.get('google_meet_url')
					meetList.append(meetingDtls)

				elif clas.get('platform') == 'safemeet':
	
					meetingDtls['zoom_meeting_id'] = ""
					meetingDtls['zoom_uuid'] = ""
					meetingDtls['zoom_join_url'] = clas.get('safemeet_url')
					meetList.append(meetingDtls)

		meetList = sorted(meetList, key = lambda i: i['START_DATE']) 
		return ({"attributes": {"status_desc": "Meeting Schedule Details",
								"status": "success"
									},
				"responseList":meetList}), status.HTTP_200_OK



@name_space.route("/updateScheduledLiveClassMeetingStatus/<int:liveclass_id>/<int:student_id>/<string:meeting_status>")
class updateScheduledLiveClassMeetingStatus(Resource):
	@api.expect()
	def put(self,liveclass_id,student_id,meeting_status):
		connection = connnect_userLibrary()
		curLib = connection.cursor()
		res = []
		# curLib.execute("""SELECT `liveclass_id` FROM `liveclass_student_mapping` WHERE 
		# 	`liveclass_id`=%s and `student_id`=%s""",(liveclass_id,student_id))
		# liveclassid = curLib.fetchone()
		# liveid = liveclassid['liveclass_id']

		update_meetingStatus = ("""UPDATE `student_liveclass_tracking` SET `Status` = %s 
			WHERE `Student_ID` = %s AND `liveclass_id` = %s""")
		update_meetingStatusdata =(meeting_status,student_id,liveclass_id)
		curLib.execute(update_meetingStatus,update_meetingStatusdata)

		res = [{'liveclass_id':liveclass_id,
				'student_id':student_id,
				'meeting_status':meeting_status
			}]
		connection.commit()
		curLib.close()

		return ({"attributes": {"status_desc": "Meeting Status",
								"status": "success"
									},
				"responseList":res}), status.HTTP_200_OK

		
@name_space.route("/getLiveClassScheduleforTeacher/v2/<int:teacher_id>/<string:liveclass_status>/<int:institution_id>")
class getScheduleLiveClassforTeacherV2(Resource):
	def get(self,teacher_id,liveclass_status,institution_id):

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		conn = connect_logindb()
		curLog = conn.cursor()
		if liveclass_status == 'today':
			curLib.execute("""SELECT lm.`liveclass_id`, lm.`platform`, `zoom_meeting_id`, `zoom_uuid`, 
				`zoom_join_url`, `webex_meetingkey`, `webex_hosturl`, `webex_attendeeurl`, 
				`meeting_id`, `webex_meeting_pwd`, `google_meet_url`, `safemeet_url`,`start_date`, `end_date`, 
				`location`, `subject`, `description`, `teacher_id`, `institution_id`,is_webinar,webinar_qrcode 
				FROM `liveclass_mapping` lm WHERE `teacher_id` = %s 
				and lm.`meeting_status` = 'created' and date(`start_date`) = CURRENT_DATE""",(teacher_id))

			classList = curLib.fetchall()
		elif liveclass_status == 'upcoming':
			curLib.execute("""SELECT lm.`liveclass_id`, lm.`platform`, `zoom_meeting_id`, `zoom_uuid`, 
				`zoom_join_url`, `webex_meetingkey`, `webex_hosturl`, `webex_attendeeurl`, 
				`meeting_id`, `webex_meeting_pwd`, `google_meet_url`,`safemeet_url`, `start_date`, `end_date`, 
				`location`, `subject`, `description`, `teacher_id`, `institution_id`,is_webinar,webinar_qrcode 
				FROM `liveclass_mapping` lm WHERE `teacher_id` = %s 
				and lm.`meeting_status` = 'created' and date(`start_date`) > CURRENT_DATE""",(teacher_id))

			classList = curLib.fetchall()
		elif liveclass_status == 'completed':
			curLib.execute("""SELECT lm.`liveclass_id`, lm.`platform`, `zoom_meeting_id`, `zoom_uuid`, 
				`zoom_join_url`, `webex_meetingkey`, `webex_hosturl`, `webex_attendeeurl`, 
				`meeting_id`, `webex_meeting_pwd`, `google_meet_url`, `safemeet_url`,`start_date`, `end_date`, 
				`location`, `subject`, `description`, `teacher_id`, `institution_id`,is_webinar,webinar_qrcode
				FROM `liveclass_mapping` lm WHERE `teacher_id` = %s 
				and lm.`meeting_status` = 'created' and date(`start_date`) < CURRENT_DATE""",(teacher_id))

			classList = curLib.fetchall()
		else:
			curLib.execute("""SELECT lm.`liveclass_id`, lm.`platform`, `zoom_meeting_id`, `zoom_uuid`, 
				`zoom_join_url`, `webex_meetingkey`, `webex_hosturl`, `safemeet_url`,`webex_attendeeurl`, 
				`meeting_id`, `webex_meeting_pwd`, `google_meet_url`, `start_date`, `end_date`, 
				`location`, `subject`, `description`, `teacher_id`, `institution_id`,is_webinar,webinar_qrcode 
				FROM `liveclass_mapping` lm WHERE `teacher_id` = %s 
				and lm.`meeting_status` = 'created'""",(teacher_id))

			classList = curLib.fetchall()
		
		meetList = []
		if classList:
			for cid, clas in enumerate(classList):
				meetingDtls = {}
				curLib.execute("""SELECT `Student_ID`,`liveclass_id`,`Status` 
					FROM `student_liveclass_tracking` WHERE `Student_ID`=%s
					and liveclass_id=%s""",
					(teacher_id,clas.get('liveclass_id')))

				teacherclassDtls = curLib.fetchone()
				if teacherclassDtls:
					meetingDtls['class_start'] = teacherclassDtls.get('Status')
				else:
					meetingDtls['class_start'] = 'scheduled'
				meetingDtls['START_DATE'] = clas.get('start_date').isoformat()
				meetingDtls['END_DATE'] = clas.get('end_date').isoformat()
				meetingDtls['LOCATION'] = clas.get('location')
				meetingDtls['Topic'] = clas.get('subject')
				meetingDtls['Description'] = clas.get('description')
				meetingDtls['teacher_id'] = teacher_id
				meetingDtls['liveclass_id'] = clas.get('liveclass_id')
				meetingDtls['meeting_id'] = clas.get('meeting_id')	
				meetingDtls['platform'] = clas.get('platform')

				if clas.get('platform') == 'zoom':
					
					meetingDtls['zoom_join_url'] = clas.get('zoom_join_url')
					meetingDtls['zoom_meeting_id'] = clas.get('zoom_meeting_id')
					meetList.append(meetingDtls)
				
				if clas.get('platform') == 'webex':
					
					meetingDtls['webex_attendeeurl'] = clas.get('webex_attendeeurl')
					meetingDtls['webex_meeting_pwd'] = clas.get('webex_meeting_pwd')
					meetingDtls['zoom_join_url'] = clas.get('webex_hosturl')
					meetingDtls['zoom_meeting_id'] = clas.get('webex_meetingkey')	
					meetList.append(meetingDtls)

				elif clas.get('platform') == 'google':
	
					meetingDtls['zoom_join_url'] = clas.get('google_meet_url')
					meetingDtls['zoom_meeting_id'] = ""
					meetList.append(meetingDtls)

				elif clas.get('platform') == 'safemeet':
	
					meetingDtls['zoom_join_url'] = clas.get('safemeet_url')
					meetingDtls['zoom_meeting_id'] = ""
					meetList.append(meetingDtls)
		curLib.close()
		curLog.close()

		return ({"attributes": {"status_desc": "Meeting Schedule Details",
								"status": "success"
									},
				"responseList":meetList}), status.HTTP_200_OK




if __name__ == '__main__':
	app.run()
