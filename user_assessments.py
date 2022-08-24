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
user_library_assessments = Blueprint('user_library_assessments_api', __name__)
api = Api(user_library_assessments,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('assessmentsController',description='User Library')

create_assessments = api.model('create_assessments', {
	"teacher_id":fields.Integer(required=True),
	"assessment_desc":fields.String(required=True),
	"subject_id":fields.Integer(required=True),
	"topic_id":fields.Integer(required=True),
	"content_filepath":fields.String(),
	"content_filetype":fields.String(),
	"feature_flag":fields.String(required=True),
	"content_id":fields.Integer(),
	"liveclass_id":fields.Integer(),
	"assessment_duration":fields.String(),
	})

assign_assessment = api.model('assign_assessment', {
	"assessment_id":fields.Integer(required=True),
	"student_id":fields.List(fields.Integer()),
	"group_id":fields.List(fields.Integer()),
	"is_group":fields.Integer(required=True),
	})


options_model = api.model('options_model', {
		"option":fields.String(),
		"option_content_file_path":fields.String(),
		"option_content_filename":fields.String(),
		"option_filetype_id":fields.String()
		})

answers_model  = api.model('answers_model', {
			"answer":fields.String(),
			"answer_additional_text":fields.String(),
		})

upload_question_model = api.model('upload_question_model', {
	"question_type":fields.Integer(),
	"question":fields.String(),
	"question_content_file_path":fields.String(),
	"question_content_filename":fields.String(),
	"question_filetype_id":fields.String(),
	"level":fields.Integer(),
	"answers": fields.Nested(answers_model),
	"options":fields.List(fields.Nested(options_model))
	})

add_questions_model = api.model('add_questions_model', {
			"questions":fields.List(fields.Nested(upload_question_model)),
			"assessment_id":fields.Integer(),
			"teacher_id":fields.Integer(),
			"subject_id":fields.Integer(),
			"topic_id":fields.Integer(),
			"content_id":fields.Integer(),
		})

answer_details = api.model('answer details', {
	"question_id":fields.Integer(required=True),
	"option_id":fields.Integer(),
	"answer":fields.String(),
	"answer_filepath":fields.String(),
	"filetype":fields.String(),
	"remark":fields.String()
	})

submit_answers = api.model('Submit Answers', {
	"answer_details":fields.List(fields.Nested(answer_details)),
	"status":fields.String()
	})

addmarks = api.model('addmarks', {
	"question_id":fields.Integer(required=True),
	"marks":fields.Integer(required=True),
	"remarks":fields.String(),
	})

submit_marks = api.model('SubmitMarks', {
	"marks_details":fields.List(fields.Nested(addmarks))
	})

feedback_model = api.model('AssessmentFeedback', {
	"feedback":fields.String(),
	"total_marks":fields.Integer()
	})

student_assessment_upload = api.model('student_assessment_upload', {
	"asssessment_filepath":fields.String(required=True),
	"assessment_filetype":fields.String(required=True),
	"student_id":fields.Integer(required=True),
	"assessment_id":fields.Integer(required=True),
	})

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

# BASE_URL_LOCAL = 'http://127.0.0.1:5000/'

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'

@name_space.route("/createAssessment")
class createAssessment(Resource):
	@api.expect(create_assessments)
	def post(self):
		connection = connnect_userLibrary()
		cursor = connection.cursor()
		message = 'Assessment Successfully Created.'
		details = request.get_json()
		teacher_id = details.get('teacher_id')
		assessment_desc = details.get('assessment_desc')
		subject_id = details.get('subject_id')
		topic_id = details.get('topic_id')
		filepath = details.get('content_filepath')
		assessment_duration = details.get('assessment_duration')
		if assessment_duration == "":
			assessment_duration = None
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
			`FileType_Id`, `feature_flag`,`assessment_duration`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		conAssMapInsertQuery = ("""INSERT INTO `content_assessment_mapping`(`Content_ID`, 
			`Assessment_ID`) VALUES (%s,%s)""")

		conLiveMapInsertQuery = ("""INSERT INTO `content_liveclass_mapping`(`content_id`, `liveclass_id`, 
			`pre_post_flag`) VALUES (%s,%s,%s)""")

		conPostUrl = BASE_URL + 'user_library/userLibraryController/uploadContentToMyLibrary'

		assesmntStudentMapURL = BASE_URL + 'user_library_assessments/assessmentsController/assignAssessment'

		headers = {'Content-type':'application/json', 'Accept':'application/json'}

		if contentId:
			cursor.execute("""SELECT `student_id` FROM `content_student_mapping` 
				WHERE `content_id` = %s""",(contentId))

			contentStudentMapList = cursor.fetchall()
			studentList = []

			if contentStudentMapList:
				for i, sid in enumerate(contentStudentMapList):
					studentList.append(sid.get('student_id'))
			
			assesmntStudent_payload = {
										"student_id": studentList,
										"assessment_id": 0,
										"is_group": 0,
										"group_id": []
										}
			if featureFlag == 'content':

				assessmentData = (assessment_desc,teacher_id,subject_id,topic_id,content_filepath,content_filename,
					content_filetype,featureFlag,assessment_duration)

				cursor.execute(assessmentInsertQuery,assessmentData)

				assessmentId = cursor.lastrowid

				conAssData = (contentId,assessmentId)

				cursor.execute(conAssMapInsertQuery,conAssData)


				details['assessment_id'] = assessmentId

				if studentList:
					assesmntStudent_payload['assessment_id'] = assessmentId
					requests.post(assesmntStudentMapURL, data=json.dumps(assesmntStudent_payload), headers=headers)


			elif (featureFlag == 'prelive' or featureFlag == 'postlive') and liveClassId:

				
				assessmentData = (assessment_desc,teacher_id,subject_id,topic_id,content_filepath,content_filename,
					content_filetype,featureFlag,assessment_duration)

				cursor.execute(assessmentInsertQuery,assessmentData)
				assessmentId = cursor.lastrowid

				conAssData = (contentId,assessmentId)

				cursor.execute(conAssMapInsertQuery,conAssData)

				details['assessment_id'] = assessmentId
				if studentList:
					assesmntStudent_payload['assessment_id'] = assessmentId
					requests.post(assesmntStudentMapURL, data=json.dumps(assesmntStudent_payload), headers=headers)
			else:
				message = 'Invalid Feature Flag'
				details = {}

		else:
			if featureFlag == 'question':

				assessmentData = (assessment_desc,teacher_id,subject_id,topic_id,content_filepath,content_filename,
					content_filetype,featureFlag,assessment_duration)

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
					content_filetype,featureFlag,assessment_duration)

				cursor.execute(assessmentInsertQuery,assessmentData)
				assessmentId = cursor.lastrowid

				conAssData = (contentId,assessmentId)

				cursor.execute(conAssMapInsertQuery,conAssData)

				contentStudentMapURL = BASE_URL + 'user_library/userLibraryController/studentContentMappingByLiveclassId/{}/{}'.format(liveClassId,contentId)
				requests.post(contentStudentMapURL,headers=headers)

				cursor.execute("""SELECT `student_id` FROM `content_student_mapping` 
				WHERE `content_id` = %s""",(contentId))

				contentStudentMapList = cursor.fetchall()
				studentList = []

				if contentStudentMapList:
					for i, sid in enumerate(contentStudentMapList):
						studentList.append(sid.get('student_id'))
				
				assesmntStudent_payload = {
											"student_id": studentList,
											"assessment_id": 0,
											"is_group": 0,
											"group_id": []
											}
				if studentList:
					assesmntStudent_payload['assessment_id'] = assessmentId
					requests.post(assesmntStudentMapURL, data=json.dumps(assesmntStudent_payload), headers=headers)
				
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


