from flask import Flask, request, jsonify, json
from flask_api import status
from jinja2._compat import izip
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
# from werkzeug.utils import cached_property
import requests
import calendar
import json

app = Flask(__name__)
cors = CORS(app)

#----------------------database-connection---------------------#
def mysql_connection():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_third_party_library',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection---------------------#

#----------------------database-connection-loginDb---------------------#
'''def mysql_connection_logindb():
	connection = pymysql.connect(host='creamsonservices.com',
	                             user='creamson_langlab',
	                             password='Langlab@123',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection'''

def mysql_connection_logindb():
	connection = pymysql.connect(host='myelsa.cdcuaa7mp0jm.us-east-2.rds.amazonaws.com',
	                             user='admin',
	                             password='cbdHoRPQPRfTdC0uSPLt',
	                             db='creamson_logindb',
	                             charset='utf8mb4',
	                             cursorclass=pymysql.cursors.DictCursor)
	return connection

#----------------------database-connection-loginDb---------------------#

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'

myelsa_third_partycourse = Blueprint('myelsa_third_partycourse_api', __name__)
api = Api(myelsa_third_partycourse,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('MyelsaThirdPartyCourse',description='Myelsa Third Party Course')

course_postmodel = api.model('SelectCourse', {
	"institution_id":fields.Integer(required=True),
	"course_title":fields.String(required=True),
	"course_description":fields.String(required=True),
	"course_global":fields.String(required=True),
	"course_image":fields.String(required=True),
	"course_filetype":fields.String(required=True),
	"teacher_id":fields.Integer(required=True),
	"subject_id":fields.Integer(required=True),
	"topic_id":fields.Integer(required=True),
	"language":fields.String(required=True)
	})

create_assessments = api.model('create_assessments', {
	"teacher_id":fields.Integer(required=True),
	"assessment_desc":fields.String(required=True),
	"subject_id":fields.Integer(required=True),
	"topic_id":fields.Integer(required=True),
	"content_filepath":fields.String(),
	"content_filetype":fields.String(),
	"feature_flag":fields.String(required=True),
	"content_id":fields.Integer(),
	"liveclass_id":fields.Integer()
	})

unlockcourse = api.model('unlockcourse', {
	"course_id":fields.Integer(),
	"student_id":fields.Integer(),
	"institution_id":fields.Integer(),
	"teacher_id":fields.Integer()
})

#----------------------Post-Course---------------------#
@name_space.route("/CreateCourse")
class CreateCourse(Resource):
	@api.expect(course_postmodel)
	def post(self):
	
		connection = mysql_connection()
		cursor = connection.cursor()		
		details = request.get_json()

		institution_id = details['institution_id']
		course_title = details['course_title']
		course_description = details['course_description']
		course_global = details['course_global']
		course_image = details['course_image']
		course_filetype = details['course_filetype']
		teacher_id = details['teacher_id']
		subject_id = details['subject_id']
		topic_id = details['topic_id']
		language = details['language']

		insert_query = ("""INSERT INTO `instituition_course_master`(`institution_id`,
			`course_title`,`course_description`,`global`,`course_image`,
		`course_filetype`,`teacher_id`,`subject_id`,`topic_id`,`language`) 
		VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")
		data = (institution_id,course_title,course_description,
			course_global,course_image,course_filetype,teacher_id,
			subject_id,topic_id,language)
		cursor.execute(insert_query,data)

		course_id = cursor.lastrowid
		details['course_id'] = course_id

		connection.commit()
		cursor.close()

		return ({"attributes": {
	    				"status_desc": "Course Details.",
	    				"status": "success"
	    				},
	    				"responseList":{"CourseDtls":details}}), status.HTTP_200_OK

#--------------------Post-Course---------------------#

#----------------------Get-Course-List-with-institute---------------------#

@name_space.route("/getCourseListIns/<int:teacher_id>/<int:institution_id>")	
class getCourseListIns(Resource):
	def get(self,teacher_id,institution_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		if teacher_id == 0:
			course_get_query = ("""SELECT `course_id`,`institution_id`,`course_title`,`course_description`,`course_image`,
			`course_filetype`,`teacher_id`,`subject_id`,`topic_id`
			FROM `instituition_course_master` WHERE `institution_id` = %s """)

			getData = (institution_id)

			row_count_course = cursor.execute(course_get_query,getData)

			couse_data = cursor.fetchall()
		else:	
			course_get_query = ("""SELECT `course_id`,`institution_id`,`course_title`,`course_description`,`course_image`,
				`course_filetype`,`teacher_id`,`subject_id`,`topic_id`
				FROM `instituition_course_master` WHERE `teacher_id` = %s and `institution_id` = %s""")

			getData = (teacher_id,institution_id)

			row_count_course = cursor.execute(course_get_query,getData)

			if row_count_course>0:
				couse_data = cursor.fetchall()

			else:
				course_get_query = ("""SELECT `course_id`,`institution_id`,`course_title`,`course_description`,`course_image`,
				`course_filetype`,`teacher_id`,`subject_id`,`topic_id`
				FROM `instituition_course_master` WHERE `institution_id` = %s""")

				getData = (institution_id)

				cursor.execute(course_get_query,getData)

				couse_data = cursor.fetchall()

		for key,data in enumerate(couse_data):
			get_topic_query = ("""SELECT `topic_id`,`topic_name`
			FROM `topic` WHERE `topic_id` = %s """)

			topicData = (data['topic_id'])

			row_count_topic = cursor.execute(get_topic_query,topicData)

			if row_count_topic>0:
				topic_data = cursor.fetchone()

				couse_data[key]['topic_name'] = topic_data['topic_name']
				
			else:
				couse_data[key]['topic_name'] = ""

			get_subject_query = ("""SELECT `subject_id`,`subject_name`
			FROM `subject` WHERE `subject_id` = %s """)

			subjectData = (data['subject_id'])

			row_subject_topic = cursor.execute(get_subject_query,subjectData)

			if row_subject_topic>0:
				subject_data = cursor.fetchone()

				couse_data[key]['subject_name'] = subject_data['subject_name']
				
			else:
				couse_data[key]['subject_name'] = ""
			
			no_of_student_assign_query = ("""SELECT count(Distinct(student_id)) as no_of_student_assign FROM `student_course_master` where course_id = %s """)	
			student_assign_data = (data['course_id'])
			row_student_assign = cursor.execute(no_of_student_assign_query,student_assign_data)

			if row_student_assign>0:
				student_data = cursor.fetchone()

				couse_data[key]['no_of_student_assign'] = student_data['no_of_student_assign']
				
			else:
				couse_data[key]['no_of_student_assign'] = ""

			couse_data[key]['no_of_student_seen'] = 1
				
		return ({"attributes": {
		    		"status_desc": "Course_details",
		    		"status": "success"
		    	},
		    	"responseList":couse_data}), status.HTTP_200_OK
		
#----------------------Get-Course-List-with-institute---------------------#

@name_space.route("/getTopicBySubjectId/<int:subject_id>")	
class getTopicBySubjectId(Resource):
	def get(self,subject_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `topic_id`,`topic_name` FROM `topic` 
			WHERE `subject_id` = %s""",(subject_id))

		topicDtls = cursor.fetchall()

		cursor.close()

		return ({"attributes": {"status_desc": "Topic Details.",
								"status": "success"},
				"responseList":topicDtls}), status.HTTP_200_OK


@name_space.route("/getSubTopicByTopicId/<int:topic_id>")	
class getSubTopicByTopicId(Resource):
	def get(self,topic_id):

		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `subtopic_id`,`subtopic_name` FROM `subtopic` 
			WHERE `topic_id` = %s""",(topic_id))

		subtopicDtls = cursor.fetchall()

		cursor.close()

		return ({"attributes": {"status_desc": "Sub Topic Details.",
								"status": "success"},
				"responseList":subtopicDtls}), status.HTTP_200_OK


@name_space.route("/getContentListBySubtopicId/<int:institution_id>/<int:course_id>/<int:subtopic_id>")	
class getContentListBySubtopicId(Resource):
	def get(self,institution_id,course_id,subtopic_id):
		
		connection = mysql_connection()
		cursor = connection.cursor()
		
		cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,`content_filename`, 
			`content_filetype`,`topic_id`,`teacher_id`, '' as 'course_id' FROM `content_library` 
			WHERE (`subtopic_id` = %s or `subtopic_id` = 0) and `content_id` in(SELECT `content_id` 
			FROM `course_content_mapping` WHERE `course_id` = %s) 
			AND `institution_id` = %s""",(subtopic_id,course_id,institution_id))
		contentDtls = cursor.fetchall()
		for cid, con in enumerate(contentDtls):
			con['course_id'] = course_id
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Content Details",
		    					"status": "success"
		    					},
		    	"responseList":contentDtls}), status.HTTP_200_OK


