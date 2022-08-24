import requests
import pymysql
import json
import utils
from datetime import datetime,timedelta,date

def connnect_userLibrary():
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
	return connection

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'
def sendLiveClassNotification():
	conn = connect_logindb()
	curLog = conn.cursor()
	studentList = []
	appResponse = []
	url = BASE_URL + 'app_notify/AppCommunicationAPI/appMessage'
	headers = {'Content-type':'application/json', 'Accept':'application/json'}

	curLog.execute("""SELECT `MEETING_ID`,`INSTITUTION_ID`,`TEACHER_ID`,`START_DATE`,`END_DATE`,
		`LOCATION`,`SUBJECT`,`DESCRIPTION` FROM `meeting_dtls` WHERE `START_DATE` BETWEEN NOW() 
		and DATE_ADD(NOW() , INTERVAL 10 MINUTE) and `CREATED_BY_ID` = 'zoom'""")

	meetingDtls = curLog.fetchall()

	for mid, meet in enumerate(meetingDtls):
		
		curLog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
		`image_url` as teacher_image FROM `institution_user_credential` 
		WHERE `INSTITUTION_USER_ID` = %s""",(meet.get('TEACHER_ID')))
		teacher = curLog.fetchone()

		if teacher:
			teacher_name = teacher['name']
		else:
			teacher_name = 'ELSA'


		tdata = {'appParams': {},
				'mailParams': {"username":teacher_name,
									"liveclass":meet.get('DESCRIPTION'),
									"startdate":meet.get('START_DATE').isoformat().replace('T',' '),
									},
				'role': 'TA',
				'toMail': '',
				'toNumber': '',
				'userId': meet.get('TEACHER_ID'),
				'sourceapp': 'LCREM0T1'
				}
		appResponse.append((requests.post(url, data=json.dumps(tdata), headers=headers)).json())
		liveclassDtls = utils.getLiveClassIdByMeetingId(meet.get('MEETING_ID'))

		for lid, live in enumerate(liveclassDtls):
			studentList = utils.getStudentListByLiveClassId(live)
			
			for sid in studentList:
				curLog.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name 
					FROM `institution_user_credential` WHERE `INSTITUTION_USER_ID` = %s""",(sid))
				student = curLog.fetchone()

				
				if student:
					student_name = student['name']
					sdata = {'appParams': {},
							'mailParams': {"username":student_name,
												"liveclass":meet.get('DESCRIPTION'),
												"startdate":meet.get('START_DATE').isoformat().replace('T',' '),
												"teachername":teacher_name},
							'role': 'S1',
							'toMail': '',
							'toNumber': '',
							'userId': sid,
							'sourceapp': 'LCREM0S1'
							}
					
					appResponse.append(requests.post(url, data=json.dumps(sdata), headers=headers).json())
	print(appResponse)
	return appResponse

sendLiveClassNotification()