@name_space.route("/assignAssessment")
class assignAssessment(Resource):
	@api.expect(assign_assessment)
	def post(self):
		details = request.get_json()

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		conn = connect_logindb()
		cur = conn.cursor()

		assessmentId = details.get('assessment_id')
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
		assessmentInsertQuery = ("""INSERT INTO `student_assessment_mapping`(`student_id`, 
			`assessment_id`, `status`) VALUES (%s,%s,%s)""")

		for i, stid in enumerate(studentList):

			cursor.execute("""SELECT `student_id` FROM `student_assessment_mapping` 
				WHERE `student_id` = %s and `assessment_id` = %s""",(stid,assessmentId))

			sid = cursor.fetchone()
			
			if sid:
				continue
			else:
				userList.append(stid)
				assessmentData = (stid,assessmentId,'a')
				cursor.execute(assessmentInsertQuery,assessmentData)

				cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
					`image_url` as student_image FROM `institution_user_credential` 
					WHERE `INSTITUTION_USER_ID` = %s""",(stid))
				student_name = cur.fetchone()

				if student_name:
					assigned_to.append({'student_name':student_name['name'],
										'student_image':student_name['student_image'],
										'mapping_id':cursor.lastrowid,
										})
		cursor.close()
		cur.close()
		return ({"attributes": {"status_desc": "Student Assessment Details",
								"status": "success"
									},
				"responseList":assigned_to}), status.HTTP_200_OK


@name_space.route("/getAssessmentType")
class getAssessmentType(Resource):
	def get(self):

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Assessment_Type_ID`,`Assessment_Type_Desc` FROM `assessment_type`""")

		typeDtls = cursor.fetchall()

		cursor.close()
		return ({"attributes": {"status_desc": "Assessment Type Details",
								"status": "success"
									},
				"responseList":typeDtls}), status.HTTP_200_OK