@name_space.route("/getCourseListInsitutionId/<int:institution_id>")	
class getCourseListInsitutionId(Resource):
	def get(self,institution_id):
		connection = mysql_connection()
		cursor = connection.cursor()

		cursor.execute("""SELECT `institution_id` FROM `instituition_course_master` WHERE 
		 `institution_id` = %s """,(institution_id))

		course = cursor.fetchone()
		cursor.execute("""SELECT `course_id`,`institution_id`,`course_title`,
		 `course_description`,`course_image`,`course_filetype`,`teacher_id`,
		 `subject_id`,`topic_id` FROM `instituition_course_master` WHERE 
		 `institution_id` = %s """,(institution_id))

		couse_data = cursor.fetchall()
		course['course_dtls'] = couse_data
		return ({"attributes": {"status_desc": "Course Details",
		    					"status": "success"
		    					},
		    	"responseList":course}), status.HTTP_200_OK


@name_space.route("/getCourseList")	
class getCourseList(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = mysql_connection_logindb()
		cur = conn.cursor()

		cursor.execute("""SELECT distinct(`institution_id`) FROM `instituition_course_master`""")
		institutionid = cursor.fetchall()

		for ins in range(len(institutionid)):

			cur.execute("""SELECT `INSTITUTION_ID`,`INSTITUTION_NAME` FROM `institution_dtls` 
				WHERE `INSTITUTION_ID`=%s""",(institutionid[ins]['institution_id']))

			CourseDtls = cur.fetchone()
			# print(CourseDtls)
			if CourseDtls == None:
				cursor.execute("""SELECT `course_id`,`course_title`,
				 `course_description`,`course_image`,`course_filetype`,`teacher_id`,
				 instituition_course_master.`subject_id`,`subject_name`,`topic_id` FROM 
				 `instituition_course_master` inner join `subject` on 
				 instituition_course_master.`subject_id`= subject.`subject_id` WHERE 
				 instituition_course_master.`institution_id` = %s""",(institutionid[ins]['institution_id']))

				couse_data = cursor.fetchall()

				institutionid[ins]['INSTITUTION_ID'] = institutionid[ins]['institution_id']
				institutionid[ins]['INSTITUTION_NAME'] = "2226"
				institutionid[ins]['course_dtls'] = couse_data
				
			else:
				cursor.execute("""SELECT `course_id`,`course_title`,
				 `course_description`,`course_image`,`course_filetype`,`teacher_id`,
				 instituition_course_master.`subject_id`,`subject_name`,`topic_id` FROM `instituition_course_master`  inner join `subject` on 
				 instituition_course_master.`subject_id`= subject.`subject_id` WHERE 
				 instituition_course_master.`institution_id` = %s""",(institutionid[ins]['institution_id']))

				couse_data = cursor.fetchall()
				
				institutionid[ins]['INSTITUTION_ID'] = institutionid[ins]['institution_id']
				institutionid[ins]['INSTITUTION_NAME'] =  CourseDtls['INSTITUTION_NAME']
				institutionid[ins]['course_dtls'] = couse_data

		return ({"attributes": {"status_desc": "Course Details",
		    					"status": "success"
		    					},
		    	"responseList":institutionid}), status.HTTP_200_OK

@name_space.route("/getContentListByTopicId/<int:institution_id>/<int:course_id>/<int:topic_id>")	
class getContentListByTopicId(Resource):
	def get(self,institution_id,course_id,topic_id):
		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = []

		cursor.execute("""SELECT `mapping_id`,`course_id`,`content_id` FROM 
			`course_content_mapping` WHERE `course_id`=%s""",(course_id))
		contentid = cursor.fetchall()
		# print(contentid)
		for cid in range(len(contentid)):
			details.append(
                contentid[cid]['content_id'])
		details = tuple(details)
		# print(details)
		cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,
		   `content_filename`,`content_filetype`,content_library.`topic_id`,`topic_name`,`teacher_id` FROM 
		   `content_library` inner join `topic` on content_library.`topic_id`= 
		   topic.`topic_id` WHERE `content_id`in %s and content_library.`topic_id`=%s and 
		   `institution_id`=%s and `content_filetype`!='video' and 
		   `content_filepath`!=''""",(details,topic_id,institution_id))
		document_dtls = cursor.fetchall()
		# print(document_dtls)

		cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,
		   `content_filename`,`content_filetype`,content_library.`topic_id`,`topic_name`,`teacher_id` FROM 
		   `content_library` inner join `topic` on content_library.`topic_id`= 
		   topic.`topic_id` WHERE `content_id`in %s and content_library.`topic_id`=%s and 
		   `institution_id`=%s and `content_filetype`='video'""",(details,topic_id,institution_id))
		content_dtls = cursor.fetchall()

		cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,
		   `content_filename`,`content_filetype`,content_library.`topic_id`,`topic_name`,`teacher_id` FROM 
		   `content_library` inner join `topic` on content_library.`topic_id`= 
		   topic.`topic_id` WHERE `content_id`in %s and content_library.`topic_id`=%s and 
		   `institution_id`=%s and `content_filepath`=''""",(details,topic_id,institution_id))
		quiz_dtls = cursor.fetchall()
		for con in range(len(quiz_dtls)):
		 	cursor.execute("""SELECT `Assessment_ID`,`Assesment_Desc`,
				`feature_flag`,`teacher_id`,assessment.`subject_id`,
				`subject_name`,assessment.`topic_id`,`topic_name`,
	            `Content_File_Path`,`Content_FileName`,`FileType_Id` 
	            FROM `assessment`,`topic`,`subject` WHERE 
	            `Assessment_ID` in(SELECT `Assessment_ID` FROM 
	            `content_assessment_mapping` WHERE `Content_ID`=%s) and 
	            assessment.`topic_id`= topic.`topic_id` and 
	            assessment.`subject_id`= subject.`subject_id` 
	            order by Assessment_ID asc""",(quiz_dtls[con]['content_id']))
		 	get_assessment = cursor.fetchall()
		 	quiz_dtls[con]['assessment_dtls'] = get_assessment

		ContentDtls = {
					"institution_id":institution_id,
					"course_id":course_id,
					"document_dtls":document_dtls,
					"content_dtls":content_dtls,
					"quiz_dtls":quiz_dtls,
				}
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Content Details",
		    					"status": "success"
		    					},
		    	"responseList":ContentDtls}), status.HTTP_200_OK


@name_space.route("/createAssessment")
class createAssessment(Resource):
	@api.expect(create_assessments)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()
		message = 'Assessment Successfully Created.'
		details = request.get_json()
		teacher_id = details.get('teacher_id')
		assessment_desc = details.get('assessment_desc')
		subject_id = details.get('subject_id')
		topic_id = details.get('topic_id')
		filepath = details.get('content_filepath')
		if filepath:
			split_filepath = filepath.split('/')
			content_filepath = "/".join(split_filepath[:-1]) + '/'
			content_filename = filepath.split('/')[-1]
		else:
			content_filepath = None
			content_filename = None
		content_filetype = details.get('content_filetype')
		contentId = details.get('content_id',None)
		featureFlag = details.get('feature_flag','').lower()
		liveClassId = details.get('liveclass_id',None)

		assessmentInsertQuery = ("""INSERT INTO `assessment`(`Assesment_Desc`, `teacher_id`, 
			`subject_id`, `topic_id`, `Content_File_Path`, `Content_FileName`, 
			`FileType_Id`, `feature_flag`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")

		conAssMapInsertQuery = ("""INSERT INTO `content_assessment_mapping`(`Content_ID`, 
			`Assessment_ID`) VALUES (%s,%s)""")

		conLiveMapInsertQuery = ("""INSERT INTO `content_liveclass_mapping`(`content_id`, `liveclass_id`, 
			`pre_post_flag`) VALUES (%s,%s,%s)""")

		conPostUrl = BASE_URL + 'user_library/userLibraryController/uploadContentToMyLibrary'

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		if contentId:
			if featureFlag == 'content':

				assessmentData = (assessment_desc,teacher_id,subject_id,topic_id,content_filepath,content_filename,
					content_filetype,featureFlag)

				cursor.execute(assessmentInsertQuery,assessmentData)

				assessmentId = cursor.lastrowid

				conAssData = (contentId,assessmentId)

				cursor.execute(conAssMapInsertQuery,conAssData)


				details['assessment_id'] = assessmentId

			elif (featureFlag == 'prelive' or featureFlag == 'postlive') and liveClassId:

				conLiveData = (contentId,liveClassId,featureFlag)
				cursor.execute(conLiveMapInsertQuery,conLiveData)

				assessmentData = (assessment_desc,teacher_id,subject_id,topic_id,content_filepath,content_filename,
					content_filetype,featureFlag)

				cursor.execute(assessmentInsertQuery,assessmentData)
				assessmentId = cursor.lastrowid

				conAssData = (contentId,assessmentId)

				cursor.execute(conAssMapInsertQuery,conAssData)

				details['assessment_id'] = assessmentId
			else:
				message = 'Invalid Feature Flag'
				details = {}

		else:
			if featureFlag == 'question':

				assessmentData = (assessment_desc,teacher_id,subject_id,topic_id,content_filepath,content_filename,
					content_filetype,featureFlag)

				cursor.execute(assessmentInsertQuery,assessmentData)
				assessmentId = cursor.lastrowid
				details['assessment_id'] = assessmentId

			elif featureFlag == 'prelive' or featureFlag == 'postlive':

				conPayload = {"teacher_id": teacher_id,
								"content_name": featureFlag+"-Dummy"
								}

				post_response = requests.post(conPostUrl, data=json.dumps(conPayload), headers=headers).json()
				
				contentId = post_response.get('responseList').get('content_id')

				conLiveData = (contentId,liveClassId,featureFlag)
				cursor.execute(conLiveMapInsertQuery,conLiveData)

				assessmentData = (assessment_desc,teacher_id,subject_id,topic_id,content_filepath,content_filename,
					content_filetype,featureFlag)

				cursor.execute(assessmentInsertQuery,assessmentData)
				assessmentId = cursor.lastrowid

				conAssData = (contentId,assessmentId)

				cursor.execute(conAssMapInsertQuery,conAssData)

				details['assessment_id'] = assessmentId
				details['content_id'] = contentId
			else:
				message = 'Invalid Feature Flag'
				details = {}

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Assessment Details",
								"status": "success",
								"message":message
									},
				"responseList":details}), status.HTTP_200_OK



