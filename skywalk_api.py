from flask import Flask, request, jsonify, json
from flask_api import status
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import json

app = Flask(__name__)
cors = CORS(app)


'''def connect_userlib():
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

def connect_userlib():
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


skywalk_section = Blueprint('skywalk_section_api', __name__)
api = Api(skywalk_section,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('skywalkSection',description='Skywalk Section')

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'

# BASE_URL = "http://127.0.0.1:5000/"

course_content_model = api.model('course_content_model', {
	"teacher_id":fields.Integer(required=True),
	"content_name":fields.String(required=True),
	"content_filepath":fields.String(required=True),
	"content_filetype":fields.String(required=True),
	"course_id":fields.Integer(required=True),
	"topic_id":fields.Integer(),
	"subtopic_id":fields.Integer(),
	"institution_id":fields.Integer()
	})


add_subtopic_model = api.model('add_subtopic_model', {
	"topic_id":fields.Integer(),
	"subtopic_name":fields.String(),
	})


update_subtopic_model = api.model('update_subtopic_model', {
	"subtopic_id":fields.Integer(),
	"subtopic_name":fields.String(),
	})


update_topic_model = api.model('update_topic_model', {
	"topic_id":fields.Integer(),
	"topic_name":fields.String(),
	"topic_order":fields.Integer()
	})


update_subject_model = api.model('update_subject_model', {
	"subject_id":fields.Integer(),
	"subject_name":fields.String(),
	})

add_student_to_institute = api.model('add_student_to_institute', {
	"user_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"institution_name":fields.String(),
	"userclass":fields.Integer(),
	"board":fields.String(),
	"user_name":fields.String(),
	"father_name":fields.String(),
	"image_url":fields.String()
	})

content_putmodel = api.model('updateContent',{
	"content_order":fields.Integer(required=True)
})


student_dtls_putmodel = api.model('updateStudentClass',{
	"class":fields.Integer(required=True)
})

@name_space.route("/getSubjectByInstitutionId/<int:institution_id>")	
class getSubjectByInstitutionId(Resource):
	def get(self,institution_id):

		connection = connect_userlib()
		curlab = connection.cursor()

		curlab.execute("""SELECT `subject_id`,`subject_name` FROM `subject` 
			WHERE `institution_id` = %s""",(institution_id))

		subDtls = curlab.fetchall()

		curlab.close()

		return ({"attributes": {"status_desc": "Subject Details.",
								"status": "success"},
				"responseList":subDtls}), status.HTTP_200_OK


@name_space.route("/getTopicBySubjectId/<int:subject_id>")	
class getTopicBySubjectId(Resource):
	def get(self,subject_id):

		connection = connect_userlib()
		curlab = connection.cursor()

		curlab.execute("""SELECT `topic_id`,`topic_name`,`topic_order` FROM `topic` 
			WHERE `subject_id` = %s order by topic_order asc""",(subject_id))

		topicDtls = curlab.fetchall()

		curlab.close()

		return ({"attributes": {"status_desc": "Topic Details.",
								"status": "success"},
				"responseList":topicDtls}), status.HTTP_200_OK


@name_space.route("/getSubTopicByTopicId/<int:topic_id>")	
class getSubTopicByTopicId(Resource):
	def get(self,topic_id):

		connection = connect_userlib()
		curlab = connection.cursor()

		curlab.execute("""SELECT `subtopic_id`,`subtopic_name` FROM `subtopic` 
			WHERE `topic_id` = %s""",(topic_id))

		subtopicDtls = curlab.fetchall()

		curlab.close()

		return ({"attributes": {"status_desc": "Sub Topic Details.",
								"status": "success"},
				"responseList":subtopicDtls}), status.HTTP_200_OK


@name_space.route("/getContentListBySubtopicId/<int:institution_id>/<int:course_id>/<int:subtopic_id>")	
class getContentListBySubtopicId(Resource):
	def get(self,institution_id,course_id,subtopic_id):
		
		connection = connect_userlib()
		curlab = connection.cursor()
		
		# curlab.execute("""SELECT `content_id`,`content_name`,`content_filepath`,`content_filename`,
		# 	`content_filetype`,`topic_id`,`teacher_id`, '' as 'course_id' FROM `content_library` 
		# 	WHERE `teacher_id` = 42430""")
		curlab.execute("""SELECT `content_id`,`content_name`,`content_filepath`,`content_filename`, 
			`content_filetype`,`topic_id`,`teacher_id`, '' as 'course_id' FROM `content_library` 
			WHERE (`subtopic_id` = %s or `subtopic_id` = 0) and `content_id` in(SELECT `content_id` 
			FROM `course_content_mapping` WHERE `course_id` = %s) 
			AND `institution_id` = %s""",(subtopic_id,course_id,institution_id))
		contentDtls = curlab.fetchall()
		for cid, con in enumerate(contentDtls):
			con['course_id'] = course_id
		connection.commit()
		curlab.close()

		return ({"attributes": {"status_desc": "Content Details",
		    					"status": "success"
		    					},
		    	"responseList":contentDtls}), status.HTTP_200_OK

@name_space.route("/getContentListBySubtopicIdByOrder/<int:institution_id>/<int:course_id>/<int:subtopic_id>")	
class getContentListBySubtopicIdByOrder(Resource):
	def get(self,institution_id,course_id,subtopic_id):
		
		connection = connect_userlib()
		curlab = connection.cursor()
		
		# curlab.execute("""SELECT `content_id`,`content_name`,`content_filepath`,`content_filename`,
		# 	`content_filetype`,`topic_id`,`teacher_id`, '' as 'course_id' FROM `content_library` 
		# 	WHERE `teacher_id` = 42430""")
		curlab.execute("""SELECT `content_id`,`content_name`,`content_filepath`,`content_filename`, 
			`content_filetype`,`topic_id`,`teacher_id`, `content_order`,'' as 'course_id' FROM `content_library` 
			WHERE (`subtopic_id` = %s or `subtopic_id` = 0) and `content_id` in(SELECT `content_id` 
			FROM `course_content_mapping` WHERE `course_id` = %s) 
			AND `institution_id` = %s order by content_order asc""",(subtopic_id,course_id,institution_id))
		contentDtls = curlab.fetchall()
		for cid, con in enumerate(contentDtls):
			con['course_id'] = course_id
		connection.commit()
		curlab.close()

		return ({"attributes": {"status_desc": "Content Details",
		    					"status": "success"
		    					},
		    	"responseList":contentDtls}), status.HTTP_200_OK


#----------------------Update-Content-Order---------------------#

@name_space.route("/UpdateContentOrder/<int:content_id>")
class UpdateCartItem(Resource):
	@api.expect(content_putmodel)
	def put(self,content_id):
		connection = connect_userlib()
		cursor = connection.cursor()
		details = request.get_json()

		content_order = details['content_order']
		update_query = ("""UPDATE `content_library` SET `content_order` = %s
				WHERE `content_id` = %s """)
		update_data = (content_order,content_id)
		cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Content Order",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Content-Order---------------------#

#----------------------Get-Content-By-Content-Id---------------------#

@name_space.route("/getContentByContentId/<int:content_id>")	
class getContentByContentId(Resource):
	def get(self,content_id):

		connection = connect_userlib()
		curlab = connection.cursor()

		curlab.execute("""SELECT `content_name`,`content_order` FROM `content_library` 
			WHERE `content_id` = %s""",(content_id))

		contentDtls = curlab.fetchone()

		curlab.close()

		return ({"attributes": {"status_desc": "Content Details.",
								"status": "success"},
				"responseList":contentDtls}), status.HTTP_200_OK

#----------------------Get-Content-By-Content-Id---------------------#

@name_space.route("/CreateCourseContent")
class CreateCourseContent(Resource):
	@api.expect(course_content_model)
	def post(self):
		connection = connect_userlib()
		cursor = connection.cursor()
		
		details = request.get_json()

		content_filepath = details.get('content_filepath')
		topic_id = details.get('topic_id',0)
		content_name = details.get('content_name')
		content_filetype = details.get('content_filetype')
		teacher_id = details.get('teacher_id')
		course_id = details.get('course_id')
		subtopic_id = details.get('subtopic_id',0)
		institution_id = details.get('institution_id')

		headers = {'Content-type':'application/json', 'Accept':'application/json'}
		create_content_url = BASE_URL + 'user_library/userLibraryController/uploadContentToMyLibrary'

		post_data = {
					  "teacher_id": teacher_id,
					  "content_name": content_name,
					  "content_filepath": content_filepath,
					  "content_filetype": content_filetype,
					  "topic_id": topic_id,
					  "subtopic_id":subtopic_id,
					  "institution_id":institution_id
					}

		contentDetails = requests.post(create_content_url, data=json.dumps(post_data), headers=headers)

		
		my_json_string = contentDetails.json()

		s1 = json.dumps(my_json_string['responseList'])
		
		s2 = json.loads(s1)

		if s2['content_id'] :
			content_status = None
		
			insert_course_content_mapping = ("""INSERT INTO `course_content_mapping`(`course_id`,`content_id`,`status`) VALUES(%s,%s,%s)""")
			mapping_data = (course_id,s2['content_id'],content_status)
			cursor.execute(insert_course_content_mapping,mapping_data)

		details['content_id'] = s2['content_id']	

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Course Content",
	    						"status": "success"},
	    		"responseList":details}), status.HTTP_200_OK


@name_space.route("/postSubTopic")
class postSubTopic(Resource):
	@api.expect(add_subtopic_model)
	def post(self):
		connection = connect_userlib()
		curlab = connection.cursor()
		
		details = request.get_json()

		subtopicInsertQuery = ("""INSERT INTO `subtopic`(`subtopic_name`, `topic_id`) VALUES (%s,%s)""")

		curlab.execute(subtopicInsertQuery,(details.get('subtopic_name'),details.get('topic_id')))

		connection.commit()

		curlab.execute("""SELECT `subtopic_id`, `subtopic_name` FROM `subtopic` 
			WHERE `topic_id` = %s""",(details.get('topic_id')))

		subtopicDtls = curlab.fetchall()

		return ({"attributes": {"status_desc": "Sub-Topic Details",
	    						"status": "success"},
	    		"responseList":subtopicDtls}), status.HTTP_200_OK


@name_space.route("/editTopicByTopicId")
class editTopicByTopicId(Resource):
	@api.expect(update_topic_model)
	def put(self):

		connection = connect_userlib()
		curlab = connection.cursor()
		details = request.get_json()
		topic_id = details.get('topic_id')
		topic_name = details.get('topic_name')
		topic_order = details.get('topic_order')

		updateTopic = ("""UPDATE `topic` SET `topic_name` = %s,`topic_order` = %s WHERE `topic_id` = %s""")
		curlab.execute(updateTopic,(topic_name.capitalize(),topic_order,topic_id))
		connection.commit()
		curlab.close()

		return ({"attributes": {"status_desc": "Update Topic Details",
								"status": "success"},
				"responseList":'Topic updated'}), status.HTTP_200_OK


@name_space.route("/editSubjectBySubjectId")
class editSubjectBySubjectId(Resource):
	@api.expect(update_subject_model)
	def put(self):

		connection = connect_userlib()
		curlab = connection.cursor()
		details = request.get_json()
		subject_id = details.get('subject_id')
		subject_name = details.get('subject_name')
		updateSubject = ("""UPDATE `subject` SET `subject_name` = %s WHERE `subject_id` = %s""")
		curlab.execute(updateSubject,(subject_name.capitalize(),subject_id))
		connection.commit()
		curlab.close()

		return ({"attributes": {"status_desc": "Update Subject Details",
								"status": "success"},
				"responseList":'Subject updated'}), status.HTTP_200_OK


@name_space.route("/editSubTopicBySubTopicId")
class editSubTopicBySubTopicId(Resource):
	@api.expect(update_subtopic_model)
	def put(self):

		connection = connect_userlib()
		curlab = connection.cursor()
		details = request.get_json()
		subtopic_id = details.get('subtopic_id')
		subtopic_name = details.get('subtopic_name')

		updateSubTopic = ("""UPDATE `subtopic` SET `subtopic_name` = %s WHERE `subtopic_id` = %s""")
		curlab.execute(updateSubTopic,(subtopic_name.capitalize(),subtopic_id))
		connection.commit()
		curlab.close()

		return ({"attributes": {"status_desc": "Update SubTopic Details",
								"status": "success"},
				"responseList":'SubTopic updated'}), status.HTTP_200_OK


@name_space.route("/getTopicNameByTopicId/<int:topic_id>")	
class getTopicNameByTopicId(Resource):
	def get(self,topic_id):

		connection = connect_userlib()
		curlab = connection.cursor()

		curlab.execute("""SELECT `topic_id`,`topic_name`,`topic_order` FROM `topic` 
			WHERE `topic_id` = %s""",(topic_id))

		topicDtls = curlab.fetchone()

		curlab.close()

		return ({"attributes": {"status_desc": "Topic Details.",
								"status": "success"},
				"responseList":topicDtls}), status.HTTP_200_OK


@name_space.route("/getSubTopicNameBySubTopicId/<int:subtopic_id>")	
class getSubTopicNameBySubTopicId(Resource):
	def get(self,subtopic_id):

		connection = connect_userlib()
		curlab = connection.cursor()

		curlab.execute("""SELECT `subtopic_id`,`subtopic_name` FROM `subtopic` 
			WHERE `subtopic_id` = %s""",(subtopic_id))

		subtopicDtls = curlab.fetchone()

		curlab.close()

		return ({"attributes": {"status_desc": "Sub Topic Details.",
								"status": "success"},
				"responseList":subtopicDtls}), status.HTTP_200_OK


@name_space.route("/getContentNameByContentId/<int:content_id>")	
class getContentNameByContentId(Resource):
	def get(self,content_id):
		
		connection = connect_userlib()
		curlab = connection.cursor()

		curlab.execute("""SELECT `content_id`,`content_name`,`content_filepath`,`content_filename`, 
			`content_filetype`,`topic_id`,`teacher_id`, institution_id FROM `content_library` 
			WHERE content_id = %s""",(content_id))
		
		contentDtls = curlab.fetchone()
		
		connection.commit()
		curlab.close()

		return ({"attributes": {"status_desc": "Content Details",
		    					"status": "success"
		    					},
		    	"responseList":contentDtls}), status.HTTP_200_OK



@name_space.route("/deleteTopic/<int:topic_id>")
class deleteTopic(Resource):
	def delete(self,topic_id):

		connection = connect_userlib()
		curlab = connection.cursor()

		curlab.execute("""SELECT `course_id`,`course_image` FROM `instituition_course_master` 
			WHERE `topic_id` = %s""",(topic_id))

		courseDtls = curlab.fetchall()
		print(courseDtls)
		curlab.execute("""SELECT `content_id`,`content_name` FROM `content_library` 
			WHERE `topic_id` = %s""",(topic_id))

		contentDtls = curlab.fetchall()
		print(contentDtls)

		curlab.execute("""SELECT `subtopic_id`,`subtopic_name` FROM `subtopic` 
			WHERE `topic_id` = %s""",(topic_id))

		subtopicDtls = curlab.fetchall()
		if courseDtls or contentDtls or subtopicDtls:
			msg = 'Delete related content/course/subtopic'
		else:
			
			deleteQuery = ("""DELETE FROM `topic` WHERE `topic_id` = %s""")

			curlab.execute(deleteQuery,(topic_id,))
			connection.commit()
			msg = 'deleted'
		curlab.close()
		return ({"attributes": {"status_desc": "Content Details",
		    					"status": "success",
		    					"msg":msg
		    					},
		    	"responseList":{"courseDtls":courseDtls,
		    					"contentDtls":contentDtls,
		    					"subtopicDtls":subtopicDtls}}), status.HTTP_200_OK


@name_space.route("/deleteSubTopic/<int:subtopic_id>")
class deleteSubTopic(Resource):
	def delete(self,subtopic_id):

		connection = connect_userlib()
		curlab = connection.cursor()

		curlab.execute("""SELECT `content_id`,`content_name` FROM `content_library` 
			WHERE `subtopic_id` = %s""",(subtopic_id))

		contentDtls = curlab.fetchall()
		print(contentDtls)

		if contentDtls:
			msg = 'Delete related content'
		else:
			
			deleteQuery = ("""DELETE FROM `subtopic` WHERE `subtopic_id` = %s""")

			curlab.execute(deleteQuery,(subtopic_id,))
			connection.commit()
			msg = 'deleted'
		curlab.close()
		return ({"attributes": {"status_desc": "Content Details",
		    					"status": "success",
		    					"msg":msg
		    					},
		    	"responseList":{"contentDtls":contentDtls}}), status.HTTP_200_OK



@name_space.route("/getPurchaseHistory/<string:from_date>/<string:to_date>/<int:institution_id>")	
class getPurchaseHistory(Resource):
	def get(self,from_date,to_date,institution_id):
		
		connection = connect_userlib()
		curlab = connection.cursor()

		conn = connect_logindb()
		curlog = conn.cursor()

		curlog.execute("""SELECT ipr.`request_id`,`student_id`,`phone`,`email`, `EMAIL_ID` as district,
			`buyer_name` as 'student_name',`amount`, `purpose`as 'course_name',ipr.`status`,`USER_UNIQUE_ID` as 'thana',
			iuc.`IMAGE_URL`,`INSTITUTION_NAME` as 'school',`STREET_ADDRESS` as 'address',`CLASS`,`created_at`,`addition_ts` as 'modified_at' FROM `instamojo_payment_request` ipr 
			INNER JOIN `instamojo_payment_student_mapping` ipsm ON ipr.`request_id` = ipsm.`request_id` 
			INNER JOIN `institution_user_credential` iuc ON ipsm.`student_id` = iuc.`INSTITUTION_USER_ID` 
			INNER JOIN `institution_user_credential_master` iucm 
			on iuc.`INSTITUTION_USER_ID` = iucm.`INSTITUTION_USER_ID` 
			and ipr.`INSTITUTION_ID` = iucm.`INSTITUTION_ID` 
			INNER JOIN `student_dtls` sd on ipr.`INSTITUTION_ID` = sd.`INSTITUTION_ID` 
			and iuc.`INSTITUTION_USER_ID` = sd.`INSTITUTION_USER_ID_STUDENT`
			WHERE ipr.`institution_id` = %s and
			date(ipr.`last_update_ts`) BETWEEN %s and %s""",(institution_id,from_date,to_date))


		purchaseDtls = curlog.fetchall()
		for pid, pur in enumerate(purchaseDtls):
			pur['modified_at'] = pur.get('modified_at').isoformat()
			pur['created_at'] = pur.get('created_at').isoformat()

		curlab.close()
		curlog.close()

		return ({"attributes": {"status_desc": "Purchase History Details",
								"status": "success"},
				"responseList":purchaseDtls}), status.HTTP_200_OK


@name_space.route("/getSoldCourseDtls/<int:institution_id>/<string:course_type>")	
class getSoldCourseDtls(Resource):
	def get(self,institution_id,course_type):
		
		connection = connect_userlib()
		curlab = connection.cursor()

		conn = connect_logindb()
		curlog = conn.cursor()
		if course_type.lower() == 'single':
			curlog.execute("""SELECT sum(`amount`) as 'amount', count(`request_id`) as 'no_of_courses' 
				FROM `instamojo_payment_request` WHERE `purpose` LIKE %s and status = 'Complete'
				and `institution_id` = %s """,('Course%',institution_id))

			courseDtls = curlog.fetchone()
			msg = 'Single Course'
		elif course_type.lower() == 'combo':
			curlog.execute("""SELECT sum(`amount`) as 'amount', count(`request_id`) as 'no_of_courses' 
				FROM `instamojo_payment_request` WHERE `purpose` LIKE %s 
				and `institution_id` = %s and `status` = 'Complete' """,('ComboCourse%',institution_id))

			courseDtls = curlog.fetchone()
			msg = 'Combo Course'
		else:
			msg = 'course type should be single / combo'
			courseDtls = {}

		curlab.close()
		curlog.close()
		return ({"attributes": {"status_desc": "Purchase History Details",
								"status": "success",
								"msg":msg
								},
				"responseList":courseDtls}), status.HTTP_200_OK



@name_space.route("/verifyUser/<string:username>")	
class verifyUser(Resource):
	def get(self,username):
		
		connection = connect_logindb()
		curlog = connection.cursor()

		curlog.execute("""SELECT `INSTITUTION_ID`,`INSTITUTION_USER_ID` FROM 
			`institution_user_credential_master` WHERE `INSTITUTION_USER_ID` in 
			(SELECT `INSTITUTION_USER_ID` FROM `institution_user_credential` WHERE 
			`INSTITUTION_USER_NAME` = %s)""",(username))

		userDtls = curlog.fetchall()

		curlog.close()
		return ({"attributes": {"status_desc": "User Details",
								"status": "success"
								},
				"responseList":userDtls}), status.HTTP_200_OK


@name_space.route("/addUserToInstitution")	
class addUserToInstitution(Resource):
	@api.expect(add_student_to_institute)
	def post(self):
		
		connection = connect_logindb()
		curlog = connection.cursor()
		details = request.get_json()

		user_id = details.get('user_id')
		institution_id = details.get('institution_id')
		institution_name = details.get('institution_name')
		userclass = details.get('userclass')
		board = details.get('board')
		user_name = details.get('user_name')
		father_name = details.get('father_name')
		image_url = details.get('image_url')
		current_date = date.today()
		start_date = str(current_date)
		nextyear_date = current_date.replace(year=current_date.year + 1)
		end_date = str(nextyear_date)

		instiMasterInsertQuery = ("""INSERT INTO `institution_user_credential_master`(`INSTITUTION_ID`, 
			`INSTITUTION_USER_ID`, `INSTITUTION_USER_ROLE`, `INSTITUTION_NAME`, `USER_ENROLL_DATE`, 
			`USER_END_DATE`) VALUES (%s,%s,%s,%s,%s,%s)""")


		instiMasterData = (institution_id,user_id,'S1',institution_name,current_date,end_date)

		curlog.execute(instiMasterInsertQuery,instiMasterData)

		studentDtlsInsertQuery = ("""INSERT INTO `student_dtls`(`INSTITUTION_ID`, 
			`INSTITUTION_USER_ID_STUDENT`, `CLASS`, `STUDENT_NAME`, `Fathers_Name`, 
			`Image_URL`, `Board`,`INSTITUTION_USER_ID_TEACHER`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")


		studentData = (institution_id,user_id,userclass,user_name,father_name,image_url,board,0)

		curlog.execute(studentDtlsInsertQuery,studentData)

		connection.commit()


		curlog.close()

		return ({"attributes": {"status_desc": "User Added",
								"status": "success"
								},
				"responseList":details}), status.HTTP_200_OK


#----------------------Update-Class-By-Student-Id---------------------#
@name_space.route("/UpdateClassByStudentId/<int:INSTITUTION_USER_ID_STUDENT>")
class UpdateClassByStudentId(Resource):
	@api.expect(student_dtls_putmodel)
	def put(self,INSTITUTION_USER_ID_STUDENT):

		connection = connect_logindb()
		cursor = connection.cursor()		
		details = request.get_json()

		if details and "class" in details:
			CLASS = details['class']
			update_query = ("""UPDATE `student_dtls` SET `CLASS` = %s
				WHERE `INSTITUTION_USER_ID_STUDENT` = %s """)
			update_data = (CLASS,INSTITUTION_USER_ID_STUDENT)
			cursor.execute(update_query,update_data)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Update Clas",
								"status": "success"},
				"responseList": 'Updated Successfully'}), status.HTTP_200_OK


#----------------------Update-Class-By-Student-Id---------------------#