def assessment_question_mapping(assessment_id,question_id):

	connection = connnect_userLibrary()
	cursor = connection.cursor()

	assQuesMapInsertQuery = ("""INSERT INTO `assessment_question_mapping`(`Assessment_ID`, 
		`Question_ID`) VALUES (%s,%s)""")

	mapData = (assessment_id,question_id)

	cursor.execute(assQuesMapInsertQuery,mapData)


	connection.commit()
	cursor.close()


@name_space.route("/createQuestion")
class createQuestion(Resource):
	@api.expect(add_questions_model)
	def post(self):
		details = request.get_json()

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		questionList = details.get('questions')
		assessment_id = details.get('assessment_id')
		teacher_id = details.get('teacher_id')
		subject_id = details.get('subject_id')
		topic_id = details.get('topic_id')
		content_id = details.get('content_id',None)

		questionInsertQuery = ("""INSERT INTO `question`(`Question_Type`, `Question`, 
			`Content_file_path`, `Content_FileName`, `File_Type_ID`,  `Content_Id`, 
			`subject_id`, `topic_id`, `level`, `teacher_id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		optionInsertQuery = ("""INSERT INTO `options`( `Question_ID`, `Option`, `Option_Sequence_ID`,
			`Content_file_path`, `Content_FileName`, 
			`File_Type_ID`) VALUES (%s,%s,%s,%s,%s,%s)""")

		answerInsertQuery = ("""INSERT INTO `answer`(`Question_ID`, `Option_ID`, 
			`Additional_Text`) VALUES (%s,%s,%s)""")

		for qid, each_ques in enumerate(questionList):
			question_type = each_ques.get('question_type')
			question = each_ques.get('question')
			question_content_file_path = each_ques.get('question_content_file_path')
			question_content_filename = each_ques.get('question_content_filename')
			question_filetype_id = each_ques.get('question_filetype_id')
			level = each_ques.get('level',None)
			answerDtls = each_ques.get('answers')
			optionDtls = each_ques.get('options')
			# each_ques.get('last_update_ts'] = last_update_ts

			questionData = (question_type,question,question_content_file_path,question_content_filename,
				question_filetype_id,content_id,subject_id,topic_id,level,teacher_id)

			cursor.execute(questionInsertQuery,questionData)

			questionId = cursor.lastrowid
			each_ques['question_id'] = questionId

			option_sequence_id = 1
			for opid, op in enumerate(optionDtls):
				option_name = op.get('option')
				op['option_sequence_id'] = option_sequence_id
				option_content_file_path = op.get('option_content_file_path')
				option_content_filename = op.get('option_content_filename')
				option_filetype_id = op.get('option_filetype_id')

				optionData = (questionId,option_name,option_sequence_id,option_content_file_path,
					option_content_filename,option_filetype_id)

				cursor.execute(optionInsertQuery, optionData)
				option_sequence_id += 1
				op['option_id'] = cursor.lastrowid

			answer = answerDtls.get('answer')
			answer_additional_text = answerDtls.get('answer_additional_text')

			cursor.execute("""SELECT `Option_ID` from options where `Question_ID` = %s
				and `Option` = %s""",(questionId,answer))

			optionId = cursor.fetchone()
			option_id = optionId.get('Option_ID',0)

			answerData = (questionId,option_id,answer_additional_text)

			cursor.execute(answerInsertQuery,answerData)

			assessment_question_mapping(assessment_id,questionId)
		
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Question Details",
								"status": "success"
									},
				"responseList":details}), status.HTTP_200_OK


@name_space.route("/getQuestionByAssessmentId/<int:assessment_id>")
class getQuestionByAssessmentId(Resource):
	def get(self,assessment_id):

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Question_ID`  FROM `assessment_question_mapping` 
			WHERE `Assessment_ID` = %s""",(assessment_id))

		questionIdList = cursor.fetchall()
		questionList = []
		if questionIdList:
			for qid in questionIdList:

				cursor.execute("""SELECT ques.`Question_Type`, ast.`Assessment_Type_Desc`, ques.`Question_ID`,
					ques.`Question`, ques.`Content_Id`, ques.`passage_id`, ques.`Content_file_path`, 
					ques.`Content_FileName`, ques.`File_Type_ID`, ques.`Question_Type`, ques.`subject_id`, 
					sub.`subject_name`, top.`topic_name`, ques.`topic_id`, ques.`level`, 
					(select op1.`option` from options op1 where op1.`option_ID` = ans.`Option_ID`) answer, 
					ans.`Option_ID` as 'correct_optionId', ans.`Additional_Text` 
					FROM `question` ques, `answer` ans, `options` op, `subject` sub, `topic` top, 
					`assessment_type` ast WHERE ques.`Question_ID` = ans.`Question_ID` 
					AND ans.`Option_ID` = op.`Option_ID` AND ques.`subject_id` = sub.`subject_id` 
					and ques.`topic_id` = top.`topic_id` AND ast.`Assessment_Type_ID` = ques.`Question_Type` 
					AND ques.`Question_ID` = %s""",(qid.get('Question_ID')))


				questionDtls = cursor.fetchone()
				if questionDtls:
					answers = {'answer':questionDtls.get('answer'),
								'correct_optionId':questionDtls.get('correct_optionId'),
								'Additional_Text':questionDtls.get('Additional_Text')}

					questionDtls.pop('answer')
					questionDtls.pop('correct_optionId')
					questionDtls.pop('Additional_Text')
					cursor.execute("""SELECT `Option_ID`, `Question_ID`, `Option`, `Option_Sequence_ID`,
						`Content_file_path`, `Content_FileName`, `File_Type_ID` 
						FROM `options` WHERE `Question_ID` = %s""",(qid.get('Question_ID')))

					options = cursor.fetchall()
					questionDtls['options'] = options
					questionDtls['answers'] = answers

					questionList.append(questionDtls)

		cursor.close()
		return ({"attributes": {"status_desc": "Question Details",
								"status": "success"
									},
				"responseList":questionList}), status.HTTP_200_OK