#-----------------------assessment-by-contentid-----------------------------#

@name_space.route("/getassessmentbyContentId/<int:contentid>")
class getassessmentbyContentId(Resource):
    def get(self,contentid):
        connection = mysql_connection()
        cursor = connection.cursor()
        cursor.execute("""SELECT `Assessment_ID`,`Assesment_Desc`,`feature_flag`,`teacher_id`,assessment.`subject_id`,`subject_name`,assessment.`topic_id`,`topic_name`,
            `Content_File_Path`,`Content_FileName`,`FileType_Id` FROM `assessment`,`topic`,
            `subject` WHERE `Assessment_ID` in(SELECT `Assessment_ID` FROM 
            `content_assessment_mapping` WHERE `Content_ID`=%s) and assessment.`topic_id`= 
            topic.`topic_id` and assessment.`subject_id`= subject.`subject_id` order by Assessment_ID asc
            """,(contentid))
        get_assessment = cursor.fetchall()
        connection.commit()
        cursor.close()
        return ({"attributes": {"status_desc": "Assessment Details",
                                "status": "success"
                                    },
                "responseList":get_assessment}), status.HTTP_200_OK
   
#-----------------------assessment-by-contentid-----------------------------#
@name_space.route("/getContentListByInstitutionIdCourseId/<int:institution_id>/<int:course_id>")	
class getContentListByInstitutionIdCourseId(Resource):
	def get(self,institution_id,course_id):
		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = []
		# detail = []

		cursor.execute("""SELECT `mapping_id`,`course_id`,`content_id` FROM 
			`course_content_mapping` WHERE `course_id`=%s""",(course_id))
		contentid = cursor.fetchall()
		# print(contentid)
		for cid in range(len(contentid)):
			details.append(
                contentid[cid]['content_id'])
		details = tuple(details)
		
		cursor.execute("""SELECT distinct(content_library.`topic_id`),`topic_name` FROM 
		   `content_library` inner join `topic` on content_library.`topic_id`= 
		   topic.`topic_id` WHERE `content_id`in %s and 
		   `institution_id`=%s""",(details,institution_id))
		topic_dtls = cursor.fetchall()
		# print(topic_dtls)
		for tid in range(len(topic_dtls)):
			cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,
			   `content_filename`,`content_filetype`,`thumbnail_filepath`,
			   `thumbnail_filename`,`thumbnail_filetype`,content_library.`topic_id`,`topic_name`,`teacher_id` FROM 
			   `content_library` inner join `topic` on content_library.`topic_id`= 
			   topic.`topic_id` WHERE content_library.`topic_id`=%s and 
			   `institution_id`=%s and `content_filetype`!='video' and 
			   `content_filepath`!=''""",(topic_dtls[tid]['topic_id'],institution_id))
			document_dtls = cursor.fetchall()
			topic_dtls[tid]['document_dtls'] = document_dtls

		cursor.execute("""SELECT distinct(content_library.`topic_id`),`topic_name` FROM 
		   `content_library` inner join `topic` on content_library.`topic_id`= 
		   topic.`topic_id` WHERE `content_id`in %s and 
		   `institution_id`=%s""",(details,institution_id))
		topic_dtl = cursor.fetchall()
		
		for tid in range(len(topic_dtl)):
			cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,
			   `content_filename`,`content_filetype`,`thumbnail_filepath`,
			   `thumbnail_filename`,`thumbnail_filetype`,content_library.`topic_id`,`topic_name`,`teacher_id` FROM 
			   `content_library` inner join `topic` on content_library.`topic_id`= 
			   topic.`topic_id` WHERE content_library.`topic_id`=%s and 
			   `institution_id`=%s and `content_filetype`='video'""",(topic_dtl[tid]['topic_id'],institution_id))
			content_dtls = cursor.fetchall()
			topic_dtl[tid]['content_dtls'] = content_dtls

		cursor.execute("""SELECT distinct(content_library.`topic_id`),`topic_name` FROM 
		   `content_library` inner join `topic` on content_library.`topic_id`= 
		   topic.`topic_id` WHERE `content_id`in %s and 
		   `institution_id`=%s""",(details,institution_id))
		topicdtls = cursor.fetchall()
		
		for tid in range(len(topicdtls)):
			cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,
			   `content_filename`,`content_filetype`,content_library.`topic_id`,`topic_name`,`teacher_id` FROM 
			   `content_library` inner join `topic` on content_library.`topic_id`= 
			   topic.`topic_id` WHERE content_library.`topic_id`=%s and 
			   `institution_id`=%s and `content_filepath`=''""",(topicdtls[tid]['topic_id'],institution_id))
			quiz_dtls = cursor.fetchall()
			topicdtls[tid]['quiz_dtls'] = quiz_dtls
			for con in range(len(quiz_dtls)):
			 	cursor.execute("""SELECT `Assessment_ID`,`Assesment_Desc`,
					`feature_flag`,`teacher_id` FROM `assessment` WHERE 
		            `Assessment_ID` in(SELECT `Assessment_ID` FROM 
		            `content_assessment_mapping` WHERE `Content_ID`=%s)
		            order by Assessment_ID asc""",(quiz_dtls[con]['content_id']))
			 	get_assessment = cursor.fetchall()
			 	quiz_dtls[con]['assessment_dtls'] = get_assessment

		ContentDtls = {
					"document_dtls":topic_dtls,
					"content_dtls":topic_dtl,
					"quiz_dtls":topicdtls,
				}
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Content Details",
		    					"status": "success"
		    					},
		    	"responseList":ContentDtls}), status.HTTP_200_OK



@name_space.route("/getListOfCourses")	
class getListOfCourses(Resource):
	def get(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		conn = mysql_connection_logindb()
		cur = conn.cursor()

		
		cursor.execute("""SELECT instituition_course_master.`course_id`,
		  `course_title`,`course_description`,`global`,`course_image`,
		  `course_filetype`,`teacher_id`,instituition_course_master.`subject_id`,`subject_name`,
		  `language`,`fee_id`,`is_paid_course`,`total_fee`,`installment_available`,
		  `installment_type`,`no_of_installments` FROM 
		  `instituition_course_master` INNER JOIN `course_fee_mapping` on 
		  instituition_course_master.`course_id`= course_fee_mapping.`course_id` 
		  INNER JOIN `subject` on 
		  instituition_course_master.`subject_id`=subject.`subject_id`""")

		course_data = cursor.fetchall()
		for cid in range(len(course_data)):
			cur.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as name,
				`IMAGE_URL`,`PRIMARY_CONTACT_NUMBER` FROM 
				`institution_user_credential` WHERE `INSTITUTION_USER_ID`=%s""",
				(course_data[cid]['teacher_id']))

			teacherDtls = cur.fetchone()
			course_data[cid]['Teacher_NAME'] = teacherDtls['name']
			course_data[cid]['IMAGE_URL'] = teacherDtls['IMAGE_URL']
			course_data[cid]['PRIMARY_CONTACT_NUMBER'] = teacherDtls['PRIMARY_CONTACT_NUMBER']
		
		connection.commit()
		cursor.close()
		conn.commit()
		cur.close()

		return ({"attributes": {"status_desc": "Course Details",
		    					"status": "success"
		    					},
		    	"responseList":course_data}), status.HTTP_200_OK



