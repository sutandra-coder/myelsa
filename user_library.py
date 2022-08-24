import pymysql
import configparser
from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests

app = Flask(__name__)
cors = CORS(app)
user_library = Blueprint('user_library_api', __name__)
api = Api(user_library,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('userLibraryController',description='User Library')

upload_model = api.model('upload_model', {
	"teacher_id":fields.Integer(required=True),
	"content_name":fields.String(required=True),
	"content_filepath":fields.String(required=True),
	"content_filetype":fields.String(required=True),
	"topic_id":fields.Integer(),
	"liveclass_id":fields.Integer(),
	"feature_flag":fields.String(),
	"subtopic_id":fields.Integer(),
	"institution_id":fields.Integer(),
	})

assign_content = api.model('assign_content', {
	"content_id":fields.Integer(required=True),
	"student_id":fields.List(fields.Integer()),
	"group_id":fields.List(fields.Integer()),
	"is_group":fields.Integer(required=True),
	})

add_subject = api.model('add_subject', {
	"subject_name":fields.String(required=True),
	"institution_id":fields.Integer()
	})

add_topic = api.model('add_topic', {
	"topic_name":fields.String(required=True),
	"subject_id":fields.Integer(required=True)
	})

map_content_liveclass_model = api.model('map_content_liveclass_model', {
	"content_id":fields.Integer(required=True),
	"liveclass_id":fields.Integer(required=True),
	"feature_flag":fields.String(required=True)
	})

map_multiple_content = api.model('map_multiple_content', {
	"content_dtls":fields.List(fields.Nested(map_content_liveclass_model))
	})


'''def mysql_connection():
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

def mysql_connection():
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

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'


@name_space.route("/uploadContentToMyLibrary")
class uploadContentToMyLibrary(Resource):
	@api.expect(upload_model)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		
		details = request.get_json()
		filepath = details.get('content_filepath')
		if filepath:
			split_filepath = filepath.split('/')
			content_filepath = "/".join(split_filepath[:-1]) + '/'
			content_filename = filepath.split('/')[-1]
		else:
			content_filepath = None
			content_filename = None
		topic_id = details.get('topic_id')
		liveClassId = details.get('liveclass_id')
		featureFlag = details.get('feature_flag')
		subtopic_id = details.get('subtopic_id')
		institution_id = details.get('institution_id')
		contentInsertQuery = ("""INSERT INTO `content_library`(`content_name`, `content_filepath`, 
			`content_filename`, `content_filetype`, `teacher_id`, 
			`topic_id`,`subtopic_id`,`institution_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")

		contentData = (details.get('content_name').title(),content_filepath,content_filename,
			details.get('content_filetype'),details.get('teacher_id'),topic_id,subtopic_id,institution_id)

		cursor.execute(contentInsertQuery,contentData)
		contentId = cursor.lastrowid
		details['content_id'] = contentId

		if liveClassId:
			conLiveMapInsertQuery = ("""INSERT INTO `content_liveclass_mapping`(`content_id`, 
				`liveclass_id`, `pre_post_flag`) VALUES (%s,%s,%s)""")

			conLiveData = (contentId,liveClassId,featureFlag)
			cursor.execute(conLiveMapInsertQuery,conLiveData)
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			contentStudentMapURL = BASE_URL + 'user_library/userLibraryController/studentContentMappingByLiveclassId/{}/{}'.format(liveClassId,contentId)
			requests.post(contentStudentMapURL,headers=headers)
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Content Upload Details",
								"status": "success"
									},
				"responseList":details}), status.HTTP_200_OK


@name_space.route("/assignContent")
class assignContent(Resource):
	@api.expect(assign_content)
	def post(self):
		details = request.get_json()

		connection = mysql_connection()
		cursor = connection.cursor()

		conn = connect_logindb()
		cur = conn.cursor()

		contentId = details.get('content_id')
		studentList = details.get('student_id',[])
		groupList = details.get('group_id',[])
		is_group = details.get('is_group')

		if is_group:
			for gid in groupList:
				cur.execute("""SELECT `Student_Id` FROM `group_student_mapping`
					WHERE `Group_ID` = %s""",(gid))

				std_id = cur.fetchall()

				if std_id:
					for idx,std in enumerate(std_id):
						studentList.append(std['Student_Id'])
		studentList = list(set(studentList))

		userList = []
		assigned_to = []
		contentInsertQuery = ("""INSERT INTO `content_student_mapping`( `content_id`, `student_id`) 
			VALUES (%s,%s)""")

		for i, stid in enumerate(studentList):

			cursor.execute("""SELECT `student_id` FROM `content_student_mapping` 
				WHERE `student_id` = %s and `content_id` = %s""",(stid,contentId))

			sid = cursor.fetchone()
			
			if sid:
				continue
			else:
				userList.append(stid)
				contentData = (contentId,stid)
				cursor.execute(contentInsertQuery,contentData)

				cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
					`image_url` as student_image FROM `institution_user_credential` 
					WHERE `INSTITUTION_USER_ID` = %s""",(stid))
				student_name = cur.fetchone()

				if student_name:
					assigned_to.append({'student_name':student_name['name'],
										'student_image':student_name['student_image'],
										'mapping_id':cursor.lastrowid,
										})

		return ({"attributes": {"status_desc": "Content Assignment Details",
								"status": "success"
									},
				"responseList":assigned_to}), status.HTTP_200_OK




@name_space.route("/getContentFromMyLibraryForTeacher/<int:teacher_id>")
class getContentFromMyLibraryForTeacher(Resource):
	def get(self,teacher_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `content_id`,content_library.`topic_id`,
			`topic_name`,subject.`subject_id`,`subject_name`,
			`content_name`,concat(`content_filepath`, `content_filename`) as 
			'content_filepath',`content_filetype`,`class`,`board` FROM 
			`content_library` INNER JOIN `topic` on content_library.`topic_id`=
			 topic.`topic_id` INNER JOIN `subject` on topic.`subject_id`= subject. 
			`subject_id` WHERE `teacher_id`= %s order by `content_name`""",(teacher_id))

		contentDtls = cursor.fetchall()
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		for cid, content in enumerate(contentDtls):
			assessmentURL = BASE_URL + 'library_dtls/Library&Liveclass/getassessmentbyContentId/{}'.format(content.get('content_id'))
			assessmentDtls = requests.get(assessmentURL,headers=headers).json()

			assessmentRes = assessmentDtls.get('responseList')

			content['assessmentDtls'] = assessmentRes
		cursor.close()

		return ({"attributes": {"status_desc": "Content Details",
								"status": "success"
									},
				"responseList":contentDtls}), status.HTTP_200_OK



@name_space.route("/getContentFromMyLibraryForStudent/<int:student_id>")
class getContentFromMyLibraryForStudent(Resource):
	def get(self,student_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT csm.`content_id`,cl.`content_name`,
			cl.`topic_id`,`topic_name`,subject.`subject_id`,`subject_name`, 
			concat(cl.`content_filepath`,cl.`content_filename`) as 
			'content_filepath',cl.`content_filetype`,cl.`teacher_id` FROM 
			`content_student_mapping`csm inner join `content_library` cl on 
			csm.`content_id` = cl.`content_id` INNER JOIN `topic` on cl.`topic_id`= 
			topic.`topic_id` INNER JOIN `subject` on topic.`subject_id`= subject.
			`subject_id` WHERE `student_id`= %s order by cl.`content_name`""",(student_id))

		contentDtls = cursor.fetchall()
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		for cid, content in enumerate(contentDtls):
			assessmentURL = BASE_URL + 'library_dtls/Library&Liveclass/getassessmentbyContentId/{}'.format(content.get('content_id'))
			assessmentDtls = requests.get(assessmentURL,headers=headers).json()

			assessmentRes = assessmentDtls.get('responseList')

			content['assessmentDtls'] = assessmentRes

		
		cursor.close()

		return ({"attributes": {"status_desc": "Content Details",
								"status": "success"
									},
				"responseList":contentDtls}), status.HTTP_200_OK


@name_space.route("/addSubject")
class addSubject(Resource):
	@api.expect(add_subject)
	def post(self):

		details = request.get_json()
		subjectName = details.get('subject_name')
		institution_id = details.get('institution_id')
		connection = mysql_connection()
		cursor = connection.cursor()

		subInsertQuery = ("""INSERT INTO `subject`(`subject_name`,`institution_id`) VALUES (%s,%s)""")

		subData = (subjectName.title(),institution_id)

		cursor.execute(subInsertQuery,subData)
		subjectId = cursor.lastrowid
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Add New Subject",
								"status": "success"
								},
				"responseList":{'subject_id':subjectId}}), status.HTTP_200_OK


@name_space.route("/addTopic")
class addTopic(Resource):
	@api.expect(add_topic)
	def post(self):

		details = request.get_json()
		topicName = details.get('topic_name')
		subjectId = details.get('subject_id')

		connection = mysql_connection()
		cursor = connection.cursor()

		topicInsertQuery = ("""INSERT INTO `topic`(`topic_name`, `subject_id`) VALUES (%s,%s)""")

		topicData = (topicName.title(),subjectId)

		cursor.execute(topicInsertQuery,topicData)
		topicId = cursor.lastrowid
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Add New Subject",
								"status": "success"
								},
				"responseList":{'topic_id':topicId,
								'subject_id':subjectId}}), status.HTTP_200_OK


@name_space.route("/studentContentMappingByLiveclassId/<int:liveclass_id>/<int:content_id>")
class studentContentMappingByLiveclassId(Resource):
	def post(self,liveclass_id,content_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		getStudentListbyLiveClass = BASE_URL + 'library_dtls/Library&Liveclass/getLiveClassNotificationforStudent/{}'.format(liveclass_id)
		getResponse = requests.get(getStudentListbyLiveClass).json()

		assignedList = getResponse.get('responseList')

		groupList = []

		studentList = []
		isGroup = 0
		for i, gid in enumerate(assignedList):
			if 'Group_ID' in assignedList[0]:
				groupList.append(gid.get('Group_ID'))
				isGroup = 1
			else:
				studentList.append(gid.get('Student_id'))
				
		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		contentMappingURL = BASE_URL + 'user_library/userLibraryController/assignContent'

		contentMapPayload = {"content_id": content_id,
								"student_id": studentList,
								"group_id": groupList,
								"is_group": isGroup
							}
		print(contentMapPayload)
		postRes = requests.post(contentMappingURL, data = json.dumps(contentMapPayload),headers=headers).json()

		return postRes

@name_space.route("/mapContentWithLiveClass")
class mapContentWithLiveClass(Resource):
	@api.expect(map_multiple_content)
	def post(self):

		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()
		content_dtls = details.get('content_dtls')
		for cid, con in enumerate(content_dtls):
			contentId = con.get('content_id')
			liveClassId = con.get('liveclass_id')
			featureFlag = con.get('feature_flag')

			conLiveMapInsertQuery = ("""INSERT INTO `content_liveclass_mapping`(`content_id`, 
					`liveclass_id`, `pre_post_flag`) VALUES (%s,%s,%s)""")

			conLiveData = (contentId,liveClassId,featureFlag)
			cursor.execute(conLiveMapInsertQuery,conLiveData)
			headers = {'Content-type':'application/json', 'Accept':'application/json'}
			contentStudentMapURL = BASE_URL + 'user_library/userLibraryController/studentContentMappingByLiveclassId/{}/{}'.format(liveClassId,contentId)
			requests.post(contentStudentMapURL,headers=headers)

			cursor.execute("""SELECT `content_id`, `content_name`, `content_filepath`, `content_filename`, 
				`content_filetype`, `topic_id`, `teacher_id`, `class`, `board`,`las_update_ts` as 'created_on'
				FROM `content_library` WHERE `content_id`= %s""",(contentId))
			conDtls = cursor.fetchone()
			conDtls['created_on'] = conDtls.get('created_on').isoformat()
			con['content'] = conDtls

		return ({"attributes": {"status_desc": "Content Upload Details",
								"status": "success"
									},
				"responseList":details}), status.HTTP_200_OK



@name_space.route("/deleteContentLiveClassMapping/<int:content_id>/<int:liveclass_id>")
class deleteContentLiveClassMapping(Resource):
	def delete(self,content_id,liveclass_id):

		connection = mysql_connection()
		cursor = connection.cursor()


		cursor.execute("""DELETE FROM `content_liveclass_mapping` WHERE `content_id` = %s 
			and `liveclass_id` = %s""",(content_id,liveclass_id))

		return ({"attributes": {"status_desc": "Delete Mapping Details",
								"status": "success"
									},
				"responseList":'Content Removed.'}), status.HTTP_200_OK