@name_space.route("/submitStudentAssessmemtAnswers/<int:student_id>/<int:assessment_id>")
class submitStudentAssessmemtAnswers(Resource):
	@api.expect(submit_answers)
	def post(self, student_id, assessment_id):
		connection = connnect_userLibrary()
		cursor = connection.cursor()

		details = request.get_json()

		answerDtls = details.get('answer_details')

		answerInsertQuery = ("""INSERT INTO `student_answers`(`Assessment_ID`, `Student_ID`, 
			`Question_ID`, `Option_ID`, `Answer`, `answersheet_filepath`, `filetype`, 
			`student_remark`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""")

		for aid, ans in enumerate(answerDtls):

			question_id = ans.get('question_id')
			option_id = ans.get('option_id')
			answer = ans.get('answer')
			answer_filepath = ans.get('answer_filepath')
			filetype = ans.get('filetype')
			remark = ans.get('remark')

			answerData = (assessment_id,student_id,question_id,option_id,answer,answer_filepath,
				filetype,remark)

			cursor.execute(answerInsertQuery,answerData)

		assmentMappingUpdate = ("""UPDATE `student_assessment_mapping` SET `status` = %s 
			WHERE `student_id` = %s and `assessment_id` = %s""")

		assmentUpdateData = (details.get('status'),student_id, assessment_id)

		cursor.execute(assmentMappingUpdate,assmentUpdateData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Answer Submission Details",
								"status": "success"},
				"responseList": 'Answers Submitted Successfully'}), status.HTTP_200_OK



