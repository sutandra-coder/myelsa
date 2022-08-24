from flask import Flask, request, jsonify, json
from flask_api import status
import datetime
from datetime import datetime,timedelta,date
import pymysql
from flask_cors import CORS, cross_origin
from flask import Blueprint
from flask_restplus import Api, Resource, fields
import requests
import utils
import collections
from threading import Thread
import time

app = Flask(__name__)
cors = CORS(app)

'''def connnect_userLibrary():
	connection = pymysql.connect(host='creamsonservices.com',
									user='creamson_langlab',
									password='Langlab@123',
									db='creamson_user_library',
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


onlinetest_section = Blueprint('onlinetest_api', __name__)
api = Api(onlinetest_section,  title='MyElsa API',description='MyElsa API')
name_space = api.namespace('OnlineTestController',description='Online Test')

create_onlinetest_assessment = api.model('create_onlinetest_assessment', {
	"teacher_id":fields.Integer(required=True),
	"assessment_desc":fields.String(required=True),
	"online_test_section":fields.String(required=True),
	"subject_id":fields.Integer(required=True),
	"topic_id":fields.Integer(required=True),
	"content_filepath":fields.String(),
	"content_filetype":fields.String(),
	"online_testId":fields.Integer(),
	"institution_id":fields.Integer()
	})

update_onlinetest_assessment = api.model('update_onlinetest_assessment', {
	"assessment_desc":fields.String(required=True),
	"online_test_section":fields.String(required=True),
	"content_filepath":fields.String(),
	"content_filetype":fields.String()
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
	"marks":fields.Integer(),
	"answers": fields.List(fields.Nested(answers_model)),
	"options":fields.List(fields.Nested(options_model)),
	"negative_marks":fields.String(),
	})

add_questions_model = api.model('add_questions_model', {
			"questions":fields.List(fields.Nested(upload_question_model)),
			"assessment_id":fields.Integer(),
			"teacher_id":fields.Integer(),
			"subject_id":fields.Integer(),
			"topic_id":fields.Integer(),
		})


update_attendance = api.model('update_attendance_model', {
	"user_id":fields.Integer(),
	"onlinetest_id":fields.Integer(),
	"platform":fields.String()
	})


update_answer_and_marks = api.model('update_answer_and_marks', {
	"onlinetest_id":fields.Integer(),
	"updated_questions":fields.List(fields.Integer()),
	})

onlinetest_intropage = api.model('onlinetest_intropage_model ', {
	"onlinetest_id":fields.Integer(),
	"intoduction_text":fields.String(),
	})

BASE_URL = 'http://ec2-18-191-221-235.us-east-2.compute.amazonaws.com/'

@name_space.route("/createOnlineTestAssessment")
class createOnlineTestAssessment(Resource):
	@api.expect(create_onlinetest_assessment)
	def post(self):

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		details = request.get_json()

		teacher_id = details.get('teacher_id')
		assessment_desc = details.get('assessment_desc')
		online_test_section = details.get('online_test_section')
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
		featureFlag = "online_test"
		online_testId = details.get('online_testId')
		institution_id = details.get('institution_id')

		assessmentInsertQuery = ("""INSERT INTO `assessment`(`Assesment_Desc`, `teacher_id`, 
			`subject_id`, `topic_id`, `Content_File_Path`, `Content_FileName`, 
			`FileType_Id`, `feature_flag`, `Institution_Id`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		assessmentData = (assessment_desc,teacher_id,subject_id,topic_id,content_filepath,content_filename,
			content_filetype,featureFlag,institution_id)

		curLib.execute(assessmentInsertQuery,assessmentData)

		assessmentId = curLib.lastrowid
		details['assessmentId'] = assessmentId

		testAssessmentMapQuery = ("""INSERT INTO `online_test_assesment_mapping`(`Institution_ID`, 
			`teacher_id`, `online_test_id`, `assessment_id`, `Section_Name`) VALUES (%s,%s,%s,%s,%s)""")

		mapData = (institution_id,teacher_id,online_testId,assessmentId,online_test_section)

		curLib.execute(testAssessmentMapQuery,mapData)

		mappingId = curLib.lastrowid
		details['testAssessmentMapId'] = mappingId
		connection.commit()
		curLib.close()
		return ({"attributes": {"status_desc": "Online Test Assessment Details",
								"status": "success"
									},
				"responseList":details}), status.HTTP_200_OK


@name_space.route("/getAssessmentsByOnlineTestId/<int:online_testId>")
class getAssessmentsByOnlineTestId(Resource):
	def get(self,online_testId):

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		curLib.execute("""SELECT `Assesment_Desc`,concat(`Content_File_Path`,`Content_FileName`) as 
			'Content_File_Path',`FileType_Id`,date(ass.`Last_Update_TS`) as 'created_on', 
			ots.`assessment_id`,`Section_Name`,ass.`subject_id`,sub.`subject_name`, ass.`topic_id`,
			top.`topic_name` FROM `assessment` ass inner JOIN subject sub 
			on ass.`subject_id` = sub.`subject_id` inner JOIN topic top 
			on ass.`topic_id` = top.`topic_id` inner JOIN `online_test_assesment_mapping` ots 
			on ass.`Assessment_ID` = ots.`Assessment_ID` 
			WHERE `online_test_id` = %s""",(online_testId))


		assessmentDtls = curLib.fetchall()

		for aid, assess in enumerate(assessmentDtls):
			assess['created_on'] = assess.get('created_on').isoformat()

		curLib.close()
		return ({"attributes": {"status_desc": "Online Test Assessment Details",
								"status": "success"
									},
				"responseList":assessmentDtls}), status.HTTP_200_OK

@name_space.route("/updateOnlineTestAssessmentByAssessmentId/<int:assessmentId>")
class updateOnlineTestAssessmentByAssessmentId(Resource):
	@api.expect(update_onlinetest_assessment)
	def put(self,assessmentId):

		connection = connnect_userLibrary()
		curLib = connection.cursor()
		details = request.get_json()
		msg = 'Assessment updated not successful.'
		assessment_desc = details.get('assessment_desc')
		online_test_section = details.get('online_test_section')
		filepath = details.get('content_filepath')
		if filepath:
			split_filepath = filepath.split('/')
			content_filepath = "/".join(split_filepath[:-1]) + '/'
			content_filename = filepath.split('/')[-1]
		else:
			content_filepath = None
			content_filename = None
		content_filetype = details.get('content_filetype')

		curLib.execute("""SELECT `Assesment_Desc`,`Content_File_Path`,`Content_FileName`,
			`FileType_Id`,`Section_Name` FROM `assessment` ass 
			inner JOIN `online_test_assesment_mapping` ots 
			on ass.`Assessment_ID` = ots.`Assessment_ID` 
			WHERE ass.`Assessment_ID` = %s""",(assessmentId))


		assessmentDtls = curLib.fetchone()

		if assessmentDtls:
			msg = 'Assessment updated successfully.'
			if not assessment_desc:
				assessment_desc = assessmentDtls.get('Assesment_Desc')
			if not content_filepath:
				content_filepath = assessmentDtls.get('Content_File_Path')
			if not content_filename:
				content_filename = assessmentDtls.get('Content_FileName')
			if not content_filetype:
				content_filetype = assessmentDtls.get('FileType_Id')
			if not online_test_section:
				online_test_section = assessmentDtls.get('Section_Name')


			updateAssessmentQuery = ("""UPDATE `assessment` SET  `Assesment_Desc` = %s,
				`Content_File_Path` = %s,`Content_FileName`= %s,`FileType_Id` = %s
				WHERE `Assessment_ID` = %s""")

			assessmentData = (assessment_desc,content_filepath,content_filename,content_filetype,
				assessmentId)

			curLib.execute(updateAssessmentQuery,assessmentData)

			updateAssessmentMapping = ("""UPDATE `online_test_assesment_mapping` SET `Section_Name` = %s 
				WHERE `assessment_id` = %s""")

			mappingData = (online_test_section,assessmentId)

			curLib.execute(updateAssessmentMapping,mappingData)

		connection.commit()
		curLib.close()

		return ({"attributes": {"status_desc": "Online Test Assessment Update Details",
								"status": "success"
									},
				"responseList":msg}), status.HTTP_200_OK


@name_space.route("/deleteOnlineTestAssessmentByAssessmentId/<int:assessmentId>")
class deleteOnlineTestAssessmentByAssessmentId(Resource):
	def delete(self,assessmentId):

		connection = connnect_userLibrary()
		curLib = connection.cursor()

		deleteAssessmentQuery = ("""DELETE FROM `assessment` WHERE `Assessment_ID` = %s""")

		curLib.execute(deleteAssessmentQuery,(assessmentId))

		deleteQuesAssessmentMap = ("""DELETE FROM `assessment_question_mapping` WHERE `Assessment_ID` = %s""")

		curLib.execute(deleteQuesAssessmentMap,(assessmentId))

		deleteAssessmentMapping = ("""DELETE FROM `online_test_assesment_mapping` WHERE `assessment_id` = %s""")

		curLib.execute(deleteAssessmentMapping,(assessmentId))

		msg = 'Assessment deleted successfully.'
		connection.commit()
		curLib.close()

		return ({"attributes": {"status_desc": "Online Test Assessment delete Details",
								"status": "success"
									},
				"responseList":msg}), status.HTTP_200_OK


@name_space.route("/createQuestionForOnlineTestAssessment")
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
			`subject_id`, `topic_id`, `marks`,`level`, `teacher_id`,`negative_marks`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

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
			marks = each_ques.get('marks',None)
			if each_ques.get('negative_marks'):
				negative_marks = each_ques.get('negative_marks',0)
			else:
				negative_marks = 0
			answerDtls = each_ques.get('answers')
			optionDtls = each_ques.get('options')
			# each_ques.get('last_update_ts'] = last_update_ts

			questionData = (question_type,question,question_content_file_path,question_content_filename,
				question_filetype_id,content_id,subject_id,topic_id,marks,level,teacher_id,negative_marks)

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

			for aid, ans in enumerate(answerDtls):
				answer = ans.get('answer')
				answer_additional_text = ans.get('answer_additional_text')

				cursor.execute("""SELECT `Option_ID` from options where `Question_ID` = %s
					and `Option` = %s""",(questionId,answer))

				optionId = cursor.fetchone()
				option_id = optionId.get('Option_ID',0)

				answerData = (questionId,option_id,answer_additional_text)

				cursor.execute(answerInsertQuery,answerData)

			utils.assessment_question_mapping(assessment_id,questionId)
		
		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Question Details",
								"status": "success"
									},
				"responseList":details}), status.HTTP_200_OK


@name_space.route("/getOnlineTestQuestionByAssessmentId/<int:assessment_id>")
class getOnlineTestQuestionByAssessmentId(Resource):
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
					ques.`Content_FileName`, ques.`File_Type_ID`, ques.`subject_id`, ques.`negative_marks`,
					sub.`subject_name`, top.`topic_name`, ques.`topic_id`, ques.`level`, ques.`marks`,
					GROUP_CONCAT((select op1.`option` from options op1 where op1.`option_ID` = ans.`Option_ID`) SEPARATOR '|') answer, 
					GROUP_CONCAT(ans.`Option_ID` SEPARATOR '|') as 'correct_optionId', GROUP_CONCAT(ans.`Additional_Text` SEPARATOR '|') as 'Additional_Text',
					GROUP_CONCAT((select op1.`Content_file_path` from options op1 where op1.`option_ID` = ans.`Option_ID`) SEPARATOR '|') as 'answer_filepath'
					FROM `question` ques, `answer` ans, `options` op, `subject` sub, `topic` top, 
					`assessment_type` ast WHERE ques.`Question_ID` = ans.`Question_ID` 
					AND ans.`Option_ID` = op.`Option_ID` AND ques.`subject_id` = sub.`subject_id` 
					and ques.`topic_id` = top.`topic_id` AND ast.`Assessment_Type_ID` = ques.`Question_Type` 
					AND ques.`Question_ID` = %s""",(qid.get('Question_ID')))


				questionDtls = cursor.fetchone()
				answers = []
				if questionDtls:
					if questionDtls.get('Assessment_Type_Desc') == 'MSQ':
						correct_ans = questionDtls.get('answer')
						if correct_ans:
							correct_ans = questionDtls.get('answer').split('|')

						correct_option = questionDtls.get('correct_optionId')
						if correct_option:
							correct_option = questionDtls.get('correct_optionId').split('|')
						addition_ans_text = []

						answer_filepath = questionDtls.get('answer_filepath')
						if answer_filepath:
							answer_filepath = questionDtls.get('answer_filepath').split('|')
						
						# print(addition_ans_text)
						if correct_ans and not answer_filepath:
							for aid, ans in enumerate(correct_ans):
								if questionDtls.get('Additional_Text'):
									addition_ans_text = questionDtls.get('Additional_Text').split('|')
								else:
									addition_ans_text = None
								answers.append({'answer':correct_ans[aid],
											'correct_optionId':correct_option[aid],
											'answer_filepath':answer_filepath,
											'Additional_Text':addition_ans_text})
						elif answer_filepath and not correct_ans:
							for aid, ans in enumerate(correct_ans):
								if questionDtls.get('Additional_Text'):
									addition_ans_text = questionDtls.get('Additional_Text').split('|')
								else:
									addition_ans_text = None
								answers.append({'answer':correct_ans,
											'correct_optionId':correct_option[aid],
											'answer_filepath':answer_filepath[aid],
											'Additional_Text':addition_ans_text})
						elif correct_ans and answer_filepath:
							for aid, ans in enumerate(correct_ans):
								if questionDtls.get('Additional_Text'):
									addition_ans_text = questionDtls.get('Additional_Text').split('|')
								else:
									addition_ans_text = None
								answers.append({'answer':correct_ans[aid],
											'correct_optionId':correct_option[aid],
											'answer_filepath':answer_filepath[aid],
											'Additional_Text':addition_ans_text})
						else:
							answers.append({'answer':correct_ans,
											'correct_optionId':correct_option,
											'answer_filepath':answer_filepath,
											'Additional_Text':addition_ans_text})

					else:
						answers.append({'answer':questionDtls.get('answer'),
										'correct_optionId':questionDtls.get('correct_optionId'),
										'answer_filepath':questionDtls.get('answer_filepath'),
										'Additional_Text':questionDtls.get('Additional_Text')})

					questionDtls.pop('answer')
					questionDtls.pop('correct_optionId')
					questionDtls.pop('answer_filepath')
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


@name_space.route("/getFullOnlineTestByTestId/<int:online_testId>")
class getFullOnlineTestByTestId(Resource):
	def get(self,online_testId):

		connection = connnect_userLibrary()
		cursor = connection.cursor()


		assessmentURL = BASE_URL + 'onlinetest_section/OnlineTestController/getAssessmentsByOnlineTestId/{}'.format(online_testId)

		assessmentDtls = requests.get(assessmentURL).json().get('responseList')
		# print(assessmentDtls)

		if assessmentDtls:
			for aid, assess in enumerate(assessmentDtls):
				assessment_id = assess.get('assessment_id')
				quesURL = BASE_URL + 'onlinetest_section/OnlineTestController/getOnlineTestQuestionByAssessmentId/{}'.format(assessment_id)
				quesDtls = requests.get(quesURL).json().get('responseList')

				assess['questionDtls'] = quesDtls

		return ({"attributes": {"status_desc": "Online Test Details",
								"status": "success"
									},
				"responseList":assessmentDtls}), status.HTTP_200_OK



@name_space.route("/getStudentAnswersByOnlineTestId/<int:student_id>/<int:onlinetest_id>")
class getStudentAnswersByOnlineTestId(Resource):
	def get(self, student_id, onlinetest_id):

		connection = connnect_userLibrary()
		cursor = connection.cursor()
		fileList = []
		totatMarks = 0
		cursor.execute("""SELECT `Assesment_Desc`,concat(`Content_File_Path`,`Content_FileName`) as 
			'Content_File_Path',`FileType_Id`,date(ass.`Last_Update_TS`) as 'created_on', 
			ots.`assessment_id`,`Section_Name`,ass.`subject_id`,sub.`subject_name`, ass.`topic_id`,
			top.`topic_name` FROM `assessment` ass inner JOIN subject sub 
			on ass.`subject_id` = sub.`subject_id` inner JOIN topic top 
			on ass.`topic_id` = top.`topic_id` inner JOIN `online_test_assesment_mapping` ots 
			on ass.`Assessment_ID` = ots.`Assessment_ID` 
			INNER JOIN `online_test` ot on ots.`Online_Test_ID` = ot.`Online_Test_ID`
			WHERE ots.`online_test_id` = %s""",(onlinetest_id))


		assessmentDtls = cursor.fetchall()

		cursor.execute("""SELECT `Marks`,`No_Of_attempts`,`is_reviwed` FROM `online_test_student_marks` 
			WHERE `Online_Test_ID` = %s AND `Student_ID` = %s""",(onlinetest_id,student_id))
		totalmarksDict = cursor.fetchone()
		if totalmarksDict:
			totalOnlineTestMarks = totalmarksDict.get('Marks',0)
		else:
			totalOnlineTestMarks = 0

		for aid, assess in enumerate(assessmentDtls):
			assess['created_on'] = assess.get('created_on').isoformat()

			cursor.execute("""SELECT `Marks` FROM `online_assesment_student_marks` WHERE 
				`Online_Test_ID` = %s and `Online_assesment_ID` = %s 
				AND `Student_ID` = %s""",(onlinetest_id,assess.get('assessment_id'),student_id))

			assessmentMarksDict = cursor.fetchone()
			if assessmentMarksDict:
				assessMarks =  assessmentMarksDict.get('Marks',0)
			else:
				assessMarks = 0
			assess['assessmentMarks'] = assessMarks
			cursor.execute("""SELECT `student_assesssment_filepath`,`student_assesssment_filename`,
				`student_assessment_filetype`,`total_marks`,`teacher_feedback` FROM `student_assessment_mapping`
				WHERE `student_id` = %s and `assessment_id` = %s""",(student_id,assess.get('assessment_id')))

			fileDtls = cursor.fetchone()
			fileList.append(fileDtls)
			getQuestionsURL = BASE_URL + 'onlinetest_section/OnlineTestController/getOnlineTestQuestionByAssessmentId/{}'.format(assess.get('assessment_id'))

			getQuestions = requests.get(getQuestionsURL).json()
			# print(getQuestions)
			questionList = getQuestions.get('responseList')
			for qid, ques in enumerate(questionList):

				cursor.execute("""SELECT `Option_ID`,`Answer`,`answersheet_filepath`,`filetype`,
				 	`student_remark`,`marks`,`teacher_remark` FROM `student_answers` WHERE `Assessment_ID` = %s
				 	and `Student_ID` = %s and `Question_ID` =  %s order by `Last_Update_TS`
				 	desc limit 1""",(assess.get('assessment_id'),student_id,ques.get('Question_ID')))


				studentAns = cursor.fetchall()

				if studentAns:
					ques['studentAnswer'] = studentAns
				else:
					ques['studentAnswer'] = []
				if ques.get('marks'):
					totatMarks += ques.get('marks',0)
			assess['questionDtls'] = questionList
		cursor.close()
		return ({"attributes": {"status_desc": "Student Answer Details",
								"status": "success",
								"fileDtls":fileList,
								"studentTotalMarks":totalOnlineTestMarks,
								"TestTotalMarks":totatMarks},
				"responseList": assessmentDtls}), status.HTTP_200_OK


@name_space.route("/markAttendanceForOnlineTest")
class markAttendanceForOnlineTest(Resource):
	@api.expect(update_attendance)
	def put(self):

		details = request.get_json()

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		user_id = details.get('user_id')
		onlinetest_id = details.get('onlinetest_id')
		platform  = details.get('platform')

		updateAttendanceQuery = ("""UPDATE `online_test_student_mapping` SET `attendance` = 'p', 
			`platform` = %s WHERE `online_test_id` = %s and `Institution_user_ID` = %s""")


		cursor.execute(updateAttendanceQuery,(platform,onlinetest_id,user_id))

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Online Test Attendance Details",
								"status": "success"
									},
				"responseList":'Attendance has been marked'}), status.HTTP_200_OK



def syncCorrectAnswers(details):
	connection = connnect_userLibrary()
	cursor = connection.cursor()
	marks = 0
	onlinetest_id = details.get('onlinetest_id')
	updatedQuestions = details.get('updated_questions')
	print(updatedQuestions)
	cursor.execute("""SELECT DISTINCT `Institution_user_ID` FROM `online_test_student_mapping` 
		WHERE `online_test_id` = %s and `status` = 'y'""",(onlinetest_id))

	studentListDtls = cursor.fetchall()

	for qid in updatedQuestions:

		cursor.execute("""SELECT GROUP_CONCAT(ans.`Option_ID` SEPARATOR ',') as 'answer',`marks`, 
			`negative_marks`, GROUP_CONCAT(`Option` SEPARATOR '|') as 'option' FROM `answer` ans, 
			question q, `options` op WHERE ans.`Question_ID` = q.`Question_ID` 
			and ans.`Question_ID` = op.`Question_ID` and ans.`Option_ID` = op.`Option_ID` 
			and ans.`Question_ID` = %s""",(qid))

		correctAnsDtls = cursor.fetchone()
		correctAns = correctAnsDtls['answer'].split(',')
		CorrectOptions = correctAnsDtls['option'].split('|')
		for sid, student in enumerate(studentListDtls):
			cursor.execute("""SELECT `Student_Answer_Tracking_Id`,`Option_ID` FROM `student_answers` 
				WHERE `Student_ID` = %s and `Question_ID` = %s 
				order by `Last_Update_TS` desc limit 1""",(student['Institution_user_ID'],qid))
				
			studentAnsDtls = cursor.fetchone()
			studentAns = studentAnsDtls['Option_ID'].split(',')
			updateMarksQuery = ("""UPDATE `student_answers` SET `marks` = %s 
					where `Student_Answer_Tracking_Id` = %s""")
			if collections.Counter(studentAns) == collections.Counter(correctAns):
				marks = correctAnsDtls.get('marks')
				print('if')
			else:
				marks = correctAnsDtls.get('negative_marks')
				print('else')
			cursor.execute(updateMarksQuery,(marks,studentAnsDtls.get('Student_Answer_Tracking_Id')))

	return {'studentAnsDtls':studentAns,
			'correctAnsDtls':correctAns}


class Compute(Thread):
	def __init__(self, request, funcname):
		Thread.__init__(self)
		self.request = request
		self.funcname = funcname

	def run(self):
		time.sleep(5)
		if self.funcname == 'updateStudentAnswersAndMarks':
			syncCorrectAnswers(self.request)
		else:
			pass

@name_space.route("/updateStudentAnswersAndMarks")
class updateStudentAnswersAndMarks(Resource):
	@api.expect(update_answer_and_marks)
	def put(self):

		details = request.get_json()

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		sendrReq = (details)
		thread_a = Compute(sendrReq,'updateStudentAnswersAndMarks')
		thread_a.start()
		
		return ({"attributes": {"status_desc": "Online Test Marks Uodate",
								"status": "success"
									},
				"responseList":'Marks will be updated'}), status.HTTP_200_OK



@name_space.route("/createOnlineTestIntroductionPage")
class createOnlineTestIntroductionPage(Resource):
	@api.expect(onlinetest_intropage)
	def post(self):

		details = request.get_json()

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		introInsertQuery = ("""INSERT INTO `onlinetest_introduction`(`introduction_text`) VALUES (%s)""")

		cursor.execute(introInsertQuery,(details.get('intoduction_text'),))
		introID = cursor.lastrowid
		details['introduction_id'] = introID

		updateQuery = ("""UPDATE `online_test` SET `introduction_id` = %s 
			WHERE `Online_Test_ID` = %s""")

		cursor.execute(updateQuery,(introID,details.get('onlinetest_id')))

		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Introduction details",
								"status": "success"
									},
				"responseList":details}), status.HTTP_200_OK



@name_space.route("/duplicateOnlineTest/<int:onlinetest_id>")
class duplicateOnlineTest(Resource):
	def post(self,onlinetest_id):

		details = {}

		connection = connnect_userLibrary()
		cursor = connection.cursor()

		cursor.execute("""SELECT `Institution_ID`,`Institution_user_ID`,`Title`,`Total_Marks`,
			`duration`,`Description`,`introduction_id`,`Subject_id`,`Topic_id`,`Class`,`Board` 
			FROM `online_test` WHERE `Online_Test_ID` = %s""",(onlinetest_id))

		testIdDtls = cursor.fetchone()

		onlinetestInsertQuery = ("""INSERT INTO `online_test`(`Institution_ID`, `Institution_user_ID`, 
			`Title`, `Total_Marks`, `duration`, `Description`, `introduction_id`, `Subject_id`, 
			`Topic_id`, `Class`, `Board`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")

		testData = (testIdDtls['Institution_ID'],testIdDtls['Institution_user_ID'],testIdDtls['Title']+'-duplicate',
			testIdDtls['Total_Marks'],testIdDtls['duration'],testIdDtls['Description'],
			testIdDtls['introduction_id'],testIdDtls['Subject_id'],testIdDtls['Topic_id'],testIdDtls['Class'],
			testIdDtls['Board'])

		cursor.execute(onlinetestInsertQuery,testData)

		newTestId = cursor.lastrowid

		details['onlinetest_id'] = newTestId
		details['assessments'] = []

		cursor.execute("""SELECT `Institution_ID`,`teacher_id`,`Section_Name`,`assessment_id` FROM 
			`online_test_assesment_mapping` WHERE `online_test_id` = %s""",(onlinetest_id))


		onlineTestDtls = cursor.fetchall()

		assessmentTestMapQuery = ("""INSERT INTO `online_test_assesment_mapping`(`Institution_ID`, 
			`teacher_id`, `online_test_id`, `assessment_id`, 
			`Section_Name`) VALUES (%s,%s,%s,%s,%s)""")

		assessInsertQuery = ("""INSERT INTO `assessment`(`Assesment_Desc`, `Institution_Id`, 
			`teacher_id`, `subject_id`, `topic_id`, `Content_File_Path`, `Content_FileName`, 
			`FileType_Id`, `feature_flag`, 
			`assessment_duration`, `Assessment_Status`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""")


		assessQuesInsertQuery = ("""INSERT INTO `assessment_question_mapping`(`Assessment_ID`, 
			`Question_ID`) VALUES (%s,%s)""")
 
		for oid, test in enumerate(onlineTestDtls):

			cursor.execute("""SELECT `Assesment_Desc`,`Institution_Id`,`teacher_id`,`subject_id`,
				`topic_id`,`Content_File_Path`,`Content_FileName`,`FileType_Id`,`feature_flag`,
				`assessment_duration`,`Assessment_Status` FROM `assessment` WHERE `Assessment_ID` = %s""",(test['assessment_id']))

			assessDtl = cursor.fetchone()

			assessData = (assessDtl['Assesment_Desc'],assessDtl['Institution_Id'],assessDtl['teacher_id'],
					assessDtl['subject_id'],assessDtl['topic_id'],assessDtl['Content_File_Path'],assessDtl['Content_FileName'],
					assessDtl['FileType_Id'],assessDtl['feature_flag'],assessDtl['assessment_duration'],assessDtl['Assessment_Status'])

			cursor.execute(assessInsertQuery,assessData)

			assessId = cursor.lastrowid
			details['assessments'].append(assessId)
			assessTestMapData = (test['Institution_ID'],test['teacher_id'],newTestId,
				assessId,test['Section_Name'])

			cursor.execute(assessmentTestMapQuery,assessTestMapData)

			cursor.execute("""SELECT `Question_ID` FROM `assessment_question_mapping` 
				WHERE `Assessment_ID` = %s""",(test['assessment_id']))


			quesDtls = cursor.fetchall()


			for q, qid in enumerate(quesDtls):

				assessQuesData = (assessId,qid['Question_ID'])

				cursor.execute(assessQuesInsertQuery,assessQuesData)


		connection.commit()
		cursor.close()

		return ({"attributes": {"status_desc": "Dulpicate Test details",
								"status": "success"
									},
				"responseList":details}), status.HTTP_200_OK