@name_space.route("/getContentListByTeacherIdCourseId/<int:teacher_id>/<int:course_id>")	
class getContentListByTeacherIdCourseId(Resource):
	def get(self,teacher_id,course_id):
		
		connection = mysql_connection()
		cursor = connection.cursor()
		details = []
		# detail = []

		cursor.execute("""SELECT `course_id`,`institution_id` FROM `instituition_course_master` 
			WHERE `course_id`=%s and `teacher_id`=%s""",(course_id,teacher_id))
		courseid = cursor.fetchone()

		if courseid:
			cursor.execute("""SELECT `mapping_id`,`course_id`,`content_id` FROM 
				`course_content_mapping` WHERE `course_id`=%s""",(courseid['course_id']))
			contentid = cursor.fetchall()
			# print(contentid)
			for cid in range(len(contentid)):
				details.append(
	                contentid[cid]['content_id'])
			details = tuple(details)
			
			cursor.execute("""SELECT distinct(content_library.`topic_id`),`topic_name` FROM 
			   `content_library` inner join `topic` on content_library.`topic_id`= 
			   topic.`topic_id` WHERE `content_id`in %s and 
			   `institution_id`=%s""",(details,courseid['institution_id']))
			topic_dtls = cursor.fetchall()
			# print(topic_dtls)
			for tid in range(len(topic_dtls)):
				cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,
				   `content_filename`,`content_filetype`,`thumbnail_filepath`,
				   `thumbnail_filename`,`thumbnail_filetype`,content_library.`topic_id`,`topic_name`,`teacher_id` FROM 
				   `content_library` inner join `topic` on content_library.`topic_id`= 
				   topic.`topic_id` WHERE content_library.`topic_id`=%s and 
				   `institution_id`=%s and `content_filetype`!='video' and 
				   `content_filepath`!=''""",(topic_dtls[tid]['topic_id'],courseid['institution_id']))
				document_dtls = cursor.fetchall()
				topic_dtls[tid]['document_dtls'] = document_dtls

			cursor.execute("""SELECT distinct(content_library.`topic_id`),`topic_name` FROM 
			   `content_library` inner join `topic` on content_library.`topic_id`= 
			   topic.`topic_id` WHERE `content_id`in %s and 
			   `institution_id`=%s""",(details,courseid['institution_id']))
			topic_dtl = cursor.fetchall()
			
			for tid in range(len(topic_dtl)):
				cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,
				   `content_filename`,`content_filetype`,`thumbnail_filepath`,
				   `thumbnail_filename`,`thumbnail_filetype`,content_library.`topic_id`,`topic_name`,`teacher_id` FROM 
				   `content_library` inner join `topic` on content_library.`topic_id`= 
				   topic.`topic_id` WHERE content_library.`topic_id`=%s and 
				   `institution_id`=%s and `content_filetype`='video'""",(topic_dtl[tid]['topic_id'],courseid['institution_id']))
				content_dtls = cursor.fetchall()
				topic_dtl[tid]['content_dtls'] = content_dtls

			cursor.execute("""SELECT distinct(content_library.`topic_id`),`topic_name` FROM 
			   `content_library` inner join `topic` on content_library.`topic_id`= 
			   topic.`topic_id` WHERE `content_id`in %s and 
			   `institution_id`=%s""",(details,courseid['institution_id']))
			topicdtls = cursor.fetchall()
			
			for tid in range(len(topicdtls)):
				cursor.execute("""SELECT `content_id`,`content_name`,`content_filepath`,
				   `content_filename`,`content_filetype`,content_library.`topic_id`,`topic_name`,`teacher_id` FROM 
				   `content_library` inner join `topic` on content_library.`topic_id`= 
				   topic.`topic_id` WHERE content_library.`topic_id`=%s and 
				   `institution_id`=%s and `content_filepath`=''""",(topicdtls[tid]['topic_id'],courseid['institution_id']))
				quiz_dtls = cursor.fetchall()
				topicdtls[tid]['quiz_dtls'] = quiz_dtls
				for con in range(len(quiz_dtls)):
				 	cursor.execute("""SELECT `Assessment_ID`,`Assesment_Desc`,
						`feature_flag`,`teacher_id` FROM `assessment` WHERE 
			            `Assessment_ID` in(SELECT `Assessment_ID` FROM 
			            `content_assessment_mapping` WHERE `Content_ID`=%s)
			            order by Assessment_ID asc""",(quiz_dtls[con]['content_id']))
				 	get_assessment = cursor.fetchall()
				 	quiz_dtls[con]['assessment_dtls'] = get_assessment
		

			ContentDtls = {
						"document_dtls":topic_dtls,
						"content_dtls":topic_dtl,
						"quiz_dtls":topicdtls,
					}
		else:
			ContentDtls = []
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Content Details",
		    					"status": "success"
		    					},
		    	"responseList":ContentDtls}), status.HTTP_200_OK

