import requests
import pymysql
import time
from lxml import etree
from threading import Thread
import utils
import configparser
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields


app = Flask(__name__)
cors = CORS(app)
voicechat_section = Blueprint('voicechat_section_api', __name__)
api = Api(voicechat_section,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('voiceChatController',description='Voicechat Section')


'''def connect_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_logindb',
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



create_voice_session = api.model('create_voice_session', {
	"teacher_id":fields.Integer(required=True),
	"group_id":fields.Integer(required=True),
	"institution_id":fields.Integer(required=True),
	"status":fields.String(),
	"session_description":fields.String()
	})

send_voice_note = api.model('send_voice_note', {
	"user_id":fields.Integer(required=True),
	"session_id":fields.Integer(required=True),
	"audio_filepath":fields.String(),
	"filetype":fields.String()
	})

def appnotify(teacher_id,sessionDesc,teachername,sessionId):
	connection = connect_logindb()
	cursor = connection.cursor()
	
	url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/app_notify/AppCommunicationAPI/appMessage'
	headers = {'Content-type':'application/json', 'Accept':'application/json'}
	data ={
            "appParams": {},
            "userId": teacher_id,
            "sourceapp": "VCSCRET1",
            "toMail": "",
            "role": "T1",
            "toNumber": 0,
            "mailParams": {"vcname":sessionDesc}
            }
	response = requests.post(url, data=json.dumps(data), headers=headers).json()
    
	cursor.execute("""SELECT distinct(`student_id`) FROM `voicechat_student_mapping` WHERE 
    	`session_id`=%s""",(sessionId))

	studentList = cursor.fetchall()
	# print(studentList)
	for j in range(len(studentList)):
		studentid = studentList[j]['student_id']
		
		cursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as
            student_name FROM `institution_user_credential` WHERE 
            `INSTITUTION_USER_ID` =%s""",(studentid))

		studentnames = cursor.fetchone()
		if studentnames :
			studentname = studentnames['student_name']
			
			data_stu ={
			        "appParams": {},
			        "userId": studentid,
			        "sourceapp": "VCSCRES1",
			        "toMail": "",
			        "role": "S1",
			        "toNumber": 0,
			        "mailParams": {"studentname":studentname,
			        			   "vcname":sessionDesc,
			        			   "teachername":teachername}
			        }

			response_stu = requests.post(url, data=json.dumps(data_stu), headers=headers).json()
			    
	cursor.close()
	return 'success'


class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'startVoiceChatSession':
			teacher_id = self.request[0]
			sessionDesc = self.request[1]
			teachername = self.request[2]
			sessionId = self.request[3]
			appnotify(teacher_id,sessionDesc,teachername,sessionId)
		else:
			pass 

@name_space.route("/startVoiceChatSession")
class startVoiceChatSession(Resource):
	@api.expect(create_voice_session)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		details = request.get_json()
		teacher_id = details.get('teacher_id')
		group_id = details.get('group_id')
		institution_id = details.get('institution_id')
		chatStatus = details.get('status')
		if details.get('session_description') == None:
			sessionDesc = utils.getGroupNameFromGroupid(group_id)
		else:
			sessionDesc = details.get('session_description')

		cursor.execute("""SELECT `INSTITUTION_USER_ID`,concat(`FIRST_NAME`,' ',`LAST_NAME`)as
                    teachername FROM `institution_user_credential` WHERE 
                    `INSTITUTION_USER_ID` =%s""",(teacher_id))

		teacherList = cursor.fetchone()
		if teacherList != None:
		    teachername =teacherList.get('teachername')

		chatInsertQuery = ("""INSERT INTO `voicechat_session`(`teacher_id`, `group_id`, 
			`institution_id`, `status`, `session_description`) VALUES (%s,%s,%s,%s,%s)""")


		chatData = (teacher_id,group_id,institution_id,chatStatus,sessionDesc)

		cursor.execute(chatInsertQuery,chatData)

		sessionId = cursor.lastrowid
		details['session_id'] = sessionId
		details['session_description'] = sessionDesc
		groupList = [group_id]
		studentList = utils.getStudentListFromGroupid(groupList)
		studntMapInsertQuery = ("""INSERT INTO `voicechat_student_mapping`(`session_id`, 
			`student_id`) VALUES (%s,%s)""")
		for sid in studentList:
			studentData = (sessionId,sid)

			cursor.execute(studntMapInsertQuery,studentData)

		connection.commit()
		cursor.close()

		sendrReq = (teacher_id,sessionDesc,teachername,sessionId)
		thread_a = Compute(sendrReq,'startVoiceChatSession')
		thread_a.start()

		return ({"attributes": {"status_desc": "Voice Chat Details",
								"status": "success",
									},
				"responseList":details}), status.HTTP_200_OK



def appnotifyaudio(user_id,session_id,audio_filepath):
	connection = connect_logindb()
	cursor = connection.cursor()
	
	url = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/app_notify/AppCommunicationAPI/appMessage'
	headers = {'Content-type':'application/json', 'Accept':'application/json'}
	
	cursor.execute("""SELECT `teacher_id` FROM `voicechat_session` WHERE `session_id`=%s""",
		(session_id))
	teacher = cursor.fetchone()
	if teacher :
		teacherid = teacher.get('teacher_id')
		# print(teacherid)
	if 	user_id == teacherid:
		cursor.execute("""SELECT distinct(`student_id`) FROM `voicechat_student_mapping` WHERE 
	    	`session_id`=%s""",(session_id))

		studentList = cursor.fetchall()
		# print(studentList)
		for j in range(len(studentList)):
			studentid = studentList[j]['student_id']
			
			cursor.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as
	            student_name FROM `institution_user_credential` WHERE 
	            `INSTITUTION_USER_ID` =%s""",(studentid))

			studentnames = cursor.fetchone()
			if studentnames :
				studentname = studentnames['student_name']
				
				data_stu ={
				        "appParams": {},
				        "userId": studentid,
				        "sourceapp": "VCUPADS1",
				        "toMail": "",
				        "role": "S1",
				        "toNumber": 0,
				        "mailParams": {"audiopath":audio_filepath}
				        }

				response_stu = requests.post(url, data=json.dumps(data_stu), headers=headers).json()
	else:
		data = {
		        "appParams": {},
		        "userId": teacherid,
		        "sourceapp": "VCUPADS1",
		        "toMail": "",
		        "role": "S1",
		        "toNumber": 0,
		        "mailParams": {"audiopath":audio_filepath}
		        }
		# print(data)
		response = requests.post(url, data=json.dumps(data), headers=headers).json()
		cursor.execute("""SELECT distinct(`student_id`) FROM `voicechat_student_mapping` WHERE 
	    	`session_id`=%s""",(session_id))

		studentList = cursor.fetchall()
		# print(studentList)
		for j in range(len(studentList)):
			studentid = studentList[j]['student_id']
			# print(studentid)
			if 	user_id !=studentid:
				studata = {
					        "appParams": {},
					        "userId": studentid,
					        "sourceapp": "VCUPADS1",
					        "toMail": "",
					        "role": "S1",
					        "toNumber": 0,
					        "mailParams": {"audiopath":audio_filepath}
					        }
				# print(studata)
				response = requests.post(url, data=json.dumps(studata), headers=headers).json()

	cursor.close()
	return 'success'


class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'sendVoiceNote':
			user_id = self.request[0]
			session_id = self.request[1]
			audio_filepath = self.request[2]
			appnotifyaudio(user_id,session_id,audio_filepath)
		else:
			pass 
@name_space.route("/sendVoiceNote")
class sendVoiceNote(Resource):
	@api.expect(send_voice_note)
	def post(self):

		connection = connect_logindb()
		cursor = connection.cursor()

		details = request.get_json()
		user_id = details.get('user_id')
		session_id = details.get('session_id')
		audio_filepath = details.get('audio_filepath')
		filetype = details.get('filetype')

		sendNoteInsertQuery = ("""INSERT INTO `voicechat_session_mapping`( `session_id`, `user_id`, 
			`audio_filepath`,`filetype`) VALUES (%s,%s,%s,%s)""")

		noteData = (session_id,user_id,audio_filepath,filetype)

		cursor.execute(sendNoteInsertQuery,noteData)
		noteId = cursor.lastrowid
		details['voicenote_id'] = noteId
		connection.commit()
		cursor.close()

		session_id = details.get('session_id')
		sendrReq = (user_id,session_id,audio_filepath)
		thread_a = Compute(sendrReq,'sendVoiceNote')
		thread_a.start()
		return ({"attributes": {"status_desc": "Voice Note Details",
								"status": "success",
									},
				"responseList":details}), status.HTTP_200_OK



@name_space.route("/getChatListByTeacherId/<int:teacher_id>")
class getChatListByTeacherId(Resource):
	def get(self,teacher_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT `session_id`,`session_description`,`group_id`,	`last_update_ts` as 'createdOn'
			FROM `voicechat_session` WHERE `teacher_id` = %s and `status` = 'start'""",(teacher_id))

		chatDtls = cursor.fetchall()
		if chatDtls:
			for cid,chat in enumerate(chatDtls):
				groupList = [chat.get('group_id')]
				studentList = utils.getStudentListFromGroupid(groupList)
				chat['totalParticipants'] = len(studentList)
				chat['createdOn'] = chat.get('createdOn').isoformat()
		cursor.close()

		return ({"attributes": {"status_desc": "Voice Chat Details",
								"status": "success",
									},
				"responseList":chatDtls}), status.HTTP_200_OK


@name_space.route("/getChatListByStudentId/<int:student_id>")
class getChatListByStudentId(Resource):
	def get(self,student_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		cursor.execute("""SELECT vsm.`session_id`, vs.`session_description`,vs.`group_id`,
			vs.`last_update_ts` as 'createdOn'
			FROM `voicechat_student_mapping` vsm INNER JOIN `voicechat_session` vs 
			ON vsm.`session_id` = vs.`session_id` WHERE `student_id` = %s 
			and vs.`status` = 'start'""",(student_id))

		chatDtls = cursor.fetchall()
		if chatDtls:
			for cid,chat in enumerate(chatDtls):
				groupList = [chat.get('group_id')]
				studentList = utils.getStudentListFromGroupid(groupList)
				chat['totalParticipants'] = len(studentList)
				chat['createdOn'] = chat.get('createdOn').isoformat()
		cursor.close()

		return ({"attributes": {"status_desc": "Voice Chat Details",
								"status": "success",
									},
				"responseList":chatDtls}), status.HTTP_200_OK



@name_space.route("/getChatDetailsBySessionId/<int:session_id>")
class getChatDetailsBySessionId(Resource):
	def get(self,session_id):

		connection = connect_logindb()
		cursor = connection.cursor()

		details = {}
		cursor.execute("""SELECT vs.`group_id`,gm.`Group_Description`,vsm.`student_id`,
			sd.`STUDENT_NAME`,sd.`Image_URL`,vs.`teacher_id`, iuc.`FIRST_NAME`, iuc.`LAST_NAME`,
			iuc.`IMAGE_URL` as 'teacherImage' FROM `voicechat_session` vs
			INNER JOIN `voicechat_student_mapping` vsm ON
			vs.`session_id` = vsm.`session_id`
			INNER JOIN `group_master` gm ON vs.`Group_ID` = gm.`Group_ID`
			INNER JOIN `student_dtls` sd ON
			vsm.`student_id` = sd.`INSTITUTION_USER_ID_STUDENT` 
			AND vs.`INSTITUTION_ID` = sd.`INSTITUTION_ID`
			INNER JOIN `institution_user_credential` iuc ON vs.`teacher_id` = iuc.`INSTITUTION_USER_ID`
			WHERE vs.`session_id` = %s""",(session_id))


		chatDtls = cursor.fetchall()
		if chatDtls:
			print(chatDtls)
			totalParticipants = len(chatDtls)
			paricipantList = []
			groupId = chatDtls[0].get('group_id')
			groupDesc = chatDtls[0].get('Group_Description')
			teacherId = chatDtls[0].get('teacher_id')
			teacherName = chatDtls[0].get('FIRST_NAME') + " " + chatDtls[0].get('LAST_NAME')
			teacherImage = chatDtls[0].get('teacherImage')
			for cid, chat in enumerate(chatDtls):
				paricipantList.append({"studentId":chat.get('student_id'),
										"imageurl":chat.get('Image_URL'),
										"studentName":chat.get('STUDENT_NAME')})

			cursor.execute("""SELECT vs.`session_description`,vsm.`mapping_id` AS 'voicenoteId',
				vsm.`user_id`,iuc.`FIRST_NAME`,iuc.`LAST_NAME`,iuc.`IMAGE_URL`,iuc.`PRIMARY_CONTACT_NUMBER`,
				vsm.`audio_filepath`,vsm.`filetype` FROM `voicechat_session` vs
				INNER JOIN `voicechat_session_mapping` vsm ON vs.`session_id` = vsm.`session_id`
				INNER JOIN `institution_user_credential` iuc on vsm.`user_id` = iuc.`INSTITUTION_USER_ID`
				WHERE vs.`session_id` = %s ORDER BY vsm.`mapping_id` ASC""",(session_id))

			voiceNoteDtls = cursor.fetchall()
			for nid, note in enumerate(voiceNoteDtls):
				username = note.get('FIRST_NAME')+ ' '+note.get('LAST_NAME')
				note['userName'] = username
				note.pop('FIRST_NAME',None)
				note.pop('LAST_NAME',None)
			cursor.close()

			details = {"participantList":paricipantList,
						"totalParticipants":totalParticipants,
						"teacherId":teacherId,
						"teacherName":teacherName,
						"teacherImage":teacherImage,
						"groupDescription":groupDesc,
						"groupId":groupId,
						"chatDtls":voiceNoteDtls}

		return ({"attributes": {"status_desc": "Voice Chat Details",
								"status": "success",
									},
				"responseList":details}), status.HTTP_200_OK