@name_space.route("/getStudentAnswersByAssessmentId/<int:student_id>/<int:assessment_id>")
class getStudentAnswersByAssessmentId(Resource):
	def get(self, student_id, assessment_id):

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT concat(`student_assesssment_filepath`,`student_assesssment_filename`) as 'student_assesssment_filepath',
			`student_assessment_filetype`,`total_marks`,`teacher_feedback` FROM `student_assessment_mapping` 
			WHERE `student_id` = %s and `assessment_id` = %s""",(student_id,assessment_id))

		fileDtls = cursor.fetchone()

		# getQuestionsURL = BASE_URL_LOCAL + 'user_library_assessments/assessmentsController/getQuestionByAssessmentId/{}'.format(assessment_id)
		getQuestionsURL = BASE_URL + 'user_library_assessments/assessmentsController/getQuestionByAssessmentId/{}'.format(assessment_id)

		getQuestions = requests.get(getQuestionsURL).json()
		# print(getQuestions)
		questionList = getQuestions.get('responseList')

		for qid, ques in enumerate(questionList):

			 cursor.execute("""SELECT `Option_ID`,`Answer`,`answersheet_filepath`,`filetype`,
			 	`student_remark`,`marks`,`teacher_remark` FROM `student_answers` WHERE `Assessment_ID` = %s
			 	and `Student_ID` = %s and `Question_ID` =  %s""",(assessment_id,student_id,ques.get('Question_ID')))


			 studentAns = cursor.fetchone()

			 if studentAns:
			 	ques['studentAnswer'] = studentAns
			 else:
			 	ques['studentAnswer'] = {}

		cursor.close()
		return ({"attributes": {"status_desc": "Student Answer Details",
								"status": "success",
								"fileDtls":fileDtls},
				"responseList": questionList}), status.HTTP_200_OK


@name_space.route("/submitMarksOnAssessment/<int:student_id>/<int:assessment_id>")
class submitMarksOnAssessment(Resource):
	@api.expect(submit_marks)
	def put(self, student_id, assessment_id):

		details = request.get_json()

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		marks_details = details.get('marks_details')

		marksUpdateQuery = ("""UPDATE `student_answers` SET `marks` = %s,`teacher_remark` = %s 
			WHERE `Student_ID` = %s and `Assessment_ID` = %s and `Question_ID` = %s""")

		for mid, marks in enumerate(marks_details):

			question_id = marks.get('question_id')
			mark = marks.get('marks')
			remarks = marks.get('remarks')

			marksData = (mark,remarks,student_id, assessment_id, question_id)

			cursor.execute(marksUpdateQuery,marksData)

		markedUpdateQuery = ("""UPDATE `student_assessment_mapping` SET `status` = %s 
			where `student_id` = %s and `assessment_id` = %s""")

		markedData = ('marked',student_id, assessment_id)

		cursor.execute(markedUpdateQuery,markedData)

		connection.commit()

		cursor.close()

		return ({"attributes": {"status_desc": "Submit Marks",
								"status": "success"},
				"responseList": 'Marks Submitted Successfully'}), status.HTTP_200_OK

@name_space.route("/submitFeedbackOnAssessment/<int:student_id>/<int:assessment_id>")
class submitFeedbackOnAssessment(Resource):
	@api.expect(feedback_model)
	def put(self, student_id, assessment_id):

		details = request.get_json()

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		feedback = details.get('feedback')
		total_marks = details.get('total_marks')
		if feedback:
			feedbackUpdateQuery = ("""UPDATE `student_assessment_mapping` SET `teacher_feedback` = %s 
				where `student_id` = %s and `assessment_id` = %s""")

			feedbackData = (feedback,student_id, assessment_id)
			cursor.execute(feedbackUpdateQuery,feedbackData)
		if total_marks:
			marksUpdateQuery = ("""UPDATE `student_assessment_mapping` SET `total_marks` = %s,
				`status` = %s where `student_id` = %s and `assessment_id` = %s""")

			marksData = (total_marks,'marked',student_id, assessment_id)
			cursor.execute(marksUpdateQuery,marksData)

		connection.commit()

		cursor.close()

		return ({"attributes": {"status_desc": "Feedback and Marks Details",
								"status": "success"},
				"responseList": 'Submitted Successfully'}), status.HTTP_200_OK



@name_space.route("/getStudentListByAssessmentId/<int:assessment_id>")
class getStudentListByAssessmentId(Resource):
	def get(self, assessment_id):

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		conn = connect_logindb()
		cur = conn.cursor()

		cursor.execute("""SELECT `student_id`,`status`, `teacher_feedback` FROM `student_assessment_mapping` 
			WHERE `assessment_id` = %s""",(assessment_id))


		studentList = cursor.fetchall()

		for i, sid in enumerate(studentList):
			cur.execute("""SELECT concat(`FIRST_NAME`," ",`LAST_NAME`) as name, 
				`image_url` as student_image FROM `institution_user_credential` 
				WHERE `INSTITUTION_USER_ID` = %s""",(sid.get('student_id')))
				
			student_name = cur.fetchone()
			if student_name:
				sid['student_name']  = student_name.get('name')
				sid['student_image'] = student_name.get('student_image')
					
		return ({"attributes": {"status_desc": "Student Details",
								"status": "success"},
				"responseList": studentList}), status.HTTP_200_OK
		

@name_space.route("/uploadStudentAssessmentFile")
class uploadStudentAssessmentFile(Resource):
	@api.expect(student_assessment_upload)
	def post(self):
		connection = connnect_userLibrary()
		cursor = connection.cursor()

		details = request.get_json()
		assessment_filetype = details.get('assessment_filetype')
		student_id = details.get('student_id')
		assessment_id = details.get('assessment_id')

		filepath = details.get('asssessment_filepath')
		if filepath:
			split_filepath = filepath.split('/')
			asssessment_filepath = "/".join(split_filepath[:-1]) + '/'
			asssessment_filename = filepath.split('/')[-1]
		else:
			asssessment_filepath = None
			asssessment_filename = None


		updateStudentAsmntfile = ("""UPDATE `student_assessment_mapping` SET 
			`student_assesssment_filepath` = %s,`student_assesssment_filename` = %s,
			`student_assessment_filetype` = %s,`status` = %s WHERE `student_id` = %s 
			and `assessment_id` = %s""")

		fileData = (asssessment_filepath,asssessment_filename,assessment_filetype,'c',student_id,assessment_id)

		cursor.execute(updateStudentAsmntfile,fileData)

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Student Assessment Upload Details",
								"status": "success"},
				"responseList": 'File Uploaded Successfully'}), status.HTTP_200_OK