#-------------------------------------------------------------------------#
@name_space.route("/UnlockCourse")
class UnlockCourse(Resource):
	@api.expect(unlockcourse)
	def post(self):
		connection = mysql_connection()
		cursor = connection.cursor()

		details = request.get_json()

		course_id = details.get('course_id')
		student_id = details.get('student_id')
		institution_id = details.get('institution_id')
		teacher_id = details.get('teacher_id')

		
		InsertQuery = ("""INSERT INTO `student_course_master`(`student_id`,
			`course_id`,`is_Lock`,`institution_id`,`teacher_id`,`last_update_id`) 
			VALUES (%s,%s,%s,%s,%s,%s)""")
		cursor.execute(InsertQuery,(student_id,course_id,'n',institution_id,teacher_id,teacher_id))

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Unlock Course Details",
								"status": "success"
								},
				"responseList":details}), status.HTTP_200_OK

#-----------------------------------------------------------------------#
@name_space.route("/getListOfCoursesByStudentId/<int:student_id>")	
class getListOfCoursesByStudentId(Resource):
	def get(self,student_id):
		connection = mysql_connection()
		cursor = connection.cursor()
		conn = mysql_connection_logindb()
		cur = conn.cursor()
		
		cursor.execute("""SELECT instituition_course_master.`course_id`,
		  instituition_course_master.`institution_id`,
		  `course_title`,`course_description`,`global`,`course_image`,
		  `course_filetype`,`teacher_id`,instituition_course_master.`subject_id`,`subject_name`,
		  `language`,`fee_id`,`is_paid_course`,`total_fee`,`installment_available`,
		  `installment_type`,`no_of_installments` FROM 
		  `instituition_course_master` INNER JOIN `course_fee_mapping` on 
		  instituition_course_master.`course_id`= course_fee_mapping.`course_id` 
		  INNER JOIN `subject` on 
		  instituition_course_master.`subject_id`=subject.`subject_id`""")

		course_data = cursor.fetchall()
		for cid in range(len(course_data)):
			cur.execute("""SELECT concat(`FIRST_NAME`,' ',`LAST_NAME`)as name,
				`IMAGE_URL`,`PRIMARY_CONTACT_NUMBER` FROM 
				`institution_user_credential` WHERE `INSTITUTION_USER_ID`=%s""",
				(course_data[cid]['teacher_id']))

			teacherDtls = cur.fetchone()
			course_data[cid]['Teacher_NAME'] = teacherDtls['name']
			course_data[cid]['IMAGE_URL'] = teacherDtls['IMAGE_URL']
			course_data[cid]['PRIMARY_CONTACT_NUMBER'] = teacherDtls['PRIMARY_CONTACT_NUMBER']
			
			cursor.execute("""SELECT `student_id`,`is_Lock` FROM 
				`student_course_master` WHERE student_id=%s and `course_id`=%s""",
				(student_id,course_data[cid]['course_id']))

			lockcourseDtls = cursor.fetchone()
			if lockcourseDtls:
				course_data[cid]['is_Lock'] = lockcourseDtls['is_Lock']
			else:
				course_data[cid]['is_Lock'] = 'y'
		connection.commit()
		cursor.close()
		conn.commit()
		cur.close()

		return ({"attributes": {"status_desc": "Student Course Details",
		    					"status": "success"
		    					},
		    	"responseList":course_data}), status.HTTP